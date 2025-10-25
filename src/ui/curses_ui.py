"""Curses UI backend using urwid.

This module provides a full-screen terminal UI for MBASIC using the urwid library.
It provides an editor, output window, and menu system.
"""

import urwid
from .base import UIBackend
from runtime import Runtime
from interpreter import Interpreter
from lexer import Lexer
from parser import Parser


class TopLeftBox(urwid.WidgetWrap):
    """Custom box widget that only draws top and left borders.

    Unlike LineBox, this doesn't reserve space for bottom/right borders,
    allowing content to use the full available space.
    """

    def __init__(self, original_widget, title=''):
        """Create a box with only top and left borders.

        Args:
            original_widget: The widget to wrap
            title: Title to display in top border
        """
        self.title = title
        self.original_widget = original_widget

        # Create the top border line with title
        if title:
            # Title in the top border: "┌─ Title ────────"
            title_text = urwid.Text(f'┌─ {title} ', wrap='clip')
            fill_text = urwid.Text('─' * 200, wrap='clip')
            top_border = urwid.Columns([
                ('pack', title_text),
                fill_text
            ], dividechars=0)
        else:
            top_border = urwid.Text('┌' + '─' * 200, wrap='clip')

        # Use SolidFill with │ for the left border (fills all vertical space)
        left_border = urwid.SolidFill('│')

        content_with_border = urwid.Columns([
            ('fixed', 1, left_border),
            original_widget
        ], dividechars=0)

        # Set focus to the content (column 1, not the border)
        content_with_border.focus_position = 1

        # Stack top border and content
        pile = urwid.Pile([
            ('pack', top_border),
            content_with_border
        ])

        # Set focus to the content area (not the top border)
        pile.focus_position = 1

        super().__init__(pile)


class OutputLineWidget(urwid.WidgetWrap):
    """Selectable text widget for output lines with cursor indicator on first char."""

    def __init__(self, text):
        """Initialize output line widget.

        Args:
            text: The line text to display
        """
        self.text = text
        self._text_widget = urwid.Text("")
        super().__init__(self._text_widget)
        self._update_display(False)

    def selectable(self):
        """Make this widget selectable for focus."""
        return True

    def keypress(self, size, key):
        """Handle keypresses - just return them to allow navigation."""
        return key

    def _update_display(self, has_focus):
        """Update display based on focus state.

        Args:
            has_focus: True if this widget has focus
        """
        if has_focus:
            # Show green background on first character only
            if self.text and len(self.text) > 0:
                first_char = self.text[0]
                rest = self.text[1:] if len(self.text) > 1 else ""
                markup = [('output_focus', first_char), rest]
                self._text_widget.set_text(markup)
            else:
                # Empty line - show a visible cursor character
                markup = [('output_focus', ' ')]
                self._text_widget.set_text(markup)
        else:
            # No focus, show plain text
            self._text_widget.set_text(self.text)

    def render(self, size, focus=False):
        """Render with focus highlighting on first character.

        Args:
            size: Rendering size
            focus: True if this widget has focus

        Returns:
            Canvas for rendering
        """
        self._update_display(focus)
        return super().render(size, focus)


