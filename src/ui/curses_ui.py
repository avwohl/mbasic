"""Curses UI backend using urwid.

This module provides a full-screen terminal UI for MBASIC using the urwid library.
It provides an editor, output window, and menu system.
"""

import urwid
from pathlib import Path
from .base import UIBackend
from .keybindings import (
    HELP_KEY, MENU_KEY, QUIT_KEY, QUIT_ALT_KEY,
    VARIABLES_KEY, STACK_KEY, RUN_KEY, STEP_LINE_KEY, NEW_KEY, SAVE_KEY, OPEN_KEY,
    BREAKPOINT_KEY, CLEAR_BREAKPOINTS_KEY,
    DELETE_LINE_KEY, INSERT_LINE_KEY, RENUMBER_KEY,
    CONTINUE_KEY, STEP_KEY, STOP_KEY, TAB_KEY, SETTINGS_KEY,
    MAXIMIZE_OUTPUT_KEY,
    ENTER_KEY, ESC_KEY, BACKSPACE_KEY, DOWN_KEY, UP_KEY,
    VARS_SORT_MODE_KEY, VARS_SORT_DIR_KEY, VARS_EDIT_KEY, VARS_FILTER_KEY, VARS_CLEAR_KEY,
    DIALOG_YES_KEY, DIALOG_NO_KEY,
    STATUS_BAR_SHORTCUTS,
    key_to_display
)
from .markdown_renderer import MarkdownRenderer
from .help_widget import HelpWidget
from .recent_files import RecentFilesManager
from .auto_save import AutoSaveManager
from .interactive_menu import InteractiveMenuBar
from src.runtime import Runtime
from src.interpreter import Interpreter
from src.lexer import Lexer
from src.parser import Parser
from src.immediate_executor import ImmediateExecutor, OutputCapturingIOHandler
from src.input_sanitizer import is_valid_input_char, clear_parity
from src.debug_logger import debug_log_error, is_debug_mode
from src.ui.variable_sorting import sort_variables, get_sort_mode_label


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

    def set_title(self, title):
        """Update the title in the top border.

        Args:
            title: New title text
        """
        self.title = title
        # Recreate the top border with new title
        if title:
            title_text = urwid.Text(f'── {title} ', wrap='clip')
            fill_text = urwid.Text('─' * 200, wrap='clip')
            top_border = urwid.Columns([
                ('pack', title_text),
                fill_text
            ], dividechars=0)
        else:
            top_border = urwid.Text('─' * 200, wrap='clip')

        # Get the pile and update the top border
        pile = self._w
        pile.contents[0] = (top_border, ('pack', None))


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


class InputDialog(urwid.WidgetWrap):
    """A popup dialog for text input using urwid signals."""
    signals = ['close']

    def __init__(self, prompt, initial=""):
        self.edit = urwid.Edit(caption=prompt, edit_text=initial)

        pile = urwid.Pile([
            urwid.Text("Press Enter to submit, ESC to cancel"),
            urwid.Divider(),
            self.edit,
        ])

        fill = urwid.Filler(pile, valign='top')
        box = urwid.LineBox(fill, title="Input Required")
        super().__init__(urwid.AttrMap(box, 'body'))

    def keypress(self, size, key):
        if key == ENTER_KEY:
            urwid.emit_signal(self, 'close', self.edit.get_edit_text())
            return None
        elif key == ESC_KEY:
            urwid.emit_signal(self, 'close', None)
            return None
        return super().keypress(size, key)


class YesNoDialog(urwid.WidgetWrap):
    """A popup dialog for yes/no questions using urwid signals."""
    signals = ['close']

    def __init__(self, title, message):
        self.title = title
        text = urwid.Text(message)

        pile = urwid.Pile([
            urwid.Text("Press 'y' for Yes, 'n' for No, ESC to cancel"),
            urwid.Divider(),
            text,
        ])

        fill = urwid.Filler(pile, valign='top')
        box = urwid.LineBox(fill, title=title)
        super().__init__(urwid.AttrMap(box, 'body'))

    def selectable(self):
        """Make this widget selectable so it receives keypresses."""
        return True

    def keypress(self, size, key):
        if key in ('y', 'Y'):
            urwid.emit_signal(self, 'close', True)
            return None
        elif key in ('n', 'N', 'esc'):
            urwid.emit_signal(self, 'close', False)
            return None
        return None  # Consume all other keys


