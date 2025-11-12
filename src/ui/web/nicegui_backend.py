"""NiceGUI web backend for MBASIC.

Provides a modern web-based UI for the MBASIC interpreter using NiceGUI.
"""

import re
import sys
import asyncio
import traceback
import signal
from typing import Dict
from nicegui import ui, app
from pathlib import Path
from ..base import UIBackend
from src.runtime import Runtime
from src.interpreter import Interpreter
from src.iohandler.base import IOHandler
from src.version import VERSION
from src.pc import PC
from src.ui.web.codemirror5_editor import CodeMirror5Editor
from src.ui.variable_sorting import sort_variables, get_sort_mode_label, cycle_sort_mode, get_default_reverse_for_mode
from src.error_logger import log_web_error
from src.usage_tracker import init_usage_tracker, get_usage_tracker


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

        The input_callback handles asyncio.Future coordination between synchronous
        interpreter and async web UI. The input field appears below the output pane,
        allowing users to see all previous output while typing.
        """
        # Don't print prompt here - the input_callback (backend._get_input) handles
        # prompt display via _enable_inline_input() method in the NiceGUIBackend class
        # Get input from UI (this will block until user enters input)
        result = self.input_callback(prompt)

        # Note: Input echoing (displaying what user typed) happens naturally because
        # the user types directly into the output textarea, which is made editable
        # by _enable_inline_input() in the NiceGUIBackend class.

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
        # Sort state (matches Tk UI defaults: see sort_mode and sort_reverse in src/ui/tk_ui.py)
        self.sort_mode = 'accessed'  # Current sort mode
        self.sort_reverse = True  # Sort direction

    def _toggle_direction(self):
        """Toggle sort direction and refresh display."""
        self.sort_reverse = not self.sort_reverse
        self.close()
        self.show()

    def _cycle_mode(self):
        """Cycle to next sort mode and refresh display."""
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

        # Sort using common helper (imported at module level)
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
            self._log_error("_open_file", ex)
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
            # Note: '5.21' is the MBASIC language version (intentionally hardcoded)
            # VERSION below is the implementation/package version (from src.version)
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
                    self._log_error("do_find_next", ex)

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
                    self._log_error("do_replace", ex)

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
                    self._log_error("do_replace_all", ex)

            def on_close():
                """Clear dialog reference when closed."""
                self._is_open = False
                self.close()
                # Note: CodeMirror maintains scroll position automatically when dialog closes

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
    - Breakpoint support (toggle, clear all, visual indicators)

    Based on TK UI feature set (see docs/dev/claude_if_you_read_in_here_you_loop/TK_UI_FEATURE_AUDIT.md).
    """

    def __init__(self, io_handler, program_manager):
        """Initialize NiceGUI backend.

        Args:
            io_handler: IOHandler for I/O operations
            program_manager: ProgramManager instance
        """
        super().__init__(io_handler, program_manager)

        # Per-client state (now instance variables instead of session storage)
        from src.runtime import Runtime
        from src.resource_limits import create_local_limits
        from src.file_io import SandboxedFileIO
        from src.filesystem import SandboxedFileSystemProvider

        self.runtime = Runtime({}, {})

        # Create session ID for this backend instance
        # Used for sandboxed filesystem and settings isolation
        session_id = str(id(self))  # Unique ID for this backend instance

        # Create sandboxed filesystem for this session
        self.sandboxed_fs = SandboxedFileSystemProvider(user_id=session_id)

        # Settings manager with pluggable backend
        # Uses Redis for per-session settings if NICEGUI_REDIS_URL is set
        from src.settings import SettingsManager
        from src.settings_backend import create_settings_backend
        settings_backend = create_settings_backend(session_id=session_id)
        self.settings_manager = SettingsManager(backend=settings_backend)

        # Configuration
        self.max_recent_files = 10
        self.auto_save_enabled = True       # Enable auto-save
        self.auto_save_interval = 30        # Auto-save every 30 seconds
        self.output_max_lines = 1000  # Maximum lines to keep in output buffer (reduced for web performance)

        # UI elements (created in build_ui())
        self.editor = None
        self.output = None
        self.status_label = None
        self.auto_line_label = None  # Auto line number indicator
        self.current_line_label = None  # Current line indicator
        self.immediate_entry = None  # Immediate mode command input
        self.recent_files_menu = None  # Recent files submenu

        # INPUT row elements (for inline input)
        self.input_row = None
        self.input_label = None
        self.input_field = None
        self.input_submit_btn = None

        # Create one interpreter for the session - don't create multiple!
        # Create IO handler for immediate mode
        immediate_io = SimpleWebIOHandler(self._append_output, self._get_input)
        sandboxed_file_io = SandboxedFileIO(self)
        self.interpreter = Interpreter(self.runtime, immediate_io,
                                      limits=create_local_limits(),
                                      file_io=sandboxed_file_io,
                                      filesystem_provider=self.sandboxed_fs)

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

        # Pending editor content (for state restoration)
        self._pending_editor_content = None

    def _log_error(self, context: str, exception: Exception):
        """Log an error with session tracking.

        Helper method to log errors with automatic session ID tracking.

        Args:
            context: Function/method name where error occurred
            exception: The exception that occurred
        """
        session_id = self.sandboxed_fs.user_id if hasattr(self, 'sandboxed_fs') else None
        log_web_error(context, exception, session_id=session_id)

    def _track_program_execution(self, success: bool, error_message: str = None):
        """Track program execution statistics.

        Args:
            success: Whether execution completed successfully
            error_message: Error message if execution failed
        """
        tracker = get_usage_tracker()
        if not tracker:
            return

        try:
            import time
            # Calculate execution time
            execution_time_ms = 0
            if hasattr(self, '_exec_start_time'):
                execution_time_ms = int((time.time() - self._exec_start_time) * 1000)

            # Get program size
            program_lines = self._exec_start_line_count if hasattr(self, '_exec_start_line_count') else 0

            # Get lines executed from runtime
            lines_executed = self.runtime.lines_executed if hasattr(self.runtime, 'lines_executed') else 0

            # Get session ID
            session_id = app.storage.client.id if app.storage.client else 'unknown'

            # Track the execution
            tracker.track_program_execution(
                session_id=session_id,
                program_lines=program_lines,
                execution_time_ms=execution_time_ms,
                lines_executed=lines_executed,
                success=success,
                error_message=error_message
            )
        except Exception as e:
            sys.stderr.write(f"Warning: Failed to track program execution: {e}\n")
            sys.stderr.flush()

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

        # Remove body margins/padding to eliminate space around top menu
        ui.add_head_html('''
            <style>
                body, html {
                    margin: 0 !important;
                    padding: 0 !important;
                    overflow: hidden !important;
                }
                .q-page, .q-page-container, .nicegui-content {
                    padding: 0 !important;
                    margin: 0 !important;
                }
                .q-layout, .q-drawer-container {
                    margin: 0 !important;
                    padding: 0 !important;
                }
                /* Remove NiceGUI's default column gap completely */
                .nicegui-content > .column {
                    gap: 0 !important;
                }
                /* Target NiceGUI's column wrapper */
                .nicegui-content > .q-pa-md {
                    padding: 0 !important;
                }
                /* Aggressively remove ALL row gaps and spacing */
                .row, .q-row, [class*="row"] {
                    gap: 0 !important;
                    row-gap: 0 !important;
                }
                /* Remove any child spacing in rows */
                .row > *, .q-row > * {
                    margin: 0 !important;
                }
            </style>
        ''')

        # Set page title ('5.21' is MBASIC language version, intentionally hardcoded)
        ui.page_title('MBASIC 5.21 - Web IDE')

        # Add global CSS to ensure full viewport height in both Firefox and Chrome
        ui.add_head_html('''
            <style>
                html, body {
                    height: 100%;
                    margin: 0;
                    padding: 0;
                    overflow: hidden;
                }
                #app, .q-page {
                    height: 100%;
                    display: flex;
                    flex-direction: column;
                }
                /* Force Quasar textarea to fill flex container in Chrome */
                .q-textarea, .q-field__control {
                    height: 100% !important;
                }
                .q-field__control-container {
                    height: 100% !important;
                }
            </style>
        ''')

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

        # Settings dialog
        from .web_settings_dialog import WebSettingsDialog
        self.settings_dialog = WebSettingsDialog(self)

        # Wrap top rows in column with zero gap to eliminate spacing between them
        # Use height: 100vh and display: flex to work in both Firefox and Chrome
        with ui.column().style('row-gap: 0; width: 100%; height: 100vh; display: flex; flex-direction: column; overflow: hidden;'):
            # Menu bar
            self._create_menu()

            # Toolbar
            with ui.row().classes('w-full bg-gray-100 px-2 gap-2').style('align-items: center; min-height: 36px; margin: 2px 0;'):
                ui.button('Run', on_click=self._menu_run, icon='play_arrow', color='green').mark('btn_run')
                ui.button('Stop', on_click=self._menu_stop, icon='stop', color='red').mark('btn_stop')
                ui.button('Step', on_click=self._menu_step_line, icon='skip_next').mark('btn_step_line')
                ui.button('Stmt', on_click=self._menu_step_stmt, icon='redo').mark('btn_step_stmt')
                ui.button('Cont', on_click=self._menu_continue, icon='play_circle').mark('btn_continue')
                ui.separator().props('vertical')
                ui.button(icon='check_circle', on_click=self._check_syntax).mark('btn_check_syntax').props('flat').tooltip('Check Syntax')

            # Command input row - single line like status bar
            with ui.row().classes('w-full bg-gray-100 px-2 gap-2').style('align-items: center; min-height: 32px; margin: 0;'):
                ui.label('>').classes('font-mono')
                self.immediate_entry = ui.input(placeholder='BASIC command...').classes('flex-grow').props('dense outlined').mark('immediate_entry')
                self.immediate_entry.on('keydown.enter', self._on_immediate_enter)
                ui.button('Execute', on_click=self._execute_immediate, icon='play_arrow', color='green').props('dense flat').mark('btn_immediate')

            # Status bar
            with ui.row().classes('w-full bg-gray-200 px-2').style('justify-content: space-between; min-height: 28px; align-items: center; margin: 0;'):
                self.status_label = ui.label('Ready').mark('status')
                with ui.row().classes('gap-4'):
                    self.auto_line_label = ui.label('').classes('text-gray-600 font-mono')
                    self.resource_usage_label = ui.label('').classes('text-gray-600')
                    ui.label(f'v{VERSION}').classes('text-gray-600')

            # Main content area - use splitter for resizable editor/output
            # horizontal=True means top/bottom split with horizontal drag bar
            with ui.splitter(value=40, horizontal=True).style('width: 100%; flex: 1; min-height: 0;') as splitter:
                with splitter.before:
                    # Editor panel
                    with ui.column().style('width: 100%; height: 100%; display: flex; flex-direction: column; gap: 0;'):
                        # Editor - using CodeMirror 5 (legacy, no ES6 modules)
                        self.editor = CodeMirror5Editor(
                            value='',
                            on_change=self._on_editor_change
                        ).style('width: 100%; flex: 1; min-height: 0; border: 1px solid #ccc;').mark('editor')

                        # Restore editor content if restoring from saved state
                        if self._pending_editor_content is not None:
                            self.editor.set_value(self._pending_editor_content)
                            self._pending_editor_content = None

                        # Add auto-numbering handlers
                        # Track last edited line for auto-numbering
                        self.last_edited_line_index = None
                        self.last_edited_line_text = None
                        self.last_line_count = 0  # Track number of lines to detect Enter
                        self.auto_numbering_in_progress = False  # Prevent recursive calls
                        self.editor_has_been_used = False  # Track if user has typed anything

                        # Content change handlers via CodeMirror's on_change callback
                        # The _on_editor_change method handles:
                        # - Removing blank lines
                        # - Auto-numbering
                        # - Placeholder clearing
                        # (Note: Method defined later in this class - search for 'def _on_editor_change')

                        # Click and blur handlers registered separately
                        self.editor.on('click', self._on_editor_click, throttle=0.05)
                        self.editor.on('blur', self._on_editor_blur)

                        # Current line indicator
                        self.current_line_label = ui.label('').classes('text-sm font-mono bg-yellow-100 p-1')
                        self.current_line_label.visible = False

                        # Syntax error indicator
                        self.syntax_error_label = ui.label('').classes('text-sm font-mono bg-red-100 text-red-700 p-1')
                        self.syntax_error_label.visible = False

                with splitter.after:
                    # Output panel
                    # Use important to override Quasar defaults in Chrome
                    self.output = ui.textarea(
                        value=f'MBASIC 5.21 Web IDE - {VERSION}\n',
                        placeholder='Output'
                    ).style('width: 100%; height: 100%; flex: 1 1 auto !important; min-height: 0 !important;').props('readonly outlined dense spellcheck=false').mark('output')

                    # Restore output if restoring from saved state
                    if hasattr(self, 'output_text') and self.output_text:
                        self.output.value = self.output_text

        # INPUT handling: When INPUT statement executes, the immediate_entry input box
        # is focused for user input (see _execute_tick() at line 1932).
        # The output textarea remains readonly.
        # Store state for input handling
        self.input_prompt_text = None  # Track current input prompt
        self.waiting_for_input = False

        # Set up Enter key handler for output textarea (for future inline input feature)
        self.output.on('keydown.enter', self._handle_output_enter)

        # Start auto-save timer
        self._start_auto_save()

        # Initialize editor with line number prompt if auto-numbering is enabled
        auto_number_enabled = self.settings_manager.get('auto_number')
        if auto_number_enabled and not self.editor.value:
            # Set initial line number with cursor positioned after it
            self.editor.run_method('setValueAndCursor', '10 ', 0, 3)
            self.editor._value = '10 '
            self.last_line_count = 1  # Initialize line count
        else:
            # Set initial focus to program editor
            self.editor.run_method('focus')
            self.last_line_count = 0

        # Update auto-line indicator
        self._update_auto_line_indicator()

    def _create_menu(self):
        """Create menu bar."""
        with ui.row().classes('w-full bg-gray-800 text-white px-2 gap-4').style('min-height: 36px; align-items: center; margin: 0;'):
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
            self._log_error("_save_recent_files", e)

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
            self._log_error("_add_recent_file", e)

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
            self._log_error("_update_recent_files_menu", e)

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
        """Toggle breakpoint at current cursor position.

        Supports both line-level and statement-level breakpoints:
        - If cursor is on first statement: sets line-level breakpoint (PC with stmt_offset=0)
        - If cursor is within multi-statement line: sets statement-level breakpoint (PC with stmt_offset>0)
        """
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
            self._log_error("_toggle_breakpoint", e)
            self._notify(f'Error: {e}', type='negative')

    async def _update_breakpoint_display(self):
        """Update the editor to show breakpoint markers using CodeMirror."""
        try:
            # Clear all existing breakpoint markers
            self.editor.clear_breakpoints()

            # Add markers for all current breakpoints
            # Note: self.runtime.breakpoints is a set that can contain:
            #   - PC objects (statement-level breakpoints, created by _toggle_breakpoint)
            #   - Plain integers (line-level breakpoints, legacy/compatibility)
            # This implementation uses PC objects exclusively, but handles both for robustness.
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
            self._log_error("_update_breakpoint_display", e)

    async def _do_toggle_breakpoint(self, line_num_str, dialog):
        """Actually toggle the breakpoint."""
        try:
            line_num = int(line_num_str)

            # Use PC object for consistency with _toggle_breakpoint
            # When setting breakpoint via dialog (no cursor position), use statement 0
            pc = PC(line_num, 0)

            if pc in self.runtime.breakpoints:
                self.runtime.breakpoints.discard(pc)
                self._notify(f'❌ Breakpoint removed: line {line_num}', type='info')
                self._set_status(f'Removed breakpoint at {line_num}')
            else:
                self.runtime.breakpoints.add(pc)
                self._notify(f'🔴 Breakpoint set: line {line_num}', type='positive')
                self._set_status(f'Breakpoint at {line_num}')

            await self._update_breakpoint_display()
            dialog.close()

        except ValueError:
            self._notify('Please enter a valid line number', type='warning')
        except Exception as e:
            self._log_error("_do_toggle_breakpoint", e)
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
            self._log_error("_clear_all_breakpoints", e)
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
            self._log_error("_menu_new", e)
            self._notify(f'Error: {e}', type='negative')

    def cmd_new(self) -> None:
        """Execute NEW command - clear program and variables (called by interpreter)."""
        # Clear the program
        self.program.clear()

        # Clear the editor
        self.editor.value = ''

        # Clear runtime if it exists
        if self.runtime:
            self.runtime.clear_variables()
            self.runtime.clear_arrays()

        # Reset current file
        self.current_file = None

        # Stop any running execution
        if self.exec_timer:
            self.exec_timer.cancel()
            self.exec_timer = None

        self.running = False
        self.paused = False

        self._set_status('Ready')
        self.io.output("New")

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
            self._log_error("_handle_file_upload", ex)
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
            self._log_error("_menu_save", e)
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
            self._log_error("_handle_save_as", e)
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
            self._log_error("_handle_merge_upload", ex)
            self._notify(f'Error merging file: {ex}', type='negative')

    async def _menu_exit(self):
        """File > Exit - Quit application."""
        app.shutdown()

    async def _menu_merge(self):
        """File > Merge - Merge another BASIC file into current program."""
        self.merge_file_dialog.show()

    async def _menu_run(self):
        """Run > Run Program - Execute program.

        RUN clears variables but preserves breakpoints (via runtime.reset_for_run())
        and starts execution from first line.
        Note: This implementation does NOT clear output (see comment at line ~1845 below).
        RUN on empty program is fine (just clears variables, no execution).
        RUN at a breakpoint restarts from the beginning.

        Breakpoints: User can set_breakpoint via Toggle Breakpoint menu (_toggle_breakpoint).
        Breakpoints are stored in runtime.breakpoints and honored during execution.
        """
        try:
            # Stop any existing execution timer first (defensive programming - prevents multiple timers)
            # Note: This pattern is applied uniformly across all timer management (see _menu_continue,
            # _menu_new, _menu_stop, etc.)
            if self.exec_timer:
                self.exec_timer.cancel()
                self.exec_timer = None

            # Save editor content to program first
            if not self._save_editor_to_program():
                return  # Parse errors, don't run

            # RUN on empty program is allowed (just clears variables, nothing to execute)
            # Don't show error - this matches real MBASIC behavior

            # Don't clear output - continuous scrolling like ASR33 teletype
            # Design choice: Unlike some modern BASIC interpreters that clear output on RUN,
            # we preserve historical ASR33 behavior (continuous scrolling, no auto-clear).
            # Note: Step commands also preserve output (no clearing during debugging either)
            self._set_status('Running...')

            # Get program AST
            program_ast = self.program.get_program_ast()

            # Reset runtime with current program - RUN = CLEAR + GOTO first line
            # This preserves breakpoints but clears variables
            self.runtime.reset_for_run(self.program.line_asts, self.program.lines)

            # Update interpreter's IO handler to output to execution pane
            self.exec_io = SimpleWebIOHandler(self._append_output, self._get_input)
            self.interpreter.io = self.exec_io

            # Start interpreter (sets up statement table, etc.)
            state = self.interpreter.start()
            if state.error_info:
                error_msg = state.error_info.error_message
                self._append_output(f"\n--- Setup error: {error_msg} ---\n")
                self._set_status('Error')
                self.running = False  # Mark as not running (updates UI spinner/status)
                return

            # Check if RUN was called with a line number (e.g., RUN 120)
            # This is set by immediate_executor when user types "RUN 120"
            if hasattr(self, '_run_start_line') and self._run_start_line:
                # Set PC to start at the specified line
                from src.pc import PC
                self.runtime.npc = PC.from_line(self._run_start_line)
                # Clear the temporary attribute
                self._run_start_line = None

            # If empty program, just show Ready (variables cleared, nothing to execute)
            if not self.program.lines:
                self._set_status('Ready')
                self.running = False  # Mark as not running (updates UI spinner/status)
                return

            # Mark as running (for display and state tracking - spinner, status, continue/step logic)
            self.running = True

            # Track execution start time
            import time
            self._exec_start_time = time.time()
            self._exec_start_line_count = len(self.program.lines) if self.program else 0

            # Start async execution - store timer handle so we can cancel it
            self.exec_timer = ui.timer(0.01, self._execute_tick, once=False)

        except Exception as e:
            self._log_error("_menu_run", e)
            self._append_output(f"\n--- Error: {e} ---\n")
            self._set_status(f'Error: {e}')
            self.running = False

    def _execute_tick(self):
        """Execute one tick of the interpreter.

        This method is called every 10ms by ui.timer() during program execution.

        Note: In the web UI, Ctrl+C in the browser does not send interrupt signals to
        the Python backend process. To stop a running program, users must use the Stop
        menu item or the server-side interrupt mechanism (if running from terminal).
        This differs from terminal-based UIs where Ctrl+C works directly.
        """
        # Check if we have an interpreter before proceeding
        # Note: self.running is also set/cleared elsewhere but may not persist reliably in async callbacks
        if not self.interpreter:
            return

        try:
            state = self.interpreter.state if self.interpreter else None
            if not state:
                return

            # If waiting for input, don't tick - wait for input to be provided
            if state.input_prompt:
                self._set_status("Waiting for input...")
                # Show prompt and focus the immediate mode input box
                if not self.waiting_for_input:
                    self.waiting_for_input = True
                    self.input_prompt_text = state.input_prompt
                    # Note: We don't append the prompt to output here because the interpreter
                    # has already printed it via io.output() before setting input_prompt state.
                    # Verified: INPUT statement calls io.output(prompt) before awaiting user input.
                    # Change placeholder text to indicate we're waiting for input
                    self.immediate_entry.props('placeholder="Input: "')
                    # Focus the immediate input box for user to type
                    self.immediate_entry.run_method('focus')
                return

            # Execute one tick (up to 1000 statements)
            state = self.interpreter.tick(mode='run', max_statements=1000)

            # Handle state using microprocessor model
            if state.error_info:
                error_msg = state.error_info.error_message
                self._append_output(f"\n--- Error: {error_msg} ---\n")
                self._set_status("Error")
                self.running = False

                # Track failed program execution
                self._track_program_execution(success=False, error_message=error_msg)

                # Hide current line highlight
                if self.current_line_label:
                    self.current_line_label.visible = False
                if self.exec_timer:
                    self.exec_timer.cancel()
                    self.exec_timer = None
            elif state.input_prompt:
                # Pause execution until input is provided
                self._set_status("Waiting for input...")
                # Show prompt and focus the immediate mode input box
                if not self.waiting_for_input:
                    self.waiting_for_input = True
                    self.input_prompt_text = state.input_prompt
                    # Note: We don't append the prompt to output here because the interpreter
                    # has already printed it via io.output() before setting input_prompt state.
                    # Verified: INPUT statement calls io.output(prompt) before awaiting user input.
                    # Change placeholder text to indicate we're waiting for input
                    self.immediate_entry.props('placeholder="Input: "')
                    # Focus the immediate input box for user to type
                    self.immediate_entry.run_method('focus')
                # Don't cancel timer - keep ticking to check when input is provided
            elif not self.runtime.pc.is_running():
                # Check if done or paused at breakpoint
                if not self.runtime.is_paused_at_statement():
                    # Past end of program - done
                    self._append_output("\n--- Program finished ---\n")
                    self._set_status("Ready")
                    self.running = False

                    # Track successful program execution
                    self._track_program_execution(success=True)

                    # Hide current line highlight
                    if self.current_line_label:
                        self.current_line_label.visible = False
                    if self.exec_timer:
                        self.exec_timer.cancel()
                        self.exec_timer = None
                else:
                    # Paused at a statement (breakpoint or step)
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
                    self.exec_timer = None

        except Exception as e:
            self._log_error("_execute_tick", e)
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
        # Note: PC handles halted state - no need to set flags

        # Update UI state
        self.running = False
        self.paused = False

        # Cancel inline input if waiting
        if self.waiting_for_input:
            self.waiting_for_input = False
            self.input_prompt_text = None
            # Make output readonly again - use JavaScript to set readonly attribute
            self.output.run_method('''() => {
                const el = this.$el.querySelector('textarea');
                if (el) {
                    el.setAttribute('readonly', 'readonly');
                }
            }''')

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

                # If empty program, just show Ready (matches RUN behavior - silent success)
                if not self.program.lines:
                    self._set_status('Ready')
                    self.running = False  # Mark as not running (matches RUN behavior)
                    return

                # Start execution
                # Note: Output is NOT cleared - continuous scrolling like ASR33 teletype

                # Create or reset runtime - preserves breakpoints
                from src.resource_limits import create_local_limits
                if self.runtime is None:
                    self.runtime = Runtime(self.program.line_asts, self.program.lines)
                    self.runtime.setup()
                else:
                    # Reset runtime for fresh execution (clears variables but preserves breakpoints)
                    self.runtime.reset_for_run(self.program.line_asts, self.program.lines)

                # Create new IO handler for execution
                self.exec_io = SimpleWebIOHandler(self._append_output, self._get_input)
                self.interpreter.io = self.exec_io
                self.interpreter.limits = create_local_limits()

                # Wire up interpreter
                self.interpreter.interactive_mode = self

                # Start interpreter
                state = self.interpreter.start()
                if state.error_info:
                    error_msg = state.error_info.error_message
                    self._append_output(f"\n--- Setup error: {error_msg} ---\n")
                    self._set_status('Error')
                    return

                # Execute one line
                state = self.interpreter.tick(mode='step_line', max_statements=100)
                self._handle_step_result(state, 'line')

            else:
                # Already running - step one line
                if self.interpreter:
                    try:
                        # PC will be updated by tick - no need to manipulate flags
                        state = self.interpreter.tick(mode='step_line', max_statements=100)
                        self._handle_step_result(state, 'line')
                    except Exception as e:
                        self._log_error("_menu_step_line tick", e)
                        self._append_output(f"\n--- Step error: {e} ---\n")
                        self._set_status('Error')
                        self.running = False
                        self.paused = False
                else:
                    self._notify('No interpreter - program not started', type='warning')

        except Exception as e:
            self._log_error("_menu_step_line", e)
            self._notify(f'Error: {e}', type='negative')

    async def _menu_step_stmt(self):
        """Run > Step Statement - Execute one statement and pause."""
        try:
            if not self.running and not self.paused:
                # Not running - start program and step one statement
                if not self._save_editor_to_program():
                    return  # Parse errors

                # If empty program, just show Ready (matches RUN behavior - silent success)
                if not self.program.lines:
                    self._set_status('Ready')
                    self.running = False  # Mark as not running (matches RUN behavior)
                    return

                # Start execution
                # Note: Output is NOT cleared - continuous scrolling like ASR33 teletype

                # Create or reset runtime - preserves breakpoints
                from src.resource_limits import create_local_limits
                if self.runtime is None:
                    self.runtime = Runtime(self.program.line_asts, self.program.lines)
                    self.runtime.setup()
                else:
                    self.runtime.reset_for_run(self.program.line_asts, self.program.lines)

                # Create new IO handler for execution
                # Note: Interpreter/runtime objects are reused across runs (not recreated each time).
                # The runtime.reset_for_run() call above clears variables but preserves breakpoints.
                self.exec_io = SimpleWebIOHandler(self._append_output, self._get_input)
                self.interpreter.io = self.exec_io
                self.interpreter.limits = create_local_limits()

                # Wire up interpreter
                self.interpreter.interactive_mode = self

                # Start interpreter
                state = self.interpreter.start()
                if state.error_info:
                    error_msg = state.error_info.error_message
                    self._append_output(f"\n--- Setup error: {error_msg} ---\n")
                    self._set_status('Error')
                    return

                # Execute one statement
                state = self.interpreter.tick(mode='step_statement', max_statements=1)
                self._handle_step_result(state, 'statement')

            else:
                # Already running - step one statement
                if self.interpreter:
                    try:
                        # PC will be updated by tick - no need to manipulate flags
                        state = self.interpreter.tick(mode='step_statement', max_statements=1)
                        self._handle_step_result(state, 'statement')
                    except Exception as e:
                        self._log_error("_menu_step_stmt tick", e)
                        self._append_output(f"\n--- Step error: {e} ---\n")
                        self._set_status('Error')
                        self.running = False
                        self.paused = False
                else:
                    self._log_error("_menu_step_stmt", "No interpreter")
                    self._notify('No interpreter - program not started', type='warning')

        except Exception as e:
            self._log_error("_menu_step_stmt", e)
            self._notify(f'Error: {e}', type='negative')

    def _handle_step_result(self, state, step_type):
        """Handle result of a step operation."""
        # Use microprocessor model: check error_info, input_prompt, and pc.is_running()
        if state.input_prompt:
            # Waiting for input - show input UI
            self._show_input_prompt(state.input_prompt)
            self.running = True
            self.paused = True
            self._set_status(f"Waiting for input at line {state.current_line}")
            # Show current line highlight
            if self.current_line_label:
                self.current_line_label.set_text(f'>>> Waiting for input at line {state.current_line}')
                self.current_line_label.visible = True
            # Highlight current statement
            char_start = state.current_statement_char_start if state.current_statement_char_start > 0 else None
            char_end = state.current_statement_char_end if state.current_statement_char_end > 0 else None
            self.editor.set_current_statement(state.current_line, char_start, char_end)
        elif state.error_info:
            error_msg = state.error_info.error_message
            self._append_output(f"\n--- Error: {error_msg} ---\n")
            self._set_status("Error")
            self.running = False
            self.paused = False
            # Hide current line highlight
            if self.current_line_label:
                self.current_line_label.visible = False
            # Clear CodeMirror current statement highlight
            self.editor.set_current_statement(None)
        elif not self.runtime.pc.is_running():
            # Runtime is not running - could be paused at statement or finished
            # Check PC directly - state.current_line returns None when not running
            pc = self.runtime.pc
            if pc and pc.line_num is not None:
                # Paused at a statement - ready for next step
                self._set_status(f"Paused at line {pc.line_num}")
                self.running = True
                self.paused = True
                # Show current line highlight
                if self.current_line_label:
                    self.current_line_label.set_text(f'>>> Executing line {pc.line_num}')
                    self.current_line_label.visible = True
                # Get char positions directly from statement_table (state properties return 0 when halted)
                char_start = None
                char_end = None
                stmt = self.runtime.statement_table.get(pc)
                if stmt:
                    char_start = getattr(stmt, 'char_start', 0) if hasattr(stmt, 'char_start') else 0
                    char_end = getattr(stmt, 'char_end', 0) if hasattr(stmt, 'char_end') else 0
                    if char_start > 0 and char_end > char_start:
                        # Valid positions
                        pass
                    else:
                        char_start = None
                        char_end = None
                self.editor.set_current_statement(pc.line_num, char_start, char_end)
            else:
                # No current line - program finished
                self._append_output("\n--- Program finished ---\n")
                self._set_status("Ready")
                self.running = False
                self.paused = False
                # Hide current line highlight
                if self.current_line_label:
                    self.current_line_label.visible = False
                # Clear CodeMirror current statement highlight
                self.editor.set_current_statement(None)
        else:
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
                # Cancel any existing timer first (defensive programming - prevents multiple timers)
                if self.exec_timer:
                    self.exec_timer.cancel()
                    self.exec_timer = None
                # Start timer to continue execution in run mode
                self.exec_timer = ui.timer(0.01, self._execute_tick, once=False)
            else:
                self._notify('Not paused', type='warning')

        except Exception as e:
            self._log_error("_menu_continue", e)
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
            self._log_error("_menu_sort_lines", e)
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
            from ...docs_config import get_docs_url
            topic_path = "ui/web/"
            url = get_docs_url(topic_path, "web")

            # Use JavaScript to open URL in client's browser
            ui.run_javascript(f'window.open("{url}", "_blank");')
            self._notify('Opening help in new tab...', type='positive', log_to_output=False)
        except Exception as e:
            self._log_error("_menu_help", e)
            self._notify(f'Error opening help: {e}', type='negative')

    def _menu_games_library(self):
        """Help > Games Library - Opens program library in browser."""
        try:
            from ...docs_config import get_site_url
            # Library is at site root, not under /help/
            url = get_site_url("library/")

            # Use JavaScript to open URL in client's browser
            ui.run_javascript(f'window.open("{url}", "_blank");')
            self._notify('Opening program library in new tab...', type='positive', log_to_output=False)
        except Exception as e:
            self._log_error("_menu_games_library", e)
            self._notify(f'Error opening library: {e}', type='negative')

    async def _menu_settings(self):
        """Edit > Settings - Open settings dialog."""
        self.settings_dialog.show()

    def _menu_about(self):
        """Help > About."""
        self.about_dialog.show()

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
            self._log_error("_auto_save_tick", e)

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
            self._log_error("_auto_save_to_storage", e)

    def _load_auto_save(self):
        """Load auto-saved content from localStorage if available."""
        try:
            # This would typically be called on startup
            # For now, it's a placeholder for future enhancement
            pass
        except Exception as e:
            self._log_error("_load_auto_save", e)

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
                    from src.lexer import Lexer, LexerError
                    lexer = Lexer(line_text)
                    tokens = lexer.tokenize()
                    parser = Parser(tokens)
                    parser.parse_line()
                except LexerError as e:
                    # Lexer reports token position (1:col), replace with BASIC line number
                    error_msg = str(e).replace(f'at {e.line}:', f'at {line_num}:')
                    # Check if error already contains "in {line_num}"
                    if f' in {line_num}' in error_msg or f'in {line_num}:' in error_msg:
                        errors.append(error_msg)
                    else:
                        errors.append(f'{line_num}: {error_msg}')
                except Exception as e:
                    error_msg = str(e)
                    # If error already contains "in {line_num}", don't add duplicate prefix
                    if f' in {line_num}' in error_msg or f'in {line_num}:' in error_msg:
                        errors.append(error_msg)
                    else:
                        errors.append(f'{line_num}: {error_msg}')

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
            self._log_error("_check_syntax", e)
            self._notify(f'Error checking syntax: {e}', type='negative')

    # =========================================================================
    # Editor Actions
    # =========================================================================

    def _sync_program_to_runtime(self):
        """Sync program to runtime, conditionally preserving PC.

        Updates runtime's statement_table and line_text_map from self.program.

        PC handling (conditional preservation):
        - If exec_timer is active (execution in progress): Preserves PC and halted state,
          allowing program to resume from current position after rebuild.
        - Otherwise (no active execution): Resets PC to halted state, preventing
          unexpected execution when LIST/edit commands modify the program.
        """
        # Save current PC before rebuilding statement table
        # We'll conditionally restore based on whether execution is active (see below)
        old_pc = self.runtime.pc

        # Clear and rebuild statement table
        self.runtime.statement_table.statements.clear()
        self.runtime.statement_table._keys_cache = None

        # Update line text map
        self.runtime.line_text_map = dict(self.program.lines)

        # Rebuild statement table from program ASTs
        for line_num in sorted(self.program.line_asts.keys()):
            line_ast = self.program.line_asts[line_num]
            for stmt_offset, stmt in enumerate(line_ast.statements):
                pc = PC(line_num, stmt_offset)
                self.runtime.statement_table.add(pc, stmt)

        # Conditionally restore PC based on whether execution timer is active
        # This logic is about PRESERVING vs RESETTING state, not about preventing accidental starts
        if self.exec_timer and self.exec_timer.active:
            # Timer is active - execution is in progress, so preserve PC
            # (allows program to resume from current position after statement table rebuild)
            self.runtime.pc = old_pc
        else:
            # Timer is not active - no execution in progress, so reset to halted state
            # (ensures program doesn't start executing unexpectedly when LIST/edit commands run)
            self.runtime.pc = PC.halted_pc()

    def _save_editor_to_program(self):
        """Save editor content to program.

        Parses all lines in the editor and updates the program.
        Returns True if successful, False if there were errors.
        """
        try:
            # Clear existing program
            self.program.clear()

            # Get editor content - always use the property which handles dict conversion
            text = self.editor.value

            if not text:
                self._set_status('Program cleared')
                return True

            # Normalize line endings and remove CP/M EOF markers
            # \r\n -> \n (Windows line endings, may appear if user pastes text)
            # \r -> \n (old Mac line endings, may appear if user pastes text)
            # \x1a (Ctrl+Z, CP/M EOF marker - included for consistency with file loading)
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
            self._log_error("_save_editor_to_program", e)
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
            self._log_error("_load_program_to_editor", e)
            self._notify(f'Error: {e}', type='negative')

    def _remove_blank_lines(self, e=None):
        """Remove blank lines from editor except the last line.

        The last line is preserved even if blank to avoid removing it while the user
        is actively typing on it. Only the final line is preserved; all other blank
        lines are removed regardless of cursor position.
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
            self._log_error("_remove_blank_lines", ex)

    def _on_editor_change(self, e):
        """Handle CodeMirror editor content changes.

        This replaces the old keyup and paste handlers, handling:
        - Clearing placeholder on first edit
        - Removing blank lines
        - Auto-numbering lines
        - Detecting Enter key (new line added)
        - Detecting paste and clearing auto-number prompts
        """
        try:
            # Get current text
            current_text = self.editor.value

            # Track when editor has been used (for placeholder management)
            if not self.editor_has_been_used and current_text:
                self.editor_has_been_used = True

            # Detect paste: large content change (threshold: >5 chars)
            # This heuristic helps clear auto-number prompts before paste content merges with them.
            # The 5-char threshold is arbitrary - balances detecting small pastes while avoiding
            # false positives from rapid typing (e.g., typing "PRINT" quickly = 5 chars but not a paste).
            last_text = self.last_edited_line_text or ''
            content_diff = abs(len(current_text) - len(last_text))

            # If content changed significantly (>5 chars), likely a paste - check for double line numbers
            if content_diff > 5:
                # When pasting with auto-numbering enabled, the first line may have a double line number
                # (e.g., "10 100 PRINT" where "10 " is the auto-number prompt and "100 PRINT" is pasted)
                lines = current_text.split('\n')
                if lines and re.match(r'^\d+\s+\d+\s+', lines[0]):
                    # First line has format "10 100 ..." - double line number from paste
                    # Extract the auto-number prompt and remove it
                    match = re.match(r'^(\d+)\s+(.*)$', lines[0])
                    if match:
                        lines[0] = match.group(2)  # Keep only the pasted content
                        self.editor.value = '\n'.join(lines)
                        current_text = self.editor.value

            # Detect if a new line was added (Enter key pressed)
            current_line_count = len(current_text.split('\n'))

            if current_line_count > self.last_line_count:
                # New line was added - add line number prompt
                ui.timer(0.1, self._add_next_line_number, once=True)

            self.last_line_count = current_line_count

            # Immediately remove blank lines (but not the last one where cursor is)
            self._remove_blank_lines()

            # Update auto-line indicator
            self._update_auto_line_indicator()

            # Schedule auto-number check with small delay
            ui.timer(0.05, self._check_auto_number, once=True)

        except Exception as ex:
            self._log_error("_on_editor_change", ex)

    def _on_enter_key(self):
        """Handle Enter key press in editor - triggers auto-numbering.

        Note: This method is called internally by _on_editor_change when a new line
        is detected. The actual auto-numbering logic is in _add_next_line_number.
        """
        # Auto-numbering on Enter is handled by _on_editor_change detecting new lines
        # and calling _add_next_line_number via timer
        pass

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
            self._log_error("_on_paste", ex)

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

    async def _add_next_line_number(self):
        """Add next line number to the new line created by Enter.

        Also auto-numbers the previous line if it doesn't have a line number.
        """
        try:
            # Get current editor content
            current_text = self.editor.value or ''
            lines = current_text.split('\n')

            if len(lines) < 2:
                return  # Need at least 2 lines (previous + new)

            # Find highest line number and check if previous line needs numbering
            highest_line_num = 0
            prev_line_needs_number = False

            for i, line in enumerate(lines):
                match = re.match(r'^\s*(\d+)', line.strip())
                if match:
                    highest_line_num = max(highest_line_num, int(match.group(1)))
                elif i == len(lines) - 2 and line.strip():  # Previous line (before last)
                    prev_line_needs_number = True

            # Calculate next line numbers
            auto_number_step = self.settings_manager.get('auto_number_step')
            if highest_line_num > 0:
                next_line_num = highest_line_num + auto_number_step
            else:
                next_line_num = 10  # Default start

            # Auto-number previous line if it needs it
            if prev_line_needs_number:
                prev_line = lines[-2].strip()
                lines[-2] = f'{next_line_num} {prev_line}'
                next_line_num += auto_number_step

            # Add line number to the new blank line
            if lines[-1].strip() == '':
                line_num_prompt = f'{next_line_num} '
                lines[-1] = line_num_prompt
                new_content = '\n'.join(lines)

                # Position cursor at end of line number (after the space)
                # Line is 0-based, last line is len(lines) - 1
                cursor_line = len(lines) - 1
                cursor_col = len(line_num_prompt)

                # Set value and cursor together (JavaScript will skip change event to avoid interference)
                await self.editor.run_method('setValueAndCursor', new_content, cursor_line, cursor_col)

                # Update internal Python state (since JavaScript skipped change event)
                self.editor._value = new_content
                self.last_line_count = len(lines)  # Update line count to prevent re-triggering
                self._update_auto_line_indicator()

        except Exception as ex:
            self._log_error("_add_next_line_number", ex)

    async def _check_and_autonumber_on_blur(self):
        """Check auto-number then remove blank lines on blur."""
        try:
            await self._check_auto_number()
            self._remove_blank_lines()
        except Exception as ex:
            self._log_error("_check_and_autonumber_on_blur", ex)

    async def _check_auto_number(self):
        """Check if we should auto-number lines without line numbers.

        Tracks last edited line text to avoid re-numbering unchanged content.
        Lines without line numbers will be auto-numbered based on the highest
        existing line number plus the configured step value.
        """
        # Prevent recursive calls when we update the editor
        if self.auto_numbering_in_progress:
            return

        auto_number_enabled = self.settings_manager.get('auto_number')
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
            auto_number_step = self.settings_manager.get('auto_number_step')
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
            self._log_error("_check_auto_number", ex)
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
        Updates are flushed every 50ms or after 50 updates, whichever comes first.
        """

        # Add to batch
        self.output_batch.append(text)
        self.output_update_count += 1

        # Flush immediately if batch reaches 50 updates
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

    def _handle_output_enter(self, e):
        """Handle Enter key in output textarea for inline input."""
        if not self.waiting_for_input:
            # Not waiting for input, ignore Enter
            e.sender.run_method('event.preventDefault')
            return

        # Get the text from the output
        current_text = self.output.value or ''

        # Find what the user typed after the prompt
        if self.input_prompt_text:
            # Extract user input (everything after the prompt)
            prompt_pos = current_text.rfind(self.input_prompt_text)
            if prompt_pos >= 0:
                user_input = current_text[prompt_pos + len(self.input_prompt_text):]
            else:
                user_input = ''
        else:
            # Get last line as input
            lines = current_text.split('\n')
            user_input = lines[-1] if lines else ''

        # Clean up the input (remove trailing whitespace)
        user_input = user_input.strip()

        # Add newline after input to move to next line
        self.output.value = current_text + '\n'

        # Make output readonly again - use JavaScript to set readonly attribute
        self.output.run_method('() => { const el = this.$el.querySelector("textarea"); if (el) { el.setAttribute("readonly", "readonly"); } }')

        # Mark that we're no longer waiting
        self.waiting_for_input = False
        self.input_prompt_text = None

        # Provide input to interpreter via TWO mechanisms (we check both in case either is active):
        # 1. interpreter.provide_input() - Used when interpreter is waiting synchronously
        #    (checked via interpreter.state.input_prompt). Stores input for retrieval.
        if self.interpreter and self.interpreter.state.input_prompt:
            self.interpreter.provide_input(user_input)

        # 2. input_future.set_result() - Used when async code is waiting via asyncio.Future
        #    (see _get_input_async method). Only one path will be active at a time, but we
        #    check both to handle whichever path the interpreter is currently using.
        if self.input_future and not self.input_future.done():
            self.input_future.set_result(user_input)

        # Prevent default Enter behavior
        e.sender.run_method('event.preventDefault')

    def _enable_inline_input(self, prompt=''):
        """Enable inline input in output textarea."""
        # Append prompt to output without newline
        current_text = self.output.value or ''
        if not current_text.endswith('\n') and current_text:
            self.output.value = current_text + '\n' + prompt
        else:
            self.output.value = current_text + prompt

        # Store prompt for later extraction of user input
        self.input_prompt_text = prompt
        self.waiting_for_input = True

        # Make output editable - use JavaScript to directly remove readonly attribute
        # Use single line to avoid line break issues
        self.output.run_method('() => { const el = this.$el.querySelector("textarea"); if (el) { el.removeAttribute("readonly"); el.focus(); el.setSelectionRange(el.value.length, el.value.length); } }')

    async def _get_input_async(self, prompt):
        """Get input from user (async version).

        Creates a Future that will be resolved when user submits input.
        """
        # Create a new future for this input request
        loop = asyncio.get_event_loop()
        self.input_future = loop.create_future()

        # Enable inline input
        self._enable_inline_input(prompt)

        # Wait for user to submit input
        result = await self.input_future

        return result

    def _get_input(self, prompt):
        """Get input from user (non-blocking version for web UI).

        Protocol: Returns empty string to signal interpreter state transition.

        This implements a non-blocking input pattern for the web UI:
        1. Show input UI by calling _enable_inline_input(prompt)
        2. Return empty string immediately (non-blocking)
        3. Interpreter detects empty string and transitions to 'waiting_for_input' state
        4. Program execution pauses
        5. When user submits via _handle_output_enter(), call interpreter.provide_input()
        6. Interpreter resumes execution from waiting state

        Implementation note: This relies on interpreter.input() treating empty string
        as a signal to enter waiting state. If interpreter behavior changes, this
        state transition protocol will break silently (program will hang).
        """
        # Enable inline input in output textarea
        self._enable_inline_input(prompt)

        # Return empty string to signal interpreter state transition
        return ""

    def _on_immediate_enter(self, e):
        """Handle Enter key in immediate mode input."""
        # Check if we're waiting for LINE INPUT
        if self.waiting_for_input and self.interpreter and self.interpreter.state.input_prompt:
            # Submit the input to the running program
            user_input = self.immediate_entry.value
            self.immediate_entry.value = ''

            # Echo the input to output
            self._append_output(user_input + '\n')

            # Provide input to interpreter
            self.interpreter.provide_input(user_input)

            # Clear waiting state and restore placeholder
            self.waiting_for_input = False
            self.input_prompt_text = None
            self.immediate_entry.props('placeholder="BASIC command..."')
            return

        # Normal immediate mode command
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

            # Use the session's single interpreter and runtime
            # Don't create temporary ones!
            runtime = self.runtime
            interpreter = self.interpreter

            # Parse editor content into program (in case user typed lines directly)
            # This updates self.program but doesn't affect runtime yet
            self._save_editor_to_program()

            # Sync program to runtime (but don't reset PC - keep current execution state)
            # This allows LIST to work, but doesn't start execution
            self._sync_program_to_runtime()

            # Create immediate executor (runtime, interpreter, output_io)
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

                # Architecture: We do NOT auto-sync editor from AST after immediate commands.
                # This preserves one-way data flow (editor → AST → execution) and prevents
                # losing user's formatting/comments. Commands that modify code (like RENUM)
                # update the editor text directly.

                # If statement set NPC (like RUN/GOTO), move it to PC
                # This is what the tick loop does after executing a statement
                if self.runtime.npc is not None:
                    self.runtime.pc = self.runtime.npc
                    self.runtime.npc = None

                # Check if interpreter has work to do (after RUN statement)
                # Query interpreter directly via has_work() instead of checking runtime flags
                has_work = self.interpreter.has_work() if self.interpreter else False
                if self.interpreter and has_work:
                    # Start execution timer if not already running
                    if not self.exec_timer:
                        self._set_status('Running...')
                        self.exec_timer = ui.timer(0.01, self._execute_tick, once=False)
            else:
                self._set_status('Immediate command error')

        except Exception as e:
            self._log_error("_execute_immediate", e)
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

    def _update_auto_line_indicator(self):
        """Update auto line number indicator to show next line number."""
        if not hasattr(self, 'auto_line_label') or not self.auto_line_label:
            return

        auto_number_enabled = self.settings_manager.get('auto_number')
        if not auto_number_enabled:
            self.auto_line_label.text = ''
            return

        try:
            # Calculate next line number
            current_text = self.editor.value or ''
            lines = current_text.split('\n')

            # Find highest line number
            highest_line_num = 0
            for line in lines:
                match = re.match(r'^\s*(\d+)', line.strip())
                if match:
                    highest_line_num = max(highest_line_num, int(match.group(1)))

            # Calculate next line number
            auto_number_step = self.settings_manager.get('auto_number_step')
            if highest_line_num > 0:
                next_line_num = highest_line_num + auto_number_step
            else:
                next_line_num = 10  # Default start

            self.auto_line_label.text = f'Auto {next_line_num}'
        except Exception as ex:
            self._log_error("_update_auto_line_indicator", ex)

    # =========================================================================
    # Session State Serialization (for Redis storage support)
    # =========================================================================

    def serialize_state(self) -> dict:
        """Serialize backend state for storage.

        This enables session persistence in Redis for load-balanced deployments.
        The state is stored in app.storage.client, which NiceGUI automatically
        backs by Redis when NICEGUI_REDIS_URL is set.

        Returns:
            dict: Serializable state dictionary
        """
        from src.ui.web.session_state import SessionState

        # Sync program manager from editor content before serializing
        # This ensures we capture any edits that haven't been run yet
        self._sync_program_from_editor()

        # Close any open files before serialization
        self._close_all_files()

        state = SessionState(
            session_id=self.sandboxed_fs.user_id,
            program_lines=self._serialize_program(),
            runtime_state=self._serialize_runtime(),
            running=self.running,
            paused=self.paused,
            output_text=self.output_text,
            current_file=self.current_file,
            recent_files=self.recent_files.copy() if self.recent_files else [],
            last_save_content=self.last_save_content,
            max_recent_files=self.max_recent_files,
            auto_save_enabled=self.auto_save_enabled,
            auto_save_interval=self.auto_save_interval,
            last_find_text=self.last_find_text,
            last_find_position=self.last_find_position,
            last_case_sensitive=self.last_case_sensitive,
            editor_content=self.editor.value if self.editor else "",
            last_edited_line_index=self.last_edited_line_index,
            last_edited_line_text=self.last_edited_line_text,
        )

        return state.to_dict()

    def restore_state(self, state_dict: dict) -> None:
        """Restore backend state from storage.

        Args:
            state_dict: State dictionary from serialize_state()
        """
        from src.ui.web.session_state import SessionState

        state = SessionState.from_dict(state_dict)

        # Restore session ID (critical for Redis settings and filesystem)
        # This ensures we reconnect to the same Redis keys after page refresh
        if state.session_id:
            # Update sandboxed filesystem to use restored session ID
            self.sandboxed_fs.user_id = state.session_id

            # Recreate settings backend with restored session ID
            # This ensures we access the same settings in Redis
            from src.settings import SettingsManager
            from src.settings_backend import create_settings_backend
            settings_backend = create_settings_backend(session_id=state.session_id)
            self.settings_manager = SettingsManager(backend=settings_backend)

        # Restore program
        self._restore_program(state.program_lines)

        # Restore runtime
        if state.runtime_state:
            self._restore_runtime(state.runtime_state)

        # Recreate interpreter with restored runtime
        self._recreate_interpreter()

        # Restore execution state
        self.running = state.running
        self.paused = state.paused
        self.output_text = state.output_text
        self.current_file = state.current_file
        self.recent_files = state.recent_files
        self.last_save_content = state.last_save_content

        # Restore configuration
        self.max_recent_files = state.max_recent_files
        self.auto_save_enabled = state.auto_save_enabled
        self.auto_save_interval = state.auto_save_interval

        # Restore find/replace
        self.last_find_text = state.last_find_text
        self.last_find_position = state.last_find_position
        self.last_case_sensitive = state.last_case_sensitive

        # Restore editor state (will be set after UI is built)
        self._pending_editor_content = state.editor_content
        self.last_edited_line_index = state.last_edited_line_index
        self.last_edited_line_text = state.last_edited_line_text

    def _sync_program_from_editor(self) -> None:
        """Sync program manager from editor content.

        This ensures the program manager reflects the current editor content,
        even if the user hasn't run the program yet. Important for serialization.
        """
        if not self.editor:
            return  # No editor yet

        try:
            # Get current editor content
            editor_content = self.editor.value or ""

            # Clear existing program
            self.program.clear()

            # Parse each line from editor
            for line in editor_content.split('\n'):
                line = line.strip()
                if not line:
                    continue  # Skip blank lines

                # Try to parse as a numbered line (e.g., "10 PRINT")
                # Match lines that start with a line number
                import re
                match = re.match(r'^(\d+)\s+(.*)$', line)
                if match:
                    line_num = int(match.group(1))
                    rest = match.group(2).strip()
                    if rest:  # Only add if there's content after line number
                        self.program.add_line(line_num, line)
        except Exception as e:
            # If sync fails, write to stderr but don't crash - we'll serialize what we have.
            # Using sys.stderr.write directly to ensure output even if logging fails.
            sys.stderr.write(f"Warning: Failed to sync program from editor: {e}\n")
            sys.stderr.flush()

    def _serialize_program(self) -> Dict[int, str]:
        """Serialize program lines to dict.

        Returns:
            Dict[int, str]: Mapping of line_number -> source_text
        """
        result = {}
        # get_lines() returns List[Tuple[int, str]]
        for line_number, line_text in self.program.get_lines():
            result[line_number] = line_text
        return result

    def _restore_program(self, program_lines: Dict[int, str]) -> None:
        """Restore program from serialized lines.

        Args:
            program_lines: Dict of line_number -> source_text
        """
        # Clear existing program
        self.program.clear()

        # Add each line
        for line_num in sorted(program_lines.keys()):
            source_text = program_lines[line_num]
            self.program.add_line(line_num, source_text)

    def _serialize_runtime(self) -> dict:
        """Serialize runtime state.

        Uses pickle for complex objects:
        - statement_table: Contains StatementTable with AST statement nodes (pickled)
        - user_functions: Contains DefFnStatementNode AST nodes (pickled)
        Other fields use direct serialization (dicts, lists, primitives).

        Returns:
            dict: Serialized runtime state
        """
        import pickle

        # Close open files first
        self._close_all_files()

        return {
            'variables': self.runtime._variables,
            'arrays': self.runtime._arrays,
            'variable_case_variants': self.runtime._variable_case_variants,
            'array_element_tracking': self.runtime._array_element_tracking,
            'common_vars': self.runtime.common_vars,
            'array_base': self.runtime.array_base,
            'option_base_executed': self.runtime.option_base_executed,
            'pc': {'line': self.runtime.pc.line_num, 'stmt': self.runtime.pc.stmt_offset} if self.runtime.pc else None,
            'npc': {'line': self.runtime.npc.line_num, 'stmt': self.runtime.npc.stmt_offset} if self.runtime.npc else None,
            'statement_table': pickle.dumps(self.runtime.statement_table).hex(),
            # Note: halted flag removed - PC is now immutable and indicates running state
            'execution_stack': self.runtime.execution_stack,
            'for_loop_vars': self.runtime.for_loop_vars,
            'line_text_map': self.runtime.line_text_map,
            'data_items': self.runtime.data_items,
            'data_pointer': self.runtime.data_pointer,
            'data_line_map': self.runtime.data_line_map,
            'user_functions': pickle.dumps(self.runtime.user_functions).hex(),
            'field_buffers': self.runtime.field_buffers,
            'error_handler': self.runtime.error_handler,
            'error_handler_is_gosub': self.runtime.error_handler_is_gosub,
            'rnd_last': self.runtime.rnd_last,
            # Note: stopped flag removed - PC.stop_reason now indicates stop state (display only)
            'breakpoints': [{'line': bp.line_num, 'stmt': bp.stmt_offset} for bp in self.runtime.breakpoints],
            'break_requested': self.runtime.break_requested,
            'trace_on': self.runtime.trace_on,
            'trace_detail': self.runtime.trace_detail,
        }

    def _restore_runtime(self, state: dict) -> None:
        """Restore runtime from serialized state.

        Args:
            state: Serialized runtime state from _serialize_runtime()
        """
        import pickle
        from src.pc import PC

        self.runtime._variables = state['variables']
        self.runtime._arrays = state['arrays']
        self.runtime._variable_case_variants = state['variable_case_variants']
        self.runtime._array_element_tracking = state['array_element_tracking']
        self.runtime.common_vars = state['common_vars']
        self.runtime.array_base = state['array_base']
        self.runtime.option_base_executed = state['option_base_executed']
        self.runtime.pc = PC(state['pc']['line'], state['pc']['stmt']) if state['pc'] else PC.halted_pc()
        self.runtime.npc = PC(state['npc']['line'], state['npc']['stmt']) if state['npc'] else None
        self.runtime.statement_table = pickle.loads(bytes.fromhex(state['statement_table']))
        # Note: halted flag removed - PC is now immutable and indicates running state
        # Ignore 'halted' key if present (backwards compatibility with old saved states)
        self.runtime.execution_stack = state['execution_stack']
        self.runtime.for_loop_vars = state['for_loop_vars']
        self.runtime.line_text_map = state['line_text_map']
        self.runtime.data_items = state['data_items']
        self.runtime.data_pointer = state['data_pointer']
        self.runtime.data_line_map = state['data_line_map']
        self.runtime.user_functions = pickle.loads(bytes.fromhex(state['user_functions']))
        self.runtime.field_buffers = state['field_buffers']
        self.runtime.error_handler = state['error_handler']
        self.runtime.error_handler_is_gosub = state['error_handler_is_gosub']
        self.runtime.rnd_last = state['rnd_last']
        # Note: stopped flag removed - PC.stop_reason now indicates stop state (display only)
        # Ignore 'stopped' key if present (backwards compatibility with old saved states)
        self.runtime.breakpoints = {PC(bp['line'], bp['stmt']) for bp in state['breakpoints']}
        self.runtime.break_requested = state['break_requested']
        self.runtime.trace_on = state['trace_on']
        self.runtime.trace_detail = state['trace_detail']

    def _close_all_files(self) -> None:
        """Close all open file handles before serialization."""
        if hasattr(self.runtime, 'files'):
            open_file_numbers = list(self.runtime.files.keys())
            for file_num in open_file_numbers:
                try:
                    self.runtime.files[file_num].close()
                except Exception:
                    pass  # Ignore errors closing files
            self.runtime.files.clear()

    def _recreate_interpreter(self) -> None:
        """Recreate interpreter instance with restored runtime."""
        from src.interpreter import Interpreter
        from src.resource_limits import create_local_limits
        from src.file_io import SandboxedFileIO

        # Create IO handler for immediate mode
        immediate_io = SimpleWebIOHandler(self._append_output, self._get_input)
        sandboxed_file_io = SandboxedFileIO(self)

        # Recreate interpreter with restored runtime
        self.interpreter = Interpreter(
            self.runtime,
            immediate_io,
            limits=create_local_limits(),
            file_io=sandboxed_file_io,
            filesystem_provider=self.sandboxed_fs
        )

    # =========================================================================
    # UIBackend Interface
    # =========================================================================

    def start(self):
        """NOT IMPLEMENTED - raises NotImplementedError.

        Web backend cannot be started per-instance. Use start_web_ui() module
        function instead, which creates backend instances per user session.

        Raises:
            NotImplementedError: Always raised
        """
        raise NotImplementedError("Web backend uses start_web_ui() function, not backend.start()")

    def stop(self):
        """Stop the web UI server and shut down NiceGUI app.

        Calls app.shutdown() to terminate the NiceGUI application.
        """
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

    # Initialize usage tracking
    import os
    import json
    config_path = os.path.join(os.path.dirname(__file__), '../../..', 'config/multiuser.json')
    if os.path.exists(config_path):
        try:
            with open(config_path) as f:
                multiuser_config = json.load(f)

            # Replace environment variables in config
            config_str = json.dumps(multiuser_config)
            for env_var in ['MYSQL_HOST', 'MYSQL_USER', 'MYSQL_PASSWORD']:
                config_str = config_str.replace(f'${{{env_var}}}', os.environ.get(env_var, ''))
            multiuser_config = json.loads(config_str)

            # Initialize usage tracker
            usage_config = multiuser_config.get('usage_tracking', {})
            if usage_config.get('enabled'):
                init_usage_tracker(usage_config)
                sys.stderr.write("Usage tracking enabled\n")
                sys.stderr.flush()
            else:
                sys.stderr.write("Usage tracking disabled\n")
                sys.stderr.flush()
        except Exception as e:
            sys.stderr.write(f"Warning: Failed to initialize usage tracking: {e}\n")
            sys.stderr.flush()

    # Redirect root to IDE
    @ui.page('/')
    def landing():
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url='/ide')

    # Serve IDE on /ide path
    @ui.page('/ide', viewport='width=device-width, initial-scale=1.0')
    def main_page():
        """Create or restore backend instance for each client."""
        import os
        from src.editing.manager import ProgramManager
        from src.ast_nodes import TypeInfo

        # Try to restore existing session state
        saved_state = app.storage.client.get('session_state')

        # Initialize DEF type map with all letters as SINGLE precision
        def_type_map = {}
        for letter in 'abcdefghijklmnopqrstuvwxyz':
            def_type_map[letter] = TypeInfo.SINGLE

        # Create new program manager for this client
        program_manager = ProgramManager(def_type_map)

        # Create new backend instance
        backend = NiceGUIBackend(None, program_manager)

        # Track IDE session start
        tracker = get_usage_tracker()
        if tracker:
            try:
                from nicegui import context
                session_id = app.storage.client.id
                user_agent = context.client.request.headers.get('user-agent') if context.client.request else None
                ip = context.client.request.client.host if context.client.request and context.client.request.client else None
                tracker.start_ide_session(session_id, user_agent, ip)
            except Exception as e:
                sys.stderr.write(f"Warning: Failed to track session start: {e}\n")
                sys.stderr.flush()

        # Restore state if available
        if saved_state:
            try:
                backend.restore_state(saved_state)
            except Exception as e:
                sys.stderr.write(f"Warning: Failed to restore session state: {e}\n")
                sys.stderr.flush()
                # Continue with fresh state

        # Build the UI for this client
        backend.build_ui()

        # Set up periodic state saving (every 5 seconds while connected)
        def save_state_periodic():
            try:
                app.storage.client['session_state'] = backend.serialize_state()
            except Exception as e:
                sys.stderr.write(f"Warning: Failed to save session state: {e}\n")
                sys.stderr.flush()

        # Save state periodically (errors are caught and logged, won't crash the UI)
        ui.timer(5.0, save_state_periodic)

        # Save state on disconnect
        def save_on_disconnect():
            try:
                app.storage.client['session_state'] = backend.serialize_state()
            except Exception as e:
                sys.stderr.write(f"Warning: Failed to save final session state: {e}\n")
                sys.stderr.flush()

            # Track session end
            tracker = get_usage_tracker()
            if tracker:
                try:
                    tracker.end_ide_session(app.storage.client.id)
                except Exception as e:
                    sys.stderr.write(f"Warning: Failed to track session end: {e}\n")
                    sys.stderr.flush()

        ui.context.client.on_disconnect(save_on_disconnect)

    # Health check endpoint for Kubernetes liveness/readiness probes
    @app.get('/health')
    def health_check():
        """Simple health check endpoint for container orchestration.

        Returns 200 OK if the server is running and able to respond.
        Used by Docker HEALTHCHECK and Kubernetes probes.
        """
        return {'status': 'healthy', 'version': VERSION}

    # Landing page visit tracking endpoint
    @app.post('/api/track-visit')
    def track_visit(page: str = '/', referrer: str = None, userAgent: str = None, sessionId: str = None):
        """Track landing page visit."""
        tracker = get_usage_tracker()
        if tracker:
            try:
                # Get IP from request (FastAPI context)
                from starlette.requests import Request
                from fastapi import Request as FastAPIRequest
                # Note: IP extraction handled in tracker, pass None for now
                tracker.track_page_visit(page, referrer, userAgent, None, sessionId)
            except Exception as e:
                sys.stderr.write(f"Warning: Failed to track page visit: {e}\n")
                sys.stderr.flush()
        return {'status': 'ok'}

    # Check if Redis is configured
    import os
    redis_url = os.environ.get('NICEGUI_REDIS_URL')
    if redis_url:
        sys.stderr.write(f"Redis storage enabled: {redis_url}\n")
        sys.stderr.write("Session state will be shared across load-balanced instances\n\n")
    else:
        sys.stderr.write("In-memory storage (default): Session state per process only\n")
        sys.stderr.write("Set NICEGUI_REDIS_URL to enable Redis storage for session persistence\n\n")
    sys.stderr.flush()

    # Start NiceGUI server
    ui.run(
        title='MBASIC 5.21 - Web IDE',
        port=port,
        storage_secret=os.environ.get('MBASIC_STORAGE_SECRET', 'dev-default-change-in-production'),
        reload=False,
        show=True
    )
