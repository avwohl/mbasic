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
    """Custom box widget that only draws top border (no left/bottom/right).

    This allows edge-to-edge content that doesn't interfere with copying text.
    """

    def __init__(self, original_widget, title=''):
        """Create a box with only top border.

        Args:
            original_widget: The widget to wrap
            title: Title to display in top border
        """
        self.title = title
        self.original_widget = original_widget

        # Create the top border line with title
        if title:
            # Title in the top border: "── Title ────────"
            title_text = urwid.Text(f'── {title} ', wrap='clip')
            fill_text = urwid.Text('─' * 200, wrap='clip')
            top_border = urwid.Columns([
                ('pack', title_text),
                fill_text
            ], dividechars=0)
        else:
            top_border = urwid.Text('─' * 200, wrap='clip')

        # Stack top border and content (no left border)
        pile = urwid.Pile([
            ('pack', top_border),
            original_widget
        ])

        # Set focus to the content area (not the top border)
        pile.focus_position = 1

        super().__init__(pile)

    def selectable(self):
        """Pass through selectability of wrapped widget."""
        return self._w.selectable()


class SelectableText(urwid.Text):
    """Text widget that is selectable for ListBox scrolling."""

    def selectable(self):
        return True

    def keypress(self, size, key):
        # Return key unconsumed so ListBox can handle up/down scrolling
        return key


