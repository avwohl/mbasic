#!/usr/bin/env python3
"""
NiceGUI-based web interface for MBASIC.

Provides a full-featured web IDE for running BASIC programs with:
- Code editor with line numbers
- Real-time output display
- Interactive INPUT support
- Debugger (breakpoints, step, continue)
- Variables watch window
- Execution stack window
- File save/load
- Help system
"""

from nicegui import ui, app
from pathlib import Path
import sys
import asyncio
from datetime import datetime
from typing import Optional, Set
import base64

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from iohandler.web_io import WebIOHandler
from lexer import Lexer
from parser import Parser
from interpreter import Interpreter
from runtime import Runtime
from filesystem import SandboxedFileSystemProvider


class MBasicWebIDE:
    """Main MBASIC Web IDE application with full debugger support."""

    def __init__(self):
        """Initialize the IDE."""
        # UI components
        self.editor = None
        self.output_log = None
        self.status_label = None
        self.line_display = None

        # File state
        self.current_file = "untitled.bas"
        self.current_path = None

        # MBASIC components
        self.io_handler = None
        self.runtime = None
        self.interpreter = None

        # Debugger state
        self.running = False
        self.paused_at_breakpoint = False
        self.breakpoints: Set[int] = set()
        self.tick_timer = None

        # Variables window
        self.variables_dialog = None
        self.variables_table = None
        self.variables_visible = False

        # Stack window
        self.stack_dialog = None
        self.stack_table = None
        self.stack_visible = False

    def create_ui(self):
        """Create the main UI layout."""
        # Page configuration
        ui.colors(primary='#1976D2', secondary='#26A69A', accent='#9C27B0')

        # Add custom CSS for better code display
        ui.add_head_html('''
        <style>
        .code-editor {
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.5;
        }
        .output-log {
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 13px;
        }
        .line-number-area {
            background-color: #f5f5f5;
            color: #666;
            padding: 4px 8px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 13px;
            user-select: none;
            cursor: pointer;
        }
        .breakpoint-line {
            background-color: #ffebee;
        }
        </style>
        ''')

        # Header with menu
        with ui.header().classes('items-center'):
            with ui.row().classes('w-full items-center'):
                ui.label('MBASIC 5.21 Web IDE').classes('text-h6')
                ui.space()

                # File menu
                with ui.button(icon='folder', color='white').props('flat'):
                    with ui.menu() as menu:
                        ui.menu_item('New', on_click=self.menu_new, auto_close=True)
                        ui.menu_item('Open from Computer', on_click=self.menu_open, auto_close=True)
                        ui.menu_item('Open from Server', on_click=self.menu_open_server, auto_close=True)
                        ui.menu_item('Save', on_click=self.menu_save, auto_close=True)
                        ui.menu_item('Save As', on_click=self.menu_save_as, auto_close=True)
                        ui.separator()
                        ui.menu_item('Load Example', on_click=self.show_examples, auto_close=True)

                # Run menu
                with ui.button(icon='play_arrow', color='white').props('flat'):
                    with ui.menu() as menu:
                        ui.menu_item('Run (Ctrl+R)', on_click=self.menu_run, auto_close=True)
                        ui.menu_item('Step (Ctrl+T)', on_click=self.menu_step, auto_close=True)
                        ui.menu_item('Continue (Ctrl+G)', on_click=self.menu_continue, auto_close=True)
                        ui.menu_item('Stop (Ctrl+Q)', on_click=self.menu_stop, auto_close=True)
                        ui.separator()
                        ui.menu_item('Clear Output', on_click=self.clear_output, auto_close=True)

                # Debug menu
                with ui.button(icon='bug_report', color='white').props('flat'):
                    with ui.menu() as menu:
                        ui.menu_item('Toggle Breakpoint', on_click=self.toggle_breakpoint, auto_close=True)
                        ui.menu_item('Variables Window', on_click=self.toggle_variables, auto_close=True)
                        ui.menu_item('Stack Window', on_click=self.toggle_stack, auto_close=True)

                # Help menu
                with ui.button(icon='help', color='white').props('flat'):
                    with ui.menu() as menu:
                        ui.menu_item('Help Topics', on_click=self.menu_help, auto_close=True)
                        ui.menu_item('About', on_click=self.menu_about, auto_close=True)

                self.line_display = ui.label('').classes('text-sm')

        # Main content area with splitter
        with ui.splitter(value=50).classes('w-full').style('height: calc(100vh - 100px)') as splitter:

            # Left panel: Code editor
            with splitter.before:
                with ui.card().classes('w-full h-full'):
                    with ui.row().classes('items-center mb-2'):
                        ui.label('Program Editor').classes('text-h6')
                        ui.space()
                        ui.label('').bind_text_from(self, 'current_file').classes('text-sm text-grey-7')

                    # Editor with line numbers
                    with ui.row().classes('w-full').style('height: calc(100% - 80px)'):
                        # Line numbers column (will be populated based on editor content)
                        self.line_numbers = ui.column().classes('line-number-area').style('width: 40px; overflow-y: hidden')

                        # Editor
                        self.editor = ui.textarea(
                            placeholder='10 PRINT "HELLO WORLD"\n20 END'
                        ).classes('code-editor flex-grow').props('outlined autogrow').style('min-height: 400px')

                        # Update line numbers when editor changes
                        self.editor.on('update:model-value', self.update_line_numbers)

                    # Set initial example code
                    self.editor.value = '''10 REM MBASIC Web IDE
20 PRINT "Welcome to MBASIC 5.21!"
30 PRINT
40 FOR I = 1 TO 5
50   PRINT "Count: "; I
60 NEXT I
70 PRINT
80 PRINT "Full debugger support!"
90 END
'''

                    # Toolbar
                    with ui.row().classes('gap-2 mt-2'):
                        ui.button('Run', on_click=self.menu_run, icon='play_arrow').props('color=primary')
                        ui.button('Step', on_click=self.menu_step, icon='skip_next').props('color=secondary')
                        ui.button('Continue', on_click=self.menu_continue, icon='play_circle_outline')
                        ui.button('Stop', on_click=self.menu_stop, icon='stop').props('color=negative')
                        ui.separator().props('vertical')
                        ui.button('Breakpoint', on_click=self.toggle_breakpoint, icon='radio_button_checked').props('outline')
                        ui.button('Variables', on_click=self.toggle_variables, icon='list').props('outline')
                        ui.button('Stack', on_click=self.toggle_stack, icon='view_list').props('outline')

            # Right panel: Output
            with splitter.after:
                with ui.card().classes('w-full h-full'):
                    ui.label('Output').classes('text-h6 mb-2')

                    # Output log
                    self.output_log = ui.log(max_lines=1000).classes('output-log w-full').style('height: calc(100% - 40px)')
                    self.output_log.push('MBASIC 5.21 Web IDE')
                    self.output_log.push('Ready')
                    self.output_log.push('')

        # Footer status bar
        with ui.footer():
            self.status_label = ui.label('Ready').classes('text-sm')

        # Initialize line numbers
        self.update_line_numbers()

    def update_line_numbers(self, e=None):
        """Update line numbers display based on editor content."""
        if not self.editor or not self.line_numbers:
            return

        lines = self.editor.value.split('\n') if self.editor.value else ['']
        self.line_numbers.clear()

        for i, line in enumerate(lines, 1):
            # Check if line has breakpoint
            has_breakpoint = i in self.breakpoints
            bg_color = '#ffebee' if has_breakpoint else 'transparent'

            with self.line_numbers:
                ui.label(str(i)).classes('text-right').style(
                    f'width: 100%; padding: 2px 4px; background-color: {bg_color}; cursor: pointer'
                ).on('click', lambda line_num=i: self.toggle_breakpoint_at_line(line_num))

    def toggle_breakpoint_at_line(self, line_num: int):
        """Toggle breakpoint at specific line number."""
        if line_num in self.breakpoints:
            self.breakpoints.remove(line_num)
            ui.notify(f'Breakpoint removed at line {line_num}', type='info')
        else:
            self.breakpoints.add(line_num)
            ui.notify(f'Breakpoint set at line {line_num}', type='positive')
        self.update_line_numbers()

    def toggle_breakpoint(self):
        """Toggle breakpoint at current cursor position."""
        # For now, just show a dialog to enter line number
        # In future, could track cursor position
        ui.notify('Click on line numbers to toggle breakpoints', type='info')

    # File operations
    def menu_new(self):
        """Create a new program."""
        self.editor.value = '10 \n'
        self.current_file = 'untitled.bas'
        self.current_path = None
        self.breakpoints.clear()
        self.update_line_numbers()
        ui.notify('New program created')

    async def menu_open(self):
        """Open a file."""
        # Create file upload dialog
        with ui.dialog() as dialog, ui.card():
            ui.label('Open BASIC File').classes('text-h6')

            upload = ui.upload(
                label='Choose .BAS file',
                auto_upload=True,
                on_upload=lambda e: self.handle_file_upload(e, dialog)
            ).props('accept=".bas,.BAS"').classes('w-full')

            ui.button('Cancel', on_click=dialog.close).props('flat')

        dialog.open()

    def handle_file_upload(self, e, dialog):
        """Handle file upload."""
        try:
            content = e.content.read().decode('utf-8')
            self.editor.value = content
            self.current_file = e.name
            self.current_path = None
            dialog.close()
            ui.notify(f'Loaded {e.name}', type='positive')
        except Exception as ex:
            ui.notify(f'Error loading file: {str(ex)}', type='negative')

    async def menu_open_server(self):
        """Browse and open files from server."""
        # Get list of .BAS files from server
        basic_dir = Path(__file__).parent.parent.parent.parent / 'basic'

        # Collect all .bas files recursively
        bas_files = []
        if basic_dir.exists():
            for bas_file in basic_dir.rglob('*.bas'):
                # Get relative path from basic/ directory
                rel_path = bas_file.relative_to(basic_dir)
                bas_files.append((str(rel_path), bas_file))

        bas_files.sort(key=lambda x: x[0])

        if not bas_files:
            ui.notify('No .BAS files found on server', type='warning')
            return

        # Create file browser dialog
        with ui.dialog() as dialog, ui.card().classes('w-full').style('max-width: 600px; max-height: 70vh'):
            ui.label('Open from Server').classes('text-h6 mb-2')

            # Search box
            search = ui.input(label='Search', placeholder='Filter files...').classes('w-full mb-2')

            # File list
            with ui.scroll_area().classes('w-full').style('height: 400px'):
                file_list = ui.column().classes('w-full')

                def update_file_list(search_term=''):
                    """Update displayed file list based on search."""
                    file_list.clear()
                    with file_list:
                        for rel_path, abs_path in bas_files:
                            if not search_term or search_term.lower() in rel_path.lower():
                                with ui.row().classes('w-full items-center'):
                                    ui.icon('description').classes('text-grey-6')
                                    ui.button(
                                        str(rel_path),
                                        on_click=lambda p=abs_path, n=rel_path: self.load_server_file(p, n, dialog)
                                    ).props('flat align=left').classes('flex-grow')

                # Initial display
                update_file_list()

                # Update on search
                search.on('update:model-value', lambda e: update_file_list(e.args if e.args else ''))

            ui.button('Cancel', on_click=dialog.close).props('flat')

        dialog.open()

    def load_server_file(self, file_path: Path, file_name: str, dialog):
        """Load a file from server."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            self.editor.value = content
            self.current_file = file_name
            self.current_path = None
            self.breakpoints.clear()
            self.update_line_numbers()
            dialog.close()
            ui.notify(f'Loaded {file_name}', type='positive')
        except Exception as ex:
            ui.notify(f'Error loading file: {str(ex)}', type='negative')

    def menu_save(self):
        """Save current program."""
        if self.current_path:
            # Save to existing file (not possible in web, so download)
            self.download_file()
        else:
            self.menu_save_as()

    def menu_save_as(self):
        """Save program as new file."""
        self.download_file()

    def download_file(self):
        """Download current program as file."""
        content = self.editor.value or ''
        filename = self.current_file

        # Create download
        ui.download(content.encode('utf-8'), filename)
        ui.notify(f'Downloading {filename}', type='positive')

    # Program execution
    async def menu_run(self):
        """Run the BASIC program."""
        if self.running:
            ui.notify('Program already running', type='warning')
            return

        self.running = True
        self.paused_at_breakpoint = False
        self.status_label.text = 'Running...'
        self.output_log.push('')
        self.output_log.push('> RUN')

        try:
            code = self.editor.value

            # Parse the program
            lexer = Lexer(code)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            ast = parser.parse()

            # Get user session ID for filesystem isolation
            user_id = app.storage.browser.get('id', 'default-user')

            # Create sandboxed filesystem for this user
            filesystem = SandboxedFileSystemProvider(user_id=user_id, max_files=20, max_file_size=512*1024)

            # Create I/O handler and runtime
            self.io_handler = WebIOHandler(self.output_log)
            self.runtime = Runtime(ast)

            # Create interpreter with program and sandboxed filesystem
            self.interpreter = Interpreter(self.runtime, self.io_handler, filesystem_provider=filesystem)

            # Set breakpoints
            self.interpreter.breakpoints = self.breakpoints.copy()

            # Run with tick-based execution for breakpoint support
            self.execute_ticks()

        except SyntaxError as e:
            error_msg = f'Syntax Error: {str(e)}'
            self.output_log.push(error_msg)
            self.status_label.text = 'Syntax error'
            ui.notify(error_msg, type='negative')
            self.running = False

        except Exception as e:
            error_msg = f'Error: {str(e)}'
            self.output_log.push(error_msg)
            self.status_label.text = 'Error'
            ui.notify(error_msg, type='negative')
            self.running = False

    def execute_ticks(self):
        """Execute interpreter in ticks for breakpoint support."""
        if not self.running or not self.interpreter:
            return

        try:
            # Execute one tick
            result = self.interpreter.tick()

            # Update debug windows
            self.update_variables_window()
            self.update_stack_window()

            if result == 'BREAK':
                # Hit breakpoint
                self.paused_at_breakpoint = True
                self.status_label.text = f'Paused at breakpoint (line {self.interpreter.current_line_number})'
                ui.notify(f'Breakpoint at line {self.interpreter.current_line_number}', type='info')
                self.running = False
                return

            elif result == 'DONE':
                # Program finished
                self.output_log.push('')
                self.status_label.text = 'Program completed'
                ui.notify('Program completed', type='positive')
                self.running = False
                return

            # Continue execution
            ui.timer(0.01, self.execute_ticks, once=True)

        except Exception as e:
            error_msg = f'Runtime Error: {str(e)}'
            self.output_log.push(error_msg)
            self.status_label.text = 'Error'
            ui.notify(error_msg, type='negative')
            self.running = False

    def menu_step(self):
        """Execute one step."""
        if not self.interpreter:
            ui.notify('No program loaded. Run first.', type='warning')
            return

        if self.running:
            ui.notify('Program is running. Stop first.', type='warning')
            return

        try:
            result = self.interpreter.tick()
            self.update_variables_window()
            self.update_stack_window()

            if result == 'DONE':
                self.status_label.text = 'Program completed'
                ui.notify('Program completed', type='positive')
            elif result == 'BREAK':
                self.status_label.text = f'Breakpoint at line {self.interpreter.current_line_number}'
            else:
                self.status_label.text = f'Line {self.interpreter.current_line_number}'

        except Exception as e:
            error_msg = f'Error: {str(e)}'
            self.output_log.push(error_msg)
            ui.notify(error_msg, type='negative')

    def menu_continue(self):
        """Continue execution from breakpoint."""
        if not self.paused_at_breakpoint:
            ui.notify('Not paused at breakpoint', type='warning')
            return

        self.running = True
        self.paused_at_breakpoint = False
        self.status_label.text = 'Continuing...'
        self.execute_ticks()

    def menu_stop(self):
        """Stop program execution."""
        if not self.running and not self.paused_at_breakpoint:
            ui.notify('No program running', type='warning')
            return

        self.running = False
        self.paused_at_breakpoint = False
        self.status_label.text = 'Stopped'
        ui.notify('Program stopped', type='info')

    def clear_output(self):
        """Clear the output log."""
        self.output_log.clear()
        self.output_log.push('MBASIC 5.21 Web IDE')
        self.output_log.push('Ready')
        self.output_log.push('')
        ui.notify('Output cleared')

    # Debug windows
    def toggle_variables(self):
        """Toggle variables watch window."""
        if self.variables_visible:
            if self.variables_dialog:
                self.variables_dialog.close()
            self.variables_visible = False
        else:
            self.show_variables_window()

    def show_variables_window(self):
        """Show variables watch window."""
        with ui.dialog().props('maximized') as dialog:
            self.variables_dialog = dialog
            with ui.card().classes('w-full h-full'):
                with ui.row().classes('items-center mb-2'):
                    ui.label('Variables').classes('text-h6')
                    ui.space()
                    ui.button(icon='close', on_click=lambda: self.close_variables()).props('flat')

                # Variables table
                self.variables_table = ui.table(
                    columns=[
                        {'name': 'name', 'label': 'Name', 'field': 'name', 'align': 'left'},
                        {'name': 'type', 'label': 'Type', 'field': 'type', 'align': 'left'},
                        {'name': 'value', 'label': 'Value', 'field': 'value', 'align': 'left'},
                    ],
                    rows=[],
                    row_key='name'
                ).classes('w-full')

        self.variables_visible = True
        dialog.open()
        self.update_variables_window()

    def close_variables(self):
        """Close variables window."""
        if self.variables_dialog:
            self.variables_dialog.close()
        self.variables_visible = False

    def update_variables_window(self):
        """Update variables window with current state."""
        if not self.variables_visible or not self.variables_table or not self.runtime:
            return

        rows = []

        # Get all variables from runtime
        for name, value in self.runtime.variables.items():
            var_type = type(value).__name__
            if var_type == 'str':
                var_type = 'STRING'
            elif var_type == 'int':
                var_type = 'INTEGER'
            elif var_type == 'float':
                var_type = 'DOUBLE'

            rows.append({
                'name': name,
                'type': var_type,
                'value': str(value)[:100]  # Limit display length
            })

        self.variables_table.rows = rows
        self.variables_table.update()

    def toggle_stack(self):
        """Toggle execution stack window."""
        if self.stack_visible:
            if self.stack_dialog:
                self.stack_dialog.close()
            self.stack_visible = False
        else:
            self.show_stack_window()

    def show_stack_window(self):
        """Show execution stack window."""
        with ui.dialog().props('maximized') as dialog:
            self.stack_dialog = dialog
            with ui.card().classes('w-full h-full'):
                with ui.row().classes('items-center mb-2'):
                    ui.label('Execution Stack').classes('text-h6')
                    ui.space()
                    ui.button(icon='close', on_click=lambda: self.close_stack()).props('flat')

                # Stack table
                self.stack_table = ui.table(
                    columns=[
                        {'name': 'line', 'label': 'Line', 'field': 'line', 'align': 'left'},
                        {'name': 'type', 'label': 'Type', 'field': 'type', 'align': 'left'},
                        {'name': 'details', 'label': 'Details', 'field': 'details', 'align': 'left'},
                    ],
                    rows=[],
                    row_key='line'
                ).classes('w-full')

        self.stack_visible = True
        dialog.open()
        self.update_stack_window()

    def close_stack(self):
        """Close stack window."""
        if self.stack_dialog:
            self.stack_dialog.close()
        self.stack_visible = False

    def update_stack_window(self):
        """Update stack window with current state."""
        if not self.stack_visible or not self.stack_table or not self.runtime:
            return

        rows = []

        # Get FOR loop stack
        for i, frame in enumerate(self.runtime.for_stack):
            rows.append({
                'line': str(frame.get('start_line', '?')),
                'type': 'FOR',
                'details': f"{frame.get('var', '?')} = {frame.get('current', '?')} TO {frame.get('limit', '?')}"
            })

        # Get GOSUB stack
        for i, return_line in enumerate(self.runtime.gosub_stack):
            rows.append({
                'line': str(return_line),
                'type': 'GOSUB',
                'details': f'Return to line {return_line}'
            })

        self.stack_table.rows = rows
        self.stack_table.update()

    # Help and examples
    async def menu_help(self):
        """Show help browser with three-tier help system."""
        # Get help root directory
        help_root = Path(__file__).parent.parent.parent.parent / 'docs' / 'help'

        # Create maximized help browser dialog
        with ui.dialog().props('maximized') as dialog:
            with ui.card().classes('w-full h-full'):
                # Header with title and close button
                with ui.row().classes('w-full items-center mb-2'):
                    ui.label('MBASIC Help Browser').classes('text-h5')
                    ui.space()
                    ui.button(icon='close', on_click=dialog.close).props('flat')

                # Search bar
                with ui.row().classes('w-full items-center gap-2 mb-4'):
                    search_input = ui.input(
                        label='Search help topics',
                        placeholder='Type to search...'
                    ).classes('flex-grow')

                    ui.button('Search', icon='search', on_click=lambda: self._search_help(search_input.value, help_root, content_area))

                # Three-tier navigation tabs
                with ui.tabs().classes('w-full') as tabs:
                    language_tab = ui.tab('📕 Language', icon='book')
                    mbasic_tab = ui.tab('📗 MBASIC 5.21', icon='library_books')
                    ui_tab = ui.tab('📘 Web UI', icon='computer')

                # Content area
                with ui.tab_panels(tabs, value=ui_tab).classes('w-full h-full'):
                    with ui.tab_panel(language_tab):
                        with ui.scroll_area().classes('w-full h-full'):
                            self._show_help_index(help_root / 'language', 'language')

                    with ui.tab_panel(mbasic_tab):
                        with ui.scroll_area().classes('w-full h-full'):
                            self._show_help_index(help_root / 'mbasic', 'mbasic')

                    with ui.tab_panel(ui_tab):
                        with ui.scroll_area().classes('w-full h-full'):
                            content_area = ui.column().classes('w-full')
                            self._load_help_topic(help_root / 'ui' / 'web' / 'index.md', content_area)

        dialog.open()

    def _show_help_index(self, help_dir: Path, category: str):
        """Show index of help topics in a directory."""
        if not help_dir.exists():
            ui.label(f'No help available for {category}').classes('text-grey-6')
            return

        # Find all markdown files
        md_files = sorted(help_dir.rglob('*.md'))

        if not md_files:
            ui.label(f'No help topics found').classes('text-grey-6')
            return

        # Group by subdirectory
        topics_by_dir = {}
        for md_file in md_files:
            rel_path = md_file.relative_to(help_dir)
            dir_name = str(rel_path.parent) if str(rel_path.parent) != '.' else 'General'

            if dir_name not in topics_by_dir:
                topics_by_dir[dir_name] = []

            # Extract title from filename
            title = md_file.stem.replace('-', ' ').replace('_', ' ').title()
            topics_by_dir[dir_name].append((title, md_file))

        # Display grouped topics
        for dir_name in sorted(topics_by_dir.keys()):
            ui.label(dir_name).classes('text-h6 mt-4 mb-2')

            with ui.column().classes('gap-1'):
                for title, filepath in sorted(topics_by_dir[dir_name]):
                    ui.button(
                        title,
                        on_click=lambda fp=filepath: self._show_help_content(fp)
                    ).props('flat align=left color=primary').classes('w-full text-left')

    def _load_help_topic(self, topic_path: Path, container):
        """Load and display a help topic."""
        container.clear()

        with container:
            if not topic_path.exists():
                ui.label('Help topic not found').classes('text-negative')
                return

            try:
                content = topic_path.read_text(encoding='utf-8')

                # Expand macros (like {{kbd:help}})
                from ui.help_macros import HelpMacros
                help_root = Path(__file__).parent.parent.parent.parent / 'docs' / 'help'
                macros = HelpMacros('web', str(help_root))
                content = macros.expand(content)

                # Display as markdown
                ui.markdown(content).classes('w-full')

            except Exception as e:
                ui.label(f'Error loading help: {str(e)}').classes('text-negative')

    def _show_help_content(self, filepath: Path):
        """Show help content in a new dialog."""
        with ui.dialog() as dialog, ui.card().classes('w-full').style('max-width: 800px; max-height: 80vh'):
            with ui.row().classes('w-full items-center mb-2'):
                ui.label(filepath.stem.replace('-', ' ').title()).classes('text-h6')
                ui.space()
                ui.button(icon='close', on_click=dialog.close).props('flat')

            with ui.scroll_area().classes('w-full').style('height: 60vh'):
                try:
                    content = filepath.read_text(encoding='utf-8')

                    # Expand macros
                    from ui.help_macros import HelpMacros
                    help_root = Path(__file__).parent.parent.parent.parent / 'docs' / 'help'
                    macros = HelpMacros('web', str(help_root))
                    content = macros.expand(content)

                    ui.markdown(content).classes('w-full')
                except Exception as e:
                    ui.label(f'Error: {str(e)}').classes('text-negative')

        dialog.open()

    def _search_help(self, query: str, help_root: Path, results_area):
        """Search help topics."""
        if not query:
            ui.notify('Please enter a search term', type='warning')
            return

        results_area.clear()

        with results_area:
            ui.label(f'Search results for: {query}').classes('text-h6 mb-4')

            # Search all markdown files
            results = []
            query_lower = query.lower()

            for md_file in help_root.rglob('*.md'):
                try:
                    content = md_file.read_text(encoding='utf-8').lower()
                    if query_lower in content:
                        # Get relative path for display
                        rel_path = md_file.relative_to(help_root)
                        title = md_file.stem.replace('-', ' ').title()
                        results.append((title, str(rel_path), md_file))
                except:
                    pass

            if results:
                ui.label(f'Found {len(results)} matches').classes('text-grey-7 mb-2')

                with ui.column().classes('gap-2'):
                    for title, rel_path, filepath in results[:50]:  # Limit to 50 results
                        with ui.card().classes('w-full'):
                            ui.label(title).classes('text-bold')
                            ui.label(rel_path).classes('text-sm text-grey-6')
                            ui.button(
                                'View',
                                on_click=lambda fp=filepath: self._show_help_content(fp)
                            ).props('flat color=primary')
            else:
                ui.label('No results found').classes('text-grey-6')

    async def menu_about(self):
        """Show about dialog."""
        with ui.dialog() as dialog, ui.card().classes('w-96'):
            ui.label('About MBASIC').classes('text-h6')

            ui.markdown('''
**MBASIC 5.21 Web IDE**

A full-featured Python implementation of Microsoft BASIC-80 5.21
for CP/M systems, running in your web browser.

**Features:**
- Full BASIC 5.21 language support
- Visual debugger with breakpoints
- Variables and stack inspection
- File save/load
- Example programs

**License:** Open Source
**Repository:** github.com/avwohl/mbasic
''')

            ui.button('Close', on_click=dialog.close).props('flat')

        dialog.open()

    async def show_examples(self):
        """Show example programs menu."""
        examples = {
            'Hello World': '''10 PRINT "HELLO WORLD"
20 END
''',
            'Loops': '''10 REM Loop Example
20 FOR I = 1 TO 10
30   PRINT I; " squared is "; I*I
40 NEXT I
50 END
''',
            'Fibonacci': '''10 REM Fibonacci Sequence
20 A = 0
30 B = 1
40 FOR I = 1 TO 10
50   PRINT A;
60   C = A + B
70   A = B
80   B = C
90 NEXT I
100 PRINT
110 END
''',
            'User Input': '''10 REM User Input Example
20 PRINT "What is your name?"
30 INPUT N$
40 PRINT "Hello, "; N$; "!"
50 PRINT "Enter a number:"
60 INPUT X
70 PRINT "Your number squared is "; X*X
80 END
''',
            'Nested Loops': '''10 REM Multiplication Table
20 FOR I = 1 TO 5
30   FOR J = 1 TO 5
40     PRINT I*J;
50   NEXT J
60   PRINT
70 NEXT I
80 END
''',
            'GOSUB Demo': '''10 REM GOSUB Example
20 GOSUB 100
30 PRINT "Back from subroutine"
40 END
100 REM Subroutine
110 PRINT "In subroutine"
120 RETURN
''',
        }

        # Create selection dialog
        with ui.dialog() as dialog, ui.card():
            ui.label('Choose an Example Program').classes('text-h6 mb-4')

            for name, code in examples.items():
                ui.button(
                    name,
                    on_click=lambda c=code: self.load_example(c, dialog)
                ).props('flat color=primary').classes('w-full mb-2')

            ui.button('Cancel', on_click=dialog.close).props('flat')

        dialog.open()

    def load_example(self, code, dialog):
        """Load an example program into the editor."""
        self.editor.value = code
        self.current_file = 'example.bas'
        self.breakpoints.clear()
        self.update_line_numbers()
        ui.notify('Example loaded')
        dialog.close()


def create_app():
    """Create and configure the NiceGUI app."""
    ide = MBasicWebIDE()
    ide.create_ui()


# Run the app
if __name__ in {"__main__", "__mp_main__"}:
    import secrets

    # Generate a storage secret for session security
    # In production, use environment variable or config file
    storage_secret = secrets.token_urlsafe(32)

    ui.run(
        title='MBASIC 5.21 Web IDE',
        port=8080,
        reload=False,
        show=False,  # Don't auto-open browser
        storage_secret=storage_secret,  # Required for app.storage.user
    )
