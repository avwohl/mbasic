"""NiceGUI web backend for MBASIC.

Provides a modern web-based UI for the MBASIC interpreter using NiceGUI.
"""

import re
import sys
import asyncio
import traceback
import signal
from nicegui import ui, app
from pathlib import Path
from ..base import UIBackend
from src.runtime import Runtime
from src.interpreter import Interpreter
from src.iohandler.base import IOHandler
from src.version import VERSION
from src.pc import PC
from src.ui.web.codemirror5_editor import CodeMirror5Editor
import re


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


class VariablesDialog(ui.dialog):
    """Reusable dialog for showing program variables."""

    def __init__(self, backend):
        """Initialize the variables dialog.

        Args:
            backend: NiceGUIBackend instance for accessing runtime
        """
        super().__init__()
        self.backend = backend
        # Sort state (matches Tk UI defaults)
        self.sort_mode = 'accessed'  # Current sort mode
        self.sort_reverse = True  # Sort direction

    def _toggle_direction(self):
        """Toggle sort direction and refresh display."""
        self.sort_reverse = not self.sort_reverse
        self.close()
        self.show()

    def _cycle_mode(self):
        """Cycle to next sort mode and refresh display."""
        from src.ui.variable_sorting import cycle_sort_mode, get_default_reverse_for_mode
        self.sort_mode = cycle_sort_mode(self.sort_mode)
        # Use default direction for the new mode
        self.sort_reverse = get_default_reverse_for_mode(self.sort_mode)
        self.close()
        self.show()

    def show(self):
        """Show the variables dialog with current variables."""
        if not self.backend.runtime:
            self.backend._notify('No program running', type='warning')
            return

        # Clear any previous content
        self.clear()

        # Update resource usage
        self.backend._update_resource_usage()

        # Get all variables from runtime
        variables = self.backend.runtime.get_all_variables()

        if not variables:
            self.backend._notify('No variables defined yet', type='info')
            return

        # Sort using common helper
        from src.ui.variable_sorting import sort_variables, get_sort_mode_label, cycle_sort_mode
        variables_sorted = sort_variables(variables, self.sort_mode, self.sort_reverse)

        # Build dialog content
        with self, ui.card().classes('w-[800px]'):
            ui.label('Program Variables').classes('text-xl font-bold')
            ui.label('Double-click a variable to edit its value').classes('text-sm text-gray-500 mb-2')

            # Add search/filter box
            filter_input = ui.input(placeholder='Filter variables...').classes('w-full mb-2')

            # Sort controls - compact row
            arrow = '↓' if self.sort_reverse else '↑'
            mode_label = get_sort_mode_label(self.sort_mode)
            with ui.row().classes('w-full items-center gap-1 mb-2'):
                ui.label('Click arrow to toggle direction, label to change sort:').classes('text-xs text-gray-500')
                ui.button(arrow, on_click=lambda: self._toggle_direction()).props('dense flat size=sm').classes('text-base')
                ui.button(f'({mode_label})', on_click=lambda: self._cycle_mode()).props('dense flat size=sm no-caps')

            # Build column header
            name_header = f'{arrow} Variable ({mode_label})'

            # Create table - columns not sortable (we handle sorting via buttons above)
            columns = [
                {'name': 'name', 'label': name_header, 'field': 'name', 'align': 'left', 'sortable': False},
                {'name': 'type', 'label': 'Type', 'field': 'type', 'align': 'left', 'sortable': False},
                {'name': 'value', 'label': 'Value', 'field': 'value', 'align': 'left', 'sortable': False},
            ]

            rows = []
            for var_info in variables_sorted:
                var_name = var_info['name'] + var_info['type_suffix']
                suffix = var_info['type_suffix']
                if suffix == '$':
                    var_type = 'String'
                elif suffix == '%':
                    var_type = 'Integer'
                elif suffix == '#':
                    var_type = 'Double'
                elif suffix == '!':
                    var_type = 'Single'
                else:
                    var_type = 'Single'  # Default

                if var_info['is_array']:
                    var_type += ' Array'
                    dims = var_info.get('dimensions', [])
                    dims_str = ','.join(str(d) for d in dims)
                    value_display = f'Array({dims_str})'
                else:
                    value = var_info['value']
                    if suffix == '!':
                        value_display = f'{value:.7g}'  # Show 23 not 23.0
                    else:
                        value_display = str(value)

                rows.append({
                    'name': var_name,
                    'type': var_type,
                    'value': value_display,
                    '_var_info': var_info  # Store full info for editing
                })

            table = ui.table(columns=columns, rows=rows, row_key='name').classes('w-full')

            # Connect filter to table
            filter_input.bind_value(table, 'filter')

            # Handle variable editing (only for non-arrays)
            def edit_variable(e):
                # e.args is the event arguments from NiceGUI table
                # For rowClick, the clicked row data is in e.args (which is a dict-like object)
                try:
                    # Get the row data from the event
                    if hasattr(e.args, 'get'):
                        # e.args is a dict-like object
                        var_name = e.args.get('name')
                    elif isinstance(e.args, list) and len(e.args) > 0:
                        # e.args might be a list with row data
                        var_name = e.args[0].get('name') if isinstance(e.args[0], dict) else None
                    else:
                        self.backend._notify('Could not identify clicked variable', type='warning')
                        return

                    if not var_name:
                        return

                    # Find the variable info
                    var_info = None
                    for row in rows:
                        if row['name'] == var_name:
                            var_info = row['_var_info']
                            break

                    if not var_info:
                        return

                    if var_info['is_array']:
                        self.backend._notify('Cannot edit array variables', type='warning')
                        return

                    current_value = var_info['value']
                    suffix = var_info['type_suffix']

                    # Prompt for new value
                    with ui.dialog() as edit_dialog, ui.card():
                        ui.label(f'Edit {var_name}').classes('text-lg font-bold')
                        value_input = ui.input('New value', value=str(current_value)).classes('w-full')

                        def save_edit():
                            try:
                                new_val = value_input.value
                                if suffix == '$':
                                    self.backend.runtime.set_variable(var_name, new_val, line=-1, position=0)
                                elif suffix == '%':
                                    self.backend.runtime.set_variable(var_name, int(new_val), line=-1, position=0)
                                elif suffix in ('#', '!'):
                                    self.backend.runtime.set_variable(var_name, float(new_val), line=-1, position=0)
                                else:
                                    self.backend.runtime.set_variable(var_name, float(new_val), line=-1, position=0)
                                edit_dialog.close()
                                # Refresh the variables dialog
                                self.close()
                                self.show()
                            except Exception as e:
                                self.backend._notify(f'Error setting variable: {e}', type='negative')

                        with ui.row():
                            ui.button('Save', on_click=save_edit).classes('bg-blue-500').props('no-caps')
                            ui.button('Cancel', on_click=edit_dialog.close).props('no-caps')

                    edit_dialog.open()

                except Exception as ex:
                    import sys
                    sys.stderr.write(f"Error in edit_variable: {ex}\n")
                    sys.stderr.write(f"e.args type: {type(e.args)}, value: {e.args}\n")
                    sys.stderr.flush()
                    self.backend._notify(f'Error: {ex}', type='negative')

            table.on('rowDblclick', edit_variable)

            ui.button('Close', on_click=self.close).classes('mt-4').props('no-caps')

        # Open the dialog
        self.open()


class StackDialog(ui.dialog):
    """Reusable dialog for showing execution stack."""

    def __init__(self, backend):
        """Initialize the stack dialog.

        Args:
            backend: NiceGUIBackend instance for accessing runtime
        """
        super().__init__()
        self.backend = backend

    def show(self):
        """Show the stack dialog with current execution stack."""
        if not self.backend.runtime:
            self.backend._notify('No program running', type='warning')
            return

        # Clear any previous content
        self.clear()

        # Get execution stack from runtime
        stack = self.backend.runtime.get_execution_stack()

        if not stack:
            self.backend._notify('Stack is empty', type='info')
            return

        # Build dialog content
        with self, ui.card().classes('w-[700px]'):
            ui.label('Execution Stack').classes('text-xl font-bold')
            ui.label(f'{len(stack)} entries').classes('text-sm text-gray-600 mb-2')

            for i, entry in enumerate(reversed(stack)):
                with ui.row().classes('w-full p-2 bg-gray-100 rounded mb-1'):
                    ui.label(f'#{i+1}:').classes('font-bold w-12')
                    entry_type = entry.get('type', 'UNKNOWN')

                    # Format details based on entry type (matching Tk UI)
                    if entry_type == 'GOSUB':
                        from_line = entry.get('from_line', '?')
                        details = f"GOSUB from line {from_line}"
                    elif entry_type == 'FOR':
                        # Show FOR loop details: var = current TO end STEP step
                        var = entry.get('var', '?')
                        current = entry.get('current', 0)
                        end = entry.get('end', 0)
                        step = entry.get('step', 1)

                        # Format numbers naturally - show integers without decimals
                        current_str = str(int(current)) if isinstance(current, (int, float)) and current == int(current) else str(current)
                        end_str = str(int(end)) if isinstance(end, (int, float)) and end == int(end) else str(end)
                        step_str = str(int(step)) if isinstance(step, (int, float)) and step == int(step) else str(step)

                        # Only show STEP if it's not the default value of 1
                        if step == 1:
                            details = f"FOR {var} = {current_str} TO {end_str}"
                        else:
                            details = f"FOR {var} = {current_str} TO {end_str} STEP {step_str}"
                    elif entry_type == 'WHILE':
                        line = entry.get('line', '?')
                        details = f"WHILE at line {line}"
                    elif 'return_pc' in entry:
                        pc = entry['return_pc']
                        details = f"{entry_type} (return to line {pc.line_num})"
                    elif 'pc' in entry:
                        pc = entry['pc']
                        details = f"{entry_type} (at line {pc.line_num})"
                    else:
                        details = entry_type

                    ui.label(details).classes('font-mono')

            ui.button('Close', on_click=self.close).classes('mt-4').props('no-caps')

        # Open the dialog
        self.open()


