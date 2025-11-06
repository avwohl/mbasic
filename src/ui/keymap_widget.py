"""Keymap display widget showing all keyboard shortcuts."""

import urwid
from .keybindings import KEYBINDINGS_BY_CATEGORY


def _format_key_display(key_str):
    """Convert Ctrl+ notation to ^ notation for consistency.

    Args:
        key_str: Key string like "Ctrl+F" or "^F"

    Returns:
        Formatted string using ^ notation like "^F"
    """
    if key_str.startswith('Ctrl+'):
        # Convert "Ctrl+F" to "^F"
        return '^' + key_str[5:]
    elif key_str.startswith('Shift+Ctrl+'):
        # Convert "Shift+Ctrl+V" to "Shift+^V"
        return 'Shift+^' + key_str[11:]
    return key_str


class KeymapWidget(urwid.WidgetWrap):
    """Display all keyboard shortcuts in a scrollable window."""

    def __init__(self, on_close):
        """Initialize the keymap display.

        Args:
            on_close: Callback function when user closes the window
        """
        self.on_close = on_close

        # Build the keymap content with instructions at the top
        content = []

        # Add instructions as first item
        instructions = urwid.AttrMap(
            urwid.Text("↑/↓ scroll  ESC/Q close", align='center'),
            'help_text'
        )
        content.append(instructions)

        # Add keymap content
        content.extend(self._build_keymap_content())

        # Create scrollable listbox
        self.listwalker = urwid.SimpleFocusListWalker(content)
        self.listbox = urwid.ListBox(self.listwalker)

        # Wrap in line box with black background
        linebox = urwid.LineBox(
            urwid.AttrMap(self.listbox, 'body'),
            title=None
        )

        super().__init__(urwid.AttrMap(linebox, 'body'))

    def _build_keymap_content(self):
        """Build the keymap content from keybindings.

        Returns:
            List of urwid widgets for display
        """
        content = []

        for i, (category, bindings) in enumerate(KEYBINDINGS_BY_CATEGORY.items()):
            # Add blank line before category header (except for the first one)
            if i > 0:
                content.append(urwid.Divider())

            # Add category header
            content.append(
                urwid.AttrMap(
                    urwid.Text(('category', category)),
                    'category'
                )
            )

            # Add keybindings in this category
            for key, description in bindings:
                # Format: "  Key         Description"
                # Use 16 chars for key column for alignment
                # Convert Ctrl+ to ^ notation for consistency
                formatted_key = _format_key_display(key)
                line = f"  {formatted_key:<16} {description}"
                content.append(
                    urwid.Text(line)
                )

        return content

    def keypress(self, size, key):
        """Handle key presses."""
        # ESC or Q closes the window
        if key in ('esc', 'q', 'Q'):
            self.on_close()
            return None

        # Pass other keys to listbox for scrolling
        return super().keypress(size, key)
