"""NiceGUI web backend for MBASIC.

Provides a modern web-based UI for the MBASIC interpreter using NiceGUI.
"""

import re
import sys
import asyncio
import traceback
from nicegui import ui, app
from pathlib import Path
from ..base import UIBackend
from src.runtime import Runtime
from src.interpreter import Interpreter
from src.iohandler.base import IOHandler
from src.version import VERSION


def log_web_error(context: str, exception: Exception):
    """Log web UI error to stderr for debugging.

    Args:
        context: Description of where error occurred (e.g., "_menu_run")
        exception: The exception that was caught
    """
    sys.stderr.write(f"\n{'='*70}\n")
    sys.stderr.write(f"WEB UI ERROR in {context}\n")
    sys.stderr.write(f"{'='*70}\n")
    sys.stderr.write(f"Error: {exception}\n")
    sys.stderr.write(f"{'-'*70}\n")
    traceback.print_exc(file=sys.stderr)
    sys.stderr.write(f"{'='*70}\n\n")
    sys.stderr.flush()


class SimpleWebIOHandler(IOHandler):
    """Simple IO handler for NiceGUI that appends to textarea."""

    def __init__(self, output_callback, input_callback):
        """
        Initialize web IO handler.

        Args:
            output_callback: Function to call with output text
            input_callback: Function to call to get input from user (blocking)
        """
        self.output_callback = output_callback
        self.input_callback = input_callback

    def output(self, text: str, end: str = '\n') -> None:
        """Output text to the web UI."""
        output = str(text) + end
        self.output_callback(output)

    def print(self, text="", end="\n"):
        """Output text to the web UI (alias for output)."""
        self.output(str(text), end)

    def input(self, prompt=""):
        """Get input from user via inline input field.

        Uses asyncio.Future for coordination between synchronous interpreter
        and async web UI. The input field appears below the output pane,
        allowing users to see all previous output while typing.
        """
        # Show prompt in output
        if prompt:
            self.print(prompt, end='')

        # Get input from UI (this will block until user enters input)
        result = self.input_callback(prompt)

        # Echo input to output
        self.print(result)

        return result

    def input_line(self, prompt: str = '') -> str:
        """Input complete line from user (LINE INPUT statement)."""
        return self.input(prompt)

    def input_char(self, blocking: bool = True) -> str:
        """Get single character (not implemented for web)."""
        return ""

    def error(self, message: str) -> None:
        """Output error message."""
        self.output(f"Error: {message}\n")

    def debug(self, message: str) -> None:
        """Output debug message."""
        # Don't show debug in web UI output
        pass

    def clear_screen(self):
        """Clear screen (not applicable for textarea)."""
        pass

    def set_cursor_position(self, row, col):
        """Set cursor position (not applicable)."""
        pass

    def get_screen_size(self):
        """Get screen size."""
        return (24, 80)


