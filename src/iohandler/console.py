"""Console-based I/O handler for terminal/CLI use.

This module provides a console implementation of IOHandler that uses
standard Python input() and print() functions. This is the default
I/O handler for the command-line MBASIC interpreter.
"""

import sys
import os
from .base import IOHandler
from src.terminal_errors import TERMINAL_ERRORS


def input_without_history() -> str:
    """Read a line like input(), but keep it out of the command history.

    Answers to a program's INPUT statement are data, not commands. Without
    this they are recorded by readline alongside the commands the user typed,
    so pressing Up at the "Ok" prompt scrolls back through whatever a program
    asked for - and they are then persisted to ~/.mbasic_history.

    set_auto_history() is a flag inside CPython's readline module rather than
    something the C library does, so this behaves the same on GNU readline and
    on libedit. When readline is missing (or is a shim that predates the call)
    there is no history being kept, so there is nothing to suppress.
    """
    try:
        import readline
        set_auto_history = readline.set_auto_history
    except (ImportError, AttributeError):
        return input()

    # There is no getter for this flag, but mbasic never turns it off
    # globally, so restoring it to True restores the status quo. The disable
    # is inside the try so that even an exception raised between it and the
    # read cannot leave history switched off for the rest of the session.
    try:
        set_auto_history(False)
        return input()
    finally:
        set_auto_history(True)


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
        return input_without_history()

    def input_line(self, prompt: str = '') -> str:
        """Input a complete line from console.

        For console, this delegates to self.input() (same behavior).

        Note: Python's input() strips only the trailing newline. Leading/trailing
        spaces are generally preserved on most platforms, though behavior may vary
        slightly. See input_line() documentation in base.py for platform limitations.
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
                ch = None
                got_char = False
                try:
                    fd = sys.stdin.fileno()
                    old_settings = termios.tcgetattr(fd)
                    try:
                        tty.setraw(fd)
                        ch = sys.stdin.read(1)
                        got_char = True
                    finally:
                        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                except TERMINAL_ERRORS:
                    # No terminal to put in raw mode (piped input, or stdin
                    # replaced by something without a real fd). Read cooked
                    # instead of dying: termios.error is not an OSError
                    # subclass, so an unguarded tcgetattr escapes as
                    # "(25, 'Inappropriate ioctl for device')".
                    if not got_char:
                        return sys.stdin.read(1)
                    # Only the restore failed - the character is already in
                    # hand, and reading again would consume a second one.
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
                    # Whole line for a single-character request, so keep it out
                    # of the command history like every other program read.
                    line = input_without_history()
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