class OpenFileDialog(ui.dialog):
    """Reusable dialog for opening files from the server filesystem.

    Based on NiceGUI's local_file_picker example.
    """

    def __init__(self, backend):
        super().__init__()
        self.backend = backend
        self.path = Path.cwd()

        with self, ui.card().classes('w-full max-w-4xl'):
            ui.label('Open BASIC Program').classes('text-h6 mb-4')

            # Current path display
            with ui.row().classes('w-full items-center mb-2'):
                ui.label('Path:').classes('font-bold')
                self.path_label = ui.label(str(self.path)).classes('flex-grow font-mono text-sm')

            # AG Grid file browser in fixed-height scrollable container
            with ui.element('div').classes('w-full').style('height: 400px; overflow-y: auto'):
                self.grid = ui.aggrid({
                    'columnDefs': [
                        {'field': 'name', 'headerName': 'File'},
                        {'field': 'size', 'headerName': 'Size', 'width': 100}
                    ],
                    'rowSelection': {'mode': 'singleRow'},
                    'domLayout': 'autoHeight',
                }, html_columns=[0]).classes('w-full').on('cellDoubleClicked', self._handle_double_click)

            # Action buttons - fixed at bottom
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Cancel', on_click=self.close).props('outline no-caps')
                ui.button('Open', on_click=self._handle_ok, icon='folder_open').props('no-caps')

        # Populate grid with initial data
        self._update_grid()

    def show(self):
        """Show the file picker dialog."""
        self.path = Path.cwd()  # Reset to CWD each time
        self._update_grid()  # Refresh for current directory
        self.open()

    def _build_row_data(self):
        """Build row data for the current directory."""
        try:
            # Get all items in directory
            paths = list(self.path.glob('*'))

            # Filter to only show directories and .bas/.txt files
            paths = [p for p in paths if p.is_dir() or p.suffix.lower() in ['.bas', '.txt']]

            # Sort: directories first (case-insensitive), then files
            paths.sort(key=lambda p: p.name.lower())
            paths.sort(key=lambda p: not p.is_dir())

            # Build row data
            row_data = [
                {
                    'name': f'📁 <strong>{p.name}</strong>' if p.is_dir() else f'📄 {p.name}',
                    'size': '' if p.is_dir() else f'{p.stat().st_size / 1024:.1f} KB',
                    'path': str(p),
                    'is_dir': p.is_dir()
                }
                for p in paths
            ]

            # Add parent directory option if not at root
            if self.path != self.path.parent:
                row_data.insert(0, {
                    'name': '📁 <strong>..</strong>',
                    'size': '',
                    'path': str(self.path.parent),
                    'is_dir': True
                })

            return row_data

        except PermissionError:
            self.backend._notify('Permission denied', type='negative')
            return []
        except Exception as e:
            self.backend._notify(f'Error: {e}', type='negative')
            return []

    def _update_grid(self) -> None:
        """Update the grid with files from current directory."""
        self.path_label.set_text(str(self.path))
        row_data = self._build_row_data()
        self.grid.options['rowData'] = row_data
        self.grid.update()

    def _handle_double_click(self, e) -> None:
        """Handle double-click: navigate directories or open files."""
        data = e.args['data']
        self.path = Path(data['path'])

        if data['is_dir']:
            # Navigate into directory
            self._update_grid()
        else:
            # Open the file
            self._open_file(self.path)

    async def _handle_ok(self):
        """Handle OK button: open selected file."""
        rows = await self.grid.get_selected_rows()
        if rows:
            path = Path(rows[0]['path'])
            if not rows[0]['is_dir']:
                self._open_file(path)
            else:
                self.backend._notify('Please select a file, not a directory', type='warning')

    def _open_file(self, file_path: Path):
        """Open a BASIC file into the editor."""
        try:
            content = file_path.read_text()

            # Normalize line endings and remove CP/M EOF markers
            content = content.replace('\r\n', '\n').replace('\r', '\n').replace('\x1a', '')

            # Remove blank lines
            lines = content.split('\n')
            non_blank_lines = [line for line in lines if line.strip()]
            content = '\n'.join(non_blank_lines)

            # Load into editor
            self.backend.editor.value = content

            # Clear placeholder once content is loaded
            if content:
                self.backend.editor_has_been_used = True
                self.backend.editor.props('placeholder=""')

            # Parse into program
            self.backend._save_editor_to_program()

            # Store filename
            self.backend.current_file = file_path.name

            # Add to recent files
            self.backend._add_recent_file(file_path.name)

            self.backend._set_status(f'Opened: {file_path.name}')
            self.backend._notify(f'Loaded {file_path.name}', type='positive')
            self.close()

        except Exception as ex:
            log_web_error("_open_file", ex)
            self.backend._notify(f'Error loading file: {ex}', type='negative')

    def _show_upload_option(self):
        """Show upload dialog for uploading files from client computer."""
        upload_dialog = ui.dialog()
        with upload_dialog, ui.card():
            ui.label('Upload from your computer').classes('text-h6 mb-4')
            ui.label('Select a .BAS or .TXT file to upload:').classes('mb-2')
            ui.upload(
                on_upload=lambda e: self.backend._handle_file_upload(e, upload_dialog),
                auto_upload=True
            ).classes('w-full').props('accept=".bas,.txt"')
            with ui.row().classes('w-full justify-end mt-4'):
                ui.button('Cancel', on_click=upload_dialog.close).props('no-caps')
        upload_dialog.open()


class SaveAsDialog(ui.dialog):
    """Reusable dialog for Save As."""

    def __init__(self, backend):
        super().__init__()
        self.backend = backend

    def show(self):
        self.clear()
        with self, ui.card():
            ui.label('Save As')
            filename_input = ui.input(
                'Filename:',
                value=self.backend.current_file or 'program.bas',
                placeholder='program.bas'
            ).classes('w-full')

            with ui.row():
                ui.button('Save', on_click=lambda: self.backend._handle_save_as(filename_input.value, self)).props('no-caps')
                ui.button('Cancel', on_click=self.close).props('no-caps')
        self.open()


class MergeFileDialog(ui.dialog):
    """Reusable dialog for merging files."""

    def __init__(self, backend):
        super().__init__()
        self.backend = backend

    def show(self):
        self.clear()
        with self, ui.card().classes('w-[600px]'):
            ui.label('Merge BASIC Program').classes('text-h6 mb-4')
            ui.label('Select a .BAS or .TXT file to merge into current program:').classes('mb-2')
            ui.label('Lines with same numbers will be replaced.').classes('text-sm text-gray-600 mb-2')
            ui.upload(
                on_upload=lambda e: self.backend._handle_merge_upload(e, self),
                auto_upload=True
            ).classes('w-full').props('accept=".bas,.txt"')
            with ui.row().classes('w-full justify-end mt-4'):
                ui.button('Cancel', on_click=self.close).props('no-caps')
        self.open()


class AboutDialog(ui.dialog):
    """Reusable About dialog."""

    def __init__(self, backend):
        super().__init__()
        self.backend = backend

    def show(self):
        self.clear()
        with self, ui.card().classes('w-[400px]'):
            ui.label('About MBASIC').classes('text-xl font-bold mb-4')
            ui.label('MBASIC 5.21 Web IDE').classes('text-lg')
            ui.label(f'{VERSION}').classes('text-md text-gray-600 mb-4')
            ui.label('A modern implementation of Microsoft BASIC').classes('text-sm text-gray-600')
            ui.label('Built with NiceGUI').classes('text-sm text-gray-600 mb-4')
            ui.button('Close', on_click=self.close).classes('mt-4').props('no-caps')
        self.open()


