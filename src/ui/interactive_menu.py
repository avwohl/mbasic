"""Interactive menu bar for curses UI using urwid."""

import urwid


class InteractiveMenuBar(urwid.WidgetWrap):
    """Interactive menu bar with keyboard navigation.

    Features:
    - Ctrl+U activates the menu bar
    - Left/Right arrows navigate between menus
    - Up/Down arrows navigate within menu
    - Enter selects an item
    - ESC closes menu
    """

    def __init__(self, parent_ui):
        """Initialize the menu bar.

        Args:
            parent_ui: Reference to parent CursesUI for callbacks
        """
        self.parent_ui = parent_ui
        self.active = False
        self.current_menu_index = 0
        self.current_item_index = 0

        # Define menu structure: {menu_name: [(label, callback_name), ...]}
        self.menus = {
            'File': [
                ('New', '_new_program'),
                ('Open...', '_load_program'),
                ('Recent Files...', '_show_recent_files'),
                ('Save', '_save_program'),
                ('Save As...', '_save_as_program'),
                ('---', None),  # Separator
                ('Quit', 'quit'),
            ],
            'Edit': [
                ('Delete Line', '_delete_current_line'),
                ('Insert Line', '_insert_line'),
                ('Renumber...', '_renumber_program'),
                ('---', None),
                ('Toggle Breakpoint', '_toggle_breakpoint_current_line'),
                ('Clear All Breakpoints', '_clear_all_breakpoints'),
            ],
            'Run': [
                ('Run Program', '_run_program'),
                ('Continue', '_debug_continue'),
                ('Step Line', '_debug_step_line'),
                ('Step Statement', '_debug_step_statement'),
                ('Stop', '_debug_stop'),
                ('---', None),
                ('Clear Output', '_clear_output'),
            ],
            'Debug': [
                ('Variables Window', '_toggle_variables_window'),
                ('Execution Stack', '_toggle_stack_window'),
            ],
            'Help': [
                ('Help', '_show_help'),
                ('Settings', '_show_settings'),
            ],
        }

        self.menu_names = list(self.menus.keys())

        # Create the menu bar text (wrap='clip' prevents wrapping)
        self.menu_text = urwid.Text(self._get_menu_bar_text(), align='left', wrap='clip')
        super().__init__(urwid.AttrMap(self.menu_text, 'header'))

    def _get_menu_bar_text(self):
        """Get the menu bar text with highlighting."""
        if not self.active:
            # Inactive - just show menu names
            return '  ' + '   '.join(self.menu_names) + '  '
        else:
            # Active - highlight current menu
            parts = []
            for i, name in enumerate(self.menu_names):
                if i == self.current_menu_index:
                    parts.append(f'[{name}]')  # Highlighted
                else:
                    parts.append(f' {name} ')
            return ' ' + '  '.join(parts)

    def activate(self):
        """Activate the menu bar (Ctrl+U pressed)."""
        self.active = True
        self.current_menu_index = 0
        self.current_item_index = 0
        self._update_display()
        return self._show_dropdown()

    def deactivate(self):
        """Deactivate the menu bar (ESC pressed)."""
        self.active = False
        self._update_display()

    def _update_display(self):
        """Update the menu bar display."""
        self.menu_text.set_text(self._get_menu_bar_text())

    def _show_dropdown(self):
        """Show dropdown menu for current menu."""
        menu_name = self.menu_names[self.current_menu_index]
        items = self.menus[menu_name]

        # Build menu text
        menu_lines = [f" {menu_name} "]
        menu_lines.append(" " + "─" * (len(menu_name) + 2))

        for i, (label, callback) in enumerate(items):
            if label == '---':
                menu_lines.append(" " + "─" * 20)
            else:
                prefix = '>' if i == self.current_item_index else ' '
                menu_lines.append(f" {prefix} {label}")

        menu_text = '\n'.join(menu_lines)

        # Create dropdown widget
        text_widget = urwid.Text(menu_text)
        fill = urwid.Filler(text_widget, valign='top')
        box = urwid.LineBox(fill)

        # Position dropdown below menu bar
        # Calculate x position based on which menu
        x_offset = sum(len(self.menu_names[i]) + 3 for i in range(self.current_menu_index)) + 2

        overlay = urwid.Overlay(
            urwid.AttrMap(box, 'body'),
            self.parent_ui.loop.widget,
            align='left',
            width=('relative', 30),
            valign='top',
            height='pack',
            left=x_offset,
            top=2  # Below menu bar and toolbar
        )

        return overlay

    def handle_key(self, key):
        """Handle keyboard input when menu is active.

        Returns:
            'close' to close menu and return to main UI
            'refresh' to redraw dropdown
            None to continue
        """
        if key == 'esc':
            self.deactivate()
            return 'close'

        elif key == 'left':
            # Navigate to previous menu
            self.current_menu_index = (self.current_menu_index - 1) % len(self.menu_names)
            self.current_item_index = 0
            return 'refresh'

        elif key == 'right':
            # Navigate to next menu
            self.current_menu_index = (self.current_menu_index + 1) % len(self.menu_names)
            self.current_item_index = 0
            return 'refresh'

        elif key == 'up':
            # Navigate to previous item (skip separators)
            menu_name = self.menu_names[self.current_menu_index]
            items = self.menus[menu_name]

            while True:
                self.current_item_index = (self.current_item_index - 1) % len(items)
                if items[self.current_item_index][0] != '---':
                    break
            return 'refresh'

        elif key == 'down':
            # Navigate to next item (skip separators)
            menu_name = self.menu_names[self.current_menu_index]
            items = self.menus[menu_name]

            while True:
                self.current_item_index = (self.current_item_index + 1) % len(items)
                if items[self.current_item_index][0] != '---':
                    break
            return 'refresh'

        elif key == 'enter':
            # Select current item
            menu_name = self.menu_names[self.current_menu_index]
            items = self.menus[menu_name]
            label, callback_name = items[self.current_item_index]

            if callback_name:
                # Execute callback
                if callback_name == 'quit':
                    raise urwid.ExitMainLoop()
                else:
                    callback = getattr(self.parent_ui, callback_name, None)
                    if callback:
                        callback()

            self.deactivate()
            return 'close'

        return None