class NiceGUIBackend(UIBackend):
    """NiceGUI web UI backend.

    Features:
    - Web-based interface accessible via browser
    - Modern, responsive design
    - Split-pane editor and output
    - Menu system
    - File management
    - Execution controls
    - Variables window
    - Breakpoint support

    Based on TK UI feature set (see docs/dev/TK_UI_FEATURE_AUDIT.md).
    """

    def __init__(self, io_handler, program_manager):
        """Initialize NiceGUI backend.

        Args:
            io_handler: IOHandler for I/O operations
            program_manager: ProgramManager instance
        """
        super().__init__(io_handler, program_manager)

        # Program state
        self.program_lines = []  # List of program lines for display
        self.output_lines = []   # Output text lines
        self.current_file = None  # Currently open file path

        # Auto-numbering configuration (like TK)
        self.auto_number_enabled = True      # Enable auto-numbering
        self.auto_number_start = 10          # Starting line number
        self.auto_number_increment = 10      # Increment between lines

        # Recent files (stored in browser localStorage)
        self.recent_files = []  # List of recent file names
        self.max_recent_files = 10

        # Execution state
        self.running = False
        self.paused = False

        # Output buffer limiting
        self.output_max_lines = 3000  # Maximum lines to keep in output buffer
        self.breakpoints = set()  # Line numbers with breakpoints
        self.interpreter = None

        # Initialize a default runtime for immediate mode
        # This gets replaced when a program runs
        from src.runtime import Runtime
        self.runtime = Runtime({}, {})

        self.exec_io = None
        self.tick_task = None  # Async task for execution

        # Output buffer
        self.output_text = 'MBASIC 5.21 Web IDE\nReady\n'

        # UI elements (created in build_ui())
        self.editor = None
        self.output = None
        self.status_label = None
        self.immediate_entry = None  # Immediate mode command input
        self.recent_files_menu = None  # Recent files submenu

        # INPUT row elements (for inline input)
        self.input_row = None
        self.input_label = None
        self.input_field = None
        self.input_submit_btn = None
        self.input_future = None  # Future for async input coordination

    def build_ui(self):
        """Build the NiceGUI interface.

        Creates the main UI with:
        - Menu bar
        - Toolbar
        - Editor pane
        - Output pane
        - Status bar
        """

        # Main page
        @ui.page('/')
        def main_page():
            # Set page title
            ui.page_title('MBASIC 5.21 - Web IDE')

            # Menu bar
            self._create_menu()

            # Toolbar
            with ui.row().classes('w-full bg-gray-100 p-2 gap-2'):
                ui.button('New', on_click=self._menu_new, icon='description').mark('btn_new')
                ui.button('Open', on_click=self._menu_open, icon='folder_open').mark('btn_open')
                ui.button('Save', on_click=self._menu_save, icon='save').mark('btn_save')
                ui.separator().props('vertical')
                ui.button('Run', on_click=self._menu_run, icon='play_arrow', color='green').mark('btn_run')
                ui.button('Stop', on_click=self._menu_stop, icon='stop', color='red').mark('btn_stop')
                ui.button('Step', on_click=self._menu_step, icon='skip_next').mark('btn_step')
                ui.button('Continue', on_click=self._menu_continue, icon='play_circle').mark('btn_continue')

            # Main content area
            with ui.element('div').style('width: 100%; display: flex; flex-direction: column;'):
                # Editor
                self.editor = ui.textarea(
                    value='',
                    placeholder='Program Editor'
                ).style('width: 100%;').props('outlined dense rows=10').mark('editor')
                self.editor.on('keydown.enter', self._on_enter_key)

                # Output
                self.output = ui.textarea(
                    value='MBASIC 5.21 Web IDE\nReady\n',
                    placeholder='Output'
                ).style('width: 100%;').props('readonly outlined dense rows=10').mark('output')

                # INPUT row (hidden by default)
                self.input_row = ui.row().classes('w-full bg-blue-50 q-pa-sm')
                with self.input_row:
                    self.input_label = ui.label('').classes('font-bold text-blue-600')
                    self.input_field = ui.input(placeholder='Enter value...').classes('flex-grow').mark('input_field')
                    self.input_field.on('keydown.enter', self._submit_input)
                    self.input_submit_btn = ui.button('Submit', on_click=self._submit_input, icon='send', color='primary').mark('btn_input_submit')
                self.input_row.visible = False

                # Immediate
                with ui.row().style('width: 100%;'):
                    self.immediate_entry = ui.textarea(
                        value='',
                        placeholder='Command'
                    ).style('width: 100%;').props('outlined dense rows=3').mark('immediate_entry')
                    self.immediate_entry.on('keydown.enter', self._on_immediate_enter)
                    ui.button('Execute', on_click=self._execute_immediate, icon='play_arrow', color='green').mark('btn_immediate')

                # Status
                with ui.row().classes('w-full bg-gray-200 q-pa-xs').style('justify-content: space-between;'):
                    self.status_label = ui.label('Ready').mark('status')
                    ui.label(f'v{VERSION}').classes('text-gray-600')

    def _create_menu(self):
        """Create menu bar."""
        with ui.row().classes('w-full bg-gray-800 text-white p-2 gap-4'):
            # File menu
            with ui.button('File', icon='menu').props('flat color=white'):
                with ui.menu() as file_menu:
                    ui.menu_item('New', on_click=self._menu_new)
                    ui.menu_item('Open...', on_click=self._menu_open)
                    ui.menu_item('Save', on_click=self._menu_save)
                    ui.menu_item('Save As...', on_click=self._menu_save_as)
                    ui.separator()
                    # Recent Files submenu
                    with ui.menu_item('Recent Files'):
                        with ui.menu() as self.recent_files_menu:
                            self._update_recent_files_menu()
                    ui.separator()
                    ui.menu_item('Exit', on_click=self._menu_exit)

            # Run menu
            with ui.button('Run', icon='menu').props('flat color=white'):
                with ui.menu():
                    ui.menu_item('Run Program', on_click=self._menu_run)
                    ui.menu_item('Stop', on_click=self._menu_stop)
                    ui.menu_item('Step', on_click=self._menu_step)
                    ui.menu_item('Continue', on_click=self._menu_continue)
                    ui.separator()
                    ui.menu_item('List Program', on_click=self._menu_list)
                    ui.separator()
                    ui.menu_item('Show Variables', on_click=self._show_variables_window)
                    ui.menu_item('Show Stack', on_click=self._show_stack_window)
                    ui.menu_item('Clear Output', on_click=self._clear_output)

            # Help menu
            with ui.button('Help', icon='menu').props('flat color=white'):
                with ui.menu():
                    ui.menu_item('Help Topics', on_click=self._menu_help)
                    ui.separator()
                    ui.menu_item('About', on_click=self._menu_about)

    # =========================================================================
    # Recent Files Management
    # =========================================================================

    def _load_recent_files(self):
        """Load recent files from localStorage via JavaScript."""
        # This will be called when UI loads
        # For now, start with empty list
        # In a real implementation, we'd use JavaScript to read from localStorage
        self.recent_files = []

    def _save_recent_files(self):
        """Save recent files to localStorage via JavaScript."""
        try:
            # Convert list to JSON and save to localStorage
            import json
            files_json = json.dumps(self.recent_files)
            ui.run_javascript(f'''
                localStorage.setItem('mbasic_recent_files', '{files_json}');
            ''')
        except Exception as e:
            log_web_error("_save_recent_files", e)

    def _add_recent_file(self, filename):
        """Add a file to recent files list."""
        try:
            # Remove if already exists
            if filename in self.recent_files:
                self.recent_files.remove(filename)

            # Add to front
            self.recent_files.insert(0, filename)

            # Limit to max
            self.recent_files = self.recent_files[:self.max_recent_files]

            # Save to localStorage
            self._save_recent_files()

            # Update menu
            self._update_recent_files_menu()

        except Exception as e:
            log_web_error("_add_recent_file", e)

    def _update_recent_files_menu(self):
        """Update Recent Files submenu."""
        try:
            if not self.recent_files_menu:
                return

            # Clear existing items
            self.recent_files_menu.clear()

            # Add recent files
            if self.recent_files:
                for filename in self.recent_files:
                    # Create a closure to capture the filename
                    def make_handler(fname):
                        return lambda: self._open_recent_file(fname)

                    with self.recent_files_menu:
                        ui.menu_item(filename, on_click=make_handler(filename))
            else:
                with self.recent_files_menu:
                    ui.menu_item('(No recent files)', on_click=lambda: None).props('disable')

        except Exception as e:
            log_web_error("_update_recent_files_menu", e)

    def _open_recent_file(self, filename):
        """Open a file from recent files."""
        # For web UI, we can't actually open local files
        # Just show a notification
        self._notify(f'Recent file: {filename}. Use Open to load files.', type='info')
        self._set_status(f'Recent: {filename}')

    # =========================================================================
    # Breakpoint Management
    # =========================================================================

    def _toggle_breakpoint(self):
        """Toggle breakpoint on current line."""
        try:
            # Use JavaScript to get current cursor line
            ui.run_javascript('''
                const textarea = document.querySelector('[data-ref="editor"] textarea');
                if (textarea) {
                    const text = textarea.value;
                    const cursorPos = textarea.selectionStart;
                    // Count newlines before cursor to get line number
                    const textBeforeCursor = text.substring(0, cursorPos);
                    const lineIndex = textBeforeCursor.split('\\n').length - 1;
                    // Get the line text
                    const lines = text.split('\\n');
                    const lineText = lines[lineIndex];
                    // Extract BASIC line number if present
                    const match = lineText.match(/^\\s*(\\d+)/);
                    if (match) {
                        const lineNum = parseInt(match[1]);
                        // Send to Python via custom event
                        window.dispatchEvent(new CustomEvent('toggle-breakpoint', {detail: lineNum}));
                    }
                }
            ''')

            # For now, prompt for line number since we can't easily get cursor position
            # In a real implementation, we'd use JavaScript events to communicate back
            # Simple approach: ask user for line number
            with ui.dialog() as dialog, ui.card():
                ui.label('Toggle Breakpoint')
                line_input = ui.input('Line number:', placeholder='10').classes('w-full')
                with ui.row():
                    ui.button('Toggle', on_click=lambda: self._do_toggle_breakpoint(line_input.value, dialog))
                    ui.button('Cancel', on_click=dialog.close)
            dialog.open()

        except Exception as e:
            log_web_error("_toggle_breakpoint", e)
            self._notify(f'Error: {e}', type='negative')

    def _do_toggle_breakpoint(self, line_num_str, dialog):
        """Actually toggle the breakpoint."""
        try:
            line_num = int(line_num_str)

            if line_num in self.breakpoints:
                self.breakpoints.remove(line_num)
                self._notify(f'Breakpoint removed: line {line_num}', type='info')
                self._set_status(f'Removed breakpoint at {line_num}')
            else:
                self.breakpoints.add(line_num)
                self._notify(f'Breakpoint set: line {line_num}', type='positive')
                self._set_status(f'Breakpoint at {line_num}')

            dialog.close()

        except ValueError:
            self._notify('Please enter a valid line number', type='warning')
        except Exception as e:
            log_web_error("_do_toggle_breakpoint", e)
            self._notify(f'Error: {e}', type='negative')

    # =========================================================================
    # Menu Handlers
    # =========================================================================

    def _menu_new(self):
        """File > New - Clear program."""
        try:
            self.program.clear()
            self.editor.value = ''
            self.current_file = None
            self._set_status('New program')
        except Exception as e:
            log_web_error("_menu_new", e)
            self._notify(f'Error: {e}', type='negative')

    def _menu_open(self):
        """File > Open - Load program from file."""
        try:
            # Create upload dialog
            with ui.dialog() as dialog, ui.card().classes('w-96'):
                ui.label('Open BASIC Program').classes('text-h6 mb-4')
                ui.label('Select a .BAS or .TXT file to open:').classes('mb-2')
                upload = ui.upload(
                    on_upload=lambda e: self._handle_file_upload(e, dialog),
                    auto_upload=True
                ).classes('w-full').props('accept=".bas,.txt"')
                with ui.row().classes('w-full justify-end mt-4'):
                    ui.button('Cancel', on_click=dialog.close)
            dialog.open()
        except Exception as e:
            log_web_error("_menu_open", e)
            self._notify(f'Error: {e}', type='negative')

    def _handle_file_upload(self, e, dialog):
        """Handle file upload from Open dialog."""
        try:
            # Read uploaded file content
            content = e.content.read().decode('utf-8')

            # Load into editor
            self.editor.value = content

            # Parse into program
            self._save_editor_to_program()

            # Store filename
            self.current_file = e.name

            # Add to recent files
            self._add_recent_file(e.name)

            self._set_status(f'Opened: {e.name}')
            self._notify(f'Loaded {e.name}', type='positive')
            dialog.close()

        except Exception as ex:
            log_web_error("_handle_file_upload", ex)
            self._notify(f'Error loading file: {ex}', type='negative')

    def _menu_save(self):
        """File > Save - Save current program."""
        try:
            # If no filename, trigger Save As instead
            if not self.current_file:
                self._menu_save_as()
                return

            # Save editor to program first
            self._save_editor_to_program()

            # Download file with current editor content
            content = self.editor.value
            ui.download(content.encode('utf-8'), self.current_file)

            self._set_status(f'Saved: {self.current_file}')
            self._notify(f'Downloaded {self.current_file}', type='positive')

        except Exception as e:
            log_web_error("_menu_save", e)
            self._notify(f'Error: {e}', type='negative')

    def _menu_save_as(self):
        """File > Save As - Save with new filename."""
        try:
            # Create save dialog
            with ui.dialog() as dialog, ui.card():
                ui.label('Save As')
                filename_input = ui.input(
                    'Filename:',
                    value=self.current_file or 'program.bas',
                    placeholder='program.bas'
                ).classes('w-full')

                with ui.row():
                    ui.button('Save', on_click=lambda: self._handle_save_as(filename_input.value, dialog))
                    ui.button('Cancel', on_click=dialog.close)
            dialog.open()
        except Exception as e:
            log_web_error("_menu_save_as", e)
            self._notify(f'Error: {e}', type='negative')

    def _handle_save_as(self, filename, dialog):
        """Handle Save As dialog."""
        try:
            if not filename:
                self._notify('Please enter a filename', type='warning')
                return

            # Save editor to program first
            self._save_editor_to_program()

            # Update current filename
            self.current_file = filename

            # Download file
            content = self.editor.value
            ui.download(content.encode('utf-8'), filename)

            self._set_status(f'Saved: {filename}')
            self._notify(f'Downloaded {filename}', type='positive')
            dialog.close()

        except Exception as e:
            log_web_error("_handle_save_as", e)
            self._notify(f'Error: {e}', type='negative')

    def _menu_exit(self):
        """File > Exit - Quit application."""
        app.shutdown()

    def _menu_run(self):
        """Run > Run Program - Execute program."""
        if self.running:
            self._set_status('Program already running')
            return

        try:
            # Save editor content to program first
            if not self._save_editor_to_program():
                return  # Parse errors, don't run

            # Check if program has lines
            if not self.program.lines:
                self._set_status('No program loaded')
                self._notify('No program in editor. Add some lines first.', type='warning')
                return

            # Don't clear output - continuous scrolling like ASR33 teletype
            self._set_status('Running...')

            # Get program AST
            program_ast = self.program.get_program_ast()

            # Create runtime and interpreter
            from src.resource_limits import create_local_limits
            self.runtime = Runtime(self.program.line_asts, self.program.lines)

            # Create IO handler that outputs to our output pane
            self.exec_io = SimpleWebIOHandler(self._append_output, self._get_input)
            self.interpreter = Interpreter(self.runtime, self.exec_io, limits=create_local_limits())

            # Wire up interpreter to use this UI's methods
            self.interpreter.interactive_mode = self

            # Start interpreter
            state = self.interpreter.start()
            if state.status == 'error':
                error_msg = state.error_info.error_message if state.error_info else 'Unknown'
                self._append_output(f"\n--- Setup error: {error_msg} ---\n")
                self._set_status('Error')
                return

            # Mark as running
            self.running = True

            # Start async execution - store timer handle so we can cancel it
            self.exec_timer = ui.timer(0.01, self._execute_tick, once=False)

        except Exception as e:
            log_web_error("_menu_run", e)
            self._append_output(f"\n--- Error: {e} ---\n")
            self._set_status(f'Error: {e}')
            self.running = False

    def _execute_tick(self):
        """Execute one tick of the interpreter."""
        # Don't check self.running - it seems to not persist correctly in NiceGUI callbacks
        # Just check if we have an interpreter
        if not self.interpreter:
            return

        try:
            # Execute one tick (up to 1000 statements)
            state = self.interpreter.tick(mode='run', max_statements=1000)

            # Handle state
            if state.status == 'done':
                self._append_output("\n--- Program finished ---\n")
                self._set_status("Ready")
                self.running = False
                if hasattr(self, 'exec_timer') and self.exec_timer:
                    self.exec_timer.cancel()
            elif state.status == 'error':
                error_msg = state.error_info.error_message if state.error_info else "Unknown error"
                self._append_output(f"\n--- Error: {error_msg} ---\n")
                self._set_status("Error")
                self.running = False
                if hasattr(self, 'exec_timer') and self.exec_timer:
                    self.exec_timer.cancel()
            elif state.status == 'paused' or state.status == 'at_breakpoint':
                self._set_status(f"Paused at line {state.current_line}")
                self.running = False
                self.paused = True
                if hasattr(self, 'exec_timer') and self.exec_timer:
                    self.exec_timer.cancel()

        except Exception as e:
            log_web_error("_execute_tick", e)
            self._append_output(f"\n--- Tick error: {e} ---\n")
            self._set_status(f"Error: {e}")
            self.running = False

    def _menu_stop(self):
        """Run > Stop - Stop execution."""
        if self.running:
            self.running = False
            self._set_status('Stopped')
            self._append_output("\n--- Program stopped ---\n")
        else:
            self._set_status('No program running')

    def _menu_step(self):
        """Run > Step - Step one line."""
        try:
            if not self.running:
                # Not running - start in step mode
                if not self._save_editor_to_program():
                    return  # Parse errors

                if not self.program.lines:
                    self._notify('No program loaded', type='warning')
                    return

                # Start execution in step mode
                # Same setup as _menu_run
                self._clear_output()

                # Get program AST
                program_ast = self.program.get_program_ast()

                # Create runtime and interpreter
                from src.resource_limits import create_local_limits
                self.runtime = Runtime(self.program.line_asts, self.program.lines)

                # Create IO handler
                self.exec_io = SimpleWebIOHandler(self._append_output, self._get_input)
                self.interpreter = Interpreter(self.runtime, self.exec_io, limits=create_local_limits())

                # Wire up interpreter
                self.interpreter.interactive_mode = self

                # Start interpreter
                state = self.interpreter.start()
                if state.status == 'error':
                    error_msg = state.error_info.error_message if state.error_info else 'Unknown'
                    self._append_output(f"\n--- Setup error: {error_msg} ---\n")
                    self._set_status('Error')
                    return

                # Mark as running but paused
                self.running = True
                self.paused = True

                # Start async execution
                ui.timer(0.01, self._execute_tick, once=False)
                self._set_status('Stepping...')
            else:
                # Already running - step one tick
                if self.paused and self.interpreter:
                    self.paused = False  # Allow one tick
                    # The tick handler will pause again
                    self._set_status('Step')

        except Exception as e:
            log_web_error("_menu_step", e)
            self._notify(f'Error: {e}', type='negative')

    def _menu_continue(self):
        """Run > Continue - Continue from breakpoint."""
        try:
            if self.running and self.paused:
                self.paused = False
                self._set_status('Continuing...')
            else:
                self._notify('Not paused at breakpoint', type='warning')

        except Exception as e:
            log_web_error("_menu_continue", e)
            self._notify(f'Error: {e}', type='negative')

    def _menu_list(self):
        """Run > List Program - List to output."""
        lines = self.program.get_lines()
        for line_num, line_text in lines:
            self._append_output(line_text)
        self._set_status('Program listed')

    def _show_variables_window(self):
        """Show Variables window."""
        try:
            if not self.runtime:
                self._notify('No program running', type='warning')
                return

            # Create dialog with variables table
            with ui.dialog() as dialog, ui.card().classes('w-[800px]'):
                ui.label('Program Variables').classes('text-xl font-bold')

                # Get all variables from runtime
                variables = {}
                if hasattr(self.runtime, 'variables'):
                    variables = self.runtime.variables

                if not variables:
                    ui.label('No variables defined').classes('text-gray-500 p-4')
                else:
                    # Create table
                    columns = [
                        {'name': 'name', 'label': 'Name', 'field': 'name', 'align': 'left'},
                        {'name': 'type', 'label': 'Type', 'field': 'type', 'align': 'left'},
                        {'name': 'value', 'label': 'Value', 'field': 'value', 'align': 'left'},
                    ]

                    rows = []
                    for name, value in variables.items():
                        # Determine type
                        if isinstance(value, str):
                            var_type = 'String'
                        elif isinstance(value, float):
                            var_type = 'Float'
                        elif isinstance(value, int):
                            var_type = 'Integer'
                        elif isinstance(value, list):
                            var_type = 'Array'
                        else:
                            var_type = str(type(value).__name__)

                        # Format value
                        if isinstance(value, list):
                            value_str = f'[{len(value)} elements]'
                        else:
                            value_str = str(value)
                            if len(value_str) > 50:
                                value_str = value_str[:47] + '...'

                        rows.append({
                            'name': name,
                            'type': var_type,
                            'value': value_str
                        })

                    ui.table(columns=columns, rows=rows, row_key='name').classes('w-full')

                ui.button('Close', on_click=dialog.close).classes('mt-4')
            dialog.open()

        except Exception as e:
            log_web_error("_show_variables_window", e)
            self._notify(f'Error: {e}', type='negative')

    def _show_stack_window(self):
        """Show Execution Stack window."""
        try:
            if not self.runtime:
                self._notify('No program running', type='warning')
                return

            # Create dialog with stack display
            with ui.dialog() as dialog, ui.card().classes('w-[600px]'):
                ui.label('Execution Stack').classes('text-xl font-bold')

                # Get call stack from runtime
                stack = []
                if hasattr(self.runtime, 'gosub_stack'):
                    stack = self.runtime.gosub_stack

                if not stack:
                    ui.label('Stack is empty').classes('text-gray-500 p-4')
                else:
                    # Show stack entries
                    ui.label(f'{len(stack)} entries').classes('text-sm text-gray-600 mb-2')
                    for i, entry in enumerate(reversed(stack)):
                        with ui.row().classes('w-full p-2 bg-gray-100 rounded mb-1'):
                            ui.label(f'#{i+1}:').classes('font-bold w-12')
                            ui.label(f'Line {entry}').classes('font-mono')

                ui.button('Close', on_click=dialog.close).classes('mt-4')
            dialog.open()

        except Exception as e:
            log_web_error("_show_stack_window", e)
            self._notify(f'Error: {e}', type='negative')

    def _menu_help(self):
        """Help > Help Topics - Opens in web browser."""
        from ..web_help_launcher import open_help_in_browser
        open_help_in_browser(topic="help/ui/web/", ui_type="web")
        self._notify('Opening help in browser...', type='info')

    def _menu_about(self):
        """Help > About."""
        self._notify('MBASIC 5.21 Web IDE\nBuilt with NiceGUI', type='info')

    # =========================================================================
    # Editor Actions
    # =========================================================================

    def _save_editor_to_program(self):
        """Save editor content to program.

        Parses all lines in the editor and updates the program.
        Returns True if successful, False if there were errors.
        """
        try:
            # Clear existing program
            self.program.clear()

            # Get editor content
            text = self.editor.value
            if not text:
                self._set_status('Program cleared')
                return True

            # Parse each line
            lines = text.split('\n')
            errors = []

            for line_text in lines:
                line_text = line_text.strip()
                if not line_text:
                    continue  # Skip blank lines

                # Parse line number
                match = re.match(r'^(\d+)(?:\s|$)', line_text)
                if not match:
                    errors.append(f'Line must start with number: {line_text[:30]}...')
                    continue

                line_num = int(match.group(1))

                # Add to program
                success, error = self.program.add_line(line_num, line_text)
                if not success:
                    errors.append(f'{line_num}: {error}')

            if errors:
                error_msg = '; '.join(errors[:3])
                if len(errors) > 3:
                    error_msg += f' (and {len(errors)-3} more)'

                # Show in both popup and output
                self._notify(error_msg, type='warning')
                self._set_status(f'Parse errors: {len(errors)}')
                return False

            self._set_status(f'Program loaded: {len(self.program.lines)} lines')
            return True

        except Exception as e:
            log_web_error("_save_editor_to_program", e)
            self._notify(f'Error: {e}', type='negative')
            return False

    def _load_program_to_editor(self):
        """Load program content into editor."""
        try:
            lines = self.program.get_lines()
            # Format as "linenum text"
            formatted_lines = [line_text for line_num, line_text in lines]
            self.editor.value = '\n'.join(formatted_lines)
            self._set_status(f'Loaded {len(lines)} lines')
        except Exception as e:
            log_web_error("_load_program_to_editor", e)
            self._notify(f'Error: {e}', type='negative')

    def _on_enter_key(self, e):
        """Handle Enter key in editor for auto-numbering.

        If auto-numbering is enabled and current line has no line number,
        automatically add one.
        """
        if not self.auto_number_enabled:
            return  # Allow default behavior

        try:
            # Get current editor content and cursor position via JavaScript
            # This is complex in NiceGUI, so we'll use a simpler approach:
            # Just add the next line number on a new line after Enter is pressed

            # Get current text
            current_text = self.editor.value

            # Find highest line number
            lines = current_text.split('\n')
            highest_line_num = 0

            for line in lines:
                match = re.match(r'^\s*(\d+)', line.strip())
                if match:
                    line_num = int(match.group(1))
                    highest_line_num = max(highest_line_num, line_num)

            # Calculate next line number
            if highest_line_num > 0:
                next_line_num = highest_line_num + self.auto_number_increment
            else:
                next_line_num = self.auto_number_start

            # Use JavaScript to insert line number after Enter
            # The Enter key default behavior will happen, then we add the line number
            ui.run_javascript(f'''
                setTimeout(() => {{
                    const textarea = document.querySelector('[data-ref="editor"] textarea');
                    if (textarea) {{
                        const start = textarea.selectionStart;
                        const text = textarea.value;
                        // Insert line number at cursor position
                        const newText = text.substring(0, start) + "{next_line_num} " + text.substring(start);
                        textarea.value = newText;
                        textarea.selectionStart = textarea.selectionEnd = start + {len(str(next_line_num)) + 1};
                        // Trigger input event to update Vue model
                        textarea.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    }}
                }}, 10);
            ''')

        except Exception as ex:
            log_web_error("_on_enter_key", ex)
            # Don't prevent Enter if auto-numbering fails

    def _clear_output(self):
        """Clear output pane."""
        self.output_text = ''
        if self.output:
            self.output.value = ''
            self.output.update()  # Force NiceGUI to push update to browser
        self._set_status('Output cleared')

    def _append_output(self, text):
        """Append text to output pane and auto-scroll to bottom."""
        # Update our internal buffer
        self.output_text += text

        # Limit output buffer by number of lines to prevent infinite growth
        # This is more predictable than character-based limiting
        lines = self.output_text.split('\n')
        if len(lines) > self.output_max_lines:
            # Keep last N lines, add indicator at start
            lines = lines[-self.output_max_lines:]
            self.output_text = '\n'.join(lines)
            # Add truncation indicator if not already present
            if not self.output_text.startswith('[... output truncated'):
                self.output_text = '[... output truncated ...]\n' + self.output_text

        # Update the textarea directly (push-based, not polling)
        if self.output:
            self.output.value = self.output_text
            self.output.update()  # Force NiceGUI to push update to browser

            # Auto-scroll to bottom using JavaScript
            # Try multiple methods to ensure scroll works
            ui.run_javascript('''
                setTimeout(() => {
                    // Method 1: Find by marker attribute
                    let textarea = document.querySelector('[data-marker="output"] textarea');

                    // Method 2: Find any readonly textarea (likely the output)
                    if (!textarea) {
                        const textareas = document.querySelectorAll('textarea[readonly]');
                        textarea = textareas[textareas.length - 1]; // Last readonly textarea
                    }

                    // Method 3: Find by Quasar class
                    if (!textarea) {
                        const qTextarea = document.querySelector('.q-textarea textarea');
                        if (qTextarea && qTextarea.hasAttribute('readonly')) {
                            textarea = qTextarea;
                        }
                    }

                    if (textarea) {
                        textarea.scrollTop = textarea.scrollHeight;
                    }
                }, 50);
            ''')

    def _show_input_row(self, prompt=''):
        """Show the INPUT row with prompt."""
        if self.input_row and self.input_label and self.input_field:
            self.input_label.text = prompt
            self.input_field.value = ''
            self.input_row.visible = True
            # Focus on input field (NiceGUI will handle this automatically)

    def _hide_input_row(self):
        """Hide the INPUT row."""
        if self.input_row:
            self.input_row.visible = False

    def _submit_input(self):
        """Submit INPUT value from inline input field."""
        if self.input_field and self.input_future:
            value = self.input_field.value
            self.input_field.value = ''
            # Resolve the future with the input value
            if not self.input_future.done():
                self.input_future.set_result(value)

    async def _get_input_async(self, prompt):
        """Get input from user (async version).

        Creates a Future that will be resolved when user submits input.
        """
        # Create a new future for this input request
        loop = asyncio.get_event_loop()
        self.input_future = loop.create_future()

        # Show input row
        self._show_input_row(prompt)

        # Wait for user to submit input
        result = await self.input_future

        # Hide input row
        self._hide_input_row()

        return result

    def _get_input(self, prompt):
        """Get input from user (blocking version).

        Uses asyncio to wait for async input, making it compatible with
        synchronous interpreter INPUT statements.
        """
        # Run the async input function and wait for result
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If event loop is running, we need to create a task and wait
            # This is tricky - we'll use a blocking approach with Future
            import concurrent.futures
            import threading

            result_holder = []
            done_event = threading.Event()

            async def get_and_signal():
                result = await self._get_input_async(prompt)
                result_holder.append(result)
                done_event.set()

            # Schedule the coroutine on the event loop
            asyncio.create_task(get_and_signal())

            # Block until done
            done_event.wait()

            return result_holder[0] if result_holder else ""
        else:
            # Event loop not running, use run_until_complete
            return loop.run_until_complete(self._get_input_async(prompt))

    def _on_immediate_enter(self, e):
        """Handle Enter key in immediate mode input."""
        self._execute_immediate()

    def _execute_immediate(self):
        """Execute immediate mode command."""
        try:
            command = self.immediate_entry.value.strip()
            if not command:
                return

            # Clear the input
            self.immediate_entry.value = ''

            # Show command in output
            self._append_output(f'> {command}\n')

            # Execute the command
            from src.immediate_executor import ImmediateExecutor, OutputCapturingIOHandler

            # Create output capturing IO handler
            output_io = OutputCapturingIOHandler()

            # Ensure we have a runtime - create temporary one if needed
            runtime = self.runtime
            interpreter = self.interpreter

            if runtime is None:
                # Create a temporary runtime for immediate mode
                runtime = Runtime({}, {})

            if interpreter is None:
                # Create a temporary interpreter for immediate mode
                from src.resource_limits import create_local_limits
                interpreter = Interpreter(runtime, output_io, limits=create_local_limits())

            # Create immediate executor (runtime, interpreter, io_handler)
            immediate_executor = ImmediateExecutor(
                runtime,
                interpreter,
                output_io
            )

            # Execute command
            success, output = immediate_executor.execute(command)

            # Show result
            if output:
                self._append_output(output)

            if success:
                self._set_status('Immediate command executed')
            else:
                self._set_status('Immediate command error')

        except Exception as e:
            log_web_error("_execute_immediate", e)
            self._notify(f'Error: {e}', type='negative')

    def _notify(self, message, type='info', log_to_output=True):
        """Show notification popup and optionally log to output.

        Args:
            message: Notification message
            type: 'positive', 'negative', 'warning', 'info'
            log_to_output: If True, also append to output pane (default: True)
        """
        # Show popup
        ui.notify(message, type=type)

        # Also log to output (unless explicitly disabled)
        if log_to_output:
            # Format based on type
            if type == 'negative':
                prefix = '--- Error ---'
            elif type == 'warning':
                prefix = '--- Warning ---'
            elif type == 'positive':
                prefix = '--- Success ---'
            else:
                prefix = '--- Info ---'

            self._append_output(f'\n{prefix}\n{message}\n')

    def _set_status(self, message):
        """Set status bar message."""
        if self.status_label:
            self.status_label.text = message

    # =========================================================================
    # UIBackend Interface
    # =========================================================================

    def start(self):
        """Start the UI.

        This builds the UI and starts the NiceGUI server.
        """
        # Log version to debug output
        sys.stderr.write(f"\n{'='*70}\n")
        sys.stderr.write(f"MBASIC Web UI Starting - Version {VERSION}\n")
        sys.stderr.write(f"{'='*70}\n\n")
        sys.stderr.flush()

        self.build_ui()
        ui.run(
            title='MBASIC 5.21 - Web IDE',
            port=8080,
            reload=False,
            show=True
        )

    def stop(self):
        """Stop the UI."""
        app.shutdown()