def make_output_line(text):
    """Create an output line widget.

    Args:
        text: Line text to display

    Returns:
        Selectable text widget for scrolling in ListBox
    """
    return SelectableText(text if text else "")


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

        # For debouncing sorting during rapid input (paste operations)
        self._needs_sort = False  # Flag: lines need sorting when navigation happens

        # For deferred screen refresh during rapid input (paste operations)
        self._needs_refresh = False  # Flag: screen needs refresh when input stops
        self._pending_refresh_alarm = None  # Handle for pending refresh alarm
        self._loop = None  # Will be set by CursesBackend after loop creation
        self._idle_delay = 0.1  # Seconds to wait after last keystroke before refresh

        # Syntax error tracking
        self.syntax_errors = {}  # Maps line number -> error message
        self._output_walker = None  # Will be set by CursesBackend for displaying errors
        self._showing_syntax_errors = False  # Track if output window has syntax errors

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
        # CRITICAL PERFORMANCE: For paste, skip ALL processing for normal typing
        # Check if it's a single printable character (not a special key)
        if len(key) == 1 and key >= ' ' and key <= '~':
            # Fast path: normal printable ASCII - just pass through
            # This avoids expensive text parsing on every pasted character

            # Schedule deferred refresh - will happen 0.1s after typing stops
            self._schedule_deferred_refresh()

            return super().keypress(size, key)

        # NON-PRINTABLE KEY: Check if we have pending updates from paste
        # If so, process them NOW before handling this key
        if self._needs_refresh or self._needs_sort:
            self._perform_deferred_refresh()

        # Get current cursor position (only for special keys)
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

        # Check syntax when leaving line or pressing control keys
        # (Not during normal typing - avoids annoying errors for incomplete lines)
        if is_control_key or is_updown_arrow or is_other_nav_key:
            # About to navigate or run command - check syntax now
            new_text = self._update_syntax_errors(current_text)
            if new_text != current_text:
                # Text was updated with error markers - update the editor
                self.edit_widget.set_edit_text(new_text)
                # Recalculate positions
                current_text = new_text
                cursor_pos = self.edit_widget.edit_pos
                text_before_cursor = current_text[:cursor_pos]
                line_num = text_before_cursor.count('\n')
                lines = current_text.split('\n')
                if line_num < len(lines):
                    line_start_pos = sum(len(lines[i]) + 1 for i in range(line_num))
                    col_in_line = cursor_pos - line_start_pos

        # PERFORMANCE: Skip right-justification during rapid typing/paste
        # Only do it when navigating (which is when user expects formatting)
        should_right_justify = False
        if is_control_key or is_updown_arrow or is_other_nav_key:
            # About to navigate - right-justify now
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

        # Mark that sorting is needed when editing line numbers
        if 1 <= col_in_line <= 6 and len(key) == 1 and key.isdigit():
            # Typing digits in line number area - will need sorting later
            self._needs_sort = True

        # Sort lines only when navigating away (not on every keystroke)
        # This makes paste much faster - only sort once at the end
        if (is_control_key or is_other_nav_key or is_updown_arrow) and self._needs_sort:
            # About to navigate - sort now if needed
            if 1 <= col_in_line <= 6:
                self._sort_and_position_line(lines, line_num, target_column=col_in_line)
                self._needs_sort = False
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

    def _check_line_syntax(self, code_text):
        """Check if a line of BASIC code has valid syntax.

        Args:
            code_text: The BASIC code (without line number)

        Returns:
            Tuple of (is_valid: bool, error_message: str or None)
        """
        if not code_text or not code_text.strip():
            # Empty lines are valid
            return (True, None)

        try:
            # Import here to avoid circular dependencies
            from lexer import Lexer
            from parser import Parser
            from ast_nodes import RemarkStatementNode
            from tokens import TokenType

            # Tokenize the code
            lexer = Lexer(code_text)
            tokens = lexer.tokenize()

            # Reject bare identifiers (the parser treats them as implicit REMs for
            # old BASIC compatibility, but in the editor we want to be stricter)
            if len(tokens) >= 2:
                first_token = tokens[0]
                second_token = tokens[1]
                # If first token is identifier and second is EOF (or colon),
                # this is a bare identifier like "foo" which should be invalid
                if (first_token.type == TokenType.IDENTIFIER and
                    second_token.type in (TokenType.EOF, TokenType.COLON)):
                    return (False, f"Invalid statement: '{first_token.value}' is not a BASIC keyword")

            # Parse the statement
            # Create a new parser with empty def_type_map to avoid affecting existing state
            parser = Parser(tokens, def_type_map={})
            result = parser.parse_statement()

            # Additional check: reject implicit REM statements (bare identifiers)
            # The parser allows these for compatibility, but we want stricter checking
            if isinstance(result, RemarkStatementNode):
                # Check if this was an actual REM keyword or implicit REM
                # Look at first token - if it's not REM/REMARK/', it's implicit
                if tokens and tokens[0].type not in (TokenType.REM, TokenType.REMARK, TokenType.APOSTROPHE):
                    return (False, f"Invalid statement: '{tokens[0].value}' is not a BASIC keyword")

            # If we get here, parsing succeeded with valid syntax
            return (True, None)

        except Exception as e:
            # Any error (lexer or parser) means invalid syntax
            # Extract a useful error message
            error_msg = str(e)
            # Remove "Parse error at line X, column Y: " prefix if present
            if "Parse error" in error_msg and ":" in error_msg:
                error_msg = error_msg.split(":", 1)[1].strip()
            return (False, error_msg)

    def _get_status_char(self, line_number, has_syntax_error):
        """Get the status character for a line based on priority.

        Priority order (highest to lowest):
        1. Syntax error (?) - highest priority
        2. Breakpoint (●) - medium priority
        3. Normal ( ) - default

        Args:
            line_number: The line number to check
            has_syntax_error: Whether the line has a syntax error

        Returns:
            Single character status indicator
        """
        if has_syntax_error:
            return '?'
        elif line_number in self.breakpoints:
            return '●'
        else:
            return ' '

    def _update_syntax_errors(self, text):
        """Update status indicators for lines with syntax errors.

        Args:
            text: Current editor text

        Returns:
            Updated text with '?' status for lines with parse errors
        """
        lines = text.split('\n')
        changed = False

        # Clear old error messages
        self.syntax_errors.clear()

        for i, line in enumerate(lines):
            if not line or len(line) < 7:
                continue

            # Extract parts
            status = line[0]
            linenum_col = line[1:6]
            code_area = line[7:] if len(line) > 7 else ""

            # Parse line number
            line_number_str = linenum_col.strip()
            try:
                line_number = int(line_number_str) if line_number_str else 0
            except:
                line_number = 0

            # Skip empty code lines
            if not code_area.strip():
                # Clear error status for empty lines, but preserve breakpoints
                if line_number > 0:
                    new_status = self._get_status_char(line_number, has_syntax_error=False)
                    if status != new_status:
                        lines[i] = new_status + line[1:]
                        changed = True
                continue

            # Check syntax
            is_valid, error_msg = self._check_line_syntax(code_area)

            # Determine correct status based on priority
            if line_number > 0:
                new_status = self._get_status_char(line_number, has_syntax_error=not is_valid)

                # Update status if it changed
                if status != new_status:
                    lines[i] = new_status + line[1:]
                    changed = True

                # Store or clear error message
                if not is_valid and error_msg:
                    self.syntax_errors[line_number] = error_msg
                # Note: syntax_errors cleared at start, so valid lines won't have errors

        # Update output window with errors
        self._display_syntax_errors()

        if changed:
            return '\n'.join(lines)
        else:
            return text

    def _display_syntax_errors(self):
        """Display syntax error messages in the output window with context."""
        # Check if output walker is available (use 'is None' instead of 'not' to avoid false positive on empty walker)
        if self._output_walker is None:
            # Output window not available yet
            return

        if not self.syntax_errors:
            # No errors - clear output IF it was showing syntax errors before
            if self._showing_syntax_errors:
                self._output_walker.clear()
                self._showing_syntax_errors = False
            return

        # Clear output window and show syntax errors
        self._output_walker.clear()
        self._showing_syntax_errors = True

        # Add error header
        self._output_walker.append(make_output_line("┌─ Syntax Errors ──────────────────────────────────┐"))
        self._output_walker.append(make_output_line("│"))

        # Add each error with code context
        for line_number in sorted(self.syntax_errors.keys()):
            error_msg = self.syntax_errors[line_number]

            # Get the code for this line if available
            code = self.lines.get(line_number, "")

            # Format error with context
            self._output_walker.append(make_output_line(f"│ Line {line_number}:"))
            if code:
                # Show the actual code
                self._output_walker.append(make_output_line(f"│   {code}"))
                self._output_walker.append(make_output_line(f"│   ^^^^"))
            self._output_walker.append(make_output_line(f"│ Error: {error_msg}"))
            self._output_walker.append(make_output_line("│"))

        self._output_walker.append(make_output_line("└──────────────────────────────────────────────────┘"))

        # Auto-scroll to bottom to show errors
        if len(self._output_walker) > 0:
            self._output_walker.set_focus(len(self._output_walker) - 1)

    def _parse_line_numbers(self, text):
        """Parse and reformat lines that start with numbers.

        If a line starts with a number (typical BASIC format like "10 PRINT"),
        move the number to the line number column.

        Handles both:
        - Lines with column structure: " [space]     10 PRINT"
        - Raw pasted lines: "10 PRINT"

        Args:
            text: Current editor text

        Returns:
            Reformatted text with numbers in proper columns
        """
        lines = text.split('\n')
        changed = False

        for i, line in enumerate(lines):
            if not line:
                continue

            # FIRST: Check if line starts with a digit (raw pasted BASIC)
            # Since BASIC code can never legally start with a digit, this must be a line number
            if line[0].isdigit():
                # Raw pasted line like "10 PRINT" - reformat it
                # Extract number
                num_str = ""
                j = 0
                while j < len(line) and line[j].isdigit():
                    num_str += line[j]
                    j += 1

                # Get rest of line (skip spaces after number)
                while j < len(line) and line[j] == ' ':
                    j += 1
                rest = line[j:]

                # Reformat with column structure
                if num_str:
                    line_num_formatted = f"{num_str:>5}"
                    new_line = f" {line_num_formatted} {rest}"
                    lines[i] = new_line
                    changed = True
                continue

            # SECOND: Check lines with column structure
            if len(line) >= 7:
                # Extract status, line number column, and code area
                status = line[0]
                linenum_col = line[1:6]  # Existing line number column
                code_area = line[7:] if len(line) >= 7 else ""

                # Check if code area starts with a number (after stripping leading spaces)
                # (It's never legal for BASIC code to start with a digit)
                code_stripped = code_area.lstrip()
                if code_stripped and code_stripped[0].isdigit():
                    # Found a number in code area - use it as the line number

                    # Extract the number from code area
                    num_str = ""
                    j = 0
                    while j < len(code_stripped) and code_stripped[j].isdigit():
                        num_str += code_stripped[j]
                        j += 1

                    # Get rest of line (skip ALL spaces after number)
                    while j < len(code_stripped) and code_stripped[j] == ' ':
                        j += 1
                    rest = code_stripped[j:]

                    # ALWAYS use the number from code area (replaces auto-number or fills empty)
                    # This preserves user's pasted line numbers like 210, 220, 230
                    line_num_formatted = f"{num_str:>5}"
                    new_line = f"{status}{line_num_formatted} {rest}"

                    lines[i] = new_line
                    changed = True

        if changed:
            return '\n'.join(lines)
        else:
            return text

    def _schedule_deferred_refresh(self):
        """Schedule a deferred screen refresh after idle delay.

        Cancels any existing pending refresh and schedules a new one.
        This batches updates during rapid input (paste operations).
        """
        if not self._loop:
            # Loop not available yet, skip scheduling
            return

        # Cancel existing alarm if any
        if self._pending_refresh_alarm:
            self._loop.remove_alarm(self._pending_refresh_alarm)
            self._pending_refresh_alarm = None

        # Schedule new alarm
        self._pending_refresh_alarm = self._loop.set_alarm_in(
            self._idle_delay,
            self._perform_deferred_refresh
        )

        # Mark that a refresh is pending
        self._needs_refresh = True

    def _perform_deferred_refresh(self, loop=None, user_data=None):
        """Perform deferred screen refresh (alarm callback).

        Called when input has been idle for the delay period.
        Performs any pending sorting and screen updates.

        Args:
            loop: urwid MainLoop (passed by alarm callback)
            user_data: User data (passed by alarm callback, unused)
        """
        # Clear the alarm handle
        self._pending_refresh_alarm = None

        # Check if refresh is actually needed
        if not self._needs_refresh and not self._needs_sort:
            return

        # Get current state
        current_text = self.edit_widget.get_edit_text()
        cursor_pos = self.edit_widget.edit_pos

        # Step 1: Parse and reformat lines with numbers in code area
        # (This handles pasted BASIC code like "10 PRINT")
        new_text = self._parse_line_numbers(current_text)
        if new_text != current_text:
            # Text was reformatted - update the editor
            self.edit_widget.set_edit_text(new_text)
            # Try to maintain cursor position (may shift due to reformatting)
            if cursor_pos <= len(new_text):
                self.edit_widget.set_edit_pos(cursor_pos)
            current_text = new_text

        # Step 2: Perform deferred sorting if needed
        if self._needs_sort:
            lines = current_text.split('\n')

            # Find current line
            text_before_cursor = current_text[:cursor_pos]
            line_num = text_before_cursor.count('\n')

            # Sort if we're in the line number area
            if line_num < len(lines):
                line_start_pos = sum(len(lines[i]) + 1 for i in range(line_num))
                col_in_line = cursor_pos - line_start_pos

                if 1 <= col_in_line <= 6:
                    self._sort_and_position_line(lines, line_num, target_column=col_in_line)

            self._needs_sort = False

        # Clear refresh flag
        self._needs_refresh = False

        # Force screen redraw if loop is available
        if self._loop:
            self._loop.draw_screen()

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

        # Pass output_walker to editor for displaying syntax errors
        self.editor._output_walker = self.output_walker

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

        # Pass loop reference to editor for deferred refresh mechanism
        self.editor._loop = self.loop

    def _get_palette(self):
        """Get the color palette for the UI."""
        return [
            ('body', 'white', 'black'),
            ('header', 'white,bold', 'dark blue'),
            ('footer', 'white', 'dark blue'),
            # Use bright yellow for focus - this affects cursor visibility
            ('focus', 'black', 'yellow', 'standout'),
            ('error', 'light red', 'black'),
        ]

    def _handle_input(self, key):
        """Handle global keyboard shortcuts."""
        if key == 'ctrl q' or key == 'ctrl c':
            # Quit (Ctrl+Q or Ctrl+C)
            raise urwid.ExitMainLoop()

        elif key == 'tab':
            # Toggle between editor (position 0) and output (position 1)
            pile = self.loop.widget.base_widget
            if pile.focus_position == 0:
                # Switch to output for scrolling
                pile.focus_position = 1
                self.status_bar.set_text("Output - Use Up/Down to scroll, Tab to return to editor")
            else:
                # Switch back to editor
                pile.focus_position = 0
                self.status_bar.set_text("Editor - Press Ctrl+H for help")
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

        elif key == 'ctrl b':
            # Toggle breakpoint on current line
            self._toggle_breakpoint_current_line()

        elif key == 'ctrl d':
            # Delete current line
            self._delete_current_line()

        elif key == 'ctrl e':
            # Renumber all lines
            self._renumber_lines()

        elif key == 'ctrl g':
            # Continue execution (from breakpoint/pause)
            self._debug_continue()

        elif key == 'ctrl t':
            # Step - execute one line
            self._debug_step()

        elif key == 'ctrl x':
            # Stop execution
            self._debug_stop()

    def _debug_continue(self):
        """Continue execution from paused/breakpoint state."""
        if not self.interpreter:
            self.status_bar.set_text("No program running")
            return

        try:
            state = self.interpreter.get_state()
            if state.status in ('paused', 'at_breakpoint'):
                # Continue from breakpoint
                self.status_bar.set_text("Continuing execution...")
                self.interpreter.cont()
                # Schedule next tick
                self.loop.set_alarm_in(0.01, lambda loop, user_data: self._execute_tick())
            else:
                self.status_bar.set_text(f"Not paused (status: {state.status})")
        except Exception as e:
            self.status_bar.set_text(f"Continue error: {e}")

    def _debug_step(self):
        """Execute one line and pause (single-step debugging)."""
        if not self.interpreter:
            self.status_bar.set_text("No program running")
            return

        try:
            state = self.interpreter.get_state()
            if state.status in ('paused', 'at_breakpoint', 'running'):
                # Execute one statement
                self.status_bar.set_text("Stepping...")
                state = self.interpreter.tick(mode='step', max_statements=1)

                # Collect any output
                new_output = self.io_handler.get_and_clear_output()
                if new_output:
                    self.output_buffer.extend(new_output)
                    self._update_output()

                # Show where we paused
                if state.status in ('paused', 'at_breakpoint'):
                    self.output_buffer.append(f"→ Paused at line {state.current_line}")
                    self._update_output()
                    self.status_bar.set_text(f"Paused at line {state.current_line} - Ctrl+T=Step, Ctrl+G=Continue, Ctrl+X=Stop")
                elif state.status == 'done':
                    self.output_buffer.append("Program completed")
                    self._update_output()
                    self.status_bar.set_text("Program completed")
                elif state.status == 'error':
                    error_msg = state.error_info.error_message if state.error_info else "Unknown error"
                    line_num = state.error_info.error_line if state.error_info else "?"
                    self.output_buffer.append(f"Error at line {line_num}: {error_msg}")
                    self._update_output()
                    self.status_bar.set_text("Error during step")
            else:
                self.status_bar.set_text(f"Cannot step (status: {state.status})")
        except Exception as e:
            import traceback
            self.output_buffer.append(f"Step error: {e}")
            self.output_buffer.append(traceback.format_exc())
            self._update_output()
            self.status_bar.set_text(f"Step error: {e}")

    def _debug_stop(self):
        """Stop program execution."""
        if not self.interpreter:
            self.status_bar.set_text("No program running")
            return

        try:
            # Stop the interpreter
            self.interpreter = None
            self.runtime = None
            self.output_buffer.append("Program stopped by user")
            self._update_output()
            self.status_bar.set_text("Program stopped - Ready")
        except Exception as e:
            self.status_bar.set_text(f"Stop error: {e}")

    def _delete_current_line(self):
        """Delete the current line where the cursor is."""
        # Get current cursor position
        cursor_pos = self.editor.edit_widget.edit_pos
        current_text = self.editor.edit_widget.get_edit_text()

        # Find which line we're on
        text_before_cursor = current_text[:cursor_pos]
        line_index = text_before_cursor.count('\n')

        # Get the lines
        lines = current_text.split('\n')
        if line_index >= len(lines):
            return

        line = lines[line_index]

        # Extract line number from columns 1-5
        if len(line) < 6:
            return

        line_number_str = line[1:6].strip()
        if not line_number_str or not line_number_str.isdigit():
            self.status_bar.set_text("No line number to delete")
            return

        line_number = int(line_number_str)

        # Remove the line from the display
        del lines[line_index]

        # Update editor.lines dict
        if line_number in self.editor.lines:
            del self.editor.lines[line_number]

        # Remove from breakpoints and errors if present
        if line_number in self.editor.breakpoints:
            self.editor.breakpoints.remove(line_number)
        if line_number in self.editor.syntax_errors:
            del self.editor.syntax_errors[line_number]

        # Update display
        new_text = '\n'.join(lines)
        self.editor.edit_widget.set_edit_text(new_text)

        # Position cursor at beginning of next line (or previous if at end)
        if line_index < len(lines):
            # Position at start of line that moved up
            if line_index > 0:
                new_cursor_pos = sum(len(lines[i]) + 1 for i in range(line_index))
            else:
                new_cursor_pos = 0
        else:
            # Was last line, position at end of previous line
            if lines:
                new_cursor_pos = sum(len(lines[i]) + 1 for i in range(len(lines) - 1)) + len(lines[-1])
            else:
                new_cursor_pos = 0

        self.editor.edit_widget.set_edit_pos(new_cursor_pos)

        # Update status bar
        self.status_bar.set_text(f"Deleted line {line_number}")

        # Force screen redraw
        if self.loop:
            self.loop.draw_screen()

    def _renumber_lines(self):
        """Renumber all lines with a dialog for start and increment."""
        # Get current parameters
        current_text = self.editor.edit_widget.get_edit_text()
        lines = current_text.split('\n')

        # Count valid program lines
        valid_lines = []
        for line in lines:
            if len(line) >= 7:
                line_number_str = line[1:6].strip()
                if line_number_str and line_number_str.isdigit():
                    line_number = int(line_number_str)
                    code = line[7:]
                    valid_lines.append((line_number, code, line[0]))  # (line_num, code, status)

        if not valid_lines:
            self.status_bar.set_text("No lines to renumber")
            return

        # Get renumber parameters from user
        start_str = self._get_input_dialog("RENUM - Start line number (default 10): ")
        if start_str is None or start_str == '':
            start = 10
        else:
            try:
                start = int(start_str)
            except:
                self.status_bar.set_text("Invalid start number")
                return

        increment_str = self._get_input_dialog("RENUM - Increment (default 10): ")
        if increment_str is None or increment_str == '':
            increment = 10
        else:
            try:
                increment = int(increment_str)
            except:
                self.status_bar.set_text("Invalid increment")
                return

        # Build new lines with renumbered line numbers
        new_lines = []
        new_line_num = start
        old_to_new = {}  # Map old line numbers to new

        for old_line_num, code, status in valid_lines:
            old_to_new[old_line_num] = new_line_num

            # Update editor.lines dict
            self.editor.lines[new_line_num] = code
            if old_line_num != new_line_num and old_line_num in self.editor.lines:
                del self.editor.lines[old_line_num]

            # Update breakpoints
            if old_line_num in self.editor.breakpoints:
                self.editor.breakpoints.remove(old_line_num)
                self.editor.breakpoints.add(new_line_num)

            # Update syntax errors
            if old_line_num in self.editor.syntax_errors:
                error_msg = self.editor.syntax_errors[old_line_num]
                del self.editor.syntax_errors[old_line_num]
                self.editor.syntax_errors[new_line_num] = error_msg

            # Recalculate status for new line number
            has_syntax_error = new_line_num in self.editor.syntax_errors
            new_status = self.editor._get_status_char(new_line_num, has_syntax_error)

            # Format new line
            formatted_line = f"{new_status}{new_line_num:5d} {code}"
            new_lines.append(formatted_line)

            new_line_num += increment

        # Update display
        new_text = '\n'.join(new_lines)
        self.editor.edit_widget.set_edit_text(new_text)
        self.editor.edit_widget.set_edit_pos(0)

        # Update status bar
        self.status_bar.set_text(f"Renumbered {len(valid_lines)} lines from {start} by {increment}")

        # Force screen redraw
        if self.loop:
            self.loop.draw_screen()

    def _toggle_breakpoint_current_line(self):
        """Toggle breakpoint on the current line where the cursor is."""
        # Get current cursor position
        cursor_pos = self.editor.edit_widget.edit_pos
        current_text = self.editor.edit_widget.get_edit_text()

        # Find which line we're on
        text_before_cursor = current_text[:cursor_pos]
        line_index = text_before_cursor.count('\n')

        # Get the line text
        lines = current_text.split('\n')
        if line_index >= len(lines):
            return

        line = lines[line_index]

        # Extract line number from columns 1-5
        if len(line) < 6:
            return

        line_number_str = line[1:6].strip()
        if not line_number_str or not line_number_str.isdigit():
            return

        line_number = int(line_number_str)

        # Toggle breakpoint
        if line_number in self.editor.breakpoints:
            self.editor.breakpoints.remove(line_number)
            self.status_bar.set_text(f"Breakpoint removed from line {line_number}")
        else:
            self.editor.breakpoints.add(line_number)
            self.status_bar.set_text(f"Breakpoint set on line {line_number}")

        # Update display to show/hide breakpoint indicator
        # Need to recalculate status for this line
        status = line[0]
        code_area = line[7:] if len(line) > 7 else ""

        # Check if line has syntax error
        has_syntax_error = line_number in self.editor.syntax_errors

        # Get new status based on priority
        new_status = self.editor._get_status_char(line_number, has_syntax_error)

        # Update the line if status changed
        if status != new_status:
            lines[line_index] = new_status + line[1:]
            new_text = '\n'.join(lines)
            self.editor.edit_widget.set_edit_text(new_text)
            # Restore cursor position
            self.editor.edit_widget.set_edit_pos(cursor_pos)
            # Force screen redraw
            if self.loop:
                self.loop.draw_screen()

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
  Ctrl+B  - Toggle breakpoint on current line
  Ctrl+D  - Delete current line
  Ctrl+E  - Renumber all lines (RENUM)