class ProgramEditorWidget(urwid.WidgetWrap):
    """3-field program editor widget for BASIC programs.

    Display format: "S<linenum> CODE" where:
    - Field 1 (1 char): Status (●=breakpoint, ?=error, space=normal)
    - Field 2 (variable width): Line number (any number of digits, no padding)
    - Field 3 (rest of line): Program text (BASIC code)

    Line numbers use as many digits as needed (10, 100, 1000, 10000, etc.) rather
    than fixed-width formatting. This maximizes screen space for code.
    """

    def __init__(self):
        """Initialize the program editor."""
        # Program lines storage: {line_num: code_text}
        self.lines = {}
        # Breakpoints: set of line numbers
        self.breakpoints = set()
        # Errors: {line_num: error_message}
        self.errors = {}

        # Auto-numbering settings (load from settings system)
        from src.settings import get
        self.auto_number_start = get('auto_number_start')
        self.auto_number_increment = get('auto_number_step')
        self.auto_number_enabled = get('auto_number')

        # Load config file if it exists (for backwards compatibility)
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

        # For tracking line number changes to trigger auto-sort
        self._saved_line_num = None  # Save line number when entering a line, check on exit

        # For deferred processing after input completes (paste operations)
        self._needs_parse = False  # Flag: lines need parsing (reformat pasted BASIC code)
        self._needs_sort = False  # Flag: lines need sorting when idle (typing in line number area)
        self._loop = None  # Will be set by CursesBackend after loop creation
        self._idle_handle = None  # Handle for enter_idle callback

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

    def _parse_line_number(self, line):
        """Extract line number from display line.

        Format: "SNN CODE" where S=status, NN=line number (variable width)

        This finds the last valid line number before code starts. Each number must be
        followed by a space to be considered a line number (not part of code).

        Examples:
        - " 10 PRINT" → returns 10 (single line number)
        - " 10 20 PRINT" → returns 20 (last of multiple numbers)
        - " 100 FOR I=1 TO 10" → returns 100 (FOR starts code, 1 is in code)
        - " 10" → returns 10 (number with no code yet)

        Args:
            line: Display line string

        Returns:
            tuple: (line_number, code_start_col) or (None, None) if no line number
        """
        if len(line) < 3:  # Need at least status + digit + space
            return None, None

        # Loop to find all line numbers at the start, keep the last one
        pos = 1  # Start after status character
        last_line_num = None
        last_code_start = None

        while pos < len(line):
            # Skip spaces
            while pos < len(line) and line[pos] == ' ':
                pos += 1

            if pos >= len(line):
                break

            # Try to parse a number
            if not line[pos].isdigit():
                # Hit non-digit, we're at the code now
                break

            # Extract the number
            num_start = pos
            while pos < len(line) and line[pos].isdigit():
                pos += 1

            # Must be followed by space to be a line number
            if pos < len(line) and line[pos] == ' ':
                try:
                    last_line_num = int(line[num_start:pos])
                    # Code starts after this number and its following spaces
                    code_pos = pos
                    while code_pos < len(line) and line[code_pos] == ' ':
                        code_pos += 1
                    last_code_start = code_pos
                    # Continue loop to see if there's another number
                except ValueError:
                    break
            else:
                # Number not followed by space, we're at the code
                break

        if last_line_num is not None:
            return last_line_num, last_code_start

        return None, None

    def _find_last_line_number(self):
        """Find the highest line number in the editor.

        Returns:
            tuple: (line_number, code_start_col) of the last (highest) numbered line,
                   or (None, None) if no lines found
        """
        current_text = self.edit_widget.get_edit_text()
        lines = current_text.split('\n')

        last_line_number = None
        last_code_start = None

        for line in lines:
            line_num, code_start = self._parse_line_number(line)
            if line_num is not None:
                if last_line_number is None or line_num > last_line_number:
                    last_line_number = line_num
                    last_code_start = code_start

        return last_line_number, last_code_start

    def keypress(self, size, key):
        """Handle key presses for column-aware editing and auto-numbering.

        Format: "S<linenum> CODE" (where <linenum> is variable width)
        - Column 0: Status (●, ?, space) - read-only
        - Columns 1+: Line number (variable width) - editable
        - After line number: Space
        - After space: Code - editable

        Note: Methods like _sort_and_position_line use a default target_column of 7,
        which assumes typical line numbers (status=1 char + number=5 digits + space=1 char).
        This is an approximation since line numbers have variable width.
        """
        # FAST PATH: For normal printable characters, bypass editor-specific processing
        # (column protection, line number tracking, focus management) for responsive typing.
        # Note: Syntax checking only happens on special keys (below), not during normal typing.
        if len(key) == 1 and key >= ' ' and key <= '~':
            return super().keypress(size, key)

        # For special keys (non-printable), we DO process them below to handle
        # cursor navigation, protection of status column, etc.

        # Get current cursor position (only for special keys)
        current_text = self.edit_widget.get_edit_text()
        cursor_pos = self.edit_widget.edit_pos

        # Find which line we're on and position within that line
        text_before_cursor = current_text[:cursor_pos]
        line_num = text_before_cursor.count('\n')

        # Fast calculation: find last newline position instead of summing all lines
        last_newline_pos = text_before_cursor.rfind('\n')
        if last_newline_pos >= 0:
            col_in_line = cursor_pos - last_newline_pos - 1
        else:
            col_in_line = cursor_pos

        # Still need lines array for other operations
        lines = current_text.split('\n')

        # Check if pressing a control key or navigation key
        is_control_key = key.startswith('ctrl ') or key in ['tab', 'enter', 'esc']
        is_updown_arrow = key in ['up', 'down']  # Up/down move to different lines
        is_leftright_arrow = key in ['left', 'right']  # Left/right stay on same line
        is_arrow_key = is_updown_arrow or is_leftright_arrow
        is_other_nav_key = key in ['page up', 'page down', 'home', 'end']

        # Handle Tab specially - it switches focus between editor and output
        # We need to check line number changes before Tab takes effect
        is_tab = (key == TAB_KEY)

        # Check syntax when pressing control keys, navigation keys, or switching focus
        # (Not during normal typing - avoids annoying errors for incomplete lines)
        # This includes: Ctrl+X commands, up/down arrows, page up/down, home/end, and Tab
        if is_control_key or is_updown_arrow or is_other_nav_key or is_tab:
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
                # Fast calculation: find last newline position
                last_newline_pos = text_before_cursor.rfind('\n')
                if last_newline_pos >= 0:
                    col_in_line = cursor_pos - last_newline_pos - 1
                else:
                    col_in_line = cursor_pos

        # Check if line number changed and sort if navigating away
        if is_control_key or is_other_nav_key or is_updown_arrow or is_tab:
            # About to navigate - check if line number changed
            if line_num < len(lines):
                line = lines[line_num]
                current_line_num, code_start = self._parse_line_number(line)

                # If line number changed from when we entered this line, sort
                if current_line_num is not None and self._saved_line_num is not None:
                    if current_line_num != self._saved_line_num:
                        # Line number changed - sort lines
                        self._sort_and_position_line(lines, line_num, target_column=col_in_line)
                        # After sorting, save the new line number for next navigation
                        # (the line may have moved, so parse again)
                        current_text = self.edit_widget.get_edit_text()
                        cursor_pos = self.edit_widget.edit_pos
                        text_before_cursor = current_text[:cursor_pos]
                        line_num = text_before_cursor.count('\n')
                        lines = current_text.split('\n')
                        if line_num < len(lines):
                            self._saved_line_num, _ = self._parse_line_number(lines[line_num])
                        return super().keypress(size, key)

        # Handle backspace key to protect separator space and status column
        if key == BACKSPACE_KEY:
            if line_num < len(lines):
                line = lines[line_num]
                line_num_parsed, code_start = self._parse_line_number(line)

                if line_num_parsed is not None:
                    # If at code area start (right after space), don't delete the space
                    if col_in_line == code_start:
                        return None
                    # If at space after line number, delete last digit of line number
                    elif col_in_line == code_start - 1:
                        # Let normal backspace work - it will delete the space
                        # Then the line number and code will be adjacent, which is fine
                        pass

                # Don't allow backspace at column 0 (status column)
                if col_in_line == 0:
                    return None

        # Prevent typing in status column (column 0)
        if col_in_line == 0 and len(key) == 1 and key.isprintable():
            # Move cursor to line number column (column 1)
            new_cursor_pos = cursor_pos + 1
            self.edit_widget.set_edit_pos(new_cursor_pos)
            # Let key be processed at new position
            return super().keypress(size, key)

        # Handle Enter key with auto-numbering
        if key == 'enter' and self.auto_number_enabled:
            # Parse current line number (variable width)
            current_line_number = None
            if line_num < len(lines):
                line = lines[line_num]
                line_num_parsed, code_start = self._parse_line_number(line)
                if line_num_parsed is not None:
                    current_line_number = line_num_parsed

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
                if len(display_line) >= 3:  # At least status + 1-digit + space
                    try:
                        parsed_num, _ = self._parse_line_number(display_line)
                        if parsed_num is not None:
                            existing_line_nums.add(parsed_num)
                    except:
                        pass

            # Find next available number that doesn't collide
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
            # Note: Auto-numbering stops at 99999 for display consistency, but manual
            # entry of higher line numbers is not prevented by _parse_line_number().
            # This is intentional - auto-numbering uses conservative limits while
            # manual entry allows flexibility.
            attempts = 0
            while next_num in existing_line_nums or next_num >= max_allowed:
                next_num += self.auto_number_increment
                attempts += 1
                if next_num >= 99999 or attempts > 10:
                    self._parent_ui.show_yesno_popup(
                        "No Room",
                        f"No room to insert line after {current_line_number}.\n\n"
                        f"Would you like to renumber the program to make room?",
                        lambda response: self._on_auto_number_renumber_response(response)
                    )
                    return None

            # Format new line: " NN " (with status space)
            new_line_prefix = f"\n {next_num} "

            # Insert newline and prefix at end of current line
            current_text = self.edit_widget.get_edit_text()
            cursor_pos = self.edit_widget.edit_pos
            new_text = current_text[:cursor_pos] + new_line_prefix + current_text[cursor_pos:]
            self.edit_widget.set_edit_text(new_text)
            self.edit_widget.set_edit_pos(cursor_pos + len(new_line_prefix))

            # Update next_auto_line_num for next time
            self.next_auto_line_num = next_num + self.auto_number_increment

            # Set flag for deferred parsing (reformats pasted BASIC code)
            self._needs_parse = True

            return None

        # Handle Enter when auto-numbering disabled
        if key == ENTER_KEY:
            # Set flag for deferred parsing (reformats pasted BASIC code)
            self._needs_parse = True
            # Let Enter be processed normally (insert newline)
            return super().keypress(size, key)

        # Check if this is a control key we don't handle - pass to unhandled_input
        # Editor handles: arrows, backspace, delete, home, end, enter, tab
        # Pass through: All ctrl keys except those handled above
        if key.startswith('ctrl '):
            # Let unhandled_input handle all control keys
            return key

        # Prevent down arrow from moving past last line (causes cursor to disappear)
        if key == DOWN_KEY:
            current_text = self.edit_widget.get_edit_text()
            cursor_pos = self.edit_widget.edit_pos
            text_before_cursor = current_text[:cursor_pos]
            line_num = text_before_cursor.count('\n')
            total_lines = current_text.count('\n')

            # If already on last line, don't process down arrow
            if line_num >= total_lines:
                return None

        # Let parent handle the key (allows arrows, backspace, etc.)
        result = super().keypress(size, key)

        # After navigation, save the current line number for comparison on next navigation
        if is_arrow_key or is_other_nav_key:
            current_text = self.edit_widget.get_edit_text()
            cursor_pos = self.edit_widget.edit_pos
            text_before_cursor = current_text[:cursor_pos]
            line_num = text_before_cursor.count('\n')
            lines = current_text.split('\n')
            if line_num < len(lines):
                self._saved_line_num, _ = self._parse_line_number(lines[line_num])

        return result

    def _on_auto_number_renumber_response(self, response):
        """Handle response to renumber prompt during auto-numbering."""
        if response:
            # Save editor to program, renumber, and refresh
            self._parent_ui._save_editor_to_program()
            self._parent_ui._renumber_lines()
        # If response is False/None, just return (user declined)

    def _format_line(self, line_num, code_text, highlight_stmt=None, statements=None):
        """Format a single program line with status, line number, and code.

        Args:
            line_num: Line number
            code_text: BASIC code text
            highlight_stmt: Optional statement index to highlight (0-based)
            statements: Optional list of statement nodes for line (needed for highlight)

        Returns:
            Formatted string or urwid markup: "S<num> CODE" where S is status (1 char),
            <num> is the line number (variable width, no padding), and CODE is the program text.
            May include urwid markup tuples for statement highlighting.
        """
        # Status column (1 char)
        if line_num in self.breakpoints:
            status = '●'
        elif line_num in self.errors:
            status = '?'
        else:
            status = ' '

        # Line number column (variable width, no padding)
        line_num_str = f"{line_num}"

        # Prefix: status + line_num + space
        prefix = f"{status}{line_num_str} "

        # If no highlighting requested, return simple string
        if highlight_stmt is None or statements is None:
            return prefix + code_text

        # Find statement boundaries for highlighting
        try:
            if highlight_stmt < 0 or highlight_stmt >= len(statements):
                # Invalid statement index, return without highlight
                return prefix + code_text

            # Split code by colons to find statement boundaries
            parts = code_text.split(':')

            # If statement index is out of range for parts, highlight whole line
            if highlight_stmt >= len(parts):
                return [prefix, ('active_stmt', code_text)]

            # Build the result with the highlighted statement
            result = [prefix]

            for i, part in enumerate(parts):
                if i > 0:
                    result.append(':')  # Add back the colon separator

                if i == highlight_stmt:
                    # This is the statement to highlight
                    result.append(('active_stmt', part))
                else:
                    # Normal text
                    result.append(part)

            return result

        except Exception:
            # If anything goes wrong, return without highlighting
            return prefix + code_text

    def _update_display(self, highlight_line=None, highlight_stmt=None, statement_table=None):
        """Update the text display with all program lines.

        Args:
            highlight_line: Optional line number to highlight a statement on
            highlight_stmt: Optional statement index to highlight (0-based)
            statement_table: Optional StatementTable for getting statement info
        """
        if not self.lines:
            # Empty program - show line with auto-number prompt
            # Format: "S<num> " where S=status (1 char space), <num>=line# (variable width), space (1)
            display_text = f" {self.next_auto_line_num} "
            # DON'T increment counter here - that happens only on Enter
            # Bug fix: Incrementing here caused next_auto_line_num to advance prematurely,
            # displaying the wrong line number before the user typed anything
        else:
            # Format all lines (with optional highlighting)
            formatted_lines = []
            for line_num in sorted(self.lines.keys()):
                code_text = self.lines[line_num]

                # Check if this line should be highlighted
                if line_num == highlight_line and statement_table:
                    statements = statement_table.get_line_statements(line_num)
                    formatted = self._format_line(line_num, code_text, highlight_stmt, statements)
                else:
                    formatted = self._format_line(line_num, code_text)

                formatted_lines.append(formatted)

            # Join lines - handle both string and markup formats
            if any(isinstance(line, list) for line in formatted_lines):
                # We have markup - need to join carefully
                display_markup = []
                for i, line in enumerate(formatted_lines):
                    if i > 0:
                        display_markup.append('\n')
                    if isinstance(line, list):
                        display_markup.extend(line)
                    else:
                        display_markup.append(line)
                display_text = display_markup
            else:
                # All strings - simple join
                display_text = '\n'.join(formatted_lines)

        # Update the edit widget
        if isinstance(display_text, list):
            # Markup format - convert to plain text string (Edit widget doesn't support markup)
            # Extract just the text from markup tuples: ('attr', 'text') -> 'text'
            plain_text = []
            for item in display_text:
                if isinstance(item, tuple):
                    # ('attr', 'text') -> extract 'text'
                    plain_text.append(item[1])
                else:
                    # Plain string
                    plain_text.append(item)
            self.edit_widget.set_edit_text(''.join(plain_text))
        else:
            # Plain string
            self.edit_widget.set_edit_text(display_text)

        # If empty program, position cursor after line number and space (ready to type code)
        if not self.lines:
            # Display text is " NN " (status + line number + space)
            # Position cursor at end (after the trailing space, ready to type code)
            self.edit_widget.set_edit_pos(len(display_text))

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

        # Position cursor after first line number and space
        if self.lines:
            display_text = self.edit_widget.get_edit_text()
            if display_text:
                # Find first newline or use whole text if one line
                first_line = display_text.split('\n')[0] if '\n' in display_text else display_text
                # Skip status char (1), then digits, then space
                pos = 1  # Skip status char
                while pos < len(first_line) and first_line[pos].isdigit():
                    pos += 1
                if pos < len(first_line) and first_line[pos] == ' ':
                    pos += 1  # Skip space after line number
                self.edit_widget.set_edit_pos(pos)

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
            from src.lexer import Lexer
            from src.parser import Parser
            from src.ast_nodes import RemarkStatementNode
            from src.tokens import TokenType
            from src.lexer import create_keyword_case_manager

            # Tokenize the code
            keyword_mgr = create_keyword_case_manager()
            lexer = Lexer(code_text, keyword_case_manager=keyword_mgr)
            tokens = lexer.tokenize()

            # Reject bare identifiers (the parser treats them as implicit REMs for
            # old BASIC compatibility, but in the editor we want to be stricter).
            # Note: This catches bare identifiers followed by EOF or COLON (e.g., "foo" or "foo:").
            # Bare identifiers followed by other tokens (e.g., "foo + bar") will be caught by the
            # parser as syntax errors. A second check after parsing catches any remaining cases
            # where the parser returned a RemarkStatementNode for an implicit REM.
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
            if not line or len(line) < 3:
                continue

            # Parse line (variable width)
            line_number, code_start = self._parse_line_number(line)
            status = line[0]
            code_area = line[code_start:] if line_number is not None and code_start < len(line) else ""

            # Skip empty code lines
            if not code_area.strip() or line_number is None:
                # Clear error status for empty lines, but preserve breakpoints
                # Note: line_number > 0 check silently skips line 0 if present (not a valid
                # BASIC line number). This avoids setting status for malformed lines.
                # Consistent with _check_line_syntax which treats all empty lines as valid
                if line_number is not None and line_number > 0:
                    new_status = self._get_status_char(line_number, has_syntax_error=False)
                    if status != new_status:
                        lines[i] = new_status + line[1:]
                        changed = True
                continue

            # Check syntax
            is_valid, error_msg = self._check_line_syntax(code_area)

            # Determine correct status based on priority
            if line_number is not None and line_number > 0:
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
        """Display syntax error messages in the output window with context.

        Called by _update_syntax_indicators() during editing to show real-time
        syntax feedback. Errors are displayed immediately as the user types/edits lines.
        """
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

            # FIRST: Check if line starts with a digit (raw pasted BASIC with line numbers)
            # In this context, we assume lines starting with digits are numbered program lines (e.g., "10 PRINT").
            # Note: While BASIC statements can start with digits (numeric expressions), when pasting
            # program code, lines starting with digits are conventionally numbered program lines.
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

                # Reformat with column structure (variable width line numbers)
                if num_str:
                    new_line = f" {num_str} {rest}"
                    lines[i] = new_line
                    changed = True
                continue

            # SECOND: Check lines with column structure
            if len(line) >= 3:
                # Parse to get the actual line number (handles multiple numbers)
                status = line[0]
                linenum_int, code_start_col = self._parse_line_number(line)  # Variable width

                if linenum_int is not None and code_start_col is not None:
                    code_area = line[code_start_col:] if code_start_col < len(line) else ""

                    # Reconstruct line cleanly from parsed components
                    # This removes any extra line numbers that were found during parsing
                    new_line = f"{status}{linenum_int} {code_area}"

                    if new_line != line:
                        lines[i] = new_line
                        changed = True

        # THIRD: Remove empty lines that only have line numbers (no code)
        # This cleans up leftover auto-numbered lines like " 10 " when pasting over them
        filtered_lines = []
        for line in lines:
            if len(line) >= 3:
                status = line[0]
                linenum_int, code_start_col = self._parse_line_number(line)
                if linenum_int is not None and code_start_col is not None:
                    code_area = line[code_start_col:] if code_start_col < len(line) else ""
                    # Keep line if it has code, or if it's the last line (empty line at end is okay)
                    if code_area.strip() or line == lines[-1]:
                        filtered_lines.append(line)
                    else:
                        changed = True  # We're removing an empty line
                else:
                    # No line number parsed, keep the line
                    filtered_lines.append(line)
            else:
                # Short line (< 3 chars), keep it
                filtered_lines.append(line)

        if changed:
            return '\n'.join(filtered_lines)
        else:
            return text

    def _on_enter_idle(self):
        """Called by urwid when entering idle state (after all input processed).

        This is where expensive operations happen: parsing and sorting.
        Auto-numbering happens immediately on each Enter in keypress().
        urwid automatically redraws screen after this returns.
        """
        # Check if any work is needed
        if not self._needs_parse and not self._needs_sort:
            return

        # Get current state
        current_text = self.edit_widget.get_edit_text()
        cursor_pos = self.edit_widget.edit_pos

        # Step 1: Parse and reformat lines with numbers in code area
        # (This handles pasted BASIC code like "10 PRINT")
        if self._needs_parse:
            new_text = self._parse_line_numbers(current_text)
            if new_text != current_text:
                # Text was reformatted - update the editor
                self.edit_widget.set_edit_text(new_text)
                # Try to maintain cursor position (may shift due to reformatting)
                if cursor_pos <= len(new_text):
                    self.edit_widget.set_edit_pos(cursor_pos)
                current_text = new_text
                cursor_pos = self.edit_widget.edit_pos
            self._needs_parse = False

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

                # Sort only if cursor is in line number area (before code starts)
                # Check if we're editing the line number field (not the code)
                line_num_parsed, code_start = self._parse_line_number(lines[line_num])
                if line_num_parsed is not None and 1 <= col_in_line < code_start:
                    self._sort_and_position_line(lines, line_num, target_column=col_in_line)

            self._needs_sort = False

    def _sort_and_position_line(self, lines, current_line_index, target_column=7):
        """Sort lines by line number and position cursor at the moved line.

        Args:
            lines: List of text lines
            current_line_index: Index of line that triggered the sort
            target_column: Column to position cursor at (default: 7). Since line numbers have
                          variable width, this is approximate. The cursor will be positioned
                          at this column or adjusted based on actual line content.
        """
        if current_line_index >= len(lines):
            return

        # Parse all lines into (line_number, full_text) tuples
        parsed_lines = []
        current_line_text = lines[current_line_index]

        for idx, line in enumerate(lines):
            line_num, code_start = self._parse_line_number(line)
            if line_num is not None:
                parsed_lines.append((line_num, line))
            else:
                # If can't parse line number, keep it in original position
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
        # Sanitize character input: clear parity bits and filter control characters
        if len(key) == 1:
            # Clear parity bit
            key = clear_parity(key)

            # Filter invalid characters
            if not is_valid_input_char(key):
                # Block invalid character
                return None

        # Let parent handle keys
        return super().keypress(size, key)


