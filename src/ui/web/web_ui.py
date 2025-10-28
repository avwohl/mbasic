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

from src.iohandler.web_io import WebIOHandler
from src.ui.recent_files import RecentFilesManager
from lexer import Lexer
from parser import Parser
from interpreter import Interpreter
from runtime import Runtime
from filesystem import SandboxedFileSystemProvider
from immediate_executor import ImmediateExecutor, OutputCapturingIOHandler
from input_sanitizer import sanitize_and_clear_parity


class MBasicWebIDE:
    """Main MBASIC Web IDE application with full debugger support."""

    def __init__(self):
        """Initialize the IDE."""
        # UI components
        self.editor = None
        self.output_log = None
        self.status_label = None
        self.line_display = None

        # Recent files manager
        self.recent_files = RecentFilesManager()

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
        self.line_errors: Set[int] = set()  # Track lines with parse errors
        self.tick_timer = None

        # Variables window
        self.variables_dialog = None
        self.variables_table = None
        self.variables_visible = False
        self.variables_filter_text = ""  # Filter text for variables window
        self.variables_filter_input = None  # Filter input widget

        # Stack window
        self.stack_dialog = None
        self.stack_table = None
        self.stack_visible = False

        # Immediate mode
        self.immediate_executor = None
        self.immediate_log = None
        self.immediate_input = None
        self.immediate_status = None

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
        .error-line {
            background-color: #ffcccc;
            color: #c00;
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
                        ui.menu_item('Recent Files...', on_click=self.show_recent_files, auto_close=True)
                        ui.separator()
                        ui.menu_item('Save', on_click=self.menu_save, auto_close=True)
                        ui.menu_item('Save As', on_click=self.menu_save_as, auto_close=True)
                        ui.separator()
                        ui.menu_item('Load Example', on_click=self.show_examples, auto_close=True)

                # Edit menu
                with ui.button(icon='edit', color='white').props('flat'):
                    with ui.menu() as menu:
                        ui.menu_item('Sort Lines', on_click=self.sort_program_lines, auto_close=True)
                        ui.menu_item('Renumber...', on_click=self.menu_renumber, auto_close=True)
                        ui.separator()
                        ui.menu_item('Insert Line Between', on_click=self.smart_insert_line, auto_close=True)

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
                        ui.button('Sort', on_click=self.sort_program_lines, icon='sort', tooltip='Sort lines by line number').props('outline')
                        ui.button('Renumber', on_click=self.renumber_program, icon='format_list_numbered', tooltip='Renumber lines (10, 20, 30...)').props('outline')
                        ui.separator().props('vertical')
                        ui.button('Breakpoint', on_click=self.toggle_breakpoint, icon='radio_button_checked').props('outline')
                        ui.button('Variables', on_click=self.toggle_variables, icon='list').props('outline')
                        ui.button('Stack', on_click=self.toggle_stack, icon='view_list').props('outline')

            # Right panel: Output and Immediate Mode
            with splitter.after:
                # Output section (70% height)
                with ui.card().classes('w-full').style('height: 60%; margin-bottom: 8px'):
                    ui.label('Output').classes('text-h6 mb-2')

                    # Output log
                    self.output_log = ui.log(max_lines=1000).classes('output-log w-full').style('height: calc(100% - 40px)')
                    self.output_log.push('MBASIC 5.21 Web IDE')
                    self.output_log.push('Ready')
                    self.output_log.push('')

                # Immediate Mode section (30% height)
                with ui.card().classes('w-full').style('height: calc(40% - 8px)'):
                    with ui.row().classes('items-center mb-2'):
                        ui.label('Immediate Mode').classes('text-h6')
                        ui.space()
                        self.immediate_status = ui.label('Ok').classes('text-sm font-bold text-green')

                    # Immediate mode history log
                    self.immediate_log = ui.log(max_lines=100).classes('output-log w-full').style('height: calc(100% - 90px); font-size: 12px')

                    # Immediate mode input
                    with ui.row().classes('w-full items-center gap-2 mt-2'):
                        ui.label('Ok >').classes('text-sm font-mono')
                        self.immediate_input = ui.input(
                            placeholder='Enter BASIC command (e.g., PRINT X, A=5) or HELP'
                        ).classes('flex-grow code-editor').on('keydown.enter', self.execute_immediate)

                        ui.button('Execute', on_click=self.execute_immediate, icon='play_arrow').props('dense color=secondary')

                    # Help hint
                    ui.label('Type HELP for available commands').classes('text-xs text-grey-6 mt-1')

        # Footer status bar
        with ui.footer():
            self.status_label = ui.label('Ready').classes('text-sm')

        # Initialize line numbers and validate syntax
        self.update_line_numbers()
        self._validate_editor_syntax()

        # Set up keyboard shortcuts
        self._setup_keyboard_shortcuts()

    def _setup_keyboard_shortcuts(self):
        """Set up global keyboard shortcuts for the web UI."""
        async def handle_keydown(e):
            """Handle keyboard shortcuts."""
            key = e.key
            ctrl = e.modifiers.get('ctrl', False) or e.modifiers.get('ctrlKey', False)

            # Ignore if typing in input fields
            if e.sender and hasattr(e.sender, 'tag') and e.sender.tag in ['input', 'textarea']:
                # Allow shortcuts in editor, but not in other inputs
                if e.sender != self.editor:
                    return

            # Ctrl+R - Run
            if ctrl and key.lower() == 'r':
                e.handled = True
                await self.menu_run()

            # Ctrl+T - Step
            elif ctrl and key.lower() == 't':
                e.handled = True
                self.menu_step()

            # Ctrl+G - Continue
            elif ctrl and key.lower() == 'g':
                e.handled = True
                self.menu_continue()

            # Ctrl+Q - Stop
            elif ctrl and key.lower() == 'q':
                e.handled = True
                self.menu_stop()

            # Ctrl+B - Toggle breakpoint (show notification)
            elif ctrl and key.lower() == 'b':
                e.handled = True
                self.toggle_breakpoint()

            # Ctrl+V - Variables window
            elif ctrl and key.lower() == 'v':
                e.handled = True
                self.toggle_variables()

            # Ctrl+K - Stack window
            elif ctrl and key.lower() == 'k':
                e.handled = True
                self.toggle_stack()

            # Ctrl+N - New program
            elif ctrl and key.lower() == 'n':
                e.handled = True
                self.menu_new()

            # Ctrl+S - Save
            elif ctrl and key.lower() == 's':
                e.handled = True
                self.menu_save()

            # Ctrl+O - Open
            elif ctrl and key.lower() == 'o':
                e.handled = True
                await self.menu_open()

            # Ctrl+E - Renumber
            elif ctrl and key.lower() == 'e':
                e.handled = True
                self.renumber_program()

        # Register keyboard handler
        ui.keyboard(on_key=handle_keydown)

    def update_line_numbers(self, e=None):
        """Update line numbers display based on editor content."""
        if not self.editor or not self.line_numbers:
            return

        lines = self.editor.value.split('\n') if self.editor.value else ['']
        self.line_numbers.clear()

        for i, line in enumerate(lines, 1):
            # Extract BASIC line number from this editor line
            import re
            match = re.match(r'^\s*(\d+)', line)
            basic_line_num = int(match.group(1)) if match else None

            # Determine status with priority: error > breakpoint > normal
            has_error = basic_line_num in self.line_errors if basic_line_num else False
            has_breakpoint = basic_line_num in self.breakpoints if basic_line_num else False

            if has_error:
                # Error marker - red background
                bg_color = '#ffcccc'
                text_color = '#c00'
                marker = '? '
            elif has_breakpoint:
                # Breakpoint - light red background
                bg_color = '#ffebee'
                text_color = 'inherit'
                marker = '● '
            else:
                # Normal line
                bg_color = 'transparent'
                text_color = 'inherit'
                marker = ''

            with self.line_numbers:
                ui.label(marker + str(i)).classes('text-right').style(
                    f'width: 100%; padding: 2px 4px; background-color: {bg_color}; color: {text_color}; cursor: pointer'
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

    def _check_line_syntax(self, code_text: str) -> tuple[bool, Optional[str]]:
        """Check if a line of BASIC code has valid syntax.

        Args:
            code_text: The BASIC code to check (without line number)

        Returns:
            Tuple of (is_valid, error_message)
            - is_valid: True if syntax is valid, False otherwise
            - error_message: Error description if invalid, None if valid
        """
        if not code_text or not code_text.strip():
            return (True, None)

        try:
            # Try to parse the line
            lexer = Lexer(code_text)
            tokens = lexer.tokenize()

            # Create a minimal parser to check syntax
            # Note: We don't have def_type_map here, but that's okay for basic syntax checking
            parser = Parser(tokens, {}, source=code_text)
            parser.parse_line()

            return (True, None)

        except Exception as e:
            import re
            error_msg = str(e)
            # Clean up error message (remove "Parse error at line N, " prefix)
            error_msg = re.sub(r'^Parse error at line \d+, ', '', error_msg)
            return (False, error_msg)

    def _validate_editor_syntax(self):
        """Validate syntax of all lines in the editor and update error markers."""
        import re

        if not self.editor or not self.editor.value:
            return

        # Clear all previous errors
        self.line_errors.clear()

        lines = self.editor.value.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Extract line number and code
            match = re.match(r'^(\d+)\s+(.+)', line)
            if match:
                line_num = int(match.group(1))
                code = match.group(2)

                # Check syntax
                is_valid, error_msg = self._check_line_syntax(code)
                if not is_valid:
                    self.line_errors.add(line_num)

        # Update display
        self.update_line_numbers()

    def sort_program_lines(self):
        """Sort program lines by line number."""
        import re

        if not self.editor or not self.editor.value:
            ui.notify('No program to sort', type='warning')
            return

        lines = self.editor.value.split('\n')

        # Separate lines with and without line numbers
        numbered_lines = []
        unnumbered_lines = []

        line_num_pattern = re.compile(r'^\s*(\d+)\s')

        for line in lines:
            match = line_num_pattern.match(line)
            if match:
                line_number = int(match.group(1))
                numbered_lines.append((line_number, line))
            else:
                # Keep unnumbered lines (comments, blank lines) at the end
                if line.strip():  # Only keep non-empty unnumbered lines
                    unnumbered_lines.append(line)

        # Sort numbered lines
        numbered_lines.sort(key=lambda x: x[0])

        # Rebuild program
        sorted_lines = [line for _, line in numbered_lines] + unnumbered_lines

        self.editor.value = '\n'.join(sorted_lines)
        self.update_line_numbers()
        self._validate_editor_syntax()
        ui.notify('Program lines sorted', type='positive')

    def renumber_program(self):
        """Renumber program lines starting at 10 with increment of 10."""
        import re

        if not self.editor or not self.editor.value:
            ui.notify('No program to renumber', type='warning')
            return

        # Create dialog to get renumber parameters
        with ui.dialog() as dialog, ui.card():
            ui.label('Renumber Program').classes('text-h6 mb-2')

            start_input = ui.number(label='Start line number', value=10, format='%.0f').classes('w-full mb-2')
            increment_input = ui.number(label='Increment', value=10, format='%.0f').classes('w-full mb-2')

            with ui.row().classes('w-full gap-2 mt-4'):
                ui.button('Cancel', on_click=dialog.close).props('flat')
                ui.button(
                    'Renumber',
                    on_click=lambda: self._apply_renumber(int(start_input.value), int(increment_input.value), dialog)
                ).props('color=primary')

        dialog.open()

    def _apply_renumber(self, start: int, increment: int, dialog, old_start: int = 0):
        """Apply renumbering to program using shared ui_helpers module."""
        import re
        from src.ui.ui_helpers import parse_line_number, renumber_program_lines

        lines = self.editor.value.split('\n')

        # Parse lines with line numbers
        lines_dict = {}
        unnumbered_lines = []

        for line in lines:
            line_num = parse_line_number(line)
            if line_num is not None:
                lines_dict[line_num] = line
            else:
                # Keep unnumbered lines (comments, blank lines)
                if line.strip():
                    unnumbered_lines.append(line)

        if not lines_dict:
            ui.notify('No numbered lines to renumber', type='warning')
            dialog.close()
            return

        # Use shared renumber logic from ui_helpers
        new_lines, line_mapping = renumber_program_lines(lines_dict, start, old_start, increment)

        # Format lines with right-alignment (Web UI style)
        formatted_lines = [f'{num:>5} {line.split(None, 1)[1] if len(line.split(None, 1)) > 1 else ""}'
                          for num, line in sorted(new_lines.items())]

        # Rebuild program
        self.editor.value = '\n'.join(formatted_lines + unnumbered_lines)
        self.update_line_numbers()
        self._validate_editor_syntax()

        # Calculate final line number for notification
        final_num = max(new_lines.keys()) if new_lines else start
        ui.notify(f'Program renumbered ({start} to {final_num})', type='positive')
        dialog.close()

    def smart_insert_line(self):
        """Smart insert - insert blank line before cursor position with calculated line number.

        Calculates midpoint between previous and current line numbers.
        If no room, offers to renumber the program.
        """
        import re

        if not self.editor or not self.editor.value:
            ui.notify('No program loaded', type='warning')
            return

        # Get all lines
        lines = self.editor.value.split('\n')

        # Parse all line numbers from program
        all_line_numbers = []
        line_number_pattern = re.compile(r'^\s*(\d+)')

        for line in lines:
            match = line_number_pattern.match(line)
            if match:
                all_line_numbers.append(int(match.group(1)))

        if not all_line_numbers:
            ui.notify('No numbered lines found. Add a line number first.', type='warning')
            return

        all_line_numbers = sorted(set(all_line_numbers))  # Remove duplicates and sort

        # For Web UI, we don't have cursor position, so we'll prompt for the line number
        # where the user wants to insert before
        with ui.dialog() as dialog, ui.card():
            ui.label('Insert Line Between').classes('text-h6')
            ui.label('Enter the line number you want to insert BEFORE:')

            target_input = ui.input(
                label='Target Line Number',
                placeholder='e.g., 30'
            ).classes('w-full')

            with ui.row():
                ui.button('Insert', on_click=lambda: self._do_smart_insert(
                    target_input.value,
                    all_line_numbers,
                    dialog
                )).props('color=primary')
                ui.button('Cancel', on_click=dialog.close).props('flat')

        dialog.open()

    def _do_smart_insert(self, target_line_str: str, all_line_numbers: list, dialog):
        """Perform the smart insert operation.

        Args:
            target_line_str: Target line number (as string from input)
            all_line_numbers: List of existing line numbers
            dialog: Dialog to close after operation
        """
        import re

        # Validate input
        if not target_line_str or not target_line_str.strip():
            ui.notify('Please enter a line number', type='warning')
            return

        try:
            target_line = int(target_line_str.strip())
        except ValueError:
            ui.notify('Invalid line number', type='negative')
            return

        # Check if target line exists
        if target_line not in all_line_numbers:
            ui.notify(f'Line {target_line} not found in program', type='warning')
            return

        # Find previous line before target
        prev_line_num = None
        for line_num in reversed(all_line_numbers):
            if line_num < target_line:
                prev_line_num = line_num
                break

        # Calculate insertion point
        if prev_line_num is None:
            # At beginning of program
            insert_num = max(1, target_line - 10)
            if insert_num >= target_line:
                insert_num = target_line - 1 if target_line > 1 else 1
        else:
            # Between previous and target lines - try midpoint
            midpoint = (prev_line_num + target_line) // 2
            if midpoint > prev_line_num and midpoint < target_line:
                insert_num = midpoint
            else:
                # No room - offer to renumber
                with ui.dialog() as renum_dialog, ui.card():
                    ui.label('No Room').classes('text-h6')
                    ui.label(f'No room between lines {prev_line_num} and {target_line}.')
                    ui.label('Would you like to renumber the program to make room?')

                    with ui.row():
                        ui.button('Renumber', on_click=lambda: [
                            renum_dialog.close(),
                            dialog.close(),
                            self.menu_renumber()
                        ]).props('color=primary')
                        ui.button('Cancel', on_click=renum_dialog.close).props('flat')

                renum_dialog.open()
                return

        # Insert the new blank line before target line
        lines = self.editor.value.split('\n')
        new_lines = []
        inserted = False

        for line in lines:
            # Check if this is the target line
            match = re.match(r'^\s*(\d+)', line)
            if match and int(match.group(1)) == target_line and not inserted:
                # Insert blank line before this line
                new_lines.append(f'{insert_num} ')
                inserted = True

            new_lines.append(line)

        # Update editor
        self.editor.value = '\n'.join(new_lines)
        self.update_line_numbers()

        ui.notify(f'Inserted line {insert_num} before line {target_line}', type='positive')
        dialog.close()

    # File operations
    def menu_new(self):
        """Create a new program."""
        self.editor.value = '10 \n'
        self.current_file = 'untitled.bas'
        self.current_path = None
        self.breakpoints.clear()
        self.line_errors.clear()
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

            # Sanitize input: clear parity bits and filter control characters
            content, was_modified = sanitize_and_clear_parity(content)
            if was_modified:
                ui.notify('File content was sanitized (control characters removed)', type='info')

            self.editor.value = content
            self.current_file = e.name
            self.current_path = None
            self.update_line_numbers()
            self._validate_editor_syntax()
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

            # Sanitize input: clear parity bits and filter control characters
            content, was_modified = sanitize_and_clear_parity(content)
            if was_modified:
                ui.notify('File content was sanitized (control characters removed)', type='info')

            self.editor.value = content

            # Add to recent files
            self.recent_files.add_file(str(file_path))
            self.current_file = file_name
            self.current_path = None
            self.breakpoints.clear()
            self.line_errors.clear()
            self.update_line_numbers()
            self._validate_editor_syntax()
            dialog.close()
            ui.notify(f'Loaded {file_name}', type='positive')
        except Exception as ex:
            ui.notify(f'Error loading file: {str(ex)}', type='negative')

    def show_recent_files(self):
        """Show dialog with recent files."""
        from pathlib import Path

        # Get recent files
        recent_files = self.recent_files.get_recent_files_with_info(max_count=10)

        if not recent_files:
            ui.notify('No recent files', type='info')
            return

        # Create dialog with recent files
        with ui.dialog() as dialog, ui.card().classes('w-full').style('max-width: 600px'):
            ui.label('Recent Files').classes('text-h6 mb-2')

            # File list
            with ui.scroll_area().classes('w-full').style('max-height: 400px'):
                with ui.column().classes('w-full'):
                    for file_info in recent_files:
                        filepath = file_info['path']
                        filename = file_info['filename']
                        exists = file_info['exists']

                        with ui.row().classes('w-full items-center'):
                            # Icon based on existence
                            if exists:
                                ui.icon('description').classes('text-grey-6')
                            else:
                                ui.icon('warning').classes('text-red-6')

                            # File button
                            if exists:
                                ui.button(
                                    filename,
                                    on_click=lambda p=filepath, n=filename: self.open_recent_file(p, n, dialog)
                                ).props('flat align=left').classes('flex-grow')
                            else:
                                ui.button(
                                    f'{filename} (not found)',
                                    on_click=lambda: None
                                ).props('flat align=left disabled').classes('flex-grow text-grey-6')

            ui.separator()

            # Clear button
            with ui.row().classes('w-full justify-between'):
                ui.button(
                    'Clear Recent Files',
                    on_click=lambda: self.clear_recent_files(dialog)
                ).props('flat color=negative')
                ui.button('Close', on_click=dialog.close).props('flat')

        dialog.open()

    def open_recent_file(self, filepath: str, filename: str, dialog):
        """Open a file from recent files list."""
        file_path = Path(filepath)

        if not file_path.exists():
            ui.notify(f'File not found: {filename}', type='negative')
            # Remove from recent files
            self.recent_files.remove_file(filepath)
            dialog.close()
            return

        # Load the file using load_server_file logic
        self.load_server_file(file_path, filename, dialog)

    def clear_recent_files(self, dialog):
        """Clear the recent files list."""
        self.recent_files.clear()
        ui.notify('Recent files cleared', type='positive')
        dialog.close()

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

            # Sanitize input: clear parity bits and filter control characters
            code, was_modified = sanitize_and_clear_parity(code)
            if was_modified:
                ui.notify('Editor content was sanitized (control characters removed)', type='info')

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

            # Create resource limits for web environment (restrictive)
            from resource_limits import create_web_limits
            limits = create_web_limits()

            # Create interpreter with program and sandboxed filesystem
            self.interpreter = Interpreter(self.runtime, self.io_handler, filesystem_provider=filesystem, limits=limits)

            # Set breakpoints
            self.interpreter.breakpoints = self.breakpoints.copy()

            # Initialize immediate mode executor
            immediate_io = OutputCapturingIOHandler()
            self.immediate_executor = ImmediateExecutor(self.runtime, self.interpreter, immediate_io)
            self.update_immediate_status()

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
            self.update_immediate_status()

            if result == 'BREAK':
                # Hit breakpoint
                self.paused_at_breakpoint = True
                state = self.interpreter.state
                stmt_info = f' statement {state.current_statement_index + 1}' if state.current_statement_index > 0 else ''
                self.status_label.text = f'Paused at breakpoint (line {self.interpreter.current_line_number}{stmt_info})'
                ui.notify(f'Breakpoint at line {self.interpreter.current_line_number}', type='info')
                self.running = False
                self.update_immediate_status()
                return

            elif result == 'DONE':
                # Program finished
                self.output_log.push('')
                self.status_label.text = 'Program completed'
                ui.notify('Program completed', type='positive')
                self.running = False
                self.update_immediate_status()
                return

            # Continue execution - show current position
            state = self.interpreter.state
            stmt_info = f' [stmt {state.current_statement_index + 1}]' if state.current_statement_index > 0 else ''
            self.status_label.text = f'Running... line {self.interpreter.current_line_number}{stmt_info}'
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

            state = self.interpreter.state
            stmt_info = f' statement {state.current_statement_index + 1}' if state.current_statement_index > 0 else ''

            if result == 'DONE':
                self.status_label.text = 'Program completed'
                ui.notify('Program completed', type='positive')
            elif result == 'BREAK':
                self.status_label.text = f'Breakpoint at line {self.interpreter.current_line_number}{stmt_info}'
            else:
                self.status_label.text = f'Paused at line {self.interpreter.current_line_number}{stmt_info}'

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
                    ui.button('Edit Selected', on_click=self.edit_selected_variable, icon='edit').props('outline')
                    ui.button(icon='close', on_click=lambda: self.close_variables()).props('flat')

                # Filter input
                with ui.row().classes('items-center mb-2 w-full'):
                    ui.label('Filter:').classes('mr-2')
                    self.variables_filter_input = ui.input(
                        placeholder='Search name, value, or type...',
                        value=self.variables_filter_text
                    ).classes('flex-grow').on('change', self._on_variables_filter_change)
                    ui.button('Clear', on_click=self._clear_variables_filter, icon='clear').props('flat')

                # Variables table with selection enabled
                self.variables_table = ui.table(
                    columns=[
                        {'name': 'name', 'label': 'Name', 'field': 'name', 'align': 'left'},
                        {'name': 'value', 'label': 'Value', 'field': 'value', 'align': 'left'},
                        {'name': 'type', 'label': 'Type', 'field': 'type', 'align': 'left'},
                    ],
                    rows=[],
                    row_key='name',
                    selection='single'
                ).classes('w-full')

                # Enable double-click to edit
                self.variables_table.on('rowDblclick', lambda e: self.edit_variable_by_name(e.args[1]['name']))

        self.variables_visible = True
        dialog.open()
        self.update_variables_window()

    def close_variables(self):
        """Close variables window."""
        if self.variables_dialog:
            self.variables_dialog.close()
        self.variables_visible = False

    def _on_variables_filter_change(self):
        """Handle variable filter text change."""
        if self.variables_filter_input:
            self.variables_filter_text = self.variables_filter_input.value
            self.update_variables_window()

    def _clear_variables_filter(self):
        """Clear the variable filter."""
        self.variables_filter_text = ""
        if self.variables_filter_input:
            self.variables_filter_input.value = ""
        self.update_variables_window()

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

        # Apply filter if present
        if self.variables_filter_text:
            filter_lower = self.variables_filter_text.lower()
            filtered_rows = []
            for row in rows:
                # Check if filter matches name, value, or type
                if (filter_lower in row['name'].lower() or
                    filter_lower in row['value'].lower() or
                    filter_lower in row['type'].lower()):
                    filtered_rows.append(row)
            rows = filtered_rows

        self.variables_table.rows = rows
        self.variables_table.update()

    def edit_selected_variable(self):
        """Edit the currently selected variable."""
        if not self.variables_table or not self.variables_table.selected:
            ui.notify('No variable selected', type='warning')
            return

        # Get selected row
        selected = self.variables_table.selected[0] if self.variables_table.selected else None
        if not selected:
            ui.notify('No variable selected', type='warning')
            return

        var_name = selected['name']
        self.edit_variable_by_name(var_name)

    def edit_variable_by_name(self, var_name: str):
        """Edit a variable by name."""
        if not self.runtime:
            ui.notify('No program running', type='warning')
            return

        # Get variable from runtime
        if var_name not in self.runtime.variables:
            ui.notify(f'Variable {var_name} not found', type='warning')
            return

        value = self.runtime.variables[var_name]

        # Determine type suffix
        if var_name.endswith('$'):
            type_suffix = '$'
            base_name = var_name[:-1]
        elif var_name.endswith('%'):
            type_suffix = '%'
            base_name = var_name[:-1]
        elif var_name.endswith('!'):
            type_suffix = '!'
            base_name = var_name[:-1]
        elif var_name.endswith('#'):
            type_suffix = '#'
            base_name = var_name[:-1]
        else:
            type_suffix = ''
            base_name = var_name

        # Check if array
        if hasattr(value, 'dimensions'):
            # Array variable - edit last accessed element
            access_info = self.runtime.variable_accessed.get(var_name, {})
            last_subscripts = access_info.get('last_accessed_subscripts')
            last_value = access_info.get('last_accessed_value')

            if last_subscripts is not None:
                self._edit_array_element(base_name, type_suffix, last_subscripts, last_value)
            else:
                ui.notify('Array not accessed yet - no element to edit', type='warning')
        else:
            # Simple variable
            self._edit_simple_variable(base_name, type_suffix, value)

    def _edit_simple_variable(self, base_name: str, type_suffix: str, current_value):
        """Edit a simple (non-array) variable."""
        var_display = f'{base_name}{type_suffix}'

        # Create edit dialog based on type
        with ui.dialog() as dialog, ui.card():
            ui.label(f'Edit Variable: {var_display}').classes('text-h6 mb-2')
            ui.label(f'Current value: {current_value}').classes('text-sm text-grey-7 mb-4')

            # Input based on type
            if type_suffix == '$':
                # String variable
                new_value_input = ui.input(
                    label='New value',
                    value=str(current_value).strip('"'),
                    placeholder='Enter string value'
                ).classes('w-full')
            elif type_suffix == '%':
                # Integer variable
                new_value_input = ui.number(
                    label='New value',
                    value=int(current_value),
                    format='%.0f'
                ).classes('w-full')
            else:
                # Float variable (single or double precision)
                new_value_input = ui.number(
                    label='New value',
                    value=float(current_value)
                ).classes('w-full')

            with ui.row().classes('w-full gap-2 mt-4'):
                ui.button('Cancel', on_click=dialog.close).props('flat')
                ui.button(
                    'Apply',
                    on_click=lambda: self._apply_simple_variable_edit(base_name, type_suffix, new_value_input.value, dialog)
                ).props('color=primary')

        dialog.open()

    def _apply_simple_variable_edit(self, base_name: str, type_suffix: str, new_value, dialog):
        """Apply the edit to a simple variable."""
        try:
            # Set the variable in runtime
            self.runtime.set_variable(base_name, type_suffix, new_value, debugger_set=True)

            # Update display
            self.update_variables_window()

            ui.notify(f'Variable {base_name}{type_suffix} updated', type='positive')
            dialog.close()

        except Exception as e:
            ui.notify(f'Error updating variable: {str(e)}', type='negative')

    def _edit_array_element(self, base_name: str, type_suffix: str, subscripts, current_value):
        """Edit any array element by typing subscripts."""
        var_display = f'{base_name}{type_suffix}'
        default_subscripts_str = ','.join(str(s) for s in subscripts)

        # Get array dimensions
        try:
            array_var = self.runtime.get_variable(base_name, type_suffix)
            dimensions = array_var.dimensions if hasattr(array_var, 'dimensions') else []
            dimensions_str = 'x'.join(str(d) for d in dimensions)
        except:
            dimensions = []
            dimensions_str = '?'

        # Create edit dialog with subscripts input
        with ui.dialog() as dialog, ui.card().classes('w-96'):
            ui.label(f'Edit Array Element: {var_display}({dimensions_str})').classes('text-h6 mb-2')

            # Subscripts input
            subscripts_input = ui.input(
                label='Subscripts (e.g., 1,2,3)',
                value=default_subscripts_str,
                placeholder='0,0'
            ).classes('w-full mb-2')

            # Current value display (updates when subscripts change)
            current_value_label = ui.label('').classes('text-sm text-blue-7 mb-2')
            error_label = ui.label('').classes('text-sm text-red-7 mb-2')

            # Value input
            value_input = None
            if type_suffix == '$':
                value_input = ui.input(label='New value', placeholder='Enter string value').classes('w-full')
            elif type_suffix == '%':
                value_input = ui.number(label='New value', format='%.0f').classes('w-full')
            else:
                value_input = ui.number(label='New value').classes('w-full')

            def update_current_value():
                """Update current value display when subscripts change."""
                subscripts_str = subscripts_input.value.strip()
                if not subscripts_str:
                    current_value_label.text = 'Enter subscripts above'
                    error_label.text = ''
                    return

                try:
                    # Parse subscripts
                    subs = [int(s.strip()) for s in subscripts_str.split(',')]

                    # Validate dimension count
                    if dimensions and len(subs) != len(dimensions):
                        error_label.text = f'Expected {len(dimensions)} subscripts, got {len(subs)}'
                        current_value_label.text = ''
                        return

                    # Validate bounds
                    for i, sub in enumerate(subs):
                        if dimensions and i < len(dimensions):
                            if sub < 0 or sub > dimensions[i]:
                                error_label.text = f'Subscript {i} out of bounds: {sub} not in [0, {dimensions[i]}]'
                                current_value_label.text = ''
                                return

                    # Get current value
                    array_var = self.runtime.get_variable(base_name, type_suffix)
                    index = 0
                    multiplier = 1
                    for i in reversed(range(len(subs))):
                        index += subs[i] * multiplier
                        multiplier *= (dimensions[i] + 1)

                    current_val = array_var.elements[index]
                    current_value_label.text = f'Current value: {current_val}'
                    error_label.text = ''

                except ValueError:
                    error_label.text = 'Invalid subscripts (must be integers)'
                    current_value_label.text = ''
                except Exception as e:
                    error_label.text = f'Error: {str(e)}'
                    current_value_label.text = ''

            # Update on subscripts change
            subscripts_input.on('blur', update_current_value)

            # Initial update
            update_current_value()

            def on_apply():
                """Apply the array element edit."""
                subscripts_str = subscripts_input.value.strip()
                if not subscripts_str:
                    ui.notify('Please enter subscripts', type='warning')
                    return

                try:
                    # Parse subscripts
                    subs = [int(s.strip()) for s in subscripts_str.split(',')]

                    # Get new value
                    new_value = value_input.value
                    if new_value is None or new_value == '':
                        ui.notify('Please enter a new value', type='warning')
                        return

                    # Update array element
                    self.runtime.set_array_element(base_name, type_suffix, subs, new_value, token=None)

                    # Update display
                    self.update_variables_window()

                    ui.notify(f'Array element {var_display}({subscripts_str}) updated', type='positive')
                    dialog.close()

                except ValueError as e:
                    ui.notify(f'Invalid value: {str(e)}', type='negative')
                except Exception as e:
                    ui.notify(f'Error: {str(e)}', type='negative')

            with ui.row().classes('w-full gap-2 mt-4'):
                ui.button('Cancel', on_click=dialog.close).props('flat')
                ui.button('Apply', on_click=on_apply).props('color=primary')

        dialog.open()

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
                from src.ui.help_macros import HelpMacros
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
                    from src.ui.help_macros import HelpMacros
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
        self.line_errors.clear()
        self.update_line_numbers()
        self._validate_editor_syntax()
        ui.notify('Example loaded')
        dialog.close()

    def update_immediate_status(self):
        """Update immediate mode panel status based on interpreter state."""
        if not self.immediate_executor or not self.immediate_status or not self.immediate_input:
            return

        if self.immediate_executor.can_execute_immediate():
            # Safe to execute - enable input
            self.immediate_status.text = 'Ok'
            self.immediate_status.classes(remove='text-red', add='text-green')
            self.immediate_input.enable()
        else:
            # Not safe - disable input
            status = self.interpreter.state.status if hasattr(self.interpreter, 'state') else 'unknown'
            self.immediate_status.text = f'[{status}]'
            self.immediate_status.classes(remove='text-green', add='text-red')
            self.immediate_input.disable()

    def execute_immediate(self):
        """Execute immediate mode command."""
        if not self.immediate_executor or not self.immediate_input or not self.immediate_log:
            ui.notify('Immediate mode not initialized', type='warning')
            return

        command = self.immediate_input.value.strip()
        if not command:
            return

        # Check if safe to execute
        if not self.immediate_executor.can_execute_immediate():
            self.immediate_log.push('Cannot execute while program is running')
            ui.notify('Cannot execute while program is running', type='warning')
            return

        # Log the command
        self.immediate_log.push(f'> {command}')

        # Execute
        success, output = self.immediate_executor.execute(command)

        # Log the result
        if output:
            for line in output.rstrip().split('\n'):
                self.immediate_log.push(line)

        if success:
            self.immediate_log.push('Ok')
        else:
            ui.notify('Immediate mode error', type='negative')

        # Clear input
        self.immediate_input.value = ''

        # Update variables/stack windows if open
        self.update_variables_window()
        self.update_stack_window()


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
