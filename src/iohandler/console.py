"""Console-based I/O handler for terminal/CLI use.

This module provides a console implementation of IOHandler that uses
standard Python input() and print() functions. This is the default
I/O handler for the command-line MBASIC interpreter.
"""

import sys
import os
from .base import IOHandler


class ConsoleIOHandler(IOHandler):
    """Console-based I/O handler using stdin/stdout.

    This is the default I/O handler for the CLI version of MBASIC.
    It uses Python's built-in input() and print() functions.
    """

    def __init__(self, debug_enabled: bool = False):
        """Initialize console I/O handler.

        Args:
            debug_enabled: If True, debug() will output messages
        """
        self.debug_enabled = debug_enabled

    def output(self, text: str, end: str = '\n') -> None:
        """Output text to console."""
        print(text, end=end)
        sys.stdout.flush()

    def input(self, prompt: str = '') -> str:
        """Input text from console."""
        if prompt:
            print(prompt, end='')
            sys.stdout.flush()
        return input()

    def input_line(self, prompt: str = '') -> str:
        """Input a complete line from console.

        For console, this delegates to self.input() (same behavior).

        Note: Python's input() strips only the trailing newline. Leading/trailing
        spaces are generally preserved, but terminal input behavior may vary across
        platforms. See input_line() documentation in base.py for details.
        """
        return self.input(prompt)

    def input_char(self, blocking: bool = True) -> str:
        """Input single character from console.

        Args:
            blocking: If True, wait for keypress. If False, return "" if no key.

        Note: Non-blocking input is complex on different platforms.
        This implementation provides basic support.
        """
        if not blocking:
            # Non-blocking: check if input is available
            # This is platform-specific and simplified here
            import select
            if sys.platform != 'win32':
                # Unix/Linux: use select
                if select.select([sys.stdin], [], [], 0.0)[0]:
                    return sys.stdin.read(1)
                else:
                    return ""
            else:
                # Windows: use msvcrt if available
                try:
                    import msvcrt
                    if msvcrt.kbhit():
                        return msvcrt.getch().decode('utf-8', errors='ignore')
                    else:
                        return ""
                except ImportError:
                    # Fallback: return empty string (msvcrt not available)
                    import warnings
                    warnings.warn("msvcrt not available on Windows - non-blocking input_char() not supported", RuntimeWarning)
                    return ""
        else:
            # Blocking: wait for single character
            if sys.platform != 'win32':
                # Unix/Linux: read single char
                import tty
                import termios
                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                try:
                    tty.setraw(fd)
                    ch = sys.stdin.read(1)
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                return ch
            else:
                # Windows: use msvcrt
                try:
                    import msvcrt
                    return msvcrt.getch().decode('utf-8', errors='ignore')
                except ImportError:
                    # Fallback for Windows without msvcrt: use input() with severe limitations
                    # WARNING: This fallback calls input() which:
                    # - Waits for Enter key (defeats the purpose of single-char input)
                    # - Reads the entire line but returns only the first character
                    # This is a known limitation when msvcrt is unavailable.
                    # For proper single-character input on Windows, msvcrt is required.
                    import warnings
                    warnings.warn(
                        "msvcrt not available on Windows - input_char() falling back to input() "
                        "(waits for Enter, not single character)",
                        RuntimeWarning
                    )
                    line = input()
                    return line[:1] if line else ""

    def clear_screen(self) -> None:
        """Clear the console screen."""
        if sys.platform == 'win32':
            os.system('cls')
        else:
            os.system('clear')

    def error(self, message: str) -> None:
        """Output error message to console."""
        print(f"Error: {message}", file=sys.stderr)
        sys.stderr.flush()

    def debug(self, message: str) -> None:
        """Output debug message if debugging is enabled."""
        if self.debug_enabled:
            print(f"DEBUG: {message}", file=sys.stderr)
            sys.stderr.flush()

    def locate(self, row: int, col: int) -> None:
        """Move cursor to specific position using ANSI escape codes.

        Args:
            row: Row number (1-based)
            col: Column number (1-based)
        """
        # ANSI escape sequence for cursor positioning
        print(f'\033[{row};{col}H', end='')
        sys.stdout.flush()

    def get_cursor_position(self) -> tuple[int, int]:
        """Get current cursor position.

        Note: This is difficult to implement portably in console.
        Returns (1, 1) by default.
        """
        # Getting cursor position in console is complex and platform-specific
        # Return default position
        return (1, 1)
