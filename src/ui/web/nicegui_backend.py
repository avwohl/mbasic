"""NiceGUI web backend for MBASIC.

Provides a modern web-based UI for the MBASIC interpreter using NiceGUI.
"""

import re
from nicegui import ui, app
from pathlib import Path
from ..base import UIBackend


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

        # Execution state
        self.running = False
        self.paused = False
        self.breakpoints = set()  # Line numbers with breakpoints

        # UI elements (created in build_ui())
        self.editor = None
        self.output = None
        self.status_label = None
        self.program_display = None

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

            # Main content area - split pane
            with ui.splitter(value=50).classes('w-full h-[600px]') as splitter:

                # Left pane - Editor
                with splitter.before:
                    ui.label('Program Editor').classes('text-lg font-bold p-2')

                    # Program line entry
                    with ui.row().classes('w-full p-2 gap-2'):
                        self.editor = ui.textarea(
                            placeholder='Enter BASIC line (e.g., 10 PRINT "Hello")',
                            on_change=lambda: None
                        ).classes('flex-grow').mark('editor')

                        ui.button('Add Line', on_click=self._add_line, icon='add').mark('btn_add_line')

                    # Program listing
                    ui.label('Program:').classes('font-bold px-2')
                    self.program_display = ui.textarea(
                        value='',
                        placeholder='No program loaded'
                    ).classes('w-full flex-grow font-mono').props('readonly').mark('program_display')

                # Right pane - Output
                with splitter.after:
                    ui.label('Output').classes('text-lg font-bold p-2')
                    self.output = ui.textarea(
                        value='MBASIC 5.21 Web IDE\nReady\n',
                        placeholder='Program output will appear here'
                    ).classes('w-full flex-grow font-mono bg-black text-green-400').props('readonly').mark('output')

                    with ui.row().classes('w-full p-2'):
                        ui.button('Clear Output', on_click=self._clear_output, icon='clear').mark('btn_clear_output')

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
        self.program.clear()
        self.program_lines = []
        self._update_program_display()
        self.editor.value = ''
        self._set_status('New program')

    def _menu_open(self):
        """File > Open - Load program from file."""
        # TODO: Implement file picker
        self._set_status('Open not yet implemented')
        ui.notify('File picker coming soon', type='info')

    def _menu_save(self):
        """File > Save - Save current program."""
        # TODO: Implement file save
        self._set_status('Save not yet implemented')
        ui.notify('Save coming soon', type='info')

    def _menu_save_as(self):
        """File > Save As - Save with new filename."""
        # TODO: Implement save as
        self._set_status('Save As not yet implemented')
        ui.notify('Save As coming soon', type='info')

    def _menu_exit(self):
        """File > Exit - Quit application."""
        app.shutdown()

    def _menu_run(self):
        """Run > Run Program - Execute program."""
        # TODO: Implement program execution
        self._set_status('Run not yet implemented')
        ui.notify('Execution coming soon', type='info')

    def _menu_stop(self):
        """Run > Stop - Stop execution."""
        self._set_status('Stop not yet implemented')

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

    def _add_line(self):
        """Add line from editor to program."""
        line_text = self.editor.value.strip()
        if not line_text:
            return

        try:
            # Parse line number from text
            match = re.match(r'^(\d+)(?:\s|$)', line_text)
            if not match:
                self._set_status('Error: Line must start with line number')
                ui.notify('Line must start with line number', type='negative')
                return

            line_num = int(match.group(1))

            # Add line to program
            success, error = self.program.add_line(line_num, line_text)

            if not success:
                self._set_status(f'Error: {error}')
                ui.notify(f'Error: {error}', type='negative')
                return

            # Update display
            self._update_program_display()

            # Clear editor
            self.editor.value = ''

            self._set_status(f'Added: {line_text}')

        except Exception as e:
            ui.notify(f'Error: {e}', type='negative')
            self._set_status(f'Error: {e}')

    def _update_program_display(self):
        """Update program listing display."""
        lines = self.program.get_lines()
        # Format as "linenum text"
        formatted_lines = [line_text for line_num, line_text in lines]
        self.program_display.value = '\n'.join(formatted_lines)

    def _clear_output(self):
        """Clear output pane."""
        self.output.value = 'MBASIC 5.21 Web IDE\nReady\n'
        self._set_status('Output cleared')

    def _append_output(self, text):
        """Append text to output pane."""
        self.output.value += text + '\n'

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
