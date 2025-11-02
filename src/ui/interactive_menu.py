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
                ('New            ^N', '_new_program'),
                ('Open...        ^L', '_load_program'),
                ('Recent Files...', '_show_recent_files'),
                ('Save           ^S', '_save_program'),
                ('Save As...', '_save_as_program'),
                ('---', None),  # Separator
                ('Quit           ^Q', 'quit'),
            ],
            'Edit': [
                ('Delete Line    ^D', '_delete_current_line'),
                ('Insert Line    ^I', '_insert_line'),
                ('Renumber...    ^E', '_renumber_program'),
                ('---', None),
                ('Toggle Breakpoint ^B', '_toggle_breakpoint_current_line'),
                ('Clear All Breakpoints', '_clear_all_breakpoints'),
            ],
            'Run': [
                ('Run Program    ^R', '_run_program'),
                ('Continue       ^G', '_debug_continue'),
                ('Step Line      ^L', '_debug_step_line'),
                ('Step Statement ^T', '_debug_step_statement'),
                ('Stop           ^X', '_debug_stop'),
                ('---', None),
                ('Clear Output   ^Y', '_clear_output'),
            ],
            'Debug': [
                ('Variables Window ^W', '_toggle_variables_window'),
                ('Execution Stack  ^K', '_toggle_stack_window'),
            ],
            'Help': [
                ('Help           ^F', '_show_help'),
                ('Settings       ^P', '_show_settings'),
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

    def _show_dropdown(self, base_widget=None):
        """Show dropdown menu for current menu.

        Args:
            base_widget: The widget to overlay on. If None, uses parent_ui.loop.widget
        """
        menu_name = self.menu_names[self.current_menu_index]
        items = self.menus[menu_name]

        # Build menu text with proper spacing for shortcuts
        menu_lines = []
        menu_width = 24  # Width for the menu content

        for i, (label, callback) in enumerate(items):
            if label == '---':
                menu_lines.append("─" * (menu_width - 2))
            else:
                prefix = '>' if i == self.current_item_index else ' '

                # Split label and shortcut (if present)
                # Format: "Command      ^K" where shortcut is right-aligned
                if '^' in label:
                    # Has shortcut - split on last occurrence of space before ^
                    parts = label.rsplit(' ', 1)
                    if len(parts) == 2 and parts[1].startswith('^'):
                        cmd = parts[0]
                        shortcut = parts[1]
                        # Right-align shortcut
                        spacing = menu_width - 4 - len(cmd) - len(shortcut)
                        menu_lines.append(f"{prefix} {cmd}{' ' * spacing}{shortcut}")
                    else:
                        # Couldn't parse, just use as-is
                        menu_lines.append(f"{prefix} {label}")
                else:
                    # No shortcut
                    menu_lines.append(f"{prefix} {label}")

        menu_text = '\n'.join(menu_lines)

        # Create dropdown widget with explicit black background
        text_widget = urwid.Text(menu_text)
        fill = urwid.Filler(text_widget, valign='top')
        box = urwid.LineBox(fill)

        # Position dropdown below menu bar
        # Calculate x position based on which menu
        x_offset = sum(len(self.menu_names[i]) + 3 for i in range(self.current_menu_index)) + 2

        # Use provided base widget or current widget
        if base_widget is None:
            base_widget = self.parent_ui.loop.widget

        # Wrap base widget in AttrMap to ensure black background everywhere
        # This prevents urwid from using default colors (39;49) which may be white
        base_with_bg = urwid.AttrMap(base_widget, 'body')

        # Wrap entire dropdown in AttrMap with body style (white on black)
        dropdown_widget = urwid.AttrMap(box, 'body')

        overlay = urwid.Overlay(
            dropdown_widget,
            base_with_bg,
            align='left',
            width=menu_width + 2,  # Menu width + border
            valign='top',
            height='pack',
            left=x_offset,
            top=1,  # Below menu bar
            min_width=menu_width + 2,
            min_height=1
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