class ImmediateInput(urwid.Edit):
    """Custom Edit widget for immediate mode input that handles Enter key."""

    def __init__(self, caption, on_execute_callback):
        """Initialize immediate input widget.

        Args:
            caption: Text to display before input (e.g., "Ok > ")
            on_execute_callback: Function to call when Enter is pressed
        """
        super().__init__(caption)
        self.on_execute_callback = on_execute_callback

    def keypress(self, size, key):
        """Handle key presses, especially Enter."""
        if key == ENTER_KEY:
            # Execute the command
            if self.on_execute_callback:
                self.on_execute_callback()
            return None  # Consume the key
        else:
            # Sanitize character input: clear parity bits and filter control characters
            if len(key) == 1:
                # Clear parity bit
                key = clear_parity(key)

                # Filter invalid characters
                if not is_valid_input_char(key):
                    # Block invalid character
                    return None

            # Let parent handle other keys
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

        # Recent files manager
        self.recent_files = RecentFilesManager()

        # Auto-save manager
        self.auto_save = AutoSaveManager()

        # UI state
        self.app = None
        self.loop = None
        self.loop_running = False  # Track if event loop has been started
        self.editor = None
        self.output = None
        self.status_bar = None
        self.variables_walker = None
        self.variables_window = None
        self.variables_window_visible = False
        self.variables_sort_mode = 'name'  # 'name', 'accessed', 'written', 'read', 'type', 'value'
        self.variables_sort_reverse = False  # False=ascending, True=descending
        self.variables_filter_text = ""  # Filter text for variables window
        self.stack_walker = None
        self.stack_window = None
        self.stack_window_visible = False

        # Editor state
        # Note: self.editor_lines stores execution state (lines loaded from file for RUN)
        # self.editor.lines (in ProgramEditorWidget) stores the actual editing state
        # These serve different purposes and are synchronized as needed
        self.editor_lines = {}  # line_num -> text for execution (synced from editor)
        self.current_line_num = 10  # Default starting line number
        self.current_filename = None  # Track current filename for Save vs Save As

        # Execution state
        self.running = False
        self.paused_at_breakpoint = False
        self.output_buffer = []

        # Initialize runtime/interpreter for session (reused across runs)
        from src.runtime import Runtime
        from src.interpreter import Interpreter
        from src.resource_limits import create_unlimited_limits
        self.runtime = Runtime({}, {})

        # Create capturing IO handler for execution (created once, reused)
        # Import shared CapturingIOHandler
        from .capturing_io_handler import CapturingIOHandler

        # IO Handler Lifecycle:
        # 1. self.io_handler (CapturingIOHandler) - Used for RUN program execution
        #    Created ONCE here, reused throughout session (NOT recreated in start())
        # 2. immediate_io (OutputCapturingIOHandler) - Used for immediate mode commands
        #    Created here temporarily, then RECREATED in start() with fresh instance each time
        #    OutputCapturingIOHandler is imported from immediate_executor module
        self.io_handler = CapturingIOHandler()

        # Interpreter Lifecycle:
        # Created ONCE here in __init__ and reused throughout the session.
        # The interpreter object itself is NEVER recreated - the same instance is used
        # for the lifetime of the UI session.
        # Note: The immediate_io handler created here is used only for initialization.
        # The Interpreter's IO handler is replaced during program execution (_run_program)
        # to route output to the appropriate widget. ImmediateExecutor (created in start())
        # uses a separate OutputCapturingIOHandler but operates on the same Interpreter instance.
        # Use unlimited limits for immediate mode (runs will use local limits)
        # Rationale: Immediate mode commands (PRINT, LIST, etc.) should not be artificially
        # constrained by resource limits. Program execution (RUN) uses separate runtime state
        # with configurable limits applied at runtime setup in _setup_program().
        immediate_io = OutputCapturingIOHandler()
        self.interpreter = Interpreter(self.runtime, immediate_io, limits=create_unlimited_limits())

        # Set interactive_mode so that line editing (e.g., "50 PRINT") works
        self.interpreter.interactive_mode = self

        # ImmediateExecutor Lifecycle:
        # Created here with an OutputCapturingIOHandler, then recreated in start() with
        # a fresh OutputCapturingIOHandler. The recreation of the executor in start()
        # provides a fresh IO handler for each UI session, but does NOT clear the
        # interpreter's execution state (variables, execution position, etc).
        # Note: The interpreter (self.interpreter) is created once here and reused
        # across all UI sessions - only the executor wrapper and its IO handler are recreated.
        self.immediate_executor = ImmediateExecutor(self.runtime, self.interpreter, immediate_io)

        # Immediate mode UI widgets
        self.immediate_input = None
        self.immediate_status = None

        # Output maximize state (for full-screen games)
        self.output_maximized = False

        # Create the UI layout immediately so widgets exist
        # (but don't start the loop yet - that happens in start())
        self._create_ui()

    def _save_editor_to_program(self):
        """Save editor content back to program.

        Parses lines from editor and saves them to program manager.
        Returns True if successful, False if errors occurred.
        """
        if not self.editor:
            return False

        # Clear current program
        self.program.clear()

        # Parse each line from editor
        had_errors = False
        for line_num, code_text in self.editor.lines.items():
            # Reconstruct full line with line number
            full_line = f"{line_num} {code_text}"
            success, error = self.program.add_line(line_num, full_line)
            if not success:
                # Mark error in editor
                self.editor.errors[line_num] = error
                had_errors = True
            else:
                # Clear any previous error
                if line_num in self.editor.errors:
                    del self.editor.errors[line_num]

        return not had_errors

    def _renumber_lines(self):
        """Renumber program lines with default increment (10, 10)."""
        from src.ui.ui_helpers import renum_program

        try:
            # Save editor to program first
            self._save_editor_to_program()

            # Renumber with default args (start=10, step=10)
            old_lines, line_map = renum_program(
                self.program,
                "",  # Empty args = use defaults
                self._renum_statement,
                runtime=None
            )

            # Refresh editor from renumbered program
            self._refresh_editor()

        except Exception as e:
            # Silently handle errors - user already said yes to renumber
            pass

    def _renum_statement(self, stmt, line_map):
        """Update line number references in a statement node.

        Args:
            stmt: Statement node to update
            line_map: dict mapping old line numbers to new line numbers
        """
        from src.ui.ui_helpers import renum_statement_helper
        renum_statement_helper(stmt, line_map)

    def _refresh_editor(self):
        """Refresh the editor display from program manager.

        Called by immediate executor after adding/deleting lines via commands like "20 PRINT".
        Syncs the editor widget's line storage with the program manager's lines.
        """
        if not self.editor:
            return

        # Sync editor lines from program manager
        self.editor.lines.clear()
        for line_num, line_text in self.program.lines.items():
            # line_text is already a string like "20 PRINT j"
            # Extract just the code part (after line number and space)
            import re
            match = re.match(r'^\d+\s+(.*)', line_text)
            if match:
                code_only = match.group(1)
            else:
                code_only = line_text
            self.editor.lines[line_num] = code_only

        # Update the display
        self.editor._update_display()

        # Clean up any empty auto-numbered lines left in the editor
        current_text = self.editor.edit_widget.get_edit_text()
        new_text = self.editor._parse_line_numbers(current_text)
        if new_text != current_text:
            self.editor.edit_widget.set_edit_text(new_text)

    def start(self):
        """Start the urwid-based curses UI main loop."""
        # UI already created in __init__, just start the loop

        # Initialize immediate mode executor
        # Immediate mode: executes single BASIC statements/commands without line numbers,
        # used for interactive commands at the immediate input field (bottom of UI).
        # This is separate from program execution (RUN command), which runs numbered lines.
        immediate_io = OutputCapturingIOHandler()
        self.immediate_executor = ImmediateExecutor(self.runtime, self.interpreter, immediate_io)

        # Sync any pre-loaded program to the editor
        # (e.g., when loading a file from command line)
        if self.program.has_lines():
            if not self.editor_lines:
                self._sync_program_to_editor()
            # Else: editor already has content, don't overwrite

        # Set up signal handling for clean exit
        import signal

        def handle_sigint(_signum, _frame):
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
        self.loop.set_alarm_in(0, lambda _loop, _user_data: setup_cursor())

        # Run the main loop
        try:
            self.loop_running = True
            self.loop.run()
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            pass
        finally:
            self.loop_running = False
            # Cleanup
            self._cleanup()

    def _cleanup(self):
        """Clean up resources before exit."""
        # Stop autosave
        if hasattr(self, 'auto_save'):
            self.auto_save.stop_autosave()
            # Clean up old autosaves (7+ days)
            self.auto_save.cleanup_old_autosaves()

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
        if hasattr(self, 'loop') and self.loop and self.loop_running:
            try:
                # Remove all alarms
                for alarm in list(self.loop.event_loop.alarm_list):
                    self.loop.remove_alarm(alarm)
            except:
                pass

    def _create_ui(self):
        """Create the urwid UI layout."""
        # Create widgets
        self.menu_bar = InteractiveMenuBar(self)
        # Toolbar removed from UI layout - use Ctrl+U interactive menu bar instead for keyboard navigation
        self.editor = ProgramEditorWidget()
        self.editor._parent_ui = self  # Give editor access to parent UI for dialogs

        # Create scrollable output window using ListBox
        self.output_walker = urwid.SimpleFocusListWalker([])
        self.output = urwid.ListBox(self.output_walker)

        # Pass output_walker to editor for displaying syntax errors
        self.editor._output_walker = self.output_walker

        # Create variables window
        self.variables_walker = urwid.SimpleFocusListWalker([])
        self.variables_window = urwid.ListBox(self.variables_walker)

        # Create stack window (call stack and loops)
        self.stack_walker = urwid.SimpleFocusListWalker([])
        self.stack_window = urwid.ListBox(self.stack_walker)

        self.status_bar = urwid.Text(STATUS_BAR_SHORTCUTS)

        # Create editor frame with top/left border only (no bottom/right space reserved)
        self.editor_frame = TopLeftBox(
            urwid.Filler(self.editor, valign='top'),
            title="Editor"
        )

        # Create variables frame (initially hidden)
        self.variables_frame = TopLeftBox(
            self.variables_window,
            title=f"Variables ({key_to_display(VARIABLES_KEY)} to toggle)"
        )

        # Create stack frame (initially hidden)
        self.stack_frame = TopLeftBox(
            self.stack_window,
            title=f"Execution Stack ({key_to_display(STEP_LINE_KEY)} to toggle)"
        )

        # Create output frame with top/left border only (no bottom/right space reserved)
        # ListBox doesn't need Filler since it handles its own scrolling
        # Create immediate mode input field with Enter handler
        self.immediate_input = ImmediateInput("Ok > ", self._execute_immediate)

        # Merge output and immediate mode into single pane
        # This matches real BASIC where everything appears in one output area
        self.output_and_immediate_pile = urwid.Pile([
            ('weight', 1, self.output),  # Scrollable output (program + immediate history)
            ('pack', self.immediate_input)
        ])
        # Set focus to immediate input by default when in output pane
        self.output_and_immediate_pile.focus_position = 1

        self.output_frame = TopLeftBox(
            self.output_and_immediate_pile,
            title="Output"
        )

        # Create layout - menu bar at top, editor, output (with immediate at bottom), status bar at bottom
        # Store as instance variable so we can modify it when toggling variables window
        self.pile = urwid.Pile([
            ('pack', self.menu_bar),
            ('weight', 1, self.editor_frame),
            ('weight', 1, self.output_frame),
            ('pack', self.status_bar)
        ])

        # Set focus to the output/immediate pane by default (like real BASIC)
        # This allows immediate commands to be typed right away
        self.pile.focus_position = 2

        # Create main widget with keybindings
        self.base_widget = urwid.AttrMap(self.pile, 'body')

        # Dialog stack for handling nested dialogs
        self.dialog_stack = []

        # Set up the main loop with cursor visible
        self.loop = urwid.MainLoop(
            self.base_widget,
            palette=self._get_palette(),
            unhandled_input=self._handle_input,
            handle_mouse=False
        )

        # Pass loop reference to editor
        self.editor._loop = self.loop

        # Register enter_idle callback for deferred processing (parse, sort, auto-number after paste)
        self.editor._idle_handle = self.loop.event_loop.enter_idle(self.editor._on_enter_idle)

    def _get_palette(self):
        """Get the color palette for the UI."""
        return [
            ('body', 'white', 'black'),
            ('header', 'white,bold', 'dark blue'),
            ('footer', 'white', 'dark blue'),
            # Use bright yellow for focus - this affects cursor visibility
            ('focus', 'black', 'yellow', 'standout'),
            ('error', 'light red', 'black'),
            # Highlight for active statement during step debugging
            ('active_stmt', 'black', 'light cyan'),
            # Immediate mode status indicators
            ('immediate_ok', 'light green,bold', 'black'),
            ('immediate_disabled', 'light red,bold', 'black'),
            # Help system link highlighting
            ('link', 'light cyan,bold', 'black'),
            # Dimmed text for hints
            ('dim', 'dark gray', 'black'),
            # Keymap widget
            ('title', 'light cyan,bold', 'black'),
            ('category', 'yellow,bold', 'black'),
            ('help_text', 'dark gray', 'black'),
        ]

    def show_input_popup(self, prompt, callback, initial=""):
        """Show an input dialog using Overlay and call callback with result.

        This uses a stack-based approach so dialogs can be nested.

        Args:
            prompt: The prompt text to display
            callback: Function to call with result (str or None for cancel)
            initial: Initial text in the input field
        """
        dialog = InputDialog(prompt, initial)

        def on_close(result):
            # Pop this dialog from the stack and get saved state
            saved_focus = None
            saved_input_handler = None
            if self.dialog_stack:
                popped = self.dialog_stack.pop()
                saved_focus = popped.get('saved_focus')
                saved_input_handler = popped.get('saved_input_handler')

            # Restore previous widget (either base or previous dialog)
            if self.dialog_stack:
                # There's still a dialog on the stack, show it
                self.loop.widget = self.dialog_stack[-1]['overlay']
            else:
                # No more dialogs, show base widget
                self.loop.widget = self.base_widget

                # Restore the input handler (e.g., back to menu_input or _handle_input)
                if saved_input_handler is not None:
                    self.loop.unhandled_input = saved_input_handler

                # Restore focus to the saved position
                if saved_focus is not None:
                    try:
                        self.pile.focus_position = saved_focus
                    except:
                        pass

            # Call the callback
            callback(result)

        urwid.connect_signal(dialog, 'close', on_close)

        # Save current focus position before showing dialog
        saved_focus = None
        try:
            saved_focus = self.pile.focus_position
        except:
            pass

        # Save current input handler so it can be restored
        saved_input_handler = self.loop.unhandled_input

        # Get the current widget to overlay on top of
        base_for_overlay = self.loop.widget

        # Create overlay
        overlay = urwid.Overlay(
            dialog,
            base_for_overlay,
            align='center',
            width=60,
            valign='middle',
            height=10
        )

        # Push to stack with saved focus and input handler
        self.dialog_stack.append({
            'overlay': overlay,
            'dialog': dialog,
            'callback': callback,
            'saved_focus': saved_focus,
            'saved_input_handler': saved_input_handler
        })

        # Show the overlay
        self.loop.widget = overlay

    def show_yesno_popup(self, title, message, callback):
        """Show a yes/no dialog using Overlay and call callback with result.

        This uses a stack-based approach so dialogs can be nested.

        Args:
            title: The dialog title
            message: The message text to display
            callback: Function to call with result (True/False)
        """
        dialog = YesNoDialog(title, message)

        def on_close(result):
            # Pop this dialog from the stack and get saved state
            saved_focus = None
            saved_input_handler = None
            if self.dialog_stack:
                popped = self.dialog_stack.pop()
                saved_focus = popped.get('saved_focus')
                saved_input_handler = popped.get('saved_input_handler')

            # Restore previous widget (either base or previous dialog)
            if self.dialog_stack:
                # There's still a dialog on the stack, show it
                self.loop.widget = self.dialog_stack[-1]['overlay']
            else:
                # No more dialogs, show base widget
                self.loop.widget = self.base_widget

                # Restore the input handler (e.g., back to menu_input or _handle_input)
                if saved_input_handler is not None:
                    self.loop.unhandled_input = saved_input_handler

                # Restore focus to the saved position
                if saved_focus is not None:
                    try:
                        self.pile.focus_position = saved_focus
                    except:
                        pass

            # Call the callback
            callback(result)

        urwid.connect_signal(dialog, 'close', on_close)

        # Save current focus position before showing dialog
        saved_focus = None
        try:
            saved_focus = self.pile.focus_position
        except:
            pass

        # Save current input handler so it can be restored
        saved_input_handler = self.loop.unhandled_input

        # Get the current widget to overlay on top of
        base_for_overlay = self.loop.widget

        # Create overlay
        overlay = urwid.Overlay(
            dialog,
            base_for_overlay,
            align='center',
            width=60,
            valign='middle',
            height=15
        )

        # Push to stack with saved focus and input handler
        self.dialog_stack.append({
            'overlay': overlay,
            'dialog': dialog,
            'callback': callback,
            'saved_focus': saved_focus,
            'saved_input_handler': saved_input_handler
        })

        # Show the overlay
        self.loop.widget = overlay

    def _handle_input(self, key):
        """Handle global keyboard shortcuts."""
        if (QUIT_KEY and key == QUIT_KEY) or key == QUIT_ALT_KEY:
            # Quit (QUIT_KEY is menu-only, but QUIT_ALT_KEY is Ctrl+C)
            raise urwid.ExitMainLoop()

        elif key == TAB_KEY:
            # Toggle between editor (position 1) and output (position 2)
            # self.pile is the actual pile widget we created
            if self.pile.focus_position == 1:
                # Switch to output/immediate
                self.pile.focus_position = 2
            else:
                # Switch back to editor
                self.pile.focus_position = 1
            # Force screen redraw to ensure cursor appears in newly focused pane
            if self.loop and self.loop_running:
                self.loop.draw_screen()
            # Keep the startup status bar message (don't change it)
            return None

        elif key == MENU_KEY:
            # Activate interactive menu bar
            self._activate_menu()

        elif key == HELP_KEY:
            # Show help
            self._show_help()

        elif key == SETTINGS_KEY:
            # Show settings
            self._show_settings()

        elif key == MAXIMIZE_OUTPUT_KEY:
            # Toggle output maximize (for full-screen games)
            self._toggle_output_maximize()

        elif key == RUN_KEY:
            # Run program
            self._run_program()

        elif key == STEP_LINE_KEY:
            # Ctrl+L = Step Line (execute all statements on current line)
            self._debug_step_line()

        elif key == OPEN_KEY:
            # Ctrl+O = Open/Load program
            self._load_program()

        elif key == NEW_KEY:
            # New program
            self._new_program()

        elif key == SAVE_KEY:
            # Save program
            self._save_program()

        elif key == BREAKPOINT_KEY:
            # Toggle breakpoint on current line
            self._toggle_breakpoint_current_line()

        elif key == CLEAR_BREAKPOINTS_KEY:
            # Clear all breakpoints
            self._clear_all_breakpoints()

        elif key == VARIABLES_KEY:
            # Toggle variables window
            self._toggle_variables_window()

        elif STACK_KEY and key == STACK_KEY:
            # Toggle execution stack window (only if STACK_KEY is defined)
            self._toggle_stack_window()

        elif key == VARS_SORT_MODE_KEY and self.variables_window_visible:
            # Cycle sort mode in variables window
            self._cycle_variables_sort_mode()

        elif key == VARS_SORT_DIR_KEY and self.variables_window_visible:
            # Toggle sort direction in variables window
            self._toggle_variables_sort_direction()

        elif key == VARS_EDIT_KEY and self.variables_window_visible:
            # Edit selected variable value
            self._edit_selected_variable()

        elif key == 'enter' and self.variables_window_visible:
            # Edit selected variable value (Enter key)
            self._edit_selected_variable()

        elif key == VARS_FILTER_KEY and self.variables_window_visible:
            # Set filter for variables window
            self._set_variables_filter()

        elif key == VARS_CLEAR_KEY and self.variables_window_visible:
            # Clear filter for variables window
            self._clear_variables_filter()

        elif key == 'esc' and self.variables_window_visible:
            # Close variables window with ESC
            self._toggle_variables_window()
            return None

        elif key == 'esc' and self.stack_window_visible:
            # Close stack window with ESC
            self._toggle_stack_window()
            return None

        elif key == DELETE_LINE_KEY:
            # Delete current line
            self._delete_current_line()

        elif key == INSERT_LINE_KEY:
            # Smart insert line between current and next
            self._smart_insert_line()

        elif key == RENUMBER_KEY:
            # Renumber all lines
            self._renumber_lines()

        elif key == CONTINUE_KEY:
            # Continue execution (from breakpoint/pause)
            self._debug_continue()

        elif key == STEP_KEY:
            # Step Statement - execute one statement
            self._debug_step()

        elif key == STOP_KEY:
            # Stop execution
            self._debug_stop()

        # Note: Clear output removed from keyboard shortcuts (no dedicated key)
        # Clear output still available via menu: Ctrl+U -> Output -> Clear Output

    def _clear_output(self):
        """Clear the output pane."""
        self.output_buffer.clear()
        self._update_output()
        self.status_bar.set_text("Output cleared")

    def _update_status_with_errors(self, base_message="Ready"):
        """Update status bar with error count if there are syntax errors."""
        if self.editor.errors:
            error_count = len(self.editor.errors)
            plural = "s" if error_count > 1 else ""
            self.status_bar.set_text(f"{base_message} - {error_count} syntax error{plural} in program")
        else:
            self.status_bar.set_text(f"{base_message} - {key_to_display(HELP_KEY)} help  {key_to_display(MENU_KEY)} menu")

    def _debug_continue(self):
        """Continue execution from paused/breakpoint state."""
        if not self.interpreter:
            self._append_to_output("No program running")
            return

        try:
            state = self.interpreter.get_state()
            if not self.runtime.pc.is_running() and not state.error_info:
                # Clear statement highlighting when continuing
                self.editor._update_display()
                # Continue from breakpoint - resume tick execution
                # (execution will show output in output window, immediate mode updates via tick loop)
                # Schedule next tick to resume execution
                self.loop.set_alarm_in(0.01, lambda _loop, _user_data: self._execute_tick())
            else:
                # Not paused - inform user
                self._append_to_output("Not paused")
        except Exception as e:
            self._append_to_output(f"Continue error: {e}")

    def _debug_step(self):
        """Execute one statement and pause (single-step debugging)."""
        # Check if we need to setup/restart the program
        needs_setup = (not self.interpreter or
                      not hasattr(self.interpreter, 'state') or
                      not self.interpreter.state or
                      self.runtime.pc.halted())

        if needs_setup:
            # No program running or program completed - set it up without starting async execution
            if not self._setup_program():
                return  # Setup failed (error already displayed)
            # Fall through to execute first step

        try:
            # Execute one statement
            # (output shows in output window, immediate mode status updates after step completes)
            state = self.interpreter.tick(mode='step_statement', max_statements=1)

            # Collect any output
            new_output = self.io_handler.get_and_clear_output()
            if new_output:
                self.output_buffer.extend(new_output)
                self._update_output()

            # Update editor display with statement highlighting
            if not self.runtime.pc.is_running() and not state.error_info and state.current_line:
                # Highlight the current statement in the editor
                pc = self.runtime.pc
                self.editor._update_display(
                    highlight_line=state.current_line,
                    highlight_stmt=pc.stmt_offset if pc else 0,
                    statement_table=self.runtime.statement_table
                )

                # Update variables window if visible
                if self.variables_window_visible:
                    self._update_variables_window()

                # Update stack window if visible
                if self.stack_window_visible:
                    self._update_stack_window()

            # Show where we halted (if not an error and not completed)
            if not self.runtime.pc.is_running() and not state.error_info:
                pc = self.runtime.pc
                # Show PC in line.statement format (e.g., "10.2")
                pc_display = f"{pc.line_num}.{pc.stmt_offset}" if pc and not pc.halted() else str(state.current_line)
                # Show current line with code
                line_code = self.editor_lines.get(state.current_line, "")
                self.output_buffer.append(f"→ Paused at {pc_display}: {line_code}")
                self._update_output()
                self.status_bar.set_text(f"Paused at {pc_display} - {key_to_display(STEP_KEY)}=Step Stmt, {key_to_display(STEP_LINE_KEY)}=Step Line, {key_to_display(CONTINUE_KEY)}=Continue")
                self._update_immediate_status()
            elif state.error_info:
                # Clear highlighting on error
                self.editor._update_display()
                error_msg = state.error_info.error_message
                line_num = state.error_info.pc.line_num
                self.output_buffer.append(f"Error at line {line_num}: {error_msg}")
                self._update_output()
                # Update immediate status (allows immediate mode again) - error message is in output
                self._update_immediate_status()
            elif not self.runtime.pc.is_running():
                # Clear highlighting when done
                self.editor._update_display()
                self.output_buffer.append("Program completed")
                self._update_output()
                # Update immediate status (allows immediate mode again) - completion message is in output
                self._update_immediate_status()
        except Exception as e:
            import traceback

            # Log error (outputs to stderr in debug mode)
            error_msg = debug_log_error("Step error", exception=e)

            self.output_buffer.append(f"Step error: {e}")
            if is_debug_mode():
                self.output_buffer.append("(Full traceback sent to stderr - check console)")
            else:
                self.output_buffer.append(traceback.format_exc())
            self._update_output()
            # Don't update immediate status on exception - error is in output

    def _debug_step_line(self):
        """Execute all statements on current line and pause (step by line)."""
        # Check if we need to setup/restart the program
        needs_setup = (not self.interpreter or
                      not hasattr(self.interpreter, 'state') or
                      not self.interpreter.state or
                      self.runtime.pc.halted())

        if needs_setup:
            # No program running or program completed - set it up without starting async execution
            if not self._setup_program():
                return  # Setup failed (error already displayed)
            # Fall through to execute first step

        try:
            # Execute all statements on current line
            # (Immediate mode status remains disabled during execution - output shows in output window)
            state = self.interpreter.tick(mode='step_line', max_statements=100)

            # Collect any output
            new_output = self.io_handler.get_and_clear_output()
            if new_output:
                self.output_buffer.extend(new_output)
                self._update_output()

            # Update editor display based on new state
            if not self.runtime.pc.is_running() and not state.error_info and state.current_line:
                self.editor._update_display(
                    highlight_line=state.current_line,
                    highlight_stmt=0,  # Highlight whole line, not specific statement
                    statement_table=self.runtime.statement_table
                )

                # Update variables window if visible
                if self.variables_window_visible:
                    self._update_variables_window()

                # Update stack window if visible
                if self.stack_window_visible:
                    self._update_stack_window()

                # Show where we paused (with PC format)
                pc = self.runtime.pc
                pc_display = f"{pc.line_num}.{pc.stmt_offset}" if pc and not pc.halted() else str(state.current_line)
                line_code = self.editor_lines.get(state.current_line, "")
                self.output_buffer.append(f"→ Paused at {pc_display}: {line_code}")
                self._update_output()
                self.status_bar.set_text(f"Paused at {pc_display} - {key_to_display(STEP_KEY)}=Step Stmt, {key_to_display(STEP_LINE_KEY)}=Step Line, {key_to_display(CONTINUE_KEY)}=Continue")
                self._update_immediate_status()
            elif state.error_info:
                self.editor._update_display()
                error_msg = state.error_info.error_message
                line_num = state.error_info.pc.line_num
                self.output_buffer.append(f"Error at line {line_num}: {error_msg}")
                self._update_output()
                # Update immediate status (allows immediate mode again) - error message is in output
                self._update_immediate_status()
            elif not self.runtime.pc.is_running():
                self.editor._update_display()
                self.output_buffer.append("Program completed")
                self._update_output()
                # Update immediate status (allows immediate mode again) - completion message is in output
                self._update_immediate_status()
        except Exception as e:
            import traceback

            # Log error (outputs to stderr in debug mode)
            error_msg = debug_log_error("Step line error", exception=e)

            self.output_buffer.append(f"Step line error: {e}")
            if is_debug_mode():
                self.output_buffer.append("(Full traceback sent to stderr - check console)")
            else:
                self.output_buffer.append(traceback.format_exc())
            self._update_output()
            # Don't update immediate status on exception - error is in output

    def _debug_stop(self):
        """Stop program execution."""
        if not self.interpreter:
            self._append_to_output("No program running")
            return

        try:
            # Stop the interpreter (but don't destroy it - reuse for next run)
            # Note: PC handles halted state via stop_reason
            self.running = False
            self.output_buffer.append("Program stopped by user")
            self._update_output()
            # Update immediate status (allows immediate mode again) - stop message is in output
            self._update_immediate_status()
        except Exception as e:
            # Don't update immediate status on exception - just log the error
            self.output_buffer.append(f"Stop error: {e}")
            self._update_output()

    def _menu_step_line(self):
        """Menu/button handler for Step Line command."""
        self._debug_step_line()

    def _menu_step(self):
        """Menu/button handler for Step Statement command."""
        self._debug_step()

    def _menu_continue(self):
        """Menu/button handler for Continue command."""
        self._debug_continue()

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

        # Extract line number (variable width)
        line_number, code_start = self.editor._parse_line_number(line)
        if line_number is None:
            self.status_bar.set_text("No line number to delete")
            return

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

        # Position cursor intelligently after deletion:
        # - If not at last line: position at column 1 of the line that moved up
        # - If was last line: position at end of the new last line
        if line_index < len(lines):
            # Position at start of line that moved up (column 1)
            if line_index > 0:
                new_cursor_pos = sum(len(lines[i]) + 1 for i in range(line_index)) + 1
            else:
                new_cursor_pos = 1  # First line, column 1
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
        if self.loop and self.loop_running:
            self.loop.draw_screen()

    def _smart_insert_line(self):
        """Smart insert - insert blank line between previous and current line.

        Uses midpoint calculation to find appropriate line number between prev and current.
        If no room (consecutive line numbers), offers to renumber the program.
        """
        from src.ui.ui_helpers import calculate_midpoint

        # Get current cursor position and text
        cursor_pos = self.editor.edit_widget.edit_pos
        current_text = self.editor.edit_widget.get_edit_text()

        # Find which line we're on
        text_before_cursor = current_text[:cursor_pos]
        line_index = text_before_cursor.count('\n')

        # Get all lines
        lines = current_text.split('\n')
        if line_index >= len(lines):
            self.status_bar.set_text("No current line")
            return

        current_line = lines[line_index]

        # Parse current line number (variable width)
        if len(current_line) < 3:  # Need at least status + digit + space
            self.status_bar.set_text("Current line has no line number")
            return

        current_line_num, code_start = self.editor._parse_line_number(current_line)
        if current_line_num is None:
            self.status_bar.set_text("Current line has no line number")
            return

        # Collect all line numbers in program (variable width)
        all_line_numbers = []
        for line in lines:
            line_num, _ = self.editor._parse_line_number(line)
            if line_num is not None:
                all_line_numbers.append(line_num)

        all_line_numbers = sorted(set(all_line_numbers))

        if not all_line_numbers:
            self.status_bar.set_text("No program lines found")
            return

        # Find the previous line before current (to insert between prev and current)
        # Insertion will use midpoint between prev_line_num and current_line_num
        prev_line_num = None
        for i, line_num in enumerate(all_line_numbers):
            if line_num == current_line_num:
                # Found current line - get previous
                if i > 0:
                    prev_line_num = all_line_numbers[i - 1]
                break

        # Calculate insertion point (between prev and current, or before current if at start)
        if prev_line_num is None:
            # At beginning of program - insert numbered line before current
            insert_num = max(1, current_line_num - self.auto_number_increment)
            # Make sure we don't conflict with current
            if insert_num >= current_line_num:
                insert_num = current_line_num - 1 if current_line_num > 1 else None
            if insert_num is None or insert_num < 1:
                self.status_bar.set_text("No room before first line. Use RENUM to make space.")
                return
        else:
            # Between previous and current lines - try midpoint
            midpoint = calculate_midpoint(prev_line_num, current_line_num)
            if midpoint is not None:
                insert_num = midpoint
            else:
                # No room - offer to renumber
                self.show_input_popup(
                    f"No room between lines {prev_line_num} and {current_line_num}. Renumber? (y/n)\n(After renumbering, you'll need to retry the insert): ",
                    lambda response: self._on_insert_line_renumber_response(response)
                )
                return

        # Continue with the actual insert
        self._continue_smart_insert(insert_num, line_index, lines)

    def _on_insert_line_renumber_response(self, response):
        """Handle response to renumber prompt when inserting a line."""
        if response and response.lower().startswith('y'):
            # Renumber to make room
            self._renumber_lines()
        # If no or cancelled, just return (do nothing)

        # Note: Cannot continue the insert operation here because the context was lost
        # when the dialog callback was invoked (lines, line_index, insert_num variables
        # are no longer available). User will need to retry the insert operation manually.

    def _continue_smart_insert(self, insert_num, line_index, lines):
        """Continue smart insert after getting the insert number."""
        # Insert blank line BEFORE current line (at current line's position)
        # Format: status(1) + line_num(variable width) + space + code
        status_char = ' '  # New line has no breakpoint or error
        new_line_text = f"{status_char}{insert_num} "

        # Insert at current position
        lines.insert(line_index, new_line_text)

        # Update editor.lines dict
        self.editor.lines[insert_num] = ""  # Empty code

        # Update display
        new_text = '\n'.join(lines)
        self.editor.edit_widget.set_edit_text(new_text)

        # Position cursor on the new line, at the code area start.
        # Use _parse_line_number() to determine code_start position dynamically
        # to handle variable line number widths.
        _, code_start = self.editor._parse_line_number(lines[line_index])
        if code_start is None:
            code_start = 7  # Fallback to column 7 if parsing fails

        if line_index > 0:
            new_cursor_pos = sum(len(lines[i]) + 1 for i in range(line_index)) + code_start
        else:
            new_cursor_pos = code_start

        self.editor.edit_widget.set_edit_pos(new_cursor_pos)

        # Update status bar
        self.status_bar.set_text(f"Inserted line {insert_num}")

        # Force screen redraw
        if self.loop and self.loop_running:
            self.loop.draw_screen()

    def _renumber_lines(self):
        """Renumber all lines with a dialog for start and increment."""
        # Get current parameters
        current_text = self.editor.edit_widget.get_edit_text()
        lines = current_text.split('\n')

        # Count valid program lines
        valid_lines = []
        for line in lines:
            line_number, code_start = self.editor._parse_line_number(line)
            if line_number is not None:
                code = line[code_start:] if code_start < len(line) else ""
                valid_lines.append((line_number, code, line[0]))  # (line_num, code, status)

        if not valid_lines:
            self.status_bar.set_text("No lines to renumber")
            return

        # Get renumber parameters from user using callback chain
        self.show_input_popup(
            "RENUM - Start line number (default 10): ",
            lambda start_str: self._on_renum_start(start_str, valid_lines)
        )

    def _on_renum_start(self, start_str, valid_lines):
        """Handle start line number from RENUM dialog."""
        if start_str is None:
            # User cancelled
            self.status_bar.set_text("Renumber cancelled")
            return
        elif start_str == '':
            start = 10
        else:
            try:
                start = int(start_str)
            except:
                self.status_bar.set_text("Invalid start number")
                return

        # Now ask for increment (passing start and valid_lines)
        self.show_input_popup(
            "RENUM - Increment (default 10): ",
            lambda increment_str: self._on_renum_increment(increment_str, start, valid_lines)
        )

    def _on_renum_increment(self, increment_str, start, valid_lines):
        """Handle increment from RENUM dialog and perform renumbering."""
        if increment_str is None:
            # User cancelled
            self.status_bar.set_text("Renumber cancelled")
            return
        elif increment_str == '':
            increment = 10
        else:
            try:
                increment = int(increment_str)
            except:
                self.status_bar.set_text("Invalid increment")
                return

        # Perform the renumbering
        self._do_renumber(start, increment, valid_lines)

    def _do_renumber(self, start, increment, valid_lines):
        """Actually perform the renumbering with the given parameters."""

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
            formatted_line = f"{new_status}{new_line_num} {code}"
            new_lines.append(formatted_line)

            new_line_num += increment

        # Update display
        new_text = '\n'.join(new_lines)
        self.editor.edit_widget.set_edit_text(new_text)
        self.editor.edit_widget.set_edit_pos(0)

        # Update status bar
        self.status_bar.set_text(f"Renumbered {len(valid_lines)} lines from {start} by {increment}")

        # Force screen redraw
        if self.loop and self.loop_running:
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

        # Extract line number (variable width)
        line_number, code_start = self.editor._parse_line_number(line)
        if line_number is None:
            return

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
        # Use code_start already computed from _parse_line_number() above
        code_area = line[code_start:] if len(line) > code_start else ""

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
            if self.loop and self.loop_running:
                self.loop.draw_screen()

    def _clear_all_breakpoints(self):
        """Clear all breakpoints."""
        if not self.editor.breakpoints:
            self.status_bar.set_text("No breakpoints to clear")
            return

        count = len(self.editor.breakpoints)
        self.editor.breakpoints.clear()
        self.editor._update_display()
        self.status_bar.set_text(f"Cleared {count} breakpoint(s)")

        # Update interpreter if running
        if self.interpreter:
            self.interpreter.clear_breakpoints()

        # Force redraw
        if self.loop and self.loop_running:
            self.loop.draw_screen()

    def _show_help(self):
        """Show interactive help browser.

        Help widget closes via ESC/Q keys which call the on_close callback.
        """
        # Get help root directory (works in dev and installed environments)
        from src.resource_locator import find_help_dir
        try:
            help_root = find_help_dir()
        except FileNotFoundError as e:
            self.status_bar.set_text(f"Error: Help files not found - {e}")
            return

        def close_help():
            """Close help and restore main UI."""
            self.loop.widget = self.base_widget

        # Create help widget with close callback
        help_widget = HelpWidget(str(help_root), "index.md", on_close=close_help)

        # Create overlay
        # Main widget retrieval: Use self.base_widget (stored at UI creation time in __init__)
        # rather than self.loop.widget (which reflects the current widget and might be a menu
        # or other overlay). Using self.base_widget ensures a consistent base for the overlay,
        # allowing these methods to properly support toggle behavior (close own overlay if already
        # open, or create new one). This is different from _activate_menu() which extracts
        # base_widget from self.loop.widget to stack on top of existing overlays.
        overlay = urwid.Overlay(
            urwid.AttrMap(help_widget, 'body'),
            self.base_widget,
            align='center',
            width=('relative', 90),
            valign='middle',
            height=('relative', 90)
        )

        self.loop.widget = overlay

    def _show_keymap(self):
        """Show keyboard shortcuts reference.

        This method supports toggling - calling it when keymap is already open will close it.
        Main widget storage: Uses self.base_widget (stored at UI creation time in __init__)
        rather than self.loop.widget (which reflects the current widget and might be a menu
        or other overlay). Same approach as _show_help and _show_settings.
        """
        from .keymap_widget import KeymapWidget

        # Check if keymap is already open (toggle behavior)
        if hasattr(self, '_keymap_overlay') and self._keymap_overlay:
            # Close keymap
            self.loop.widget = self._keymap_main_widget
            self.loop.unhandled_input = self._handle_input
            self._keymap_overlay = None
            self._keymap_main_widget = None
            return

        def close_keymap():
            """Close keymap and restore main UI."""
            self.loop.widget = self._keymap_main_widget
            self.loop.unhandled_input = self._handle_input
            self._keymap_overlay = None
            self._keymap_main_widget = None

        # Create keymap widget
        keymap_widget = KeymapWidget(on_close=close_keymap)

        # Main widget storage: Use self.base_widget (stored at UI creation)
        # not self.loop.widget (current widget which might be a menu or overlay)
        main_widget = self.base_widget
        self._keymap_main_widget = main_widget

        # Create overlay
        overlay = urwid.Overlay(
            keymap_widget,
            main_widget,
            align='center',
            width=('relative', 80),
            valign='middle',
            height=('relative', 85)
        )

        # Set up input handler for keymap
        def keymap_input(key):
            # All input is handled by the keymap widget itself
            # Just return None to indicate we didn't handle it (widget did)
            return None

        self._keymap_overlay = overlay
        self.loop.widget = overlay
        self.loop.unhandled_input = keymap_input

    def _activate_menu(self):
        """Activate the interactive menu bar.

        Main widget storage: Unlike _show_help/_show_keymap/_show_settings which close
        existing overlays first (and thus can use self.base_widget directly), this method
        extracts base_widget from self.loop.widget to unwrap any existing overlay. This
        preserves existing overlays (like help or settings) while adding the menu dropdown
        on top of them, allowing menu navigation even when other overlays are present.
        """
        # Get the dropdown overlay from menu bar
        # Pass self.base_widget explicitly to ensure proper colors
        overlay = self.menu_bar.activate_with_base(self.base_widget)

        # Use self.base_widget for restoring (always has proper 'body' AttrMap)
        main_widget = self.base_widget

        # Track current menu overlay (updated when refreshing)
        current_overlay = {'widget': overlay}

        # Set up keypress handler for menu navigation
        def menu_input(key):
            result = self.menu_bar.handle_key(key)
            if result == 'close':
                # Close menu and return to main UI
                # BUT: if an overlay was just opened, don't overwrite it
                # Check if loop.widget changed from menu (indicates a dialog/overlay was opened)
                if self.loop.widget != current_overlay['widget']:
                    # An overlay was opened from menu (recent files, etc.), it's already handling the widget
                    pass
                elif hasattr(self, '_settings_overlay') and self._settings_overlay:
                    # Settings was opened from menu, it's already handling the widget
                    pass
                elif hasattr(self, '_keymap_overlay') and self._keymap_overlay:
                    # Keymap was opened from menu, it's already handling the widget
                    pass
                else:
                    # Restore base widget (already has proper AttrMap wrapping)
                    self.loop.widget = main_widget
                    self.loop.unhandled_input = self._handle_input
            elif result == 'refresh':
                # Refresh dropdown - rebuild overlay from scratch using self.base_widget
                # This ensures proper 'body' attribute (white on black)
                new_overlay = self.menu_bar._show_dropdown(base_widget=self.base_widget)
                self.loop.widget = new_overlay
                current_overlay['widget'] = new_overlay  # Track new overlay
            # Otherwise continue with menu navigation

        # Show overlay and set handler
        self.loop.widget = overlay
        self.loop.unhandled_input = menu_input

    def _reload_editor_settings(self):
        """Reload editor settings from settings system."""
        from src.settings import get
        self.auto_number_start = get('auto_number_start')
        self.auto_number_increment = get('auto_number_step')
        self.auto_number_enabled = get('auto_number')

        # If no lines have been entered yet, reset the next line number
        if not self.editor.lines:
            self.editor.next_auto_line_num = self.auto_number_start

    def _show_settings(self):
        """Toggle settings editor.

        This method supports toggling - calling it when settings is already open will close it.
        Main widget storage: Uses self.base_widget (stored in __init__) rather than
        self.loop.widget (which might be a menu or other overlay).
        """
        from .curses_settings_widget import SettingsWidget

        # Check if settings is already open (toggle behavior)
        if hasattr(self, '_settings_overlay') and self._settings_overlay:
            # Close settings
            self.loop.widget = self._settings_main_widget
            self.loop.unhandled_input = self._handle_input
            self._settings_overlay = None
            self._settings_main_widget = None
            return

        # Create settings widget
        settings_widget = SettingsWidget()

        # Main widget storage: Use self.base_widget (stored at UI creation)
        # not self.loop.widget (current widget which might be a menu or overlay)
        main_widget = self.base_widget
        self._settings_main_widget = main_widget

        # Create overlay
        overlay = urwid.Overlay(
            urwid.AttrMap(settings_widget, 'body'),
            main_widget,
            align='center',
            width=('relative', 80),
            valign='middle',
            height=('relative', 80)
        )
        self._settings_overlay = overlay

        # Set up alarm to check for close signals periodically
        def check_signals(loop, user_data):
            # Check if widget wants to close (signal set by ESC or keyboard shortcuts)
            if hasattr(settings_widget, 'signal') and settings_widget.signal:
                if settings_widget.signal == 'close':
                    # Reload settings in case they changed
                    self._reload_editor_settings()
                    # Close settings
                    self.loop.widget = main_widget
                    self.loop.unhandled_input = self._handle_input
                    self._settings_overlay = None
                    self._settings_main_widget = None
                    # Don't reschedule alarm
                    return
                elif settings_widget.signal == 'applied':
                    # Settings applied - reload them
                    self._reload_editor_settings()
                    # Clear the signal
                    settings_widget.signal = None

            # Reschedule to check again
            self.loop.set_alarm_in(0.1, check_signals)

        # Set up unhandled input handler for ^P
        def settings_input(key):
            # Handle ^P to toggle close
            if key == SETTINGS_KEY:
                self.loop.widget = main_widget
                self.loop.unhandled_input = self._handle_input
                self._settings_overlay = None
                self._settings_main_widget = None
                return True

        # Show overlay and set handlers
        self.loop.widget = overlay
        self.loop.unhandled_input = settings_input

        # Start checking for signals
        self.loop.set_alarm_in(0.1, check_signals)

    def _toggle_variables_window(self):
        """Toggle visibility of the variables window."""
        self.variables_window_visible = not self.variables_window_visible

        if self.variables_window_visible:
            # Add variables window to the pile (position 2, between editor and output)
            # Layout: menu (0), editor (1), variables (2), output (3), status (4)
            self.pile.contents.insert(2, (self.variables_frame, ('weight', 1)))

            # Update variables display
            self._update_variables_window()
        else:
            # Remove variables window from pile
            # Find and remove the variables frame
            for i, (widget, options) in enumerate(self.pile.contents):
                if widget is self.variables_frame:
                    self.pile.contents.pop(i)
                    break

        # Redraw screen
        if hasattr(self, 'loop') and self.loop and self.loop_running:
            self.loop.draw_screen()

    def _update_variables_window(self):
        """Update the variables window with current runtime state."""
        # Clear current display
        self.variables_walker.clear()

        # Add resource usage header
        if self.interpreter and hasattr(self.interpreter, 'limits'):
            limits = self.interpreter.limits

            # Format memory usage
            mem_pct = (limits.current_memory_usage / limits.max_total_memory * 100) if limits.max_total_memory > 0 else 0
            mem_line = f"Memory: {limits.current_memory_usage:,} / {limits.max_total_memory:,} ({mem_pct:.1f}%)"

            # Format stack depths
            stack_line = f"Stacks: GOSUB={limits.current_gosub_depth}/{limits.max_gosub_depth} FOR={limits.current_for_depth}/{limits.max_for_depth} WHILE={limits.current_while_depth}/{limits.max_while_depth}"

            # Add resource lines with divider
            self.variables_walker.append(make_output_line(mem_line))
            self.variables_walker.append(make_output_line(stack_line))
            self.variables_walker.append(make_output_line("─" * 40))

        # Get all variables from runtime
        variables = self.runtime.get_all_variables()

        if not variables:
            self.variables_walker.append(make_output_line("(no variables yet)"))
            return

        # Sort variables using common helper
        variables = sort_variables(variables, self.variables_sort_mode, self.variables_sort_reverse)

        # Store total count before filtering
        total_count = len(variables)

        # Apply filter if present
        if self.variables_filter_text:
            filter_lower = self.variables_filter_text.lower()
            filtered_variables = []

            # Type map for filtering by type name
            type_map = {
                '$': 'string',
                '%': 'integer',
                '!': 'single',
                '#': 'double',
                '': 'single'  # default
            }

            for var in variables:
                name = var['name'] + var['type_suffix']
                value_str = ""

                # Build value string for matching
                if var['is_array']:
                    value_str = f"Array({','.join(str(d) for d in var['dimensions'])})"
                else:
                    value_str = str(var['value'])

                # Check if filter matches name, value, or type
                if (filter_lower in name.lower() or
                    filter_lower in value_str.lower() or
                    filter_lower in type_map.get(var['type_suffix'], '').lower()):
                    filtered_variables.append(var)

            variables = filtered_variables

        # Update window title with counts
        mode_label = get_sort_mode_label(self.variables_sort_mode)
        arrow = '↓' if self.variables_sort_reverse else '↑'

        if self.variables_filter_text:
            title = f"Variables ({len(variables)}/{total_count} filtered: '{self.variables_filter_text}') Sort: {mode_label} {arrow} - {key_to_display(VARS_SORT_MODE_KEY)}=mode {key_to_display(VARS_SORT_DIR_KEY)}=dir {key_to_display(VARS_FILTER_KEY)}=filter {key_to_display(VARS_EDIT_KEY)}=edit {key_to_display(VARIABLES_KEY)}=toggle"
        else:
            title = f"Variables (Sort: {mode_label} {arrow}) - {key_to_display(VARS_SORT_MODE_KEY)}=mode {key_to_display(VARS_SORT_DIR_KEY)}=dir {key_to_display(VARS_FILTER_KEY)}=filter {key_to_display(VARS_EDIT_KEY)}=edit {key_to_display(VARIABLES_KEY)}=toggle"

        self.variables_frame.set_title(title)

        # Display each variable
        for var in variables:
            name = var['name'] + var['type_suffix']

            if var['is_array']:
                # Array: show dimensions and last accessed cell if available
                dims = 'x'.join(str(d) for d in var['dimensions'])

                # Check if we have last accessed info
                if var.get('last_accessed_subscripts') and var.get('last_accessed_value') is not None:
                    subs = var['last_accessed_subscripts']
                    last_val = var['last_accessed_value']

                    # Format value naturally
                    if var['type_suffix'] != '$' and isinstance(last_val, (int, float)) and last_val == int(last_val):
                        last_val_str = str(int(last_val))
                    elif var['type_suffix'] == '$':
                        last_val_str = f'"{last_val}"'
                    else:
                        last_val_str = str(last_val)

                    subs_str = ','.join(str(s) for s in subs)
                    line = f"{name:12} = Array({dims}) [{subs_str}]={last_val_str}"
                else:
                    line = f"{name:12} = Array({dims})"
            else:
                # Scalar: show value
                value = var['value']
                # Format numbers naturally - show integers without decimals
                if var['type_suffix'] != '$' and isinstance(value, (int, float)) and value == int(value):
                    value = str(int(value))
                elif var['type_suffix'] == '$':
                    # String: show with quotes
                    value = f'"{value}"'

                line = f"{name:12} = {value}"

            self.variables_walker.append(make_output_line(line))

    def _cycle_variables_sort_mode(self):
        """Cycle through variable sort modes (triggered by 's' key)."""
        # Cycle through the 4 useful sort modes
        modes = ['accessed', 'written', 'read', 'name']
        try:
            current_idx = modes.index(self.variables_sort_mode)
            next_idx = (current_idx + 1) % len(modes)
        except ValueError:
            next_idx = 0  # Default to 'accessed'

        self.variables_sort_mode = modes[next_idx]

        # Update variables display (this will also update the title)
        self._update_variables_window()

        # Show status using common helper for label
        mode_label = get_sort_mode_label(self.variables_sort_mode)
        arrow = '↓' if self.variables_sort_reverse else '↑'
        self.status_bar.set_text(f"Sorting variables by: {mode_label} {arrow}")

        # Redraw screen
        if hasattr(self, 'loop') and self.loop and self.loop_running:
            self.loop.draw_screen()

    def _toggle_variables_sort_direction(self):
        """Toggle variable sort direction (triggered by 'd' key)."""
        self.variables_sort_reverse = not self.variables_sort_reverse

        # Update variables display (this will also update the title)
        self._update_variables_window()

        # Show status
        direction = "descending ↓" if self.variables_sort_reverse else "ascending ↑"
        self.status_bar.set_text(f"Sort direction: {direction}")

        # Redraw screen
        if hasattr(self, 'loop') and self.loop and self.loop_running:
            self.loop.draw_screen()

    def _edit_selected_variable(self):
        """Edit the currently selected variable in the variables window."""
        import re

        if not self.interpreter or not self.interpreter.runtime:
            self._append_to_output("No program running")
            return

        # Get focused item from variables walker
        try:
            focus_idx = self.variables_walker.get_focus()[1]
            if focus_idx is None or focus_idx >= len(self.variables_walker):
                self.status_bar.set_text("No variable selected")
                return
        except (IndexError, AttributeError):
            self.status_bar.set_text("No variable selected")
            return

        # Get the widget at focus position
        widget = self.variables_walker[focus_idx]
        # Extract text from the widget
        text = widget.get_text()[0] if hasattr(widget, 'get_text') else str(widget)

        # Parse variable line format: "NAME$        = "value""
        # or "A%           = Array(10x10) [5,3]=42"
        parts = text.split('=', 1)
        if len(parts) != 2:
            self.status_bar.set_text("Cannot parse variable")
            return

        variable_name = parts[0].strip()
        value_part = parts[1].strip()

        # Determine variable type
        type_suffix = variable_name[-1] if variable_name[-1] in '$%!#' else None

        # Check if array
        if 'Array' in value_part:
            # Array variable - let user type any subscripts
            # Get array dimensions from display
            dims_match = re.search(r'Array\(([^)]+)\)', value_part)
            dimensions_str = dims_match.group(1) if dims_match else "?"

            # Get default subscripts from last accessed (if available)
            default_subscripts = ""
            match = re.search(r'\[([^\]]+)\]=(.+)$', value_part)
            if match:
                default_subscripts = match.group(1)

            # Get array info from runtime
            base_name = variable_name[:-1] if type_suffix else variable_name
            try:
                array_var = self.interpreter.runtime.get_variable(base_name, type_suffix)
                dimensions = array_var.dimensions if hasattr(array_var, 'dimensions') else []
            except:
                dimensions = []

            # Step 1: Get subscripts from user
            subscripts_prompt = f"Edit {variable_name}({dimensions_str}) - Enter subscripts (e.g., 1,2,3): "
            subscripts_str = self._get_input_dialog(subscripts_prompt, initial=default_subscripts)

            if subscripts_str is None:
                return  # User cancelled with ESC

            # Parse and validate subscripts
            try:
                subscripts = [int(s.strip()) for s in subscripts_str.split(',')]

                # Validate dimension count
                if dimensions and len(subscripts) != len(dimensions):
                    self.status_bar.set_text(f"Error: Expected {len(dimensions)} subscripts, got {len(subscripts)}")
                    return

                # Validate bounds
                for i, sub in enumerate(subscripts):
                    if dimensions and i < len(dimensions):
                        if sub < 0 or sub > dimensions[i]:
                            self.status_bar.set_text(f"Error: Subscript {i} out of bounds: {sub} not in [0, {dimensions[i]}]")
                            return

                # Get current value at those subscripts
                index = 0
                multiplier = 1
                for i in reversed(range(len(subscripts))):
                    index += subscripts[i] * multiplier
                    multiplier *= (dimensions[i] + 1)

                current_val = array_var.elements[index]

            except ValueError:
                self.status_bar.set_text("Invalid subscripts (must be integers)")
                return
            except Exception as e:
                self.status_bar.set_text(f"Error: {e}")
                return

            # Step 2: Show current value and get new value
            value_prompt = f"{variable_name}({subscripts_str}) = {current_val} → New value: "
            new_value_str = self._get_input_dialog(value_prompt)

            if new_value_str is None:
                return  # User cancelled with ESC

            # Convert to appropriate type
            try:
                if type_suffix == '$':
                    new_value = new_value_str
                elif type_suffix == '%':
                    new_value = int(new_value_str)
                else:
                    new_value = float(new_value_str)
            except ValueError:
                self.status_bar.set_text(f"Invalid value for type {type_suffix}")
                return

            # Update array element
            try:
                self.interpreter.runtime.set_array_element(
                    base_name,
                    type_suffix,
                    subscripts,
                    new_value,
                    token=None  # No tracking for debugger edits
                )

                self._update_variables_window()
                self.status_bar.set_text(f"{variable_name}({subscripts_str}) = {new_value}")

            except Exception as e:
                self.status_bar.set_text(f"Error: {e}")

        else:
            # Simple variable
            current_value = value_part.strip('"')

            # Get new value from user
            prompt = f"{variable_name} = "
            new_value_str = self._get_input_dialog(prompt)

            if new_value_str is None:
                return  # User cancelled with ESC

            # Convert to appropriate type
            try:
                if type_suffix == '$':
                    new_value = new_value_str
                elif type_suffix == '%':
                    new_value = int(new_value_str)
                else:
                    new_value = float(new_value_str)
            except ValueError:
                self.status_bar.set_text(f"Invalid value for type {type_suffix}")
                return

            # Update variable
            try:
                base_name = variable_name[:-1] if type_suffix else variable_name
                self.interpreter.runtime.set_variable(
                    base_name,
                    type_suffix,
                    new_value,
                    debugger_set=True
                )

                self._update_variables_window()
                self.status_bar.set_text(f"{variable_name} = {new_value}")

            except Exception as e:
                self.status_bar.set_text(f"Error: {e}")

    def _set_variables_filter(self):
        """Prompt for and set a filter for the variables window."""
        # Show input dialog for filter text
        prompt_text = "Enter filter text (search name, value, or type):"
        current_filter = self.variables_filter_text

        # Create a simple input dialog
        prompt = urwid.Text(prompt_text)
        edit = urwid.Edit(caption="Filter: ", edit_text=current_filter)

        def handle_key(key):
            if key == ENTER_KEY:
                # Set filter
                self.variables_filter_text = edit.get_edit_text()
                self._update_variables_window()

                # Close dialog
                self.loop.widget = self.loop.widget.bottom_w

                # Show status
                if self.variables_filter_text:
                    self.status_bar.set_text(f"Filter set: '{self.variables_filter_text}'")
                else:
                    self.status_bar.set_text("Filter cleared")

                # Redraw
                if self.loop_running:
                    self.loop.draw_screen()
                return True
            elif key == ESC_KEY:
                # Cancel
                self.loop.widget = self.loop.widget.bottom_w
                self.status_bar.set_text("Filter cancelled")
                if self.loop_running:
                    self.loop.draw_screen()
                return True
            return False

        # Create dialog
        pile = urwid.Pile([
            ('pack', prompt),
            ('pack', urwid.Divider()),
            ('pack', edit),
            ('pack', urwid.Divider()),
            ('pack', urwid.Text("Press Enter to apply, ESC to cancel"))
        ])
        fill = urwid.Filler(pile, valign='middle')
        box = urwid.LineBox(fill, title="Filter Variables")
        overlay = urwid.Overlay(
            urwid.AttrMap(box, 'body'),
            self.loop.widget,
            align='center',
            width=('relative', 60),
            valign='middle',
            height=('relative', 30)
        )

        # Show dialog with custom key handler
        self.loop.widget = overlay
        urwid.connect_signal(edit, 'change', lambda _w, _t: None)  # dummy handler

        # Override unhandled_input temporarily
        old_handler = self.loop.unhandled_input
        def dialog_handler(key):
            if handle_key(key):
                # Restore old handler
                self.loop.unhandled_input = old_handler
            return True
        self.loop.unhandled_input = dialog_handler

    def _clear_variables_filter(self):
        """Clear the filter for variables window."""
        self.variables_filter_text = ""
        self._update_variables_window()
        self.status_bar.set_text("Filter cleared")

        # Redraw
        if self.loop_running:
            self.loop.draw_screen()

    def _toggle_output_maximize(self):
        """Toggle output window maximize (for full-screen games)."""
        self.output_maximized = not self.output_maximized

        if self.output_maximized:
            # Hide editor, give all space to output
            # Find editor in pile and set weight to 0 (hidden)
            for i, (widget, options) in enumerate(self.pile.contents):
                if widget is self.editor_frame:
                    self.pile.contents[i] = (widget, ('weight', 0))
                elif widget is self.output_frame:
                    self.pile.contents[i] = (widget, ('weight', 1))
            self.status_bar.set_text(f"Output maximized - {key_to_display(MAXIMIZE_OUTPUT_KEY)} to restore")
        else:
            # Restore normal layout
            for i, (widget, options) in enumerate(self.pile.contents):
                if widget is self.editor_frame:
                    self.pile.contents[i] = (widget, ('weight', 1))
                elif widget is self.output_frame:
                    self.pile.contents[i] = (widget, ('weight', 1))
            self.status_bar.set_text(STATUS_BAR_SHORTCUTS)

        # Redraw
        if self.loop_running:
            self.loop.draw_screen()

    def _toggle_stack_window(self):
        """Toggle visibility of the execution stack window."""
        self.stack_window_visible = not self.stack_window_visible

        if self.stack_window_visible:
            # Determine insertion position based on whether variables window is visible
            # Layout: menu (0), editor (1), [variables (2)], [stack (2 or 3)], output, status
            insert_pos = 3 if self.variables_window_visible else 2
            self.pile.contents.insert(insert_pos, (self.stack_frame, ('weight', 1)))

            # Update stack display
            self._update_stack_window()
        else:
            # Remove stack window from pile
            for i, (widget, options) in enumerate(self.pile.contents):
                if widget is self.stack_frame:
                    self.pile.contents.pop(i)
                    break

        # Redraw screen
        if hasattr(self, 'loop') and self.loop and self.loop_running:
            self.loop.draw_screen()

    def _update_stack_window(self):
        """Update the stack window with current execution stack."""
        # Clear current display
        self.stack_walker.clear()

        # Get execution stack from runtime (GOSUB, FOR, WHILE)
        stack = self.runtime.get_execution_stack()

        if not stack:
            self.stack_walker.append(make_output_line("(empty stack)"))
            return

        # Display stack from bottom to top (oldest to newest)
        for i, entry in enumerate(stack):
            indent = "  " * i  # Indent to show nesting level

            if entry['type'] == 'GOSUB':
                # Show statement-level precision for GOSUB return address
                # return_stmt is statement offset (0-based index): 0 = first statement, 1 = second, etc.
                return_stmt = entry.get('return_stmt', 0)
                line = f"{indent}GOSUB from line {entry['from_line']}.{return_stmt}"
            elif entry['type'] == 'FOR':
                var = entry['var']
                current = entry['current']
                end = entry['end']
                step = entry['step']
                stmt = entry.get('stmt', 0)
                line = f"{indent}FOR {var} = {current} TO {end}"
                if step != 1:
                    line += f" STEP {step}"
                line += f" (line {entry['line']}.{stmt})"
            elif entry['type'] == 'WHILE':
                stmt = entry.get('stmt', 0)
                line = f"{indent}WHILE (line {entry['line']}.{stmt})"
            else:
                line = f"{indent}Unknown: {entry}"

            self.stack_walker.append(make_output_line(line))

    def _setup_program(self, start_line=None):
        """Parse and initialize the program for execution.

        Returns True if successful, False if there was an error.

        Args:
            start_line: Optional line number to start execution at
        """
        # Parse editor content into program
        self._parse_editor_content()

        if not self.editor_lines:
            self.output_buffer.append("No program to run")
            self._update_output()
            return False

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
                # Don't update immediate status here - error is displayed in output
                return False

        # Reset runtime with current program - RUN = CLEAR + GOTO first line (or start_line if specified)
        # Note: reset_for_run() clears variables and resets PC. Breakpoints are STORED in
        # the editor (self.editor.breakpoints) as the authoritative source, not in runtime.
        # This allows them to persist across runs. After reset_for_run(), we re-apply them
        # to the interpreter below via set_breakpoint() calls so execution can check them.
        self.runtime.reset_for_run(self.program.line_asts, self.program.lines)

        # Clear any buffered output from previous run
        self.io_handler.get_and_clear_output()

        # Update interpreter to use the session's io_handler
        self.interpreter.io = self.io_handler

        # Start interpreter (sets up statement table, etc.)
        state = self.interpreter.start()

        # If empty program, just return (variables cleared, nothing to execute)
        if not self.program.lines:
            # Don't update immediate status - no execution occurred
            self.running = False
            return False

        # If start_line is specified (e.g., RUN 100), set PC to that line
        # This must happen AFTER interpreter.start() because start() calls setup()
        # which resets PC to the first line in the program. By setting PC here,
        # we override that default and begin execution at the requested line.
        if start_line is not None:
            from src.runtime import PC
            # Verify the line exists
            if start_line not in self.program.line_asts:
                self.output_buffer.append(f"?Undefined line {start_line}")
                self._update_output()
                # Don't update immediate status here - error is in output
                self.running = False
                return False
            # Set PC to start at the specified line (after start() has built statement table)
            self.runtime.pc = PC.from_line(start_line)

        # Re-apply breakpoints from editor
        # Breakpoints are stored in editor UI state and must be re-applied to interpreter
        # after reset_for_run (which clears them)
        for line_num in self.editor.breakpoints:
            self.interpreter.set_breakpoint(line_num)

        # Initialize immediate mode executor
        immediate_io = OutputCapturingIOHandler()
        self.immediate_executor = ImmediateExecutor(self.runtime, self.interpreter, immediate_io)
        self._update_immediate_status()

        if state.error_info:
            error_msg = state.error_info.error_message
            self.output_buffer.append("")
            self.output_buffer.append("┌─ Startup Error ──────────────────────────────────┐")
            self.output_buffer.append(f"│ Error: {error_msg}")
            self.output_buffer.append("└──────────────────────────────────────────────────┘")
            self._update_output()
            # Don't update immediate status on exception - error is in output
            return False

        return True

    def _run_program(self, start_line=None):
        """Run the current program using tick-based interpreter.

        Args:
            start_line: Optional line number to start execution at (for RUN line_number)
        """
        try:
            # Setup program (parse, load, initialize)
            if not self._setup_program(start_line):
                return

            # Immediate mode status remains disabled during execution - program output shows in output window

            # Set up tick-based execution using urwid's alarm
            self._execute_tick()

        except Exception as e:
            import traceback

            # Log error (outputs to stderr in debug mode)
            error_msg = debug_log_error(
                "Runtime initialization error",
                exception=e,
                context={'phase': 'program setup'}
            )

            # Format error with box
            self.output_buffer.append("")
            self.output_buffer.append("┌─ Unexpected Error ───────────────────────────────┐")
            self.output_buffer.append(f"│ {type(e).__name__}: {e}")
            self.output_buffer.append("│")
            if is_debug_mode():
                self.output_buffer.append("│ (Full traceback sent to stderr - check console)")
            else:
                self.output_buffer.append("│ This is an internal error. Details below:")
            self.output_buffer.append("└──────────────────────────────────────────────────┘")
            self.output_buffer.append("")
            # Add traceback for debugging (only if not in debug mode)
            if not is_debug_mode():
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
            if state.input_prompt is not None:
                # Prompt user for input
                prompt = state.input_prompt
                self._get_input_for_interpreter(prompt)

            elif state.error_info:
                # Error occurred - show any output before error
                error_output = self.io_handler.get_and_clear_output()
                if error_output:
                    self.output_buffer.extend(error_output)

                # Format error with context
                error_msg = state.error_info.error_message
                line_num = state.error_info.pc.line_num

                # Build error display with box and context
                self.output_buffer.append("")
                self.output_buffer.append("┌─ Runtime Error ──────────────────────────────────┐")

                # Try to get the code for the error line
                if isinstance(line_num, int):
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
                # Update immediate status after error so user can continue
                self._update_immediate_status()

            elif not self.runtime.pc.is_running():
                # Halted (could be done or breakpoint/paused)
                # Check if PC is past last statement (program completed)
                pc = self.runtime.pc
                if pc.halted():
                    # Program completed - show final output if any
                    final_output = self.io_handler.get_and_clear_output()
                    if final_output:
                        self.output_buffer.extend(final_output)
                    self.output_buffer.append("Ok")
                    self._update_output()
                    self._update_status_with_errors("Ready")
                    self._update_immediate_status()
                else:
                    # Paused execution (breakpoint hit or stepping)
                    # Use PC line directly since state.current_line may be None at breakpoint
                    pc_line = self.runtime.pc.line if self.runtime.pc else None
                    self.output_buffer.append(f"→ Paused at line {pc_line}")
                    self._update_output()
                    self.status_bar.set_text(f"Paused at line {pc_line} - {key_to_display(STEP_KEY)}=Step Stmt, {key_to_display(STEP_LINE_KEY)}=Step Line, {key_to_display(CONTINUE_KEY)}=Continue")
                    self._update_immediate_status()

            else:
                # Still running - schedule next tick
                self.loop.set_alarm_in(0.01, lambda _loop, _user_data: self._execute_tick())

        except Exception as e:
            import traceback

            # Check if this is a user program error (error_info set) vs internal error
            state = self.interpreter.state if self.interpreter and hasattr(self.interpreter, 'state') else None
            is_user_error = state and state.error_info is not None

            if is_user_error:
                # User program error (like FOR/NEXT nesting) - don't spam stderr
                # Format nicely for the user
                error_msg = state.error_info.error_message
                line_num = state.error_info.pc.line_num

                self.output_buffer.append("")
                self.output_buffer.append("┌─ Runtime Error ──────────────────────────────────┐")
                if isinstance(line_num, int):
                    self.output_buffer.append(f"│ Line {line_num}:")
                    if line_num in self.editor_lines:
                        code = self.editor_lines[line_num]
                        self.output_buffer.append(f"│   {code}")
                        self.output_buffer.append(f"│   ^^^^")
                else:
                    self.output_buffer.append(f"│ Line {line_num}:")
                self.output_buffer.append(f"│ Error: {error_msg}")
                self.output_buffer.append("└──────────────────────────────────────────────────┘")
                self._update_output()
                # Update immediate status after error so user can continue
                self._update_immediate_status()
            else:
                # Internal/unexpected error - log it to stderr
                context = {}
                if state:
                    context['current_line'] = state.current_line
                    context['is_running'] = self.runtime.pc.is_running()

                error_msg = debug_log_error(
                    "Execution error",
                    exception=e,
                    context=context
                )

                # Format unexpected error with box
                self.output_buffer.append("")
                self.output_buffer.append("┌─ Execution Error ────────────────────────────────┐")
                self.output_buffer.append(f"│ {type(e).__name__}: {e}")
                self.output_buffer.append("│")
                if is_debug_mode():
                    self.output_buffer.append("│ (Full traceback sent to stderr - check console)")
                else:
                    self.output_buffer.append("│ An error occurred during program execution.")
                self.output_buffer.append("└──────────────────────────────────────────────────┘")
                self.output_buffer.append("")
                if not is_debug_mode():
                    for line in traceback.format_exc().split('\n'):
                        self.output_buffer.append(line)
                self._update_output()
                self.status_bar.set_text("Execution error - See output")

    def _get_input_for_interpreter(self, prompt):
        """Show input dialog and provide input to interpreter.

        This is an async operation - it shows the dialog and returns immediately.
        When the user provides input (or cancels), the callback will handle it.
        """
        def on_input_complete(result):
            """Called when user completes input or cancels."""
            # If user cancelled (ESC), stop program execution
            # Note: This stops the UI tick. The interpreter's PC (program counter) is already at
            # the position where execution should resume if user presses CONT.
            # The behavior is similar to STOP: user can examine variables and continue with CONT.
            if result is None:
                # Stop execution - PC already contains the position for CONT to resume from
                self.running = False
                self._append_to_output("Input cancelled - Program stopped")
                self._update_immediate_status()
                return

            # Provide input to interpreter
            self.interpreter.provide_input(result)

            # Continue execution
            self.loop.set_alarm_in(0.01, lambda _loop, _user_data: self._execute_tick())

        # Show dialog asynchronously with callback
        self._show_input_dialog_async(prompt, on_input_complete)

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

    def _get_editor_content(self) -> str:
        """Get current editor content.

        Returns:
            Current text in editor
        """
        if self.editor and self.editor.edit_widget:
            return self.editor.edit_widget.get_edit_text()
        return ""

    def _new_program(self):
        """Clear the current program."""
        # Stop current autosave
        self.auto_save.stop_autosave()

        self.editor_lines = {}
        self.editor.clear()
        self.current_filename = None  # Clear filename for new program
        self.output_buffer.append("Program cleared")
        self._update_output()
        self._update_status_with_errors("Ready")

        # Reset auto-numbering to start value
        self.editor.next_auto_line_num = self.auto_number_start

        # Start autosave for new file
        self.auto_save.start_autosave(
            'untitled.bas',
            self._get_editor_content,
            interval=30
        )

    def _parse_editor_content(self):
        """Parse the editor content into line-numbered statements."""
        # Parse the visual editor text into line-numbered statements
        self.editor_lines = {}

        # Get the raw text from the editor
        text = self.editor.edit_widget.get_edit_text()

        # Parse each line
        for line in text.split('\n'):
            # Use helper to parse variable-width line numbers
            line_num, code_start = self.editor._parse_line_number(line)
            if line_num is None:
                continue

            # Extract code after the space
            code = line[code_start:] if len(line) > code_start else ""

            # Store in editor_lines
            self.editor_lines[line_num] = code

        # Also update the editor's internal lines dictionary for consistency
        self.editor.lines = self.editor_lines.copy()

    def _sync_program_to_runtime(self):
        """Sync program to runtime, conditionally preserving PC.

        Updates runtime's statement_table and line_text_map from self.program.

        PC handling:
        - If running (and not paused at breakpoint): Preserves PC to resume correctly
        - If paused at breakpoint: Resets PC to halted to avoid accidental resumption
        - If not running: Resets PC to halted for safety

        Rationale: When syncing a modified program during execution, we need to decide
        whether to preserve the current PC (execution context) or reset it. If execution
        is actively running, the saved PC is still valid for resuming. If paused at a
        breakpoint, resetting PC prevents accidental resumption from the wrong location
        (when user continues via _debug_continue(), the interpreter maintains correct PC).
        If not running, halting ensures no accidental execution starts.
        """
        from src.pc import PC

        # Preserve current PC if it's valid (execution in progress)
        # Otherwise ensure it stays halted
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

        # PC restoration logic:
        # Only preserve PC if execution is actively running and not paused at breakpoint.
        # This allows the program to resume from where it left off. When paused at a
        # breakpoint, we reset to halted to prevent confusion about where execution will
        # resume (the actual breakpoint PC is maintained by the interpreter's own state).
        if self.running and not self.paused_at_breakpoint:
            # Execution is running - preserve current execution state
            self.runtime.pc = old_pc
        else:
            # No execution in progress or paused at breakpoint - reset to halted
            self.runtime.pc = PC.halted()

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
            # Urwid will redraw automatically - no need to force draw_screen()

    def _append_to_output(self, message):
        """Append a message to output buffer and update display.

        Args:
            message: String or list of strings to append
        """
        if isinstance(message, list):
            self.output_buffer.extend(message)
        else:
            self.output_buffer.append(message)
        self._update_output()

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
            if hasattr(self, 'loop') and self.loop and self.loop_running:
                self.loop.draw_screen()

    def _show_yesno_dialog(self, title, message):
        """Show yes/no dialog and get user response.

        Args:
            title: Dialog title
            message: Dialog message

        Returns:
            True if yes, False if no
        """
        # Create text widget
        text = urwid.Text(message)

        # Create dialog
        fill = urwid.Filler(text, valign='top')
        box = urwid.LineBox(fill, title=f"{title} - Press 'y' for Yes, 'n' for No, ESC to cancel")
        overlay = urwid.Overlay(
            urwid.AttrMap(box, 'body'),
            self.loop.widget,
            align='center',
            width=('relative', 70),
            valign='middle',
            height=('relative', 40)
        )

        # Store original widget
        original_widget = self.loop.widget
        self.loop.widget = overlay

        # Variable to store result
        result = {'value': False}
        done = {'flag': False}

        def handle_input(key):
            if key == DIALOG_YES_KEY or key == 'Y':
                result['value'] = True
                done['flag'] = True
                self.loop.widget = original_widget
            elif key == DIALOG_NO_KEY or key == 'N' or key == ESC_KEY:
                result['value'] = False
                done['flag'] = True
                self.loop.widget = original_widget
            return None

        # Store old handler
        old_handler = self.loop.unhandled_input

        # Create wrapped handler that processes input and checks for completion
        def wrapped_handler(key):
            result_key = handle_input(key)
            if done['flag']:
                # Restore and exit
                self.loop.unhandled_input = old_handler
                raise urwid.ExitMainLoop()
            return result_key

        self.loop.unhandled_input = wrapped_handler

        # Run nested main loop for this dialog
        try:
            self.loop.run()
        except urwid.ExitMainLoop:
            pass  # Dialog closed

        return result['value']

    def _show_input_dialog_async(self, prompt, callback, initial=""):
        """Show input dialog asynchronously with callback.

        Args:
            prompt: The prompt text to show
            callback: Function to call with result (or None if cancelled)
            initial: Initial text value (default: "")

        The dialog will be shown immediately and this function returns.
        When user presses Enter or ESC, the callback will be called with the result.
        """
        # Create input widget with optional initial value
        edit = urwid.Edit(caption=prompt, edit_text=initial)

        # Create dialog
        fill = urwid.Filler(edit, valign='top')
        box = urwid.LineBox(fill, title="Input Required - Enter or ESC")
        overlay = urwid.Overlay(
            urwid.AttrMap(box, 'body'),
            self.loop.widget,
            align='center',
            width=('relative', 60),
            valign='middle',
            height=5
        )

        # Store original widget and handler
        original_widget = self.loop.widget
        old_handler = self.loop.unhandled_input

        def handle_input(key):
            """Handle input for the dialog."""
            if key == ENTER_KEY:
                # Get the result and restore state
                result = edit.get_edit_text()
                self.loop.widget = original_widget
                self.loop.unhandled_input = old_handler
                # Call callback with result
                callback(result)
                return None
            elif key == ESC_KEY:
                # Restore state
                self.loop.widget = original_widget
                self.loop.unhandled_input = old_handler
                # Call callback with None (cancelled)
                callback(None)
                return None
            # Let other keys pass through to edit widget
            return key

        # Set up dialog
        self.loop.widget = overlay
        self.loop.unhandled_input = handle_input

    def _get_input_dialog(self, prompt, initial=""):
        """Show input dialog and get user response.

        Returns:
            str: The entered text, or None if cancelled with ESC
        """
        # Create input widget with optional initial value
        edit = urwid.Edit(caption=prompt, edit_text=initial)

        # Create dialog
        fill = urwid.Filler(edit, valign='top')
        box = urwid.LineBox(fill, title="Input Required - Enter or ESC")
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
        result = {'value': None}
        done = {'flag': False}

        def handle_input(key):
            if key == ENTER_KEY:
                result['value'] = edit.get_edit_text()
                done['flag'] = True
                # Exit the nested loop
                raise urwid.ExitMainLoop()
            elif key == ESC_KEY:
                # ESC cancels - return None to indicate cancellation
                result['value'] = None
                done['flag'] = True
                # Exit the nested loop
                raise urwid.ExitMainLoop()
            # Let other keys pass through
            return key

        # Store old handler
        old_handler = self.loop.unhandled_input
        self.loop.unhandled_input = handle_input

        # Run nested event loop for dialog
        try:
            self.loop.run()
        except urwid.ExitMainLoop:
            # Dialog closed - this is expected
            pass
        finally:
            # Always restore state
            self.loop.widget = original_widget
            self.loop.unhandled_input = old_handler

        return result['value']

    def _get_editor_text(self):
        """Get formatted editor text from line-numbered program."""
        lines = []
        for line_num in sorted(self.editor_lines.keys()):
            lines.append(f"{line_num} {self.editor_lines[line_num]}")
        return '\n'.join(lines)

    def _sync_program_to_editor(self):
        """Sync program from ProgramManager to editor display.

        This is used when a program is loaded externally (e.g., from command line)
        before the UI starts, and we need to populate the editor.
        """
        import re
        self.editor_lines = {}
        for line_num, line_text in sorted(self.program.lines.items()):
            # Extract just the code part (without line number)
            # The line_text includes the line number, e.g., "10 PRINT \"HELLO\""
            # We want to store just: PRINT "HELLO"
            match = re.match(r'^\d+\s+(.*)', line_text)
            if match:
                self.editor_lines[line_num] = match.group(1)
            else:
                # Fallback: store the whole line
                self.editor_lines[line_num] = line_text

        # Update editor display
        self.editor.set_edit_text(self._get_editor_text())

    def _load_program_file(self, filename):
        """Load a program from a file."""
        try:
            self.program.load_from_file(filename)

            # Sync program to editor
            self._sync_program_to_editor()

            # Runtime will be reset when user actually runs the program

            # Add to recent files
            self.recent_files.add_file(filename)

            # Store as current filename
            self.current_filename = filename

            self.output_buffer.append(f"Loaded {filename}")
            self._update_output()

            # Set focus to editor
            try:
                self.pile.focus_position = 1  # 1 = editor_frame
            except:
                pass

            # Start autosave for loaded file
            self.auto_save.stop_autosave()
            self.auto_save.start_autosave(
                filename,
                self._get_editor_content,
                interval=30
            )

        except Exception as e:
            self.output_buffer.append(f"Error loading file: {e}")
            self._update_output()

    def _save_program(self):
        """Save program to file (uses current filename if available)."""
        # Use current filename if we have one, otherwise prompt
        if self.current_filename:
            self._do_save_to_file(self.current_filename)
        else:
            # No current filename, prompt for one
            self.show_input_popup("Save as: ", lambda filename: self._on_save_filename(filename))

    def _on_save_filename(self, filename):
        """Handle filename from save dialog."""
        if not filename:
            self.output_buffer.append("Save cancelled")
            self._update_output()
            return

        self._do_save_to_file(filename)

    def _do_save_to_file(self, filename):
        """Actually save the program to a file."""
        self.output_buffer.append(f"Saving to {filename}...")
        self._update_output()

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

            # Add to recent files
            self.recent_files.add_file(filename)

            # Store as current filename
            self.current_filename = filename

            self.output_buffer.append(f"Saved to {filename}")
            self._update_output()

            # Clean up autosave after successful save
            self.auto_save.cleanup_after_save(filename)

            # Restart autosave with new filename
            self.auto_save.stop_autosave()
            self.auto_save.start_autosave(
                filename,
                self._get_editor_content,
                interval=30
            )

        except Exception as e:
            self.output_buffer.append(f"Error saving file: {e}")
            self._update_output()

    def _save_as_program(self):
        """Save program to a new file (always prompts for filename)."""
        # Always prompt for filename
        self.show_input_popup("Save as: ", lambda filename: self._on_save_filename(filename))

    def _load_program(self):
        """Load program from file."""
        self.show_input_popup("Load file: ", self._on_load_filename)

    def _on_load_filename(self, filename):
        """Handle filename from load dialog."""
        if not filename:
            self.output_buffer.append("Load cancelled")
            self._update_output()
            return

        try:
            # Check for autosave recovery
            if self.auto_save.is_autosave_newer(filename):
                prompt = self.auto_save.format_recovery_prompt(filename)
                if prompt:
                    # Show yes/no popup for recovery with callback
                    self.show_yesno_popup(
                        "Auto-save Recovery",
                        prompt + "\n\nPress 'y' to recover, 'n' to load original file",
                        lambda response: self._on_autosave_recovery_response(response, filename)
                    )
                    return

            # Normal load (no recovery or user declined)
            self._load_program_file(filename)
        except Exception as e:
            self.output_buffer.append(f"Error loading file: {e}")
            self._update_output()

    def _on_autosave_recovery_response(self, response, filename):
        """Handle autosave recovery yes/no response."""
        try:
            if response:
                # Load from autosave
                autosave_content = self.auto_save.load_autosave(filename)
                if autosave_content:
                    # Clear editor
                    self.editor_lines = {}

                    # Filter out blank lines (lines with only line number, no code)
                    lines = []
                    for line in autosave_content.split('\n'):
                        # Parse line number from the line (format: " 100 code" or "?100 code")
                        line_num, code_start = self.editor._parse_line_number(line)
                        if line_num is not None:
                            # Extract code after the space
                            code = line[code_start:].strip() if len(line) > code_start else ""
                            # Only keep lines that have actual code
                            if code:
                                lines.append(line)
                        elif line.strip():  # Keep non-numbered lines if they have content
                            lines.append(line)

                    cleaned_content = '\n'.join(lines)
                    self.editor.edit_widget.set_edit_text(cleaned_content)
                    # Parse content
                    self._parse_editor_content()
                    # Add to recent files
                    self.recent_files.add_file(filename)
                    # Set current filename
                    self.current_filename = filename
                    self.output_buffer.append(f"Recovered from autosave: {filename}")
                    self._update_output()
                    # Start autosave
                    self.auto_save.start_autosave(
                        filename,
                        self._get_editor_content,
                        interval=30
                    )
            else:
                # User declined recovery, load normally
                self._load_program_file(filename)
        except Exception as e:
            self.output_buffer.append(f"Error in autosave recovery: {e}")
            self._update_output()

    def _show_recent_files(self):
        """Show recent files dialog for selection."""
        from pathlib import Path

        # Get recent files
        recent = self.recent_files.get_recent_files(max_count=10)

        if not recent:
            self.output_buffer.append("No recent files")
            self._update_output()
            return

        # Build menu text with numbered options
        menu_lines = [
            "══════════════════════════════════════════════════════════════",
            "",
            "                     RECENT FILES",
            "",
            "══════════════════════════════════════════════════════════════",
            ""
        ]

        for i, filepath in enumerate(recent, 1):
            filename = Path(filepath).name
            menu_lines.append(f"  {i}. {filename}")

        menu_lines.extend([
            "",
            "══════════════════════════════════════════════════════════════",
            "",
            "     Enter number (1-{}) or ESC to cancel".format(len(recent)),
            "     'c' to clear recent files",
            "",
            "══════════════════════════════════════════════════════════════"
        ])

        menu_text = '\n'.join(menu_lines)

        # Create menu dialog
        text = urwid.Text(menu_text)
        fill = urwid.Filler(text, valign='middle')
        box = urwid.LineBox(fill, title="Recent Files")

        # Use base_widget as base (not current loop.widget which might be a menu)
        main_widget = self.base_widget
        overlay = urwid.Overlay(
            urwid.AttrMap(box, 'body'),
            main_widget,
            align='center',
            width=('relative', 70),
            valign='middle',
            height=('relative', 60)
        )

        # Set up keypress handler
        def handle_selection(key):
            if key == 'esc':
                # Cancel
                self.loop.widget = main_widget
                self.loop.unhandled_input = self._handle_input
            elif key == 'c' or key == 'C':
                # Clear recent files
                self.recent_files.clear()
                self.output_buffer.append("Recent files cleared")
                self._update_output()
                self.loop.widget = main_widget
                self.loop.unhandled_input = self._handle_input
            elif key in '123456789':
                # Load selected file
                index = int(key) - 1
                if index < len(recent):
                    filepath = recent[index]
                    # Check if file exists
                    if not Path(filepath).exists():
                        self.output_buffer.append(f"File not found: {filepath}")
                        self.output_buffer.append("Removed from recent files")
                        self.recent_files.remove_file(filepath)
                        self._update_output()
                    else:
                        try:
                            self._load_program_file(filepath)
                        except Exception as e:
                            self.output_buffer.append(f"Error loading file: {e}")
                            self._update_output()
                self.loop.widget = main_widget
                self.loop.unhandled_input = self._handle_input

        # Show overlay and set handler
        self.loop.widget = overlay
        self.loop.unhandled_input = handle_selection

    # Immediate mode methods

    def _execute_immediate(self):
        """Execute immediate mode command."""
        if not self.immediate_executor or not self.immediate_input:
            return

        command = self.immediate_input.get_edit_text().strip()
        if not command:
            return

        # Check if safe to execute
        if not self.immediate_executor.can_execute_immediate():
            self.output_walker.append(make_output_line("Cannot execute while program is running"))
            self.immediate_input.set_edit_text("")
            return

        # Parse editor content into program (in case user typed lines directly)
        # This updates self.program, then syncs to runtime below
        self._parse_editor_content()

        # Load program lines into program manager
        self.program.clear()
        for line_num in sorted(self.editor_lines.keys()):
            line_text = f"{line_num} {self.editor_lines[line_num]}"
            self.program.add_line(line_num, line_text)

        # Sync program to runtime (updates statement table and line text map).
        # If execution is running, _sync_program_to_runtime preserves current PC.
        # If not running, it sets PC to halted. Either way, this doesn't start execution,
        # but allows commands like LIST to see the current program.
        self._sync_program_to_runtime()

        # Log the command to output pane
        self.output_walker.append(make_output_line(f"> {command}"))

        # Execute
        success, output = self.immediate_executor.execute(command)

        # Log the result to output pane
        if output:
            for line in output.rstrip().split('\n'):
                self.output_walker.append(make_output_line(line))

        if success:
            self.output_walker.append(make_output_line("Ok"))

        # Clear input
        self.immediate_input.set_edit_text("")

        # Scroll to bottom of output
        if len(self.output_walker) > 0:
            self.output.set_focus(len(self.output_walker) - 1)

        # If immediate command set NPC (like RUN/GOTO), commit it to PC.
        # Immediate commands that modify control flow set NPC to indicate where
        # execution should start/continue. We commit this here (same as tick loop).
        if self.runtime.npc is not None:
            self.runtime.pc = self.runtime.npc
            self.runtime.npc = None

        # Check if interpreter has work to do (after RUN statement)
        # Query the interpreter's execution state to see if it has more work pending
        has_work = self.interpreter.has_work() if self.interpreter else False
        if self.interpreter and has_work:
            # Start execution if not already running
            if not self.running:
                # Switch interpreter IO to a capturing handler that outputs to the output pane
                # (Create the same CapturingIOHandler that _run_program uses)
                if not hasattr(self, 'io_handler') or self.io_handler is None:
                    # Import shared CapturingIOHandler from dedicated module
                    from .capturing_io_handler import CapturingIOHandler

                    io_handler = CapturingIOHandler()
                    self.interpreter.io = io_handler
                    self.io_handler = io_handler

                # Initialize interpreter state for execution
                # NOTE: Don't call interpreter.start() here. The RUN command (executed via the
                # immediate executor) already called interpreter.start() to set up the program and
                # position the PC at the appropriate location. This function only ensures
                # InterpreterState exists for tick-based execution tracking. If we called
                # interpreter.start() here again, it would reset PC to the beginning, overriding
                # the PC set by the RUN command.
                from src.interpreter import InterpreterState
                if not hasattr(self.interpreter, 'state') or self.interpreter.state is None:
                    self.interpreter.state = InterpreterState(_interpreter=self.interpreter)
                self.interpreter.state.is_first_line = True

                # Immediate mode status remains disabled during execution - program output shows in output window
                self.running = True
                # Start the tick loop
                self.loop.set_alarm_in(0.01, lambda loop, user_data: self._execute_tick())

        # Update variables/stack windows if visible
        if self.variables_window_visible:
            self._update_variables_window()
        if self.stack_window_visible:
            self._update_stack_window()

        # Force screen redraw to ensure cursor appears in immediate input
        if self.loop and self.loop_running:
            self.loop.draw_screen()

    def _update_immediate_status(self):
        """Update immediate mode panel status based on interpreter state."""
        if not self.immediate_executor or not self.immediate_status:
            return

        if self.immediate_executor.can_execute_immediate():
            # Safe to execute - show green "Ok"
            self.immediate_status.set_text(('immediate_ok', "Ok"))
        else:
            # Not safe - show that running
            self.immediate_status.set_text(('immediate_disabled', "[running]"))

    # Command implementations (inherited from UIBackend)

    def cmd_run(self, start_line=None):
        """Execute RUN command.

        Args:
            start_line: Optional line number to start execution at (for RUN line_number)
        """
        self._run_program(start_line=start_line)

    def cmd_list(self, args=""):
        """Execute LIST command."""
        self._list_program()

    def cmd_new(self):
        """Execute NEW command."""
        self._new_program()

    def cmd_load(self, filename):
        """Execute LOAD command."""
        self._load_program_file(filename)

    def cmd_save(self, filename):
        """Execute SAVE command."""
        try:
            if not filename:
                self._append_to_output("?Syntax error: filename required")
                return

            # Remove quotes if present
            filename = filename.strip().strip('"').strip("'")

            # Use program manager's save_to_file
            self.program.save_to_file(filename)
            self._append_to_output(f"Saved to {filename}")

        except Exception as e:
            self._append_to_output(f"?Error saving file: {e}")

    def cmd_delete(self, args):
        """Execute DELETE command using ui_helpers.

        Note: Updates self.program immediately (source of truth), then syncs to runtime.
        """
        from src.ui.ui_helpers import delete_lines_from_program

        try:
            deleted = delete_lines_from_program(self.program, args, runtime=None)
            self._sync_program_to_runtime()  # Sync runtime after program changes
            self._refresh_editor()
            if len(deleted) == 1:
                self._append_to_output(f"Deleted line {deleted[0]}")
            else:
                self._append_to_output(f"Deleted {len(deleted)} lines ({min(deleted)}-{max(deleted)})")

        except ValueError as e:
            self._append_to_output(f"?{e}")
        except Exception as e:
            self._append_to_output(f"?Error during delete: {e}")

    def cmd_renum(self, args):
        """Execute RENUM command using ui_helpers.

        Note: Updates self.program immediately (source of truth), then syncs to runtime.
        """
        from src.ui.ui_helpers import renum_program

        # Need access to InteractiveMode's _renum_statement
        # Curses UI has self.interpreter which should have interactive_mode
        if not hasattr(self, 'interpreter') or not hasattr(self.interpreter, 'interactive_mode'):
            self._append_to_output("?RENUM not available in this mode")
            return

        try:
            old_lines, line_map = renum_program(
                self.program,
                args,
                self.interpreter.interactive_mode._renum_statement,
                runtime=None
            )
            self._sync_program_to_runtime()  # Sync runtime after program changes
            self._refresh_editor()
            self._append_to_output("Renumbered")

        except ValueError as e:
            self._append_to_output(f"?{e}")
        except Exception as e:
            self._append_to_output(f"?Error during renumber: {e}")

    def cmd_merge(self, filename):
        """Execute MERGE command using ProgramManager."""
        try:
            if not filename:
                self._append_to_output("?Syntax error: filename required")
                return

            # Use ProgramManager's merge_from_file
            success, errors, lines_added, lines_replaced = self.program.merge_from_file(filename)

            # Show parse errors if any
            if errors:
                for line_num, error in errors:
                    self._append_to_output(f"?Parse error at line {line_num}: {error}")

            if success:
                self._refresh_editor()
                self._append_to_output(f"Merged from {filename}")
                self._append_to_output(f"{lines_added} line(s) added, {lines_replaced} line(s) replaced")
            else:
                self._append_to_output("?No lines merged")

        except FileNotFoundError:
            self._append_to_output(f"?File not found: {filename}")
        except Exception as e:
            self._append_to_output(f"?{e}")

    def cmd_files(self, filespec=""):
        """Execute FILES command using ui_helpers."""
        from src.ui.ui_helpers import list_files

        try:
            files = list_files(filespec)
            pattern = filespec if filespec else "*"

            if not files:
                self._append_to_output(f"No files matching: {pattern}")
                return

            self._append_to_output(f"\nDirectory listing for: {pattern}")
            self._append_to_output("-" * 50)
            for filename, size, is_dir in files:
                if is_dir:
                    self._append_to_output(f"{filename:<30}        <DIR>")
                elif size is not None:
                    self._append_to_output(f"{filename:<30} {size:>12} bytes")
                else:
                    self._append_to_output(f"{filename:<30}            ?")

            self._append_to_output(f"\n{len(files)} file(s)")

        except Exception as e:
            self._append_to_output(f"?Error listing files: {e}")

    def cmd_cont(self):
        """Execute CONT command - continue after STOP."""
        # Check if in stopped state (PC has stop_reason set)
        if self.runtime.pc.is_running():
            self._append_to_output("?Can't continue")
            return

        try:
            # PC already contains the position to resume from
            self.running = True

            # Resume execution by scheduling next tick
            self.loop.set_alarm_in(0.01, lambda _loop, _user_data: self._execute_tick())

        except Exception as e:
            self._append_to_output(f"?Error: {e}")

    def cmd_system(self):
        """Execute SYSTEM command - Exit to operating system."""
        self._append_to_output("Goodbye")
        # Exit the urwid main loop
        raise urwid.ExitMainLoop()
