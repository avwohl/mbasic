"""Curses-based I/O handler for MBASIC interpreter.

This module provides an IOHandler that redirects all I/O to curses windows,
enabling full-screen terminal UIs.
"""

from .base import IOHandler
import curses


class CursesIOHandler(IOHandler):
    """I/O handler that uses curses windows.

    Redirects all output to a curses window and handles input via curses
    prompts and dialogs.
    """

    def __init__(self, output_win=None, input_win=None, debug_enabled=False):
        """Initialize curses I/O handler.

        Args:
            output_win: Curses window for output (can be set later)
            input_win: Curses window for input prompts (optional)
            debug_enabled: Enable debug output
        """
        self.output_win = output_win
        self.input_win = input_win
        self.debug_enabled = debug_enabled
        self.output_buffer = []  # Buffer output before window is set

    def set_output_window(self, window):
        """Set the output window after initialization.

        Args:
            window: Curses window for output
        """
        self.output_win = window

        # Flush buffered output
        if self.output_buffer:
            for text in self.output_buffer:
                self._write_to_window(text)
            self.output_buffer = []

    def set_input_window(self, window):
        """Set the input window after initialization.

        Args:
            window: Curses window for input prompts
        """
        self.input_win = window

    def _write_to_window(self, text):
        """Write text to output window.

        Args:
            text: Text to write
        """
        if self.output_win is None:
            # Buffer if window not set yet
            self.output_buffer.append(text)
            return

        try:
            # Get window dimensions
            max_y, max_x = self.output_win.getmaxyx()

            # Write text, handling newlines and scrolling
            for char in text:
                if char == '\n':
                    # Move to next line
                    y, x = self.output_win.getyx()
                    if y < max_y - 1:
                        self.output_win.move(y + 1, 0)
                    else:
                        # Scroll window
                        self.output_win.scroll(1)
                        self.output_win.move(max_y - 1, 0)
                else:
                    # Write character
                    try:
                        self.output_win.addch(char)
                    except curses.error:
                        # Handle line wrap or window edge
                        y, x = self.output_win.getyx()
                        if x >= max_x - 1:
                            # At right edge, wrap to next line
                            if y < max_y - 1:
                                self.output_win.move(y + 1, 0)
                            else:
                                self.output_win.scroll(1)
                                self.output_win.move(max_y - 1, 0)
                            self.output_win.addch(char)

            # Refresh window to show output
            self.output_win.refresh()

        except curses.error:
            # Ignore errors (window too small, etc.)
            pass

    def output(self, text: str, end: str = '\n') -> None:
        """Output text to curses window.

        Args:
            text: Text to output
            end: String to append (default: newline)
        """
        self._write_to_window(text + end)

    def input(self, prompt: str = '') -> str:
        """Input text from user via curses prompt.

        Args:
            prompt: Prompt to display

        Returns:
            User input as string
        """
        if prompt:
            self.output(prompt, end='')

        # Use curses text input
        if self.output_win:
            try:
                # Enable echo and cursor
                curses.echo()
                curses.curs_set(1)

                # Get input
                input_bytes = self.output_win.getstr()
                result = input_bytes.decode('utf-8', errors='replace')

                # Disable echo and cursor
                curses.noecho()
                curses.curs_set(0)

                # Add newline to output
                self.output('\n', end='')

                return result

            except curses.error:
                curses.noecho()
                curses.curs_set(0)
                return ''
        else:
            return ''

    def input_line(self, prompt: str = '') -> str:
        """Input a full line (LINE INPUT statement).

        Args:
            prompt: Prompt to display

        Returns:
            User input as string

        Note: Current implementation does NOT preserve trailing spaces as documented
        in base class. curses getstr() strips trailing whitespace (spaces, tabs, newlines).
        Leading spaces are preserved. This is a known limitation - see input_line()
        documentation in base.py.
        """
        return self.input(prompt)

    def input_char(self, blocking: bool = True) -> str:
        """Input single character (INKEY$, INPUT$ functions).

        Args:
            blocking: If True, wait for keypress; if False, return immediately

        Returns:
            Single character as string, or empty string if no input
        """
        if self.output_win:
            try:
                if not blocking:
                    # Non-blocking mode
                    self.output_win.nodelay(True)

                ch = self.output_win.getch()

                if not blocking:
                    self.output_win.nodelay(False)

                if ch == -1:
                    # No input (non-blocking mode)
                    return ''
                elif ch < 256:
                    # Regular ASCII character
                    return chr(ch)
                else:
                    # Special key (arrow, function key, etc.)
                    # Return empty string or special code
                    return ''

            except curses.error:
                return ''
        else:
            return ''

    def clear_screen(self) -> None:
        """Clear the output window (CLS statement)."""
        if self.output_win:
            self.output_win.clear()
            self.output_win.move(0, 0)
            self.output_win.refresh()

    def error(self, message: str) -> None:
        """Output error message to curses window.

        Args:
            message: Error message
        """
        # Try to use red color for errors
        if self.output_win:
            try:
                if curses.has_colors():
                    self.output_win.addstr(message, curses.color_pair(4))
                    self.output_win.addch('\n')
                    self.output_win.refresh()
                else:
                    self._write_to_window(message + '\n')
            except curses.error:
                self._write_to_window(message + '\n')
        else:
            self._write_to_window(message + '\n')

    def debug(self, message: str) -> None:
        """Output debug message if debugging is enabled.

        Args:
            message: Debug message
        """
        if self.debug_enabled:
            self._write_to_window(f"DEBUG: {message}\n")