class ProgramEditorWidget(urwid.WidgetWrap):
    """3-column program editor widget for BASIC programs.

    Columns:
    1. Status (1 char): ● for breakpoint, ? for error, space otherwise
    2. Line number (5 chars): auto-numbered line numbers
    3. Program text (rest): BASIC code
    """

    def __init__(self):
        """Initialize the program editor."""
        # Program lines storage: {line_num: code_text}
        self.lines = {}
        # Breakpoints: set of line numbers
        self.breakpoints = set()
        # Errors: {line_num: error_message}
        self.errors = {}

        # Auto-numbering settings (defaults)
        self.auto_number_start = 10
        self.auto_number_increment = 10
        self.auto_number_enabled = True

        # Load config file if it exists
        self._load_config()

        self.next_auto_line_num = self.auto_number_start

        # Current line being edited
        self.current_line_num = None

        # Create the display widget
        self.text_widget = urwid.Text("", wrap='clip')

        # Use Edit with allow_tab=False to improve performance
        # and align='left' for faster rendering
        self.edit_widget = urwid.Edit(
            "", "",
            multiline=True,
            align='left',
            wrap='clip',
            allow_tab=False
        )

        # Use a pile to allow switching between display and edit modes
        self.pile = urwid.Pile([self.edit_widget])

        # Set focus to the edit widget
        self.pile.focus_position = 0

        super().__init__(self.pile)

        # Initialize with empty program
        self._update_display()

    def keypress(self, size, key):
        """Handle key presses for column-aware editing and auto-numbering.

        Format: "SNNNNN CODE"
        - Column 0: Status (●, ?, space) - read-only
        - Columns 1-5: Line number (5 chars) - editable
        - Column 6: Space
        - Columns 7+: Code - editable
        """
        # Get current cursor position
        current_text = self.edit_widget.get_edit_text()
        cursor_pos = self.edit_widget.edit_pos

        # Find which line we're on and position within that line
        text_before_cursor = current_text[:cursor_pos]
        line_num = text_before_cursor.count('\n')
        lines = current_text.split('\n')

        if line_num < len(lines):
            line_start_pos = sum(len(lines[i]) + 1 for i in range(line_num))  # +1 for \n
            col_in_line = cursor_pos - line_start_pos
        else:
            col_in_line = 0

        # Check if pressing a control key or navigation key
        is_control_key = key.startswith('ctrl ') or key in ['tab', 'enter', 'esc']
        is_updown_arrow = key in ['up', 'down']  # Up/down move to different lines
        is_leftright_arrow = key in ['left', 'right']  # Left/right stay on same line
        is_arrow_key = is_updown_arrow or is_leftright_arrow
        is_other_nav_key = key in ['page up', 'page down', 'home', 'end']

        # Only right-justify when actually leaving line number area or on control/nav keys
        # Don't do expensive operations on left/right arrows or regular typing
        should_right_justify = False
        if is_control_key or is_updown_arrow or is_other_nav_key:
            # Control keys, up/down, page up/down, home/end: always right-justify
            should_right_justify = True
        elif is_leftright_arrow and 1 <= col_in_line <= 6:
            # Left/right arrows IN line number area: don't right-justify (performance)
            should_right_justify = False
        elif col_in_line == 6 and len(key) == 1 and key.isprintable():
            # Typing at separator column: right-justify before moving to code area
            should_right_justify = True

        if should_right_justify:
            # Right-justify the line number on the current line
            if line_num < len(lines) and len(lines[line_num]) >= 6:
                line = lines[line_num]
                # Extract line number area (columns 1-5)
                if len(line) >= 6:
                    status = line[0] if len(line) > 0 else ' '
                    line_num_text = line[1:6].strip()
                    rest_of_line = line[6:] if len(line) > 6 else ''

                    # Right-justify the line number
                    if line_num_text:
                        line_num_formatted = f"{line_num_text:>5}"
                        new_line = f"{status}{line_num_formatted}{rest_of_line}"

                        # Replace the line
                        lines[line_num] = new_line
                        new_text = '\n'.join(lines)
                        old_cursor = cursor_pos
                        self.edit_widget.set_edit_text(new_text)
                        self.edit_widget.set_edit_pos(old_cursor)

        # Sort lines if leaving line number area
        # Up/down arrows: sort (move to different line)
        # Left/right arrows: don't sort (stay on same line)
        # Other keys (page up/down, home, end, control keys): sort
        if 1 <= col_in_line <= 6 and (is_control_key or is_other_nav_key or is_updown_arrow):
            self._sort_and_position_line(lines, line_num, target_column=col_in_line)
            # After sorting, let the key work normally
            return super().keypress(size, key)

        # Handle backspace key specially to protect separator space
        if key == 'backspace':
            if line_num < len(lines):
                line = lines[line_num]
                line_start = sum(len(lines[i]) + 1 for i in range(line_num))

                # At column 7 (code start): move to column 6 but don't delete separator
                if col_in_line == 7:
                    new_cursor_pos = line_start + 6
                    self.edit_widget.set_edit_pos(new_cursor_pos)
                    return None

                # At column 6 (separator): delete rightmost digit of line number
                elif col_in_line == 6:
                    # Ensure line is at least 7 characters
                    if len(line) < 7:
                        line = line + ' ' * (7 - len(line))

                    status = line[0]
                    linenum_field = line[1:6]
                    rest = line[6:]

                    # Replace rightmost digit (position 4) with space
                    linenum_list = list(linenum_field)
                    linenum_list[4] = ' '
                    linenum_field = ''.join(linenum_list)

                    # Right-justify the line number
                    line_num_text = linenum_field.strip()
                    if line_num_text:
                        linenum_field = f"{line_num_text:>5}"
                    else:
                        linenum_field = '     '

                    # Rebuild line
                    new_line = status + linenum_field + rest
                    lines[line_num] = new_line
                    new_text = '\n'.join(lines)
                    self.edit_widget.set_edit_text(new_text)

                    # Move cursor to column 5 (rightmost position after right-justify)
                    new_cursor_pos = line_start + 5
                    self.edit_widget.set_edit_pos(new_cursor_pos)
                    return None

                # At columns 1-5 (line number): replace digit at cursor with space
                elif 1 <= col_in_line <= 5:
                    # Ensure line is at least 7 characters
                    if len(line) < 7:
                        line = line + ' ' * (7 - len(line))

                    status = line[0]
                    linenum_field = line[1:6]
                    rest = line[6:]

                    # Replace character at cursor position with space
                    linenum_list = list(linenum_field)
                    pos_in_field = col_in_line - 1
                    linenum_list[pos_in_field] = ' '
                    linenum_field = ''.join(linenum_list)

                    # Right-justify the line number
                    line_num_text = linenum_field.strip()
                    if line_num_text:
                        linenum_field = f"{line_num_text:>5}"
                    else:
                        linenum_field = '     '

                    # Rebuild line
                    new_line = status + linenum_field + rest
                    lines[line_num] = new_line
                    new_text = '\n'.join(lines)
                    self.edit_widget.set_edit_text(new_text)

                    # After right-justify, move cursor to rightmost position (col 5)
                    # This gives consistent behavior and user knows where they are
                    new_cursor_pos = line_start + 5
                    self.edit_widget.set_edit_pos(new_cursor_pos)
                    return None

        # Prevent typing in status column (column 0)
        if col_in_line < 1 and len(key) == 1 and key.isprintable():
            # Move cursor to line number column (column 1)
            new_cursor_pos = cursor_pos + (1 - col_in_line)
            self.edit_widget.set_edit_pos(new_cursor_pos)
            # Process the key at new position
            cursor_pos = new_cursor_pos
            col_in_line = 1

        # Handle input in line number column (1-5)
        if 1 <= col_in_line <= 5 and len(key) == 1 and key.isprintable():
            if not key.isdigit():
                # Move cursor to code area (column 7) and insert character there
                if line_num < len(lines):
                    line_start = sum(len(lines[i]) + 1 for i in range(line_num))
                    # Ensure line is at least 7 characters long
                    line = lines[line_num]
                    if len(line) < 7:
                        # Pad line to have at least 7 characters
                        line = line + ' ' * (7 - len(line))
                        lines[line_num] = line
                        current_text = '\n'.join(lines)
                        self.edit_widget.set_edit_text(current_text)
                    # Move cursor to column 7
                    new_cursor_pos = line_start + 7
                    self.edit_widget.set_edit_pos(new_cursor_pos)
                    # Now let the key be processed at the new position
                    return super().keypress(size, key)
            else:
                # Typing a digit in line number area
                if line_num < len(lines):
                    line_start = sum(len(lines[i]) + 1 for i in range(line_num))
                    line = lines[line_num]

                    # Ensure line is at least 7 characters
                    if len(line) < 7:
                        line = line + ' ' * (7 - len(line))

                    # Extract parts: status (0), linenum (1-5), space (6), code (7+)
                    status = line[0]
                    linenum_field = line[1:6]  # 5 characters
                    rest = line[6:]

                    # Find position within linenum_field (0-4)
                    pos_in_field = col_in_line - 1

                    # Check if at rightmost position (column 5, pos_in_field 4)
                    if pos_in_field == 4:
                        # At rightmost position: shift left and add new digit at end
                        linenum_list = list(linenum_field)
                        linenum_list.append(key)
                        # Keep only rightmost 5 characters (shift left if overflow)
                        linenum_list = linenum_list[-5:]
                        linenum_field = ''.join(linenum_list)
                        # Stay at same position (rightmost)
                        new_col = 5
                    else:
                        # Not at rightmost: overwrite at position
                        linenum_list = list(linenum_field)
                        if pos_in_field < len(linenum_list):
                            linenum_list[pos_in_field] = key
                        linenum_field = ''.join(linenum_list)
                        # Move cursor right after typed digit
                        new_col = min(col_in_line + 1, 5)

                    # Rebuild line
                    new_line = status + linenum_field + rest
                    lines[line_num] = new_line
                    new_text = '\n'.join(lines)

                    # Update text
                    self.edit_widget.set_edit_text(new_text)

                    # Position cursor
                    new_cursor_pos = line_start + new_col
                    self.edit_widget.set_edit_pos(new_cursor_pos)

                    return None

        # Handle input at column 6 (separator space)
        if col_in_line == 6 and len(key) == 1 and key.isprintable():
            if line_num < len(lines):
                line_start = sum(len(lines[i]) + 1 for i in range(line_num))
                line = lines[line_num]

                # Ensure line is at least 7 characters long
                if len(line) < 7:
                    line = line + ' ' * (7 - len(line))

                if key.isdigit():
                    # Digit at column 6: shift left and add new digit at end
                    status = line[0]
                    linenum_field = line[1:6]  # 5 characters
                    rest = line[6:]

                    # Shift left and add new digit at end (calculator style)
                    linenum_list = list(linenum_field)
                    linenum_list.append(key)
                    # Keep only rightmost 5 characters (shift left if overflow)
                    linenum_list = linenum_list[-5:]
                    linenum_field = ''.join(linenum_list)

                    # Rebuild line
                    new_line = status + linenum_field + rest
                    lines[line_num] = new_line
                    new_text = '\n'.join(lines)
                    self.edit_widget.set_edit_text(new_text)

                    # Keep cursor at column 6 (after the line number)
                    new_cursor_pos = line_start + 6
                    self.edit_widget.set_edit_pos(new_cursor_pos)
                    return None
                else:
                    # Non-digit at column 6: moving to code area - sort lines first
                    self._sort_and_position_line(lines, line_num)
                    # Now let the key be processed at the new position
                    return super().keypress(size, key)

        # Handle Enter key - commits line and moves to next with auto-numbering
        if key == 'enter' and self.auto_number_enabled:
            # Right-justify current line number before committing
            current_line_number = None
            if line_num < len(lines) and len(lines[line_num]) >= 6:
                line = lines[line_num]
                status = line[0] if len(line) > 0 else ' '
                line_num_text = line[1:6].strip()
                rest_of_line = line[6:] if len(line) > 6 else ''

                if line_num_text:
                    # Parse current line number
                    try:
                        current_line_number = int(line_num_text)
                    except:
                        pass

                    line_num_formatted = f"{line_num_text:>5}"
                    lines[line_num] = f"{status}{line_num_formatted}{rest_of_line}"
                    current_text = '\n'.join(lines)
                    self.edit_widget.set_edit_text(current_text)

            # Move to end of current line
            if line_num < len(lines):
                line_start = sum(len(lines[i]) + 1 for i in range(line_num))
                line_end = line_start + len(lines[line_num])
                self.edit_widget.set_edit_pos(line_end)

            # Calculate next auto-number based on current line + increment
            if current_line_number is not None:
                next_num = current_line_number + self.auto_number_increment
            else:
                next_num = self.next_auto_line_num

            # Get all existing line numbers from display
            existing_line_nums = set()
            for display_line in lines:
                if len(display_line) >= 6:
                    try:
                        existing_line_nums.add(int(display_line[1:6].strip()))
                    except:
                        pass

            # Find next available number that doesn't collide
            # Also check it's not above the next line in sequence
            sorted_line_nums = sorted(existing_line_nums)
            if current_line_number in sorted_line_nums:
                idx = sorted_line_nums.index(current_line_number)
                if idx + 1 < len(sorted_line_nums):
                    max_allowed = sorted_line_nums[idx + 1]
                else:
                    max_allowed = 99999
            else:
                max_allowed = 99999

            # Find next valid number
            while next_num in existing_line_nums or next_num >= max_allowed:
                next_num += self.auto_number_increment
                if next_num >= 99999:  # Avoid overflow
                    next_num = current_line_number + 1 if current_line_number else 10
                    break

            # Format new line: " NNNNN "
            new_line_prefix = f"\n {next_num:5d} "

            # Insert newline and prefix at end of current line
            current_text = self.edit_widget.get_edit_text()
            cursor_pos = self.edit_widget.edit_pos
            new_text = current_text[:cursor_pos] + new_line_prefix + current_text[cursor_pos:]
            self.edit_widget.set_edit_text(new_text)
            self.edit_widget.set_edit_pos(cursor_pos + len(new_line_prefix))

            # Update next_auto_line_num for next time
            self.next_auto_line_num = next_num + self.auto_number_increment

            return None

        # Let parent handle the key (allows arrows, backspace, etc.)
        return super().keypress(size, key)

    def _format_line(self, line_num, code_text):
        """Format a single program line with status, line number, and code.

        Args:
            line_num: Line number
            code_text: BASIC code text

        Returns:
            Formatted string: "SNNNNN CODE"
        """
        # Status column (1 char)
        if line_num in self.breakpoints:
            status = '●'
        elif line_num in self.errors:
            status = '?'
        else:
            status = ' '

        # Line number column (5 chars, right-aligned)
        line_num_str = f"{line_num:5d}"

        # Combine: status + line_num + space + code
        return f"{status}{line_num_str} {code_text}"

    def _update_display(self):
        """Update the text display with all program lines."""
        if not self.lines:
            # Empty program - start with first line number ready
            # Format: "SNNNNN " where S=status (1), NNNNN=line# (5), space (1)
            display_text = f" {self.next_auto_line_num:5d} "
            # Increment counter since we've used this number for display
            self.next_auto_line_num += self.auto_number_increment
        else:
            # Format all lines
            formatted_lines = []
            for line_num in sorted(self.lines.keys()):
                code_text = self.lines[line_num]
                formatted_lines.append(self._format_line(line_num, code_text))
            display_text = '\n'.join(formatted_lines)

        # Update the edit widget
        self.edit_widget.set_edit_text(display_text)

        # If empty program, position cursor at code column (after line number)
        if not self.lines:
            self.edit_widget.set_edit_pos(7)  # Position 7 is start of code area

    def get_program_text(self):
        """Get the program as line-numbered text.

        Returns:
            String with all lines in format "LINENUM CODE"
        """
        if not self.lines:
            return ""

        lines_list = []
        for line_num in sorted(self.lines.keys()):
            lines_list.append(f"{line_num} {self.lines[line_num]}")
        return '\n'.join(lines_list)

    def set_program_text(self, text):
        """Set the program from line-numbered text.

        Args:
            text: String with lines in format "LINENUM CODE"
        """
        self.lines = {}
        self.errors = {}

        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue

            # Parse "LINENUM CODE"
            parts = line.split(None, 1)
            if parts and parts[0].isdigit():
                line_num = int(parts[0])
                code = parts[1] if len(parts) > 1 else ""
                self.lines[line_num] = code

        self._update_display()

    def set_edit_text(self, text):
        """Compatibility alias for set_program_text.

        Args:
            text: String with lines in format "LINENUM CODE"
        """
        self.set_program_text(text)

    def get_edit_text(self):
        """Compatibility alias for get_program_text.

        Returns:
            String with all lines in format "LINENUM CODE"
        """
        return self.get_program_text()

    def add_line(self, line_num, code_text):
        """Add or update a program line.

        Args:
            line_num: Line number
            code_text: BASIC code (without line number)
        """
        self.lines[line_num] = code_text
        # Clear any error for this line when modified
        if line_num in self.errors:
            del self.errors[line_num]
        self._update_display()

    def delete_line(self, line_num):
        """Delete a program line.

        Args:
            line_num: Line number to delete
        """
        if line_num in self.lines:
            del self.lines[line_num]
        if line_num in self.errors:
            del self.errors[line_num]
        if line_num in self.breakpoints:
            self.breakpoints.remove(line_num)
        self._update_display()

    def clear(self):
        """Clear all program lines."""
        self.lines = {}
        self.errors = {}
        self.breakpoints = set()
        self._update_display()

    def toggle_breakpoint(self, line_num):
        """Toggle breakpoint on a line.

        Args:
            line_num: Line number
        """
        if line_num in self.breakpoints:
            self.breakpoints.remove(line_num)
        else:
            self.breakpoints.add(line_num)
        self._update_display()

    def set_error(self, line_num, error_msg):
        """Mark a line as having an error.

        Args:
            line_num: Line number
            error_msg: Error message
        """
        self.errors[line_num] = error_msg
        self._update_display()

    def _load_config(self):
        """Load configuration from .mbasic.conf file."""
        import configparser
        import os
        from pathlib import Path

        # Look for config in current directory, then home directory
        config_paths = [
            Path('.mbasic.conf'),
            Path('.') / '.mbasic.conf',
            Path.home() / '.mbasic.conf',
        ]

        for config_path in config_paths:
            if config_path.exists():
                try:
                    config = configparser.ConfigParser()
                    config.read(config_path)

                    # Load editor settings
                    if 'editor' in config:
                        editor = config['editor']

                        if 'auto_number_increment' in editor:
                            self.auto_number_increment = int(editor['auto_number_increment'])

                        if 'auto_number_start' in editor:
                            self.auto_number_start = int(editor['auto_number_start'])

                        if 'auto_number_enabled' in editor:
                            self.auto_number_enabled = editor.getboolean('auto_number_enabled')

                    return  # Stop after first config found
                except Exception as e:
                    # Silently ignore config errors and use defaults
                    pass

    def _sort_and_position_line(self, lines, current_line_index, target_column=7):
        """Sort lines by line number and position cursor at the moved line.

        Args:
            lines: List of text lines
            current_line_index: Index of line that triggered the sort
            target_column: Column to position cursor at (default: 7 for code area)
        """
        if current_line_index >= len(lines):
            return

        # Parse all lines into (line_number, full_text) tuples
        parsed_lines = []
        current_line_text = lines[current_line_index]

        for idx, line in enumerate(lines):
            if len(line) >= 6:
                try:
                    line_num = int(line[1:6].strip())
                    parsed_lines.append((line_num, line))
                except:
                    # If can't parse line number, keep it in original position
                    parsed_lines.append((999999 + idx, line))
            else:
                # Short line, keep in original position
                parsed_lines.append((999999 + idx, line))

        # Sort by line number
        parsed_lines.sort(key=lambda x: x[0])

        # Rebuild text
        sorted_lines = [line_text for _, line_text in parsed_lines]
        new_text = '\n'.join(sorted_lines)
        self.edit_widget.set_edit_text(new_text)

        # Find where the current line ended up
        try:
            new_index = sorted_lines.index(current_line_text)
            # Calculate position at target column
            line_start = sum(len(sorted_lines[i]) + 1 for i in range(new_index))
            new_cursor_pos = line_start + target_column
            self.edit_widget.set_edit_pos(new_cursor_pos)
        except ValueError:
            # Line not found, position at end
            self.edit_widget.set_edit_pos(len(new_text))


