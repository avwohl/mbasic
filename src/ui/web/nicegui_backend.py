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

        # Execution state
        self.running = False
        self.paused = False
        self.breakpoints = set()  # Line numbers with breakpoints
        self.interpreter = None
        self.runtime = None
        self.exec_io = None
        self.tick_task = None  # Async task for execution

        # UI elements (created in build_ui())
        self.editor = None
        self.output = None
        self.status_label = None
        self.immediate_entry = None  # Immediate mode command input

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

            # Main content area - split pane (vertical: editor on top, output on bottom)
            with ui.splitter(value=60, vertical=True).classes('w-full h-[600px]') as splitter:

                # Top pane - Program Editor (60% of space)
                with splitter.before:
                    ui.label('Program Editor:').classes('text-lg font-bold p-2')

                    # Multi-line program editor (like TK)
                    self.editor = ui.textarea(
                        value='',
                        placeholder='Enter BASIC program here (e.g., 10 PRINT "Hello")\nPress Enter for auto-numbering'
                    ).classes('w-full h-full font-mono text-base').props('outlined').mark('editor')

                    # Bind keyboard events
                    self.editor.on('keydown.enter', self._on_enter_key)

                # Bottom pane - Output (40% of space)
                with splitter.after:
                    ui.label('Output').classes('text-lg font-bold p-2')
                    self.output = ui.textarea(
                        value='MBASIC 5.21 Web IDE\nReady\n',
                        placeholder='Program output will appear here'
                    ).classes('w-full flex-grow font-mono').props('readonly').mark('output')

                    # INPUT row (hidden by default, shown when INPUT statement needs input)
                    self.input_row = ui.row().classes('w-full p-2 gap-2')
                    with self.input_row:
                        self.input_label = ui.label('').classes('font-bold text-blue-600')
                        self.input_field = ui.input(placeholder='Enter value...').classes('flex-grow').mark('input_field')
                        self.input_field.on('keydown.enter', self._submit_input)
                        self.input_submit_btn = ui.button('Submit', on_click=self._submit_input, icon='send', color='primary').mark('btn_input_submit')
                    self.input_row.visible = False  # Hidden by default

                    with ui.row().classes('w-full p-2'):
                        ui.button('Clear Output', on_click=self._clear_output, icon='clear').mark('btn_clear_output')

                    # Immediate mode command input
                    ui.label('Immediate Mode:').classes('font-bold px-2 pt-2')
                    with ui.row().classes('w-full p-2 gap-2'):
                        self.immediate_entry = ui.input(
                            placeholder='Enter BASIC command (e.g., PRINT 2+2)',
                        ).classes('flex-grow font-mono').mark('immediate_entry')
                        self.immediate_entry.on('keydown.enter', self._on_immediate_enter)
                        ui.button('Execute', on_click=self._execute_immediate, icon='play_arrow', color='green').mark('btn_immediate')

            # Status bar
            with ui.row().classes('w-full bg-gray-200 p-2'):
                self.status_label = ui.label('Ready').mark('status')

    def _create_menu(self):
        """Create menu bar."""
        with ui.row().classes('w-full bg-gray-800 text-white p-2 gap-4'):
            # File menu
            with ui.button('File', icon='menu').props('flat color=white'):
                with ui.menu():
                    ui.menu_item('New', on_click=self._menu_new)
                    ui.menu_item('Open...', on_click=self._menu_open)
                    ui.menu_item('Save', on_click=self._menu_save)
                    ui.menu_item('Save As...', on_click=self._menu_save_as)
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
                    ui.menu_item('Clear Output', on_click=self._clear_output)

            # Help menu
            with ui.button('Help', icon='menu').props('flat color=white'):
                with ui.menu():
                    ui.menu_item('Help Topics', on_click=self._menu_help)
                    ui.separator()
                    ui.menu_item('About', on_click=self._menu_about)

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
            ui.notify(f'Error: {e}', type='negative')

    def _menu_open(self):
        """File > Open - Load program from file."""
        try:
            # Create upload dialog
            with ui.dialog() as dialog, ui.card():
                ui.label('Open BASIC Program')
                upload = ui.upload(
                    on_upload=lambda e: self._handle_file_upload(e, dialog),
                    auto_upload=True
                ).classes('w-full').props('accept=".bas,.txt"')
                ui.button('Cancel', on_click=dialog.close)
            dialog.open()
        except Exception as e:
            log_web_error("_menu_open", e)
            ui.notify(f'Error: {e}', type='negative')

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

            self._set_status(f'Opened: {e.name}')
            ui.notify(f'Loaded {e.name}', type='positive')
            dialog.close()

        except Exception as ex:
            log_web_error("_handle_file_upload", ex)
            ui.notify(f'Error loading file: {ex}', type='negative')

    def _menu_save(self):
        """File > Save - Save current program."""
        try:
            # Save editor to program first
            self._save_editor_to_program()

            # Get filename
            filename = self.current_file or 'program.bas'

            # Download file with current editor content
            content = self.editor.value
            ui.download(content.encode('utf-8'), filename)

            self._set_status(f'Saved: {filename}')
            ui.notify(f'Downloaded {filename}', type='positive')

        except Exception as e:
            log_web_error("_menu_save", e)
            ui.notify(f'Error: {e}', type='negative')

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
            ui.notify(f'Error: {e}', type='negative')

    def _handle_save_as(self, filename, dialog):
        """Handle Save As dialog."""
        try:
            if not filename:
                ui.notify('Please enter a filename', type='warning')
                return

            # Save editor to program first
            self._save_editor_to_program()

            # Update current filename
            self.current_file = filename

            # Download file
            content = self.editor.value
            ui.download(content.encode('utf-8'), filename)

            self._set_status(f'Saved: {filename}')
            ui.notify(f'Downloaded {filename}', type='positive')
            dialog.close()

        except Exception as e:
            log_web_error("_handle_save_as", e)
            ui.notify(f'Error: {e}', type='negative')

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
                ui.notify('No program in editor. Add some lines first.', type='warning')
                return
            # Clear output
            self._clear_output()
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

            # Start async execution
            ui.timer(0.01, self._execute_tick, once=False)

        except Exception as e:
            log_web_error("_menu_run", e)
            self._append_output(f"\n--- Error: {e} ---\n")
            self._set_status(f'Error: {e}')
            self.running = False

    def _execute_tick(self):
        """Execute one tick of the interpreter."""
        if not self.running or not self.interpreter:
            return

        try:
            # Execute one tick (up to 1000 statements)
            state = self.interpreter.tick(mode='run', max_statements=1000)

            # Handle state
            if state.status == 'done':
                self._append_output("\n--- Program finished ---\n")
                self._set_status("Ready")
                self.running = False
            elif state.status == 'error':
                error_msg = state.error_info.error_message if state.error_info else "Unknown error"
                self._append_output(f"\n--- Error: {error_msg} ---\n")
                self._set_status("Error")
                self.running = False
            elif state.status == 'paused' or state.status == 'at_breakpoint':
                self._set_status(f"Paused at line {state.current_line}")
                self.running = False
                self.paused = True

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
        self._set_status('Step not yet implemented')

    def _menu_continue(self):
        """Run > Continue - Continue from breakpoint."""
        self._set_status('Continue not yet implemented')

    def _menu_list(self):
        """Run > List Program - List to output."""
        lines = self.program.get_lines()
        for line_num, line_text in lines:
            self._append_output(line_text)
        self._set_status('Program listed')

    def _menu_help(self):
        """Help > Help Topics."""
        ui.notify('Help system coming soon', type='info')

    def _menu_about(self):
        """Help > About."""
        ui.notify('MBASIC 5.21 Web IDE\nBuilt with NiceGUI', type='info')

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
                ui.notify(error_msg, type='warning')
                self._set_status(f'Parse errors: {len(errors)}')
                return False

            self._set_status(f'Program loaded: {len(self.program.lines)} lines')
            return True

        except Exception as e:
            log_web_error("_save_editor_to_program", e)
            ui.notify(f'Error: {e}', type='negative')
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
            ui.notify(f'Error: {e}', type='negative')

    def _on_enter_key(self, e):
        """Handle Enter key in editor for auto-numbering.

        If auto-numbering is enabled and current line has no line number,
        automatically add one.

        Note: This is a simplified version compared to TK. Full cursor
        manipulation and line sorting happens in TK but is complex to
        implement in web textarea. For now, just allow default behavior.
        """
        # TODO: Implement auto-numbering
        # For now, just let the default Enter behavior happen
        # Users can manually add line numbers
        pass

    def _clear_output(self):
        """Clear output pane."""
        self.output.value = 'MBASIC 5.21 Web IDE\nReady\n'
        self._set_status('Output cleared')

    def _append_output(self, text):
        """Append text to output pane and auto-scroll to bottom."""
        self.output.value += text
        # Force update and then scroll
        self.output.update()
        # Auto-scroll to bottom
        # Use mark selector to find the specific textarea
        ui.run_javascript('''
            setTimeout(() => {
                // Find all textareas with the 'output' mark
                const textareas = document.querySelectorAll('textarea');
                for (let ta of textareas) {
                    // Check if this is the output textarea (readonly, has content starting with MBASIC)
                    if (ta.readOnly && ta.value.includes('MBASIC 5.21')) {
                        ta.scrollTop = ta.scrollHeight;
                        break;
                    }
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

            # Create immediate executor
            immediate_executor = ImmediateExecutor(
                self.program,
                self.runtime if self.runtime else None,
                output_io
            )

            # Execute command
            result = immediate_executor.execute_line(command)

            # Show result
            if output_io.output_buffer:
                self._append_output(output_io.output_buffer)

            self._set_status('Immediate command executed')

        except Exception as e:
            log_web_error("_execute_immediate", e)
            self._append_output(f'Error: {e}\n')
            ui.notify(f'Error: {e}', type='negative')

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