class FindReplaceDialog(ui.dialog):
    """Reusable Find & Replace dialog."""

    def __init__(self, backend):
        super().__init__()
        self.backend = backend

    def show(self):
        """Show the find & replace dialog with proper cursor positioning."""
        # If dialog already open, just bring it to front
        if hasattr(self, '_is_open') and self._is_open:
            self.open()
            return

        self.clear()

        with self, ui.card().classes('w-[500px]'):
            ui.label('Find & Replace').classes('text-lg font-bold')

            find_input = ui.input(label='Find', placeholder='Text to find...').classes('w-full').props('autofocus')
            find_input.value = self.backend.last_find_text  # Restore last search
            replace_input = ui.input(label='Replace with', placeholder='Replacement text...').classes('w-full')
            case_sensitive = ui.checkbox('Case sensitive', value=self.backend.last_case_sensitive)

            result_label = ui.label('').classes('text-sm text-gray-600')

            def do_find():
                """Find first occurrence from beginning."""
                try:
                    find_text = find_input.value
                    if not find_text:
                        result_label.text = 'Enter text to find'
                        return

                    # Reset position for new search
                    self.backend.last_find_position = 0
                    self.backend.last_find_text = find_text
                    self.backend.last_case_sensitive = case_sensitive.value

                    # Clear previous find highlights
                    self.backend.editor.clear_find_highlights()

                    do_find_next()
                except Exception as ex:
                    result_label.text = f'Error: {ex}'

            def do_find_next():
                """Find next occurrence from current position."""
                try:
                    find_text = find_input.value
                    if not find_text:
                        result_label.text = 'Enter text to find'
                        return

                    # Update state
                    self.backend.last_find_text = find_text
                    self.backend.last_case_sensitive = case_sensitive.value

                    editor_text = self.backend.editor.value

                    # Search from current position
                    if case_sensitive.value:
                        index = editor_text.find(find_text, self.backend.last_find_position)
                    else:
                        index = editor_text.lower().find(find_text.lower(), self.backend.last_find_position)

                    if index >= 0:
                        # Calculate line number for display (0-based)
                        line_num = editor_text[:index].count('\n')

                        # Calculate column position within the line
                        line_start = editor_text.rfind('\n', 0, index) + 1
                        start_col = index - line_start
                        end_col = start_col + len(find_text)

                        # Add yellow highlight to the found text
                        self.backend.editor.add_find_highlight(line_num, start_col, end_col)

                        # Scroll to show the found text
                        self.backend.editor.scroll_to_line(line_num)

                        # Update position for next search
                        self.backend.last_find_position = index + 1

                        # Extract BASIC line number if on a numbered line
                        line_end = editor_text.find('\n', index)
                        if line_end == -1:
                            line_end = len(editor_text)
                        line_text = editor_text[line_start:line_end]
                        basic_line_match = re.match(r'^\s*(\d+)', line_text)
                        if basic_line_match:
                            result_label.text = f'Found on line {line_num + 1} (BASIC line {basic_line_match.group(1)})'
                        else:
                            result_label.text = f'Found on line {line_num + 1}'
                    else:
                        # Wrap around or show not found
                        if self.backend.last_find_position > 0:
                            result_label.text = 'No more matches (wrapping to start)'
                            self.backend.last_find_position = 0
                        else:
                            result_label.text = 'Not found'
                except Exception as ex:
                    result_label.text = f'Error: {ex}'
                    log_web_error("do_find_next", ex)

            def do_replace():
                """Replace current selection and find next."""
                try:
                    find_text = find_input.value
                    replace_text = replace_input.value

                    if not find_text:
                        result_label.text = 'Enter text to find'
                        return

                    editor_text = self.backend.editor.value
                    # Find current occurrence (from last position - 1 to account for increment)
                    search_pos = max(0, self.backend.last_find_position - 1)

                    if case_sensitive.value:
                        index = editor_text.find(find_text, search_pos)
                    else:
                        index = editor_text.lower().find(find_text.lower(), search_pos)

                    if index >= 0:
                        # Replace this occurrence
                        new_text = editor_text[:index] + replace_text + editor_text[index + len(find_text):]
                        self.backend.editor.value = new_text
                        result_label.text = 'Replaced 1 occurrence'
                        # Don't increment position - stay at same spot to see replacement
                    else:
                        result_label.text = 'Not found'
                except Exception as ex:
                    result_label.text = f'Error: {ex}'
                    log_web_error("do_replace", ex)

            def do_replace_all():
                """Replace all occurrences."""
                try:
                    find_text = find_input.value
                    replace_text = replace_input.value

                    if not find_text:
                        result_label.text = 'Enter text to find'
                        return

                    editor_text = self.backend.editor.value
                    if case_sensitive.value:
                        count = editor_text.count(find_text)
                        new_text = editor_text.replace(find_text, replace_text)
                    else:
                        pattern = re.compile(re.escape(find_text), re.IGNORECASE)
                        count = len(pattern.findall(editor_text))
                        new_text = pattern.sub(replace_text, editor_text)

                    self.backend.editor.value = new_text
                    result_label.text = f'Replaced {count} occurrence(s)'
                    self.backend._notify(f'Replaced {count} occurrence(s)', type='positive')

                    # Reset search position
                    self.backend.last_find_position = 0
                except Exception as ex:
                    result_label.text = f'Error: {ex}'
                    log_web_error("do_replace_all", ex)

            def on_close():
                """Clear dialog reference when closed."""
                self._is_open = False
                self.close()
                # Note: CodeMirror maintains its own scroll position, no need to restore

            with ui.row().classes('gap-2'):
                ui.button('Find', on_click=do_find).classes('bg-blue-500').tooltip('Find from beginning').props('no-caps')
                ui.button('Find Next', on_click=do_find_next).classes('bg-blue-500').tooltip('Find next occurrence').props('no-caps')
                ui.button('Replace', on_click=do_replace).classes('bg-green-500').props('no-caps')
                ui.button('Replace All', on_click=do_replace_all).classes('bg-orange-500').props('no-caps')
                ui.button('Close', on_click=on_close).props('no-caps')

        self._is_open = True
        self.open()


class SmartInsertDialog(ui.dialog):
    """Reusable Smart Insert dialog."""

    def __init__(self, backend):
        super().__init__()
        self.backend = backend

    def show(self):
        """Show the smart insert dialog."""
        # Get existing lines to calculate default
        lines = self.backend.program.get_lines()
        if not lines:
            self.backend._notify('No program loaded', type='warning')
            return

        # Find first line number for default
        line_numbers = [ln for ln, _ in lines]
        first_line = min(line_numbers) if line_numbers else 10

        self.clear()

        with self, ui.card():
            ui.label('Smart Insert').classes('text-lg font-bold')
            ui.label('Insert a line between two existing line numbers').classes('text-sm text-gray-600')

            after_input = ui.number(label='After Line', value=first_line, min=1, max=65529).classes('w-32')

            def do_insert():
                try:
                    after_line = int(after_input.value)

                    # Get existing lines
                    lines = self.backend.program.get_lines()
                    if not lines:
                        self.backend._notify('No program loaded', type='warning')
                        self.close()
                        return

                    # Find the line after the specified line
                    line_numbers = [ln for ln, _ in lines]

                    # Find next line number
                    next_line = None
                    for ln in sorted(line_numbers):
                        if ln > after_line:
                            next_line = ln
                            break

                    # Calculate midpoint
                    if next_line:
                        new_line_num = (after_line + next_line) // 2
                        if new_line_num == after_line:
                            new_line_num = after_line + 1
                    else:
                        # No line after, just add 10
                        new_line_num = after_line + 10

                    # Add to editor
                    current_text = self.backend.editor.value
                    if current_text:
                        self.backend.editor.value = current_text + f'\n{new_line_num} '
                    else:
                        self.backend.editor.value = f'{new_line_num} '

                    self.close()
                    self.backend._notify(f'Inserted line {new_line_num}', type='positive')
                    self.backend._set_status(f'Inserted line {new_line_num}')
                except Exception as ex:
                    self.backend._notify(f'Error: {ex}', type='negative')

            with ui.row():
                ui.button('Insert', on_click=do_insert).classes('bg-blue-500').props('no-caps')
                ui.button('Cancel', on_click=self.close).props('no-caps')

        self.open()


class DeleteLinesDialog(ui.dialog):
    """Reusable Delete Lines dialog."""

    def __init__(self, backend):
        super().__init__()
        self.backend = backend

    def show(self):
        """Show the delete lines dialog."""
        self.clear()

        with self, ui.card():
            ui.label('Delete Lines').classes('text-lg font-bold')

            start_input = ui.number(label='From Line', value=10, min=1, max=65529).classes('w-32')
            end_input = ui.number(label='To Line', value=100, min=1, max=65529).classes('w-32')

            def do_delete():
                try:
                    start = int(start_input.value)
                    end = int(end_input.value)

                    if start > end:
                        self.backend._notify('Start line must be <= end line', type='warning')
                        return

                    # Get existing lines
                    lines = self.backend.program.get_lines()
                    if not lines:
                        self.backend._notify('No program to delete from', type='warning')
                        self.close()
                        return

                    # Filter out lines in the range
                    kept_lines = []
                    deleted_count = 0
                    for line_num, line_text in lines:
                        if start <= line_num <= end:
                            deleted_count += 1
                        else:
                            kept_lines.append(line_text)

                    # Update editor
                    self.backend.editor.value = '\n'.join(kept_lines)

                    # Reload into program
                    self.backend._save_editor_to_program()

                    self.close()
                    self.backend._notify(f'Deleted {deleted_count} line(s)', type='positive')
                    self.backend._set_status(f'Deleted lines {start}-{end}')
                except Exception as ex:
                    self.backend._notify(f'Error: {ex}', type='negative')

            with ui.row():
                ui.button('Delete', on_click=do_delete).classes('bg-red-500').props('no-caps')
                ui.button('Cancel', on_click=self.close).props('no-caps')

        self.open()


