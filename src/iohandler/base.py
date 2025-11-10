"""Abstract base interface for I/O operations.

This module defines the IOHandler interface that all I/O backends
must implement. This allows the interpreter to work with different
I/O systems (console, GUI, web, embedded) without changing core logic.
"""

from abc import ABC, abstractmethod
from typing import Optional


class IOHandler(ABC):
    """Abstract interface for I/O operations.

    All I/O backends (console, GUI, etc.) must implement this interface.
    This allows the MBASIC interpreter to work with any I/O system without
    modifying the core interpreter logic.

    Note: Implementations may provide additional methods beyond this interface
    for backend-specific functionality (e.g., web_io.get_screen_size()). Such
    methods are not part of the core interface and should only be used by
    backend-specific code.
    """

    @abstractmethod
    def output(self, text: str, end: str = '\n') -> None:
        """Output text to the user.

        Args:
            text: The text to output
            end: String to append after text (default: newline)

        Examples:
            output("HELLO")           # Outputs: HELLO\n
            output("HELLO", end="")   # Outputs: HELLO (no newline)
            output("X = ", end="")    # For prompts without newline
        """
        pass

    @abstractmethod
    def input(self, prompt: str = '') -> str:
        """Input text from the user (INPUT statement).

        Args:
            prompt: Optional prompt to display before input

        Returns:
            String entered by user (without trailing newline)

        Examples:
            name = input("Enter name: ")
            value = input("? ")
        """
        pass

    @abstractmethod
    def input_line(self, prompt: str = '') -> str:
        """Input a complete line from user (LINE INPUT statement).

        Design goal: Preserve leading/trailing spaces and not interpret commas as
        field separators (for MBASIC LINE INPUT compatibility).

        Args:
            prompt: Optional prompt to display

        Returns:
            Complete line entered by user

        Examples:
            line = input_line("Enter text: ")

        KNOWN LIMITATION (not a bug - platform limitation):
        Current implementations (console, curses, web) CANNOT fully preserve
        leading/trailing spaces due to underlying platform API constraints:
        - console: Python input() strips the trailing newline. Leading/trailing spaces
                   are generally preserved, but terminal behavior may vary by platform.
        - curses: getstr() strips trailing whitespace (spaces, tabs, newlines)
        - web: HTML input fields strip leading/trailing whitespace by default
        This is an accepted limitation of the underlying platform APIs, not an
        implementation defect.
        """
        pass

    @abstractmethod
    def input_char(self, blocking: bool = True) -> str:
        """Input single character (INKEY$, INPUT$).

        Args:
            blocking: If True, wait for keypress. If False, return "" if no key ready.

        Returns:
            Single character string, or "" if non-blocking and no key available

        Examples:
            key = input_char(blocking=False)  # INKEY$ - non-blocking
            ch = input_char(blocking=True)    # INPUT$(1) - blocking
        """
        pass

    @abstractmethod
    def clear_screen(self) -> None:
        """Clear the screen (CLS statement).

        Clears all output and moves cursor to top-left.
        """
        pass

    @abstractmethod
    def error(self, message: str) -> None:
        """Output error message.

        Args:
            message: Error message to display

        Examples:
            error("Syntax error in 100")
            error("Type mismatch")
        """
        pass

    @abstractmethod
    def debug(self, message: str) -> None:
        """Output debug message (if debugging enabled).

        Args:
            message: Debug message to display

        Only outputs if debug mode is enabled. In production,
        this may be a no-op.
        """
        pass

    def locate(self, row: int, col: int) -> None:
        """Move cursor to specific position (LOCATE statement).

        Args:
            row: Row number (1-based)
            col: Column number (1-based)

        Default implementation does nothing. Override for cursor control.
        """
        pass

    def get_cursor_position(self) -> tuple[int, int]:
        """Get current cursor position.

        Returns:
            Tuple of (row, col) where both are 1-based

        Default implementation returns (1, 1). Override for cursor tracking.
        """
        return (1, 1)