Debugger Commands (when program running):
  Ctrl+G  - Continue execution (Go)
  Ctrl+T  - Step - execute one line (sTep)
  Ctrl+X  - Stop execution (eXit)

Screen Editor:
  Column Layout:
    [0]   Status: ? error (highest), ● breakpoint, space normal
    [1-5] Line number (5 digits, right-aligned)
    [6]   Separator space
    [7+]  BASIC code

  Status Priority (when line has multiple states):
    1. Error (?) - highest, shown when syntax error exists
    2. Breakpoint (●) - shown when no error but breakpoint set
    3. Normal ( ) - default

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
                    # Format parse error with context
                    self.output_buffer.append("")
                    self.output_buffer.append("┌─ Parse Error ────────────────────────────────────┐")
                    self.output_buffer.append(f"│ Line {line_num}:")
                    if line_num in self.editor_lines:
                        code = self.editor_lines[line_num]
                        self.output_buffer.append(f"│   {code}")
                        self.output_buffer.append(f"│   ^^^^")
                    self.output_buffer.append(f"│ Error: {error}")
                    self.output_buffer.append("│")
                    self.output_buffer.append("│ Fix the syntax error and try running again.")
                    self.output_buffer.append("└──────────────────────────────────────────────────┘")
                    self._update_output()
                    self.status_bar.set_text("Parse error - Fix and try again")
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

            # Set breakpoints from editor
            for line_num in self.editor.breakpoints:
                self.interpreter.set_breakpoint(line_num)

            # Start execution
            state = self.interpreter.start()

            if state.status == 'error':
                error_msg = state.error_info.error_message if state.error_info else "Unknown error"
                self.output_buffer.append("")
                self.output_buffer.append("┌─ Startup Error ──────────────────────────────────┐")
                self.output_buffer.append(f"│ Error: {error_msg}")
                self.output_buffer.append("└──────────────────────────────────────────────────┘")
                self._update_output()
                self.status_bar.set_text("Startup error - Check program")
                return

            # Set up tick-based execution using urwid's alarm
            self._execute_tick()

        except Exception as e:
            import traceback
            # Format unexpected error with box
            self.output_buffer.append("")
            self.output_buffer.append("┌─ Unexpected Error ───────────────────────────────┐")
            self.output_buffer.append(f"│ {type(e).__name__}: {e}")
            self.output_buffer.append("│")
            self.output_buffer.append("│ This is an internal error. Details below:")
            self.output_buffer.append("└──────────────────────────────────────────────────┘")
            self.output_buffer.append("")
            # Add traceback for debugging
            for line in traceback.format_exc().split('\n'):
                self.output_buffer.append(line)
            self._update_output()
            self.status_bar.set_text("Internal error - See output")

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

                # Format error with context
                error_msg = state.error_info.error_message if state.error_info else "Unknown error"
                line_num = state.error_info.error_line if state.error_info else "?"

                # Build error display with box and context
                self.output_buffer.append("")
                self.output_buffer.append("┌─ Runtime Error ──────────────────────────────────┐")

                # Try to get the code for the error line
                if line_num != "?" and isinstance(line_num, int):
                    self.output_buffer.append(f"│ Line {line_num}:")
                    # Get code from editor_lines
                    if line_num in self.editor_lines:
                        code = self.editor_lines[line_num]
                        self.output_buffer.append(f"│   {code}")
                        self.output_buffer.append(f"│   ^^^^")
                else:
                    self.output_buffer.append(f"│ Line {line_num}:")

                self.output_buffer.append(f"│ Error: {error_msg}")
                self.output_buffer.append("└──────────────────────────────────────────────────┘")

                self._update_output()
                self.status_bar.set_text("Error - Press Ctrl+H for help")

            elif state.status == 'paused' or state.status == 'at_breakpoint':
                # Paused execution (breakpoint hit or stepping)
                if state.status == 'at_breakpoint':
                    self.output_buffer.append(f"● Breakpoint hit at line {state.current_line}")
                else:
                    self.output_buffer.append(f"→ Paused at line {state.current_line}")
                self._update_output()
                self.status_bar.set_text(f"Paused at line {state.current_line} - Ctrl+T=Step, Ctrl+G=Continue, Ctrl+X=Stop")

        except Exception as e:
            import traceback
            # Format unexpected tick error with box
            self.output_buffer.append("")
            self.output_buffer.append("┌─ Execution Error ────────────────────────────────┐")
            self.output_buffer.append(f"│ {type(e).__name__}: {e}")
            self.output_buffer.append("│")
            self.output_buffer.append("│ An error occurred during program execution.")
            self.output_buffer.append("└──────────────────────────────────────────────────┘")
            self.output_buffer.append("")
            # Add traceback for debugging
            for line in traceback.format_exc().split('\n'):
                self.output_buffer.append(line)
            self._update_output()
            self.status_bar.set_text("Execution error - See output")

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
        # Clear existing content
        self.output_walker[:] = []

        # Add all lines from buffer with focus highlighting on first char
        for line in self.output_buffer:
            line_widget = make_output_line(line)
            self.output_walker.append(line_widget)

        # Set focus to bottom (latest output)
        if len(self.output_walker) > 0:
            # Set focus on the walker (not the ListBox)
            self.output_walker.set_focus(len(self.output_walker) - 1)
            # Force a screen update
            if hasattr(self, 'loop') and self.loop:
                self.loop.draw_screen()

    def _update_output_with_lines(self, lines):
        """Update output window with specific lines."""
        # Clear existing content
        self.output_walker[:] = []

        # Add all lines with focus highlighting on first char
        for line in lines:
            line_widget = make_output_line(line)
            self.output_walker.append(line_widget)

        # Scroll to the bottom (last line)
        if len(self.output_walker) > 0:
            # Set focus on the walker
            self.output_walker.set_focus(len(self.output_walker) - 1)
            # Force a screen update
            if hasattr(self, 'loop') and self.loop:
                self.loop.draw_screen()

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