class RenumberDialog(ui.dialog):
    """Reusable Renumber dialog."""

    def __init__(self, backend):
        super().__init__()
        self.backend = backend

    def show(self):
        """Show the renumber dialog."""
        self.clear()

        with self, ui.card():
            ui.label('Renumber Program').classes('text-lg font-bold')

            start_input = ui.number(label='Start Line', value=10, min=1, max=65529).classes('w-32')
            increment_input = ui.number(label='Increment', value=10, min=1, max=100).classes('w-32')

            def do_renumber():
                try:
                    start = int(start_input.value)
                    increment = int(increment_input.value)

                    # Get existing lines
                    lines = self.backend.program.get_lines()
                    if not lines:
                        self.backend._notify('No program to renumber', type='warning')
                        self.close()
                        return

                    # Renumber lines
                    renumbered = []
                    new_line_num = start
                    for old_line_num, old_line_text in lines:
                        # Extract the statement part (after line number)
                        match = re.match(r'^\d+\s*(.*)', old_line_text)
                        if match:
                            statement = match.group(1)
                            renumbered.append(f'{new_line_num} {statement}')
                            new_line_num += increment

                    # Update editor
                    self.backend.editor.value = '\n'.join(renumbered)

                    # Reload into program
                    self.backend._save_editor_to_program()

                    self.close()
                    self.backend._notify(f'Renumbered {len(renumbered)} lines', type='positive')
                    self.backend._set_status('Program renumbered')
                except Exception as ex:
                    self.backend._notify(f'Error: {ex}', type='negative')

            with ui.row():
                ui.button('Renumber', on_click=do_renumber).classes('bg-blue-500').props('no-caps')
                ui.button('Cancel', on_click=self.close).props('no-caps')

        self.open()


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

        # Settings manager
        from src.settings import get_settings_manager
        self.settings_manager = get_settings_manager()

        # Configuration
        self.max_recent_files = 10
        self.auto_save_enabled = True       # Enable auto-save
        self.auto_save_interval = 30        # Auto-save every 30 seconds
        self.output_max_lines = 1000  # Maximum lines to keep in output buffer (reduced for web performance)

        # UI elements (created in build_ui())
        self.editor = None
        self.output = None
        self.status_label = None
        self.current_line_label = None  # Current line indicator
        self.immediate_entry = None  # Immediate mode command input
        self.recent_files_menu = None  # Recent files submenu

        # INPUT row elements (for inline input)
        self.input_row = None
        self.input_label = None
        self.input_field = None
        self.input_submit_btn = None

        # Per-client state (now instance variables instead of session storage)
        from src.runtime import Runtime
        self.runtime = Runtime({}, {})
        self.interpreter = None
        self.running = False
        self.paused = False
        self.output_text = f'MBASIC 5.21 Web IDE - {VERSION}\n'
        self.current_file = None
        self.recent_files = []
        self.exec_io = None
        self.input_future = None
        self.last_save_content = ''
        self.exec_timer = None
        self.auto_save_timer = None

        # Output batching to reduce DOM updates
        self.output_batch = []
        self.output_batch_timer = None
        self.output_update_count = 0

        # Find/Replace state
        self.last_find_text = ''
        self.last_find_position = 0
        self.last_case_sensitive = False

    def build_ui(self):
        """Build the NiceGUI interface.

        Creates the main UI with:
        - Menu bar
        - Toolbar
        - Editor pane
        - Output pane
        - Status bar
        """
        # Use CodeMirror 5 (legacy) - simple script tags, no ES6 modules
        ui.add_head_html('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/codemirror.min.css">')
        ui.add_head_html('<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/codemirror.min.js"></script>')

        # Set page title
        ui.page_title('MBASIC 5.21 - Web IDE')

        # Create reusable dialog instances (NiceGUI best practice: create once, reuse)
        self.variables_dialog = VariablesDialog(self)
        self.stack_dialog = StackDialog(self)
        self.open_file_dialog = OpenFileDialog(self)
        self.save_as_dialog = SaveAsDialog(self)
        self.merge_file_dialog = MergeFileDialog(self)
        self.about_dialog = AboutDialog(self)
        self.find_replace_dialog = FindReplaceDialog(self)
        self.smart_insert_dialog = SmartInsertDialog(self)
        self.delete_lines_dialog = DeleteLinesDialog(self)
        self.renumber_dialog = RenumberDialog(self)

        # Menu bar
        self._create_menu()

        # Toolbar
        with ui.row().classes('w-full bg-gray-100 p-2 gap-2'):
            ui.button('Run', on_click=self._menu_run, icon='play_arrow', color='green').mark('btn_run')
            ui.button('Stop', on_click=self._menu_stop, icon='stop', color='red').mark('btn_stop')
            ui.button('Step', on_click=self._menu_step_line, icon='skip_next').mark('btn_step_line')
            ui.button('Stmt', on_click=self._menu_step_stmt, icon='redo').mark('btn_step_stmt')
            ui.button('Cont', on_click=self._menu_continue, icon='play_circle').mark('btn_continue')
            ui.separator().props('vertical')
            ui.button(icon='check_circle', on_click=self._check_syntax).mark('btn_check_syntax').props('flat').tooltip('Check Syntax')

        # Main content area
        with ui.element('div').style('width: 100%; display: flex; flex-direction: column;'):
            # Editor - using CodeMirror 5 (legacy, no ES6 modules)
            self.editor = CodeMirror5Editor(
                value='',
                on_change=self._on_editor_change
            ).style('width: 100%; height: 300px; border: 1px solid #ccc;').mark('editor')

            # Add auto-numbering handlers
            # Track last edited line for auto-numbering
            self.last_edited_line_index = None
            self.last_edited_line_text = None
            self.auto_numbering_in_progress = False  # Prevent recursive calls
            self.editor_has_been_used = False  # Track if user has typed anything

            # Event handlers now handled through CodeMirror's on_change callback
            # The _on_editor_change method (defined below) handles:
            # - Removing blank lines
            # - Auto-numbering
            # - Placeholder clearing

            # Note: click and blur handlers can still work with CodeMirror
            self.editor.on('click', self._on_editor_click, throttle=0.05)
            self.editor.on('blur', self._on_editor_blur)

            # Current line indicator
            self.current_line_label = ui.label('').classes('text-sm font-mono bg-yellow-100 p-1')
            self.current_line_label.visible = False

            # Syntax error indicator
            self.syntax_error_label = ui.label('').classes('text-sm font-mono bg-red-100 text-red-700 p-1')
            self.syntax_error_label.visible = False

            # Output
            self.output = ui.textarea(
                value=f'MBASIC 5.21 Web IDE - {VERSION}\n',
                placeholder='Output'
            ).style('width: 100%;').props('readonly outlined dense rows=10 spellcheck=false').mark('output')

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
                ).style('width: 100%;').props('outlined dense rows=3 spellcheck=false').mark('immediate_entry')
                self.immediate_entry.on('keydown.enter', self._on_immediate_enter)
                ui.button('Execute', on_click=self._execute_immediate, icon='play_arrow', color='green').mark('btn_immediate')

            # Status
            with ui.row().classes('w-full bg-gray-200 q-pa-xs').style('justify-content: space-between;'):
                self.status_label = ui.label('Ready').mark('status')
                with ui.row().classes('gap-4'):
                    self.resource_usage_label = ui.label('').classes('text-gray-600')
                    ui.label(f'v{VERSION}').classes('text-gray-600')

        # Start auto-save timer
        self._start_auto_save()

        # Set initial focus to program editor
        self.editor.run_method('focus')

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
                    ui.menu_item('Merge...', on_click=self._menu_merge)
                    ui.separator()
                    # Recent Files submenu
                    with ui.menu_item('Recent Files'):
                        with ui.menu() as self.recent_files_menu:
                            self._update_recent_files_menu()
                    ui.separator()
                    ui.menu_item('Exit', on_click=self._menu_exit)

            # Edit menu
            with ui.button('Edit', icon='menu').props('flat color=white'):
                with ui.menu():
                    ui.menu_item('Find/Replace...', on_click=self._menu_find_replace)
                    ui.separator()
                    ui.menu_item('Delete Lines...', on_click=self._menu_delete_lines)
                    ui.menu_item('Renumber...', on_click=self._menu_renumber)
                    ui.menu_item('Sort Lines', on_click=self._menu_sort_lines)
                    ui.menu_item('Smart Insert...', on_click=self._menu_smart_insert)
                    ui.separator()
                    ui.menu_item('Settings...', on_click=self._menu_settings)

            # Run menu
            with ui.button('Run', icon='menu').props('flat color=white'):
                with ui.menu():
                    ui.menu_item('Run Program', on_click=self._menu_run)
                    ui.menu_item('Stop', on_click=self._menu_stop)
                    ui.separator()
                    ui.menu_item('List Program', on_click=self._menu_list)
                    ui.menu_item('Clear Output', on_click=self._clear_output)

            # Debug menu
            with ui.button('Debug', icon='menu').props('flat color=white'):
                with ui.menu() as debug_menu:
                    async def _toggle_bp_clicked():
                        await self._toggle_breakpoint()
                        debug_menu.close()
                    def _clear_all_bp_clicked():
                        self._clear_all_breakpoints()
                        debug_menu.close()

                    ui.menu_item('Step Line', on_click=self._menu_step_line)
                    ui.menu_item('Step Statement', on_click=self._menu_step_stmt)
                    ui.menu_item('Continue', on_click=self._menu_continue)
                    ui.separator()
                    ui.menu_item('Toggle Breakpoint', on_click=_toggle_bp_clicked)
                    ui.menu_item('Clear All Breakpoints', on_click=_clear_all_bp_clicked)
                    ui.separator()
                    ui.menu_item('Show Variables', on_click=self._show_variables_window)
                    ui.menu_item('Show Stack', on_click=self._show_stack_window)

            # Help menu
            with ui.button('Help', icon='menu').props('flat color=white'):
                with ui.menu() as help_menu:
                    def _help_clicked():
                        self._menu_help()
                        help_menu.close()
                    def _library_clicked():
                        self._menu_games_library()
                        help_menu.close()
                    def _about_clicked():
                        self._menu_about()
                        help_menu.close()

                    ui.menu_item('Help Topics', on_click=_help_clicked)
                    ui.menu_item('Games Library', on_click=_library_clicked)
                    ui.separator()
                    ui.menu_item('About', on_click=_about_clicked)

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

    async def _toggle_breakpoint(self):
        """Toggle statement-level breakpoint at current cursor position."""
        try:
            # Get cursor position from CodeMirror editor via run_method
            cursor_info = await self.editor.run_method('getCursorPosition')
            if not cursor_info:
                # Could not get cursor position, show dialog
                with ui.dialog() as dialog, ui.card():
                    ui.label('Toggle Breakpoint').classes('text-h6')
                    ui.label('Could not determine cursor position.').classes('text-caption mb-2')
                    line_input = ui.input('Line number:', placeholder='10').classes('w-full')
                    with ui.row():
                        ui.button('Toggle', on_click=lambda: self._do_toggle_breakpoint(line_input.value, dialog)).props('no-caps')
                        ui.button('Cancel', on_click=dialog.close).props('no-caps')
                dialog.open()
                return

            # Get full editor text and extract the line at cursor
            editor_text = await self.editor.run_method('getValue')
            if not editor_text:
                # Empty editor, show dialog
                with ui.dialog() as dialog, ui.card():
                    ui.label('Toggle Breakpoint').classes('text-h6')
                    ui.label('Editor is empty.').classes('text-caption mb-2')
                    line_input = ui.input('Line number:', placeholder='10').classes('w-full')
                    with ui.row():
                        ui.button('Toggle', on_click=lambda: self._do_toggle_breakpoint(line_input.value, dialog)).props('no-caps')
                        ui.button('Cancel', on_click=dialog.close).props('no-caps')
                dialog.open()
                return

            lines = editor_text.split('\n')
            cursor_line_idx = cursor_info['line']
            cursor_in_line = cursor_info['column']

            if cursor_line_idx >= len(lines):
                # Cursor beyond end of document
                with ui.dialog() as dialog, ui.card():
                    ui.label('Toggle Breakpoint').classes('text-h6')
                    ui.label('Cursor is beyond end of document.').classes('text-caption mb-2')
                    line_input = ui.input('Line number:', placeholder='10').classes('w-full')
                    with ui.row():
                        ui.button('Toggle', on_click=lambda: self._do_toggle_breakpoint(line_input.value, dialog)).props('no-caps')
                        ui.button('Cancel', on_click=dialog.close).props('no-caps')
                dialog.open()
                return

            line_text = lines[cursor_line_idx]

            # Extract BASIC line number from text
            match = re.match(r'^\s*(\d+)', line_text)
            if not match:
                # Cursor not on a BASIC line number, show dialog
                with ui.dialog() as dialog, ui.card():
                    ui.label('Toggle Breakpoint').classes('text-h6')
                    ui.label('Cursor is not on a line with a line number.').classes('text-caption mb-2')
                    line_input = ui.input('Line number:', placeholder='10').classes('w-full')
                    with ui.row():
                        ui.button('Toggle', on_click=lambda: self._do_toggle_breakpoint(line_input.value, dialog)).props('no-caps')
                        ui.button('Cancel', on_click=dialog.close).props('no-caps')
                dialog.open()
                return

            line_num = int(match.group(1))

            # Query the statement table to find which statement the cursor is in
            stmt_offset = 0
            if self.runtime and self.runtime.statement_table:
                # Get all statements for this line from the statement table
                for pc, stmt_node in self.runtime.statement_table.statements.items():
                    if pc.line_num == line_num:
                        # Check if cursor is within this statement's character range
                        if stmt_node.char_start <= cursor_in_line <= stmt_node.char_end:
                            stmt_offset = pc.stmt_offset
                            break

            # Create PC object for this statement
            pc = PC(line_num, stmt_offset)

            # Toggle the breakpoint
            if pc in self.runtime.breakpoints:
                self.runtime.breakpoints.discard(pc)
                if stmt_offset > 0:
                    self._notify(f'❌ Breakpoint removed: line {line_num} statement {stmt_offset + 1}', type='info')
                    self._set_status(f'Removed breakpoint at {line_num}.{stmt_offset}')
                else:
                    self._notify(f'❌ Breakpoint removed: line {line_num}', type='info')
                    self._set_status(f'Removed breakpoint at {line_num}')
            else:
                self.runtime.breakpoints.add(pc)
                if stmt_offset > 0:
                    self._notify(f'🔴 Breakpoint set: line {line_num} statement {stmt_offset + 1}', type='positive')
                    self._set_status(f'Breakpoint at {line_num}.{stmt_offset}')
                else:
                    self._notify(f'🔴 Breakpoint set: line {line_num}', type='positive')
                    self._set_status(f'Breakpoint at {line_num}')

            # Update editor to show breakpoint markers
            await self._update_breakpoint_display()

        except Exception as e:
            log_web_error("_toggle_breakpoint", e)
            self._notify(f'Error: {e}', type='negative')

    async def _update_breakpoint_display(self):
        """Update the editor to show breakpoint markers using CodeMirror."""
        try:
            # Clear all existing breakpoint markers
            self.editor.clear_breakpoints()

            # Add markers for all current breakpoints
            for item in self.runtime.breakpoints:
                # Handle both PC objects and plain integers
                if isinstance(item, PC):
                    # Get character positions from statement table for statement-level highlighting
                    stmt = self.runtime.statement_table.get(item)
                    if stmt and hasattr(stmt, 'char_start') and hasattr(stmt, 'char_end'):
                        # Use the same logic as current_statement_char_end for consistency
                        char_start = stmt.char_start
                        # Check for next statement to calculate proper char_end
                        next_pc = PC(item.line_num, item.stmt_offset + 1)
                        next_stmt = self.runtime.statement_table.get(next_pc)
                        if next_stmt and hasattr(next_stmt, 'char_start') and next_stmt.char_start > 0:
                            char_end = max(stmt.char_end, next_stmt.char_start - 1)
                        elif item.line_num in self.runtime.line_text_map:
                            line_text = self.runtime.line_text_map[item.line_num]
                            char_end = len(line_text)
                        else:
                            char_end = stmt.char_end
                        self.editor.add_breakpoint(item.line_num, char_start, char_end)
                    else:
                        # No statement info - highlight whole line
                        self.editor.add_breakpoint(item.line_num)
                else:
                    # Plain integer - highlight whole line
                    self.editor.add_breakpoint(item)

        except Exception as e:
            log_web_error("_update_breakpoint_display", e)

    async def _do_toggle_breakpoint(self, line_num_str, dialog):
        """Actually toggle the breakpoint."""
        try:
            line_num = int(line_num_str)

            if line_num in self.runtime.breakpoints:
                self.runtime.breakpoints.remove(line_num)
                self._notify(f'❌ Breakpoint removed: line {line_num}', type='info')
                self._set_status(f'Removed breakpoint at {line_num}')
            else:
                self.runtime.breakpoints.add(line_num)
                self._notify(f'🔴 Breakpoint set: line {line_num}', type='positive')
                self._set_status(f'Breakpoint at {line_num}')

            await self._update_breakpoint_display()
            dialog.close()

        except ValueError:
            self._notify('Please enter a valid line number', type='warning')
        except Exception as e:
            log_web_error("_do_toggle_breakpoint", e)
            self._notify(f'Error: {e}', type='negative')

    def _clear_all_breakpoints(self):
        """Clear all breakpoints."""
        try:
            count = len(self.runtime.breakpoints)
            self.runtime.breakpoints.clear()

            # Clear CodeMirror breakpoint markers
            self.editor.clear_breakpoints()

            self._notify(f'Cleared {count} breakpoint(s)', type='info')
            self._set_status('All breakpoints cleared')
        except Exception as e:
            log_web_error("_clear_all_breakpoints", e)
            self._notify(f'Error: {e}', type='negative')

    # =========================================================================
    # Menu Handlers
    # =========================================================================

    async def _menu_new(self):
        """File > New - Clear program."""
        try:
            self.program.clear()
            self.editor.value = ''
            self.current_file = None
            self._set_status('New program')
        except Exception as e:
            log_web_error("_menu_new", e)
            self._notify(f'Error: {e}', type='negative')

    async def _menu_open(self):
        """File > Open - Load program from file."""
        self.open_file_dialog.show()

    async def _handle_file_upload(self, e, dialog):
        """Handle file upload from Open dialog."""
        try:
            # Read uploaded file content
            content_bytes = await e.file.read()
            content = content_bytes.decode('utf-8')

            # Remove blank lines
            lines = content.split('\n')
            non_blank_lines = [line for line in lines if line.strip()]
            content = '\n'.join(non_blank_lines)

            # Load into editor
            self.editor.value = content

            # Clear placeholder once content is loaded
            if content:
                self.editor_has_been_used = True
                self.editor.props('placeholder=""')

            # Parse into program
            self._save_editor_to_program()

            # Store filename
            self.current_file = e.file.filename

            # Add to recent files
            self._add_recent_file(e.file.filename)

            self._set_status(f'Opened: {e.file.filename}')
            self._notify(f'Loaded {e.file.filename}', type='positive')
            dialog.close()

        except Exception as ex:
            log_web_error("_handle_file_upload", ex)
            self._notify(f'Error loading file: {ex}', type='negative')

    async def _menu_save(self):
        """File > Save - Save current program."""
        try:
            # If no filename, trigger Save As instead
            if not self.current_file:
                await self._menu_save_as()
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

    async def _menu_save_as(self):
        """File > Save As - Save with new filename."""
        self.save_as_dialog.show()

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

    def _handle_merge_upload(self, e, dialog):
        """Handle file upload from Merge dialog."""
        try:
            # Read uploaded file content
            content = e.content.read().decode('utf-8')

            # Parse the file to extract lines
            merge_lines = content.strip().split('\n')

            # Get current editor content
            current_text = self.editor.value
            current_lines = current_text.strip().split('\n') if current_text else []

            # Combine lines
            all_lines = current_lines + merge_lines

            # Parse line numbers and sort
            numbered_lines = []
            for line in all_lines:
                match = re.match(r'^(\d+)\s+(.*)', line.strip())
                if match:
                    line_num = int(match.group(1))
                    statement = match.group(2)
                    numbered_lines.append((line_num, statement))

            # Sort by line number
            numbered_lines.sort(key=lambda x: x[0])

            # Rebuild editor text
            merged_text = '\n'.join(f'{num} {stmt}' for num, stmt in numbered_lines)
            self.editor.value = merged_text

            # Reload into program
            self._save_editor_to_program()

            dialog.close()
            self._notify(f'Merged {len(merge_lines)} lines from {e.name}', type='positive')
            self._set_status(f'Merged {len(merge_lines)} lines')

        except Exception as ex:
            log_web_error("_handle_merge_upload", ex)
            self._notify(f'Error merging file: {ex}', type='negative')

    async def _menu_exit(self):
        """File > Exit - Quit application."""
        app.shutdown()

    async def _menu_merge(self):
        """File > Merge - Merge another BASIC file into current program."""
        self.merge_file_dialog.show()

    async def _menu_run(self):
        """Run > Run Program - Execute program.

        RUN is always valid - it's just CLEAR + GOTO first line.
        RUN on empty program is fine (just clears variables).
        RUN at a breakpoint restarts from the beginning.
        """
        try:
            # Stop any existing execution timer first
            if self.exec_timer:
                self.exec_timer.cancel()
                self.exec_timer = None

            # Save editor content to program first
            if not self._save_editor_to_program():
                return  # Parse errors, don't run

            # RUN on empty program is allowed (just clears variables, nothing to execute)
            # Don't show error - this matches real MBASIC behavior

            # Don't clear output - continuous scrolling like ASR33 teletype
            self._set_status('Running...')

            # Get program AST
            program_ast = self.program.get_program_ast()

            # Create or reset runtime - RUN = CLEAR + GOTO first line
            # This preserves breakpoints but clears variables
            from src.resource_limits import create_local_limits
            if self.runtime is None:
                # First run - create new Runtime
                self.runtime = Runtime(self.program.line_asts, self.program.lines)
                self.runtime.setup()
            else:
                # Subsequent run - reset Runtime (RUN = CLEAR + restart)
                self.runtime.reset_for_run(self.program.line_asts, self.program.lines)

            # Create IO handler that outputs to our output pane
            self.exec_io = SimpleWebIOHandler(self._append_output, self._get_input)

            # Create sandboxed file I/O for web UI (uses browser localStorage)
            from src.file_io import SandboxedFileIO
            sandboxed_file_io = SandboxedFileIO(self)

            # Create interpreter with sandboxed file I/O
            self.interpreter = Interpreter(self.runtime, self.exec_io, limits=create_local_limits(), file_io=sandboxed_file_io)

            # Wire up interpreter to use this UI's methods
            self.interpreter.interactive_mode = self

            # Start interpreter
            state = self.interpreter.start()
            if state.status == 'error':
                error_msg = state.error_info.error_message if state.error_info else 'Unknown'
                self._append_output(f"\n--- Setup error: {error_msg} ---\n")
                self._set_status('Error')
                self.running = False  # For display only (spinner)
                return

            # Check if RUN was called with a line number (e.g., RUN 120)
            if hasattr(self, '_run_start_line') and self._run_start_line:
                # Set PC to start at the specified line
                self.runtime.npc = PC.from_line(self._run_start_line)
                # Clear the temporary attribute
                self._run_start_line = None

            # If empty program, just show Ready (variables cleared, nothing to execute)
            if not self.program.lines:
                self._set_status('Ready')
                self.running = False  # For display only (spinner)
                return

            # Mark as running (for display only - spinner, status indicator)
            # This should NOT control program logic - RUN is always valid
            self.running = True

            # Start async execution - store timer handle so we can cancel it
            self.exec_timer = ui.timer(0.01, self._execute_tick, once=False)

        except Exception as e:
            log_web_error("_menu_run", e)
            self._append_output(f"\n--- Error: {e} ---\n")
            self._set_status(f'Error: {e}')
            self.running = False

    def _execute_tick(self):
        """Execute one tick of the interpreter.

        Note on Ctrl+C handling:
        This method is called every 10ms by ui.timer(). During long-running programs,
        this can make Ctrl+C unresponsive because Python signal handlers only run
        between bytecode instructions, and the event loop stays busy.

        The KeyboardInterrupt handling is done at the top level in mbasic.py,
        which wraps start_web_ui() in a try/except.
        """
        # Don't check self.running - it seems to not persist correctly in NiceGUI callbacks
        # Just check if we have an interpreter
        if not self.interpreter:
            return

        try:
            status = self.interpreter.state.status if self.interpreter else 'no interpreter'

            # If waiting for input, don't tick - wait for input to be provided
            if status == 'waiting_for_input':
                return

            # Execute one tick (up to 1000 statements)
            state = self.interpreter.tick(mode='run', max_statements=1000)

            # Handle state
            if state.status == 'done':
                self._append_output("\n--- Program finished ---\n")
                self._set_status("Ready")
                self.running = False
                # Hide current line highlight
                if self.current_line_label:
                    self.current_line_label.visible = False
                if self.exec_timer:
                    self.exec_timer.cancel()
            elif state.status == 'waiting_for_input':
                # Pause execution until input is provided
                self._set_status("Waiting for input...")
                # Don't cancel timer - keep ticking to check when input is provided
            elif state.status == 'error':
                error_msg = state.error_info.error_message if state.error_info else "Unknown error"
                self._append_output(f"\n--- Error: {error_msg} ---\n")
                self._set_status("Error")
                self.running = False
                # Hide current line highlight
                if self.current_line_label:
                    self.current_line_label.visible = False
                if self.exec_timer:
                    self.exec_timer.cancel()
            elif state.status == 'paused' or state.status == 'at_breakpoint':
                self._set_status(f"Paused at line {state.current_line}")
                self.running = True  # Keep running=True so Continue works
                self.paused = True
                # Show current line highlight
                if self.current_line_label:
                    self.current_line_label.set_text(f'>>> Executing line {state.current_line}')
                    self.current_line_label.visible = True
                # Highlight current statement in CodeMirror
                char_start = state.current_statement_char_start if state.current_statement_char_start > 0 else None
                char_end = state.current_statement_char_end if state.current_statement_char_end > 0 else None
                self.editor.set_current_statement(state.current_line, char_start, char_end)
                if self.exec_timer:
                    self.exec_timer.cancel()

        except Exception as e:
            log_web_error("_execute_tick", e)
            self._append_output(f"\n--- Tick error: {e} ---\n")
            self._set_status(f"Error: {e}")
            self.running = False

    async def _menu_stop(self):
        """Run > Stop - Stop execution."""
        # Cancel the execution timer first
        if self.exec_timer:
            self.exec_timer.cancel()
            self.exec_timer = None

        # Stop the interpreter
        if self.interpreter:
            self.interpreter.state.status = 'paused'

        # Update UI state
        self.running = False
        self.paused = False

        # Hide input row if visible
        self._hide_input_row()

        # Update UI
        self._set_status('Stopped')
        self._append_output("\n--- Program stopped ---\n")

        # Hide current line highlight
        if self.current_line_label:
            self.current_line_label.visible = False

    async def _menu_step_line(self):
        """Run > Step Line - Execute all statements on current line and pause."""
        try:
            if not self.running and not self.paused:
                # Not running - start program and step one line
                if not self._save_editor_to_program():
                    return  # Parse errors

                if not self.program.lines:
                    self._notify('No program loaded', type='warning')
                    return

                # Start execution
                self._clear_output()

                # Create or reset runtime - preserves breakpoints
                from src.resource_limits import create_local_limits
                if self.runtime is None:
                    self.runtime = Runtime(self.program.line_asts, self.program.lines)
                    self.runtime.setup()
                else:
                    self.runtime.reset_for_run(self.program.line_asts, self.program.lines)

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

                # Execute one line
                state = self.interpreter.tick(mode='step_line', max_statements=100)
                self._handle_step_result(state, 'line')

            else:
                # Already running - step one line
                if self.interpreter:
                    state = self.interpreter.tick(mode='step_line', max_statements=100)
                    self._handle_step_result(state, 'line')

        except Exception as e:
            log_web_error("_menu_step_line", e)
            self._notify(f'Error: {e}', type='negative')

    async def _menu_step_stmt(self):
        """Run > Step Statement - Execute one statement and pause."""
        try:
            if not self.running and not self.paused:
                # Not running - start program and step one statement
                if not self._save_editor_to_program():
                    return  # Parse errors

                if not self.program.lines:
                    self._notify('No program loaded', type='warning')
                    return

                # Start execution
                self._clear_output()

                # Create or reset runtime - preserves breakpoints
                from src.resource_limits import create_local_limits
                if self.runtime is None:
                    self.runtime = Runtime(self.program.line_asts, self.program.lines)
                    self.runtime.setup()
                else:
                    self.runtime.reset_for_run(self.program.line_asts, self.program.lines)

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

                # Execute one statement
                state = self.interpreter.tick(mode='step_statement', max_statements=1)
                self._handle_step_result(state, 'statement')

            else:
                # Already running - step one statement
                if self.interpreter:
                    state = self.interpreter.tick(mode='step_statement', max_statements=1)
                    self._handle_step_result(state, 'statement')

        except Exception as e:
            log_web_error("_menu_step_stmt", e)
            self._notify(f'Error: {e}', type='negative')

    def _handle_step_result(self, state, step_type):
        """Handle result of a step operation."""
        if state.status == 'done':
            self._append_output("\n--- Program finished ---\n")
            self._set_status("Ready")
            self.running = False
            self.paused = False
            # Hide current line highlight
            if self.current_line_label:
                self.current_line_label.visible = False
            # Clear CodeMirror current statement highlight
            self.editor.set_current_statement(None)
        elif state.status == 'error':
            error_msg = state.error_info.error_message if state.error_info else "Unknown error"
            self._append_output(f"\n--- Error: {error_msg} ---\n")
            self._set_status("Error")
            self.running = False
            self.paused = False
            # Hide current line highlight
            if self.current_line_label:
                self.current_line_label.visible = False
            # Clear CodeMirror current statement highlight
            self.editor.set_current_statement(None)
        elif state.status in ('paused', 'at_breakpoint'):
            self._set_status(f"Paused at line {state.current_line}")
            self.running = True
            self.paused = True
            # Show current line highlight
            if self.current_line_label:
                self.current_line_label.set_text(f'>>> Executing line {state.current_line}')
                self.current_line_label.visible = True
            # Highlight current statement in CodeMirror (with character positions for statement-level highlighting)
            char_start = state.current_statement_char_start if state.current_statement_char_start > 0 else None
            char_end = state.current_statement_char_end if state.current_statement_char_end > 0 else None
            self.editor.set_current_statement(state.current_line, char_start, char_end)
        elif state.status == 'running':
            # Still running after step - mark as paused to prevent automatic continuation
            self._set_status(f"Paused at line {state.current_line}")
            self.running = True
            self.paused = True
            # Show current line highlight
            if self.current_line_label:
                self.current_line_label.set_text(f'>>> Executing line {state.current_line}')
                self.current_line_label.visible = True
            # Highlight current statement in CodeMirror (with character positions for statement-level highlighting)
            char_start = state.current_statement_char_start if state.current_statement_char_start > 0 else None
            char_end = state.current_statement_char_end if state.current_statement_char_end > 0 else None
            self.editor.set_current_statement(state.current_line, char_start, char_end)

    async def _menu_continue(self):
        """Run > Continue - Continue from breakpoint/pause."""
        try:
            if self.running and self.paused:
                self.paused = False
                self._set_status('Continuing...')
                # Start timer to continue execution in run mode
                if not self.exec_timer:
                    self.exec_timer = ui.timer(0.01, self._execute_tick, once=False)
            else:
                self._notify('Not paused', type='warning')

        except Exception as e:
            log_web_error("_menu_continue", e)
            self._notify(f'Error: {e}', type='negative')

    async def _menu_list(self):
        """Run > List Program - List to output."""
        lines = self.program.get_lines()
        for line_num, line_text in lines:
            self._append_output(line_text + '\n')
        self._set_status('Program listed')

    async def _menu_sort_lines(self):
        """Sort program lines by line number."""
        try:
            # Get all lines
            lines = self.program.get_lines()
            if not lines:
                self._notify('No program to sort', type='warning')
                return

            # Lines are already stored sorted by line number in the program
            # Just rebuild the editor text from sorted lines
            sorted_text = '\n'.join(line_text for line_num, line_text in lines)
            self.editor.value = sorted_text

            self._notify('Program lines sorted', type='positive')
            self._set_status('Lines sorted by line number')
        except Exception as e:
            log_web_error("_menu_sort_lines", e)
            self._notify(f'Error: {e}', type='negative')

    async def _menu_find_replace(self):
        """Find and replace text in the program with proper cursor positioning."""
        self.find_replace_dialog.show()

    async def _menu_smart_insert(self):
        """Insert a line number between two existing lines."""
        self.smart_insert_dialog.show()

    async def _menu_delete_lines(self):
        """Delete a range of line numbers from the program."""
        self.delete_lines_dialog.show()

    async def _menu_renumber(self):
        """Renumber program lines with new start and increment."""
        self.renumber_dialog.show()

    def _show_variables_window(self):
        """Show Variables window using reusable dialog."""
        self.variables_dialog.show()

    def _show_stack_window(self):
        """Show Execution Stack window using reusable dialog."""
        self.stack_dialog.show()

    def _menu_help(self):
        """Help > Help Topics - Opens in web browser."""
        try:
            from ..web_help_launcher import open_help_in_browser
            url = "http://localhost/mbasic_docs/help/ui/web/"

            success = open_help_in_browser(topic="help/ui/web/", ui_type="web")

            if success:
                self._notify('Opening help in browser...', type='positive', log_to_output=False)
            else:
                # Show URL in both notification and output
                msg = f'Could not open browser automatically.\n\nPlease open this URL manually:\n{url}'
                self._notify(msg, type='warning')
                self._append_output(f'\n--- Help URL ---\n{url}\n')
        except Exception as e:
            log_web_error("_menu_help", e)
            self._notify(f'Error opening help: {e}', type='negative')

    def _menu_games_library(self):
        """Help > Games Library - Opens program library in browser."""
        try:
            from ..web_help_launcher import open_help_in_browser
            url = "http://localhost/mbasic_docs/library/"

            success = open_help_in_browser(topic="library/", ui_type="web")

            if success:
                self._notify('Opening program library in browser...', type='positive', log_to_output=False)
            else:
                # Show URL in both notification and output
                msg = f'Could not open browser automatically.\n\nPlease open this URL manually:\n{url}'
                self._notify(msg, type='warning')
                self._append_output(f'\n--- Library URL ---\n{url}\n')
        except Exception as e:
            log_web_error("_menu_games_library", e)
            self._notify(f'Error opening library: {e}', type='negative')

    async def _menu_settings(self):
        """Edit > Settings - Open settings dialog."""
        from .web_settings_dialog import WebSettingsDialog

        def on_save():
            """Callback when settings saved - reload settings."""
            self._notify('Settings saved - will take effect on next auto-number', type='positive')

        dialog = WebSettingsDialog(self.settings_manager, on_save_callback=on_save)
        dialog.show()

    def _menu_about(self):
        """Help > About."""
        self.about_dialog.show()

    # ========================================================================
    # BASIC Statement Command Methods (called by interpreter)
    # TODO: Move these to interpreter - see MOVE_STATEMENTS_TO_INTERPRETER_TODO.md
    # ========================================================================

    def cmd_list(self, args: str = "") -> None:
        """Execute LIST command - list program lines to output."""
        lines = self.program.get_lines()
        for line_num, line_text in lines:
            self._append_output(line_text + "\n")

    def cmd_new(self) -> None:
        """Execute NEW command - clear program and variables."""
        # Clear the program
        self.program.clear()

        # Clear the editor
        self.editor.value = ''

        # Clear runtime if it exists
        if self.runtime:
            self.runtime.clear_variables()

        # Reset current file
        self.current_file = None

        # Stop any running execution
        if self.exec_timer:
            self.exec_timer.cancel()
            self.exec_timer = None

        self.running = False
        self.paused = False

        self._set_status('Ready')
        self._append_output("New\n")

    # ========================================================================
    # End BASIC Statement Command Methods
    # ========================================================================

    def _start_auto_save(self):
        """Start auto-save timer."""
        if self.auto_save_enabled and not self.auto_save_timer:
            # Create async timer that calls auto-save periodically
            self.auto_save_timer = ui.timer(
                self.auto_save_interval,
                self._auto_save_tick,
                active=True
            )

    def _stop_auto_save(self):
        """Stop auto-save timer."""
        if self.auto_save_timer:
            self.auto_save_timer.cancel()
            self.auto_save_timer = None

    def _auto_save_tick(self):
        """Periodic auto-save check."""
        try:
            if not self.auto_save_enabled:
                return

            # Check if editor content has changed
            current_content = self.editor.value if self.editor else ''

            if current_content and current_content != self.last_save_content:
                # Content has changed, save to browser localStorage
                self._auto_save_to_storage(current_content)
                self.last_save_content = current_content
                # Update status briefly
                if self.status_label:
                    old_status = self.status_label.text
                    self.status_label.text = 'Auto-saved'
                    # Reset status after 2 seconds
                    ui.timer(2.0, lambda: setattr(self.status_label, 'text', old_status), once=True)
        except Exception as e:
            # Log but don't crash on auto-save errors
            log_web_error("_auto_save_tick", e)

    def _auto_save_to_storage(self, content):
        """Save content to browser localStorage."""
        try:
            # In NiceGUI, we can use JavaScript to save to localStorage
            # This creates a backup that persists across page refreshes
            ui.run_javascript(f'''
                localStorage.setItem('mbasic_autosave', {repr(content)});
                localStorage.setItem('mbasic_autosave_time', new Date().toISOString());
            ''')
        except Exception as e:
            log_web_error("_auto_save_to_storage", e)

    def _load_auto_save(self):
        """Load auto-saved content from localStorage if available."""
        try:
            # This would typically be called on startup
            # For now, it's a placeholder for future enhancement
            pass
        except Exception as e:
            log_web_error("_load_auto_save", e)

    def _check_syntax(self):
        """Check syntax of current program."""
        try:
            # Get editor content
            text = self.editor.value
            if not text or not text.strip():
                self.syntax_error_label.visible = False
                self._notify('No program to check', type='info')
                return

            # Parse each line and collect errors
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

                # Try to parse the line
                try:
                    from src.parser import Parser
                    from src.lexer import Lexer
                    lexer = Lexer(line_text)
                    tokens = lexer.tokenize()
                    parser = Parser(tokens)
                    parser.parse_line()
                except Exception as e:
                    errors.append(f'Line {line_num}: {str(e)}')

            # Display results
            if errors:
                error_msg = '\n'.join(errors[:5])
                if len(errors) > 5:
                    error_msg += f'\n... and {len(errors)-5} more errors'
                self.syntax_error_label.set_text(f'Syntax Errors:\n{error_msg}')
                self.syntax_error_label.visible = True
                self._notify(f'Found {len(errors)} syntax error(s)', type='warning')
            else:
                self.syntax_error_label.visible = False
                self._notify('No syntax errors found', type='positive')

        except Exception as e:
            log_web_error("_check_syntax", e)
            self._notify(f'Error checking syntax: {e}', type='negative')

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

            # Normalize line endings and remove CP/M EOF markers
            # \r\n -> \n (Windows line endings)
            # \r -> \n (old Mac line endings)
            # \x1a (Ctrl+Z, CP/M EOF marker)
            text = text.replace('\r\n', '\n').replace('\r', '\n').replace('\x1a', '')

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
                    # Show hex representation of weird characters for debugging
                    hex_repr = ' '.join(f'{ord(c):02x}' for c in line_text[:30])
                    # Write to stderr so it shows up in the terminal
                    import sys
                    print(f'Parse error: {repr(line_text[:30])} hex: {hex_repr}', file=sys.stderr)
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

            # Update runtime statement table so breakpoints can show character positions
            # This allows setting breakpoints before running the program
            if self.program.lines:
                self.runtime.reset_for_run(self.program.line_asts, self.program.lines)

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

    def _remove_blank_lines(self, e=None):
        """Remove blank lines from editor except the current line where cursor is.

        This prevents removing the blank line user just created with Enter.
        """
        try:
            if not self.editor:
                return

            current_text = self.editor.value or ''
            if not current_text:
                return

            lines = current_text.split('\n')

            # Keep all non-blank lines, but also keep the last line even if blank
            # (it's likely where the cursor is after pressing Enter)
            non_blank_lines = []
            for i, line in enumerate(lines):
                if line.strip() or i == len(lines) - 1:
                    non_blank_lines.append(line)

            # Only update if there were blank lines removed
            if len(non_blank_lines) != len(lines):
                self.editor.value = '\n'.join(non_blank_lines)

        except Exception as ex:
            log_web_error("_remove_blank_lines", ex)

    def _on_editor_change(self, e):
        """Handle CodeMirror editor content changes.

        This replaces the old keyup and paste handlers, handling:
        - Clearing placeholder on first edit
        - Removing blank lines
        - Auto-numbering lines
        """
        try:
            # Clear placeholder once user starts typing (no longer needed for CodeMirror)
            # CodeMirror doesn't use placeholder prop like textarea
            if not self.editor_has_been_used and self.editor.value:
                self.editor_has_been_used = True

            # Immediately remove blank lines
            self._remove_blank_lines()

            # Schedule auto-number check with small delay
            ui.timer(0.05, self._check_auto_number, once=True)

        except Exception as ex:
            log_web_error("_on_editor_change", ex)

    def _on_paste(self, e=None):
        """Handle paste event - remove blank lines after paste completes."""
        try:
            # Clear placeholder when pasting
            if not self.editor_has_been_used:
                self.editor_has_been_used = True
                self.editor.props('placeholder=""')

            # Use a timer to let the paste complete before cleaning
            # This ensures it runs in the UI context
            ui.timer(0.1, self._remove_blank_lines, once=True)

        except Exception as ex:
            log_web_error("_on_paste", ex)

    def _on_key_released(self, e):
        """Handle key release - remove blank lines and schedule auto-number check."""
        # Clear placeholder once user starts typing
        if not self.editor_has_been_used and self.editor.value:
            self.editor_has_been_used = True
            self.editor.props('placeholder=""')

        # Immediately remove blank lines (no throttle, no delay)
        self._remove_blank_lines()
        # Then schedule auto-number check with small delay
        ui.timer(0.05, self._check_auto_number, once=True)

    def _on_editor_click(self, e):
        """Handle editor click - schedule auto-number check."""
        # Schedule check with small delay to let cursor settle
        ui.timer(0.05, self._check_auto_number, once=True)

    def _on_editor_blur(self):
        """Handle editor blur - check auto-number and remove blank lines."""
        ui.timer(0.05, self._check_and_autonumber_on_blur, once=True)

    async def _check_and_autonumber_on_blur(self):
        """Check auto-number then remove blank lines on blur."""
        try:
            await self._check_auto_number()
            self._remove_blank_lines()
        except Exception as ex:
            log_web_error("_check_and_autonumber_on_blur", ex)

    async def _check_auto_number(self):
        """Check if we should auto-number lines without line numbers.

        Only auto-numbers a line once - tracks the last snapshot to avoid
        re-numbering lines while user is still typing on them.
        """
        # Prevent recursive calls when we update the editor
        if self.auto_numbering_in_progress:
            return

        auto_number_enabled = self.settings_manager.get('editor.auto_number')
        if not auto_number_enabled:
            return

        try:
            self.auto_numbering_in_progress = True

            # Get current editor content
            current_text = self.editor.value or ''

            # Don't auto-number if content hasn't changed
            if current_text == self.last_edited_line_text:
                return

            lines = current_text.split('\n')

            # Find lines that already have numbers
            numbered_lines = set()
            highest_line_num = 0
            for i, line in enumerate(lines):
                match = re.match(r'^\s*(\d+)', line.strip())
                if match:
                    numbered_lines.add(i)
                    highest_line_num = max(highest_line_num, int(match.group(1)))

            # Calculate what next line number should be
            auto_number_step = self.settings_manager.get('editor.auto_number_step')
            if highest_line_num > 0:
                next_line_num = highest_line_num + auto_number_step
            else:
                next_line_num = 10  # Default start

            # Only auto-number lines that:
            # 1. Have content
            # 2. Don't already have a line number
            # 3. Existed in last snapshot (so we only number "complete" lines)
            old_lines = (self.last_edited_line_text or '').split('\n') if self.last_edited_line_text else []

            modified = False
            for i, line in enumerate(lines):
                # Skip if already numbered
                if i in numbered_lines:
                    continue

                stripped = line.strip()
                # Only auto-number if:
                # - Line has content
                # - This line existed in previous snapshot (not being actively typed)
                # OR we have more lines now (user moved to new line)
                if stripped and (i < len(old_lines) or len(lines) > len(old_lines)):
                    # Check if this line was already numbered in old snapshot
                    old_line = old_lines[i] if i < len(old_lines) else ''
                    if not re.match(r'^\s*\d+', old_line):
                        # Line wasn't numbered before, number it now
                        lines[i] = f"{next_line_num} {stripped}"
                        numbered_lines.add(i)
                        next_line_num += auto_number_step
                        modified = True

            # Update editor and tracking if we made changes
            if modified:
                # Don't remove blank lines here - let _remove_blank_lines() handle it
                # This preserves the blank line the user just created with Enter
                new_content = '\n'.join(lines)
                self.editor.value = new_content
                self.last_edited_line_text = new_content
            else:
                # No changes, just update tracking
                self.last_edited_line_text = current_text

        except Exception as ex:
            log_web_error("_check_auto_number", ex)
        finally:
            self.auto_numbering_in_progress = False

    def _clear_output(self):
        """Clear output pane."""
        # Clear batch first
        self.output_batch.clear()
        self.output_update_count = 0
        if self.output_batch_timer:
            self.output_batch_timer.cancel()
            self.output_batch_timer = None

        # Clear output
        self.output_text = ''
        if self.output:
            self.output.value = ''
            self.output.update()
        self._set_status('Output cleared')

    def _append_output(self, text):
        """Append text to output pane with batching for performance.

        Batches multiple rapid output calls to reduce DOM updates and improve performance.
        Updates are flushed every 50ms or after 100 updates, whichever comes first.
        """

        # Add to batch
        self.output_batch.append(text)
        self.output_update_count += 1

        # Flush immediately if batch is getting large (every 50 updates)
        # This prevents lag spikes from huge batches
        if self.output_update_count >= 50:
            self._flush_output_batch()
            return

        # Otherwise, schedule a batched flush
        if self.output_batch_timer:
            self.output_batch_timer.cancel()

        # Flush after 50ms of inactivity, or immediately if running slowly
        self.output_batch_timer = ui.timer(0.05, self._flush_output_batch, once=True)

    def _flush_output_batch(self):
        """Flush batched output to the textarea."""
        if not self.output_batch:
            return

        # Combine all batched text
        batch_text = ''.join(self.output_batch)
        self.output_batch.clear()
        self.output_update_count = 0

        # Cancel pending timer
        if self.output_batch_timer:
            self.output_batch_timer.cancel()
            self.output_batch_timer = None

        # Update our internal buffer
        self.output_text += batch_text

        # Limit output buffer by number of lines to prevent infinite growth
        lines = self.output_text.split('\n')
        if len(lines) > self.output_max_lines:
            # Keep last N lines, add indicator at start
            lines = lines[-self.output_max_lines:]
            self.output_text = '\n'.join(lines)
            # Add truncation indicator if not already present
            if not self.output_text.startswith('[... output truncated'):
                self.output_text = '[... output truncated ...]\n' + self.output_text

        # Update the textarea directly
        if self.output:
            self.output.value = self.output_text
            self.output.update()

            # Auto-scroll to bottom using JavaScript
            ui.run_javascript('''
                setTimeout(() => {
                    let textarea = document.querySelector('[data-marker="output"] textarea');
                    if (!textarea) {
                        const textareas = document.querySelectorAll('textarea[readonly]');
                        textarea = textareas[textareas.length - 1];
                    }
                    if (textarea) {
                        textarea.scrollTop = textarea.scrollHeight;
                    }
                }, 10);
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
        if not self.input_field:
            return

        value = self.input_field.value
        self.input_field.value = ''

        # Hide the input row
        self._hide_input_row()

        # If interpreter is waiting for input, provide it
        if self.interpreter and self.interpreter.state.status == 'waiting_for_input':
            self.interpreter.provide_input(value)
            # Execution will resume on next tick

        # Also handle async input futures for compatibility
        if self.input_future and not self.input_future.done():
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
        """Get input from user (non-blocking version for web UI).

        Instead of blocking, this shows the input UI and returns empty string.
        The interpreter will transition to 'waiting_for_input' state, and
        when the user submits input via _submit_input(), it will call
        interpreter.provide_input() to continue execution.
        """
        # Show the input row for user to enter data
        self._show_input_row(prompt)

        # Return empty string - the interpreter will handle this by transitioning
        # to 'waiting_for_input' state, and execution will pause until
        # the user provides input via _submit_input()
        return ""

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

            # Handle special commands that must be processed by UI, not interpreter
            command_upper = command.upper().strip()

            # NEW command - clear program and variables
            if command_upper == 'NEW':
                self.cmd_new()
                return

            # RUN command - with optional line number
            import re
            run_match = re.match(r'^RUN(?:\s+(\d+))?$', command_upper)
            if run_match:
                line_num_str = run_match.group(1)
                if line_num_str:
                    # RUN line_number - CLEAR variables then start from that line
                    # This is equivalent to CLEAR : GOTO line_number
                    self.runtime.clear_variables()
                    # Set the starting line number temporarily
                    self._run_start_line = int(line_num_str)
                    self._menu_run()
                else:
                    # RUN without arguments - normal RUN
                    self._menu_run()
                return

            # LIST command - list program lines
            if command_upper.startswith('LIST'):
                # Extract arguments if any (e.g., LIST 100-200)
                args = command[4:].strip() if len(command) > 4 else ""
                self.cmd_list(args)
                return

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
                # Create a temporary interpreter for immediate mode with sandboxed file I/O
                from src.resource_limits import create_local_limits
                from src.file_io import SandboxedFileIO
                sandboxed_file_io = SandboxedFileIO(self)
                interpreter = Interpreter(runtime, output_io, limits=create_local_limits(), file_io=sandboxed_file_io)

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

                # Check if command was NEW or other program-modifying commands
                # Sync editor with program state
                if command.upper().strip() in ('NEW', 'CLEAR'):
                    # Program was cleared - update editor
                    self.editor.value = ''
                    self.current_file = None
                else:
                    # For other commands that might modify the program (numbered lines),
                    # sync editor with current program state
                    lines = self.program.get_lines()
                    if lines:
                        editor_text = '\n'.join(line_text for line_num, line_text in lines)
                        if editor_text != self.editor.value:
                            self.editor.value = editor_text
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

    def _update_resource_usage(self):
        """Update resource usage display."""
        if hasattr(self, 'resource_usage_label') and self.resource_usage_label and self.runtime:
            try:
                # Count variables
                var_count = len(self.runtime.variables) if hasattr(self.runtime, 'variables') else 0
                # Get array count
                array_count = len(self.runtime.arrays) if hasattr(self.runtime, 'arrays') else 0
                self.resource_usage_label.text = f'{var_count} vars, {array_count} arrays'
            except:
                pass

    # =========================================================================
    # UIBackend Interface
    # =========================================================================

    def start(self):
        """Start the UI.

        NOTE: For web backend, use start_web_ui() module function instead.
        This method is not used for the web backend.
        """
        raise NotImplementedError("Web backend uses start_web_ui() function, not backend.start()")

    def stop(self):
        """Stop the UI."""
        app.shutdown()


# Module-level function for proper multi-user web architecture
def start_web_ui(port=8080):
    """Start the NiceGUI web server with per-client backend instances.

    Args:
        port: Port number for web server (default: 8080)

    This is the proper architecture for multi-user web apps:
    - Each page load creates a NEW backend instance for that client
    - No shared state between clients
    - UI elements naturally isolated per client
    """
    # Log version to debug output
    sys.stderr.write(f"\n{'='*70}\n")
    sys.stderr.write(f"MBASIC Web UI Starting - Version {VERSION}\n")
    sys.stderr.write(f"{'='*70}\n\n")
    sys.stderr.flush()

    @ui.page('/')
    def main_page():
        """Create a new backend instance for each client."""
        from src.editing.manager import ProgramManager
        from src.ast_nodes import TypeInfo

        # Create default DEF type map (all SINGLE precision)
        def_type_map = {}
        for letter in 'abcdefghijklmnopqrstuvwxyz':
            def_type_map[letter] = TypeInfo.SINGLE

        # Create new program manager for this client
        program_manager = ProgramManager(def_type_map)

        # Create new backend instance for this client
        # Pass None for io_handler - it's not used in the web backend
        backend = NiceGUIBackend(None, program_manager)

        # Store backend in app.storage.client to keep it alive for this client's session
        # This is the ONLY thing we store in app.storage - the backend instance itself
        app.storage.client['backend'] = backend

        # Build the UI for this client
        backend.build_ui()

    # Start NiceGUI server
    ui.run(
        title='MBASIC 5.21 - Web IDE',
        port=port,
        reload=False,
        show=True
    )