# Keep old EditorWidget for compatibility
class EditorWidget(urwid.Edit):
    """Multi-line editor widget for BASIC programs."""

    def __init__(self):
        super().__init__(multiline=True, align='left', wrap='clip')
        self.set_caption("")

    def keypress(self, size, key):
        """Handle key presses in the editor."""
        # Let parent handle most keys
        return super().keypress(size, key)


class CursesBackend(UIBackend):
    """Urwid-based curses UI backend.

    Provides a full-screen terminal interface with:
    - Multi-line editor for program entry
    - Output window for program results
    - Menu system for commands
    - Keyboard shortcuts
    """

    def __init__(self, io_handler, program_manager):
        """Initialize the curses UI backend.

        Args:
            io_handler: IOHandler instance for I/O operations
            program_manager: ProgramManager instance
        """
        super().__init__(io_handler, program_manager)

        # UI state
        self.app = None
        self.loop = None
        self.editor = None
        self.output = None
        self.status_bar = None

        # Editor state
        self.editor_lines = {}  # line_num -> text for editing
        self.current_line_num = 10  # Default starting line number

        # Execution state
        self.runtime = None
        self.interpreter = None
        self.running = False
        self.paused_at_breakpoint = False
        self.output_buffer = []

    def start(self):
        """Start the urwid-based curses UI."""
        # Create the UI layout
        self._create_ui()

        # Set up signal handling for clean exit
        import signal

        def handle_sigint(signum, frame):
            """Handle Ctrl+C (SIGINT) gracefully."""
            raise urwid.ExitMainLoop()

        # Register signal handler
        signal.signal(signal.SIGINT, handle_sigint)

        # Set up a callback to make cursor more visible after screen starts
        def setup_cursor():
            try:
                # Access the terminal file descriptor and write escape sequences
                if hasattr(self.loop.screen, '_term_output_file'):
                    fd = self.loop.screen._term_output_file.fileno()
                    import os
                    # Set cursor color to bright green (works on xterm-compatible terminals)
                    os.write(fd, b'\033]12;#00FF00\007')  # OSC sequence for cursor color
                    # Set cursor to steady block for better visibility
                    os.write(fd, b'\033[2 q')
            except:
                pass

        # Schedule cursor setup to run after screen initializes
        self.loop.set_alarm_in(0, lambda loop, user_data: setup_cursor())

        # Run the main loop
        try:
            self.loop.run()
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            pass
        finally:
            # Cleanup
            self._cleanup()

    def _cleanup(self):
        """Clean up resources before exit."""
        # Restore default cursor color
        try:
            if hasattr(self, 'loop') and hasattr(self.loop.screen, '_term_output_file'):
                fd = self.loop.screen._term_output_file.fileno()
                import os
                # Restore default cursor color (works on xterm-compatible terminals)
                os.write(fd, b'\033]112\007')  # Reset cursor color to default
        except:
            pass

        # Stop any running interpreter
        if hasattr(self, 'interpreter') and self.interpreter:
            try:
                # Try to stop cleanly
                pass
            except:
                pass

        # Clear any pending alarms
        if hasattr(self, 'loop') and self.loop:
            try:
                # Remove all alarms
                for alarm in list(self.loop.event_loop.alarm_list):
                    self.loop.remove_alarm(alarm)
            except:
                pass

    def _create_ui(self):
        """Create the urwid UI layout."""
        # Create widgets
        self.editor = ProgramEditorWidget()

        # Create scrollable output window using ListBox
        self.output_walker = urwid.SimpleFocusListWalker([])
        self.output = urwid.ListBox(self.output_walker)

        self.status_bar = urwid.Text("MBASIC 5.21 - Press Ctrl+H for help, Ctrl+Q or Ctrl+C to quit")

        # Create editor frame with top/left border only (no bottom/right space reserved)
        editor_frame = TopLeftBox(
            urwid.Filler(self.editor, valign='top'),
            title="Editor"
        )

        # Create output frame with top/left border only (no bottom/right space reserved)
        # ListBox doesn't need Filler since it handles its own scrolling
        output_frame = TopLeftBox(
            self.output,
            title="Output"
        )

        # Create layout - editor on top (70%), output on bottom (30%)
        pile = urwid.Pile([
            ('weight', 7, editor_frame),
            ('weight', 3, output_frame),
            ('pack', self.status_bar)
        ])

        # Set focus to the editor (first item in pile)
        pile.focus_position = 0

        # Create main widget with keybindings
        main_widget = urwid.AttrMap(pile, 'body')

        # Set up the main loop with cursor visible
        self.loop = urwid.MainLoop(
            main_widget,
            palette=self._get_palette(),
            unhandled_input=self._handle_input,
            handle_mouse=False
        )

    def _get_palette(self):
        """Get the color palette for the UI."""
        return [
            ('body', 'white', 'black'),
            ('header', 'white,bold', 'dark blue'),
            ('footer', 'white', 'dark blue'),
            # Use bright yellow for focus - this affects cursor visibility
            ('focus', 'black', 'yellow', 'standout'),
            ('error', 'light red', 'black'),
            # Output area styles
            ('output', 'white', 'black'),
            ('output_focus', 'black', 'light green', 'standout'),
        ]

    def _handle_input(self, key):
        """Handle global keyboard shortcuts."""
        if key == 'ctrl q' or key == 'ctrl c':
            # Quit (Ctrl+Q or Ctrl+C)
            raise urwid.ExitMainLoop()

        elif key == 'tab':
            # Toggle between editor (position 0) and output (position 1)
            # Get the pile widget from the main widget
            pile = self.loop.widget.base_widget
            if pile.focus_position == 0:
                # Switch to output
                pile.focus_position = 1
            else:
                # Switch back to editor
                pile.focus_position = 0
            return None

        elif key == 'ctrl h':
            # Show help
            self._show_help()

        elif key == 'ctrl r':
            # Run program
            self._run_program()

        elif key == 'ctrl l':
            # List program
            self._list_program()

        elif key == 'ctrl n':
            # New program
            self._new_program()

        elif key == 'ctrl s':
            # Save program
            self._save_program()

        elif key == 'ctrl o':
            # Open/Load program
            self._load_program()

    def _show_help(self):
        """Show help dialog."""
        help_text = """
MBASIC 5.21 - Keyboard Shortcuts

Global Commands:
  Ctrl+Q / Ctrl+C  - Quit
  Ctrl+H  - This help
  Ctrl+R  - Run program
  Ctrl+L  - List program
  Ctrl+N  - New program
  Ctrl+S  - Save program
  Ctrl+O  - Open/Load program
  Tab             - Toggle between Editor and Output

Screen Editor:
  Column Layout:
    [0]   Status: ● breakpoint, ? error, space normal
    [1-5] Line number (5 digits, right-aligned)
    [6]   Separator space
    [7+]  BASIC code

  Line Number Editing:
    - Type digits in columns 1-5 (calculator-style)
    - Numbers auto right-justify when leaving column
    - Leftmost digit drops when typing at rightmost position
    - Backspace deletes rightmost digit and right-justifies

  Navigation:
    Up/Down       - Move between lines (sorts if in number area)
    Left/Right    - Move within line (no auto-sort)
    Page Up/Down  - Scroll pages (triggers sort)
    Home/End      - Jump to start/end (triggers sort)
    Tab/Enter     - Move to code area / new line (triggers sort)

  Auto-Numbering:
    - First line starts at 10 (configurable)
    - Press Enter for next line (auto-increments by 10)
    - Uses current line number + increment
    - Avoids collisions with existing lines
    - Configure in .mbasic.conf

Output Area:
  Tab            - Switch to output area
  Up/Down        - Scroll through output
  Green cursor   - First character shows current line
  Tab            - Return to editor

Examples:
  10 PRINT "Hello, World!"
  20 END
"""
        # Create help dialog
        text = urwid.Text(help_text.strip())
        fill = urwid.Filler(text, valign='top')
        box = urwid.LineBox(fill, title="Help - Press any key to close")
        overlay = urwid.Overlay(
            urwid.AttrMap(box, 'body'),
            self.loop.widget,
            align='center',
            width=('relative', 80),
            valign='middle',
            height=('relative', 80)
        )

        # Show overlay and wait for key
        self.loop.widget = overlay

        # Set up a one-time keypress handler to close the dialog
        def close_help(key):
            self.loop.widget = main_widget
            self.loop.unhandled_input = self._handle_input

        # Store original widget
        main_widget = self.loop.widget.base_widget
        self.loop.unhandled_input = close_help

    def _run_program(self):
        """Run the current program using tick-based interpreter."""
        try:
            # Parse editor content into program
            self._parse_editor_content()

            if not self.editor_lines:
                self.output_buffer.append("No program to run")
                self._update_output()
                return

            # Update status
            self.status_bar.set_text("Running program...")
            # Screen will update automatically when loop is running

            # Load program lines into program manager
            self.program.clear()
            for line_num in sorted(self.editor_lines.keys()):
                line_text = f"{line_num} {self.editor_lines[line_num]}"
                success, error = self.program.add_line(line_num, line_text)
                if not success:
                    self.output_buffer.append(f"Error at line {line_num}: {error}")
                    self._update_output()
                    self.status_bar.set_text("Parse error - Press Ctrl+H for help")
                    return

            # Create a capturing IO handler that just buffers output
            class CapturingIOHandler:
                """IO handler that captures output to a buffer.

                Output is collected during tick execution and then
                picked up by the UI after the tick returns.
                """
                def __init__(self):
                    self.output_buffer = []
                    self.debug_enabled = False

                def output(self, text, end='\n'):
                    """Capture output to buffer."""
                    if end == '\n':
                        self.output_buffer.append(str(text))
                    else:
                        # For same-line output, append to last line or create new
                        if self.output_buffer:
                            self.output_buffer[-1] += str(text) + end
                        else:
                            self.output_buffer.append(str(text) + end)

                def get_and_clear_output(self):
                    """Get buffered output and clear the buffer."""
                    output = self.output_buffer[:]
                    self.output_buffer.clear()
                    return output

                def set_debug(self, enabled):
                    self.debug_enabled = enabled

                # Stub methods required by IOHandler interface
                def input(self, prompt=''):
                    return ""

                def input_line(self, prompt=''):
                    return ""

                def input_char(self, blocking=True):
                    return ""

                def clear_screen(self):
                    pass

                def error(self, message):
                    self.output(f"Error: {message}")

                def debug(self, message):
                    if self.debug_enabled:
                        self.output(f"Debug: {message}")

            # Create runtime and interpreter
            io_handler = CapturingIOHandler()
            runtime = Runtime(self.program.line_asts, self.program.lines)
            self.interpreter = Interpreter(runtime, io_handler)
            self.runtime = runtime
            self.io_handler = io_handler  # Keep reference to get output later

            # Start execution
            state = self.interpreter.start()

            if state.status == 'error':
                error_msg = state.error_info.error_message if state.error_info else "Unknown error"
                self.output_buffer.append(f"Error: {error_msg}")
                self._update_output()
                self.status_bar.set_text("Error - Press Ctrl+H for help")
                return

            # Set up tick-based execution using urwid's alarm
            self._execute_tick()

        except Exception as e:
            import traceback
            self.output_buffer.append(f"Runtime error: {e}")
            self.output_buffer.append(traceback.format_exc())
            self._update_output()
            self.status_bar.set_text("Error - Press Ctrl+H for help")

    def _execute_tick(self):
        """Execute one tick of the interpreter and schedule next tick."""
        try:
            # Execute one tick
            state = self.interpreter.tick(mode='run', max_statements=100)

            # Collect any output produced during the tick
            new_output = self.io_handler.get_and_clear_output()
            if new_output:
                self.output_buffer.extend(new_output)
                self._update_output()

            # Handle state transitions
            if state.status == 'running':
                # Schedule next tick
                self.loop.set_alarm_in(0.01, lambda loop, user_data: self._execute_tick())

            elif state.status == 'waiting_for_input':
                # Prompt user for input
                prompt = state.input_prompt or "? "
                self._get_input_for_interpreter(prompt)

            elif state.status == 'done':
                # Program completed - show final output if any
                final_output = self.io_handler.get_and_clear_output()
                if final_output:
                    self.output_buffer.extend(final_output)
                self.output_buffer.append("Ok")
                self._update_output()
                self.status_bar.set_text("Ready - Press Ctrl+H for help")

            elif state.status == 'error':
                # Error occurred - show any output before error
                error_output = self.io_handler.get_and_clear_output()
                if error_output:
                    self.output_buffer.extend(error_output)
                error_msg = state.error_info.error_message if state.error_info else "Unknown error"
                line_num = state.error_info.error_line if state.error_info else "?"
                self.output_buffer.append(f"Error in {line_num}: {error_msg}")
                self._update_output()
                self.status_bar.set_text("Error - Press Ctrl+H for help")

            elif state.status == 'paused' or state.status == 'at_breakpoint':
                # Paused execution
                self.output_buffer.append(f"Paused at line {state.current_line}")
                self._update_output()
                self.status_bar.set_text("Paused - Press Ctrl+C to continue")

        except Exception as e:
            import traceback
            self.output_buffer.append(f"Runtime error: {e}")
            self.output_buffer.append(traceback.format_exc())
            self._update_output()
            self.status_bar.set_text("Error - Press Ctrl+H for help")

    def _get_input_for_interpreter(self, prompt):
        """Show input dialog and provide input to interpreter."""
        # Get input from user
        result = self._get_input_dialog(prompt)

        # Provide input to interpreter
        self.interpreter.provide_input(result)

        # Continue execution
        self.loop.set_alarm_in(0.01, lambda loop, user_data: self._execute_tick())

    def _list_program(self):
        """List the current program."""
        # Parse editor content
        self._parse_editor_content()

        # Get program listing
        lines = []
        for line_num in sorted(self.editor_lines.keys()):
            lines.append(f"{line_num} {self.editor_lines[line_num]}")

        if lines:
            self.output_buffer.append("Program listing:")
            self.output_buffer.extend(lines)
        else:
            self.output_buffer.append("No program loaded")

        self._update_output()

    def _new_program(self):
        """Clear the current program."""
        self.editor_lines = {}
        self.editor.clear()
        self.output_buffer.append("Program cleared")
        self._update_output()
        self.status_bar.set_text("Ready - Press Ctrl+H for help")

    def _parse_editor_content(self):
        """Parse the editor content into line-numbered statements."""
        # Parse the visual editor text into line-numbered statements
        self.editor_lines = {}

        # Get the raw text from the editor
        text = self.editor.edit_widget.get_edit_text()

        # Parse each line
        for line in text.split('\n'):
            if len(line) < 7:  # Too short to have status + linenum + separator
                continue

            # Extract line number from columns 1-5
            line_num_text = line[1:6].strip()
            if not line_num_text or not line_num_text.isdigit():
                continue

            line_num = int(line_num_text)

            # Extract code from column 7 onwards
            code = line[7:] if len(line) > 7 else ""

            # Store in editor_lines
            self.editor_lines[line_num] = code

        # Also update the editor's internal lines dictionary for consistency
        self.editor.lines = self.editor_lines.copy()

    def _update_output(self):
        """Update the output window with buffered content."""
        # Remember current focus position if output area is active
        old_focus = None
        try:
            if len(self.output_walker) > 0:
                old_focus = self.output_walker.focus
        except:
            pass

        # Clear existing content
        self.output_walker[:] = []

        # Add all lines from buffer with focus highlighting on first char
        for line in self.output_buffer:
            line_widget = OutputLineWidget(line)
            self.output_walker.append(line_widget)

        # Set focus to bottom (latest output)
        if len(self.output_walker) > 0:
            # Set focus on the walker (not the ListBox)
            self.output_walker.set_focus(len(self.output_walker) - 1)
            # Force ListBox to scroll to make focused widget visible
            # This ensures the cursor is always visible after output update
            try:
                self.output.set_focus_valign('bottom')
            except:
                pass

    def _update_output_with_lines(self, lines):
        """Update output window with specific lines."""
        # Clear existing content
        self.output_walker[:] = []

        # Add all lines with focus highlighting on first char
        for line in lines:
            line_widget = OutputLineWidget(line)
            self.output_walker.append(line_widget)

        # Scroll to the bottom (last line)
        if len(self.output_walker) > 0:
            # Set focus on the walker
            self.output_walker.set_focus(len(self.output_walker) - 1)
            # Force ListBox to scroll to make focused widget visible
            try:
                self.output.set_focus_valign('bottom')
            except:
                pass

    def _get_input_dialog(self, prompt):
        """Show input dialog and get user response."""
        # Create input widget
        edit = urwid.Edit(caption=prompt)

        # Create dialog
        fill = urwid.Filler(edit, valign='top')
        box = urwid.LineBox(fill, title="Input Required - Press Enter to submit")
        overlay = urwid.Overlay(
            urwid.AttrMap(box, 'body'),
            self.loop.widget,
            align='center',
            width=('relative', 60),
            valign='middle',
            height=5
        )

        # Store original widget
        original_widget = self.loop.widget
        self.loop.widget = overlay

        # Variable to store result
        result = {'value': ''}
        done = {'flag': False}

        def handle_input(key):
            if key == 'enter':
                result['value'] = edit.get_edit_text()
                done['flag'] = True
                self.loop.widget = original_widget
            elif key == 'esc':
                result['value'] = ''
                done['flag'] = True
                self.loop.widget = original_widget
            else:
                # Let edit widget handle it
                return key

        # Temporarily override input handler
        old_handler = self.loop.unhandled_input
        self.loop.unhandled_input = handle_input

        # Run loop until we get input
        while not done['flag']:
            self.loop.draw_screen()
            keys = self.loop.screen.get_input()
            for key in keys:
                self.loop.process_input(keys)
            if done['flag']:
                break

        # Restore handler
        self.loop.unhandled_input = old_handler

        return result['value']

    def _get_editor_text(self):
        """Get formatted editor text from line-numbered program."""
        lines = []
        for line_num in sorted(self.editor_lines.keys()):
            lines.append(f"{line_num} {self.editor_lines[line_num]}")
        return '\n'.join(lines)

    def _load_program_file(self, filename):
        """Load a program from a file."""
        try:
            self.program.load_from_file(filename)

            # Convert program to editor lines
            self.editor_lines = {}
            for line_num, line_obj in sorted(self.program.lines.items()):
                # Get the original text for the line
                self.editor_lines[line_num] = line_obj.original_text

            # Update editor display
            self.editor.set_edit_text(self._get_editor_text())

            self.output_buffer.append(f"Loaded {filename}")
            self._update_output()

        except Exception as e:
            self.output_buffer.append(f"Error loading file: {e}")
            self._update_output()

    def _save_program(self):
        """Save program to file."""
        # Get filename from user
        filename = self._get_input_dialog("Save as: ")

        if not filename:
            self.output_buffer.append("Save cancelled")
            self._update_output()
            return

        try:
            # Parse editor content first
            self._parse_editor_content()

            # Create program content
            lines = []
            for line_num in sorted(self.editor_lines.keys()):
                lines.append(f"{line_num} {self.editor_lines[line_num]}")

            # Write to file
            with open(filename, 'w') as f:
                f.write('\n'.join(lines))
                f.write('\n')

            self.output_buffer.append(f"Saved to {filename}")
            self._update_output()

        except Exception as e:
            self.output_buffer.append(f"Error saving file: {e}")
            self._update_output()

    def _load_program(self):
        """Load program from file."""
        # Get filename from user
        filename = self._get_input_dialog("Load file: ")

        if not filename:
            self.output_buffer.append("Load cancelled")
            self._update_output()
            return

        try:
            self._load_program_file(filename)
        except Exception as e:
            self.output_buffer.append(f"Error loading file: {e}")
            self._update_output()

    # Command implementations (inherited from UIBackend)

    def cmd_run(self):
        """Execute RUN command."""
        self._run_program()

    def cmd_list(self, args=""):
        """Execute LIST command."""
        self._list_program()

    def cmd_new(self):
        """Execute NEW command."""
        self._new_program()

    def cmd_load(self, filename):
        """Execute LOAD command."""
        self._load_program_file(filename)
