"""Abstract base interface for I/O operations.

This module defines the IOHandler interface that all I/O backends
must implement. This allows the interpreter to work with different
I/O systems (console, GUI, web, embedded) without changing core logic.
"""

import functools
from abc import ABC, abstractmethod
from typing import Optional

from src.print_column import SCREEN_WIDTH, advance_column


class KeyInputPending(Exception):
    """Raised by input_chars() when it cannot answer without blocking.

    For a handler whose keyboard arrives on the same thread that would have to
    wait for it. The web UI is the case: its keys come over a websocket served
    by the asyncio loop that also ticks the interpreter, so blocking for a
    keypress deadlocks - the key can never arrive - and every other session on
    the server stops with it.

    The interpreter treats this as "not yet": the statement is left where it
    is, execution pauses, and the same statement runs again once the handler
    says it can answer. INPUT$ is idempotent, and this is the resume model
    Ctrl+C/CONT already uses on that statement.

    A handler that raises this MUST NOT consume anything on the way out, or
    the retry will ask for characters that have already been taken. Take all
    of them or none.

    Terminal handlers never raise it: they block, which is what a terminal is
    for.
    """


class KeyReadTransaction:
    """Mixin for a handler whose reads have to survive a retried statement.

    A handler that raises KeyInputPending makes the interpreter run the
    statement again, and a statement can read the keyboard more than once:

        10 X$=INPUT$(1)+INPUT$(1)

    The first read succeeds and takes a character; the second raises; the
    retry runs the first read AGAIN and takes another. Without this the
    program eats every key it is given and never completes - measured before
    the fix: four keys queued, four keys consumed, line 20 never reached.

    So an attempt is bracketed. Everything read since begin_key_transaction()
    is remembered, and rollback_key_transaction() puts it back in order, so
    the retry starts from exactly the state the first attempt did.

    A terminal handler cannot do this - its characters came out of the kernel
    and cannot be pushed back - which is why `defers_key_reads` is what turns
    the bracketing on rather than it being unconditional. Terminals never need
    it: they block instead of raising.
    """

    #: Set True by a handler whose input_chars() may raise KeyInputPending.
    #: The interpreter only pays for the bracketing when this is on.
    defers_key_reads = False

    def begin_key_transaction(self) -> None:
        """Start recording what this statement attempt reads."""

    def rollback_key_transaction(self) -> None:
        """Put back everything read since begin_key_transaction()."""


def _update_after_output(handler, args, kwargs):
    text = args[0] if args else kwargs.get('text', '')
    end = args[1] if len(args) > 1 else kwargs.get('end', '\n')
    handler.column = advance_column(handler.column, str(text) + str(end))


def _update_to_line_start(handler, args, kwargs):
    # INPUT and LINE INPUT end with the Enter the user typed.
    handler.column = 0


def _update_after_locate(handler, args, kwargs):
    col = args[1] if len(args) > 1 else kwargs.get('col', 1)
    try:
        handler.column = max(int(col) - 1, 0)
    except (TypeError, ValueError):
        pass


_COLUMN_UPDATES = {
    'output': _update_after_output,
    'input': _update_to_line_start,
    'input_line': _update_to_line_start,
    'clear_screen': _update_to_line_start,
    'locate': _update_after_locate,
}


def _track_column(method, update):
    """Wrap a handler method so the handler's column follows what it does.

    Only the outermost call counts: a subclass that calls super().output()
    would otherwise be counted twice.
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        depth = self.__dict__.get('_column_depth', 0)
        self._column_depth = depth + 1
        try:
            result = method(self, *args, **kwargs)
        finally:
            self._column_depth = depth
        if depth == 0:
            update(self, args, kwargs)
        return result
    wrapper._tracks_column = True
    return wrapper


class ColumnTracker:
    """Mixin that makes an output handler keep the cursor column.

    IOHandler has it, and so do the handlers that do not derive from
    IOHandler (the capturing handlers of the curses UI).
    """

    #: The width WIDTH set for the screen. PRINT wraps and sets its TAB and
    #: comma zones from it.
    width = SCREEN_WIDTH

    #: The cursor column, 0-based. Every subclass gets output(), input(),
    #: input_line(), clear_screen() and locate() wrapped (see
    #: __init_subclass__), so the column follows whatever a backend draws,
    #: and PRINT, TAB, the comma zones and POS see the real cursor column
    #: across statements and after an INPUT.
    column = 0

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        for name, update in _COLUMN_UPDATES.items():
            method = cls.__dict__.get(name)
            if method is not None and not getattr(method, '_tracks_column', False):
                setattr(cls, name, _track_column(method, update))


class IOHandler(ABC, KeyReadTransaction, ColumnTracker):
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
        """Input single character.

        This is how INKEY$ reads a key. A backend that has its own keyboard -
        curses, Tk, the web UI - implements it and the builtin gets whatever
        it returns; nothing else in the interpreter touches the keyboard.

        Args:
            blocking: If True, wait for keypress. If False, return "" if no key ready.

        Returns:
            Single character string, or "" if non-blocking and no key available

        Examples:
            key = input_char(blocking=False)  # INKEY$ - non-blocking
            ch = input_char(blocking=True)    # one character, waiting for it
        """
        pass

    def input_chars(self, count: int, interrupted=None) -> str:
        """Input up to count characters, waiting for them (INPUT$(n)).

        Separate from input_char() because a terminal cannot do this by
        calling that n times: it has to hold the terminal in one mode for the
        whole read, or the characters after the first are echoed and the read
        waits for Enter. ConsoleIOHandler overrides this; a backend with its
        own keyboard usually does not need to.

        May return fewer than count characters - at end of input, if
        `interrupted` becomes true, or when an interrupt character is read.

        Args:
            count: how many characters to read.
            interrupted: optional zero-argument callable polled while waiting.
                Returning True abandons the read. The console handler uses it
                to notice a SIGINT that arrived before the terminal was in raw
                mode; a backend that never blocks the interpreter can ignore
                it.

        Returns:
            The characters read. Ctrl+C (CHR$(3)) is returned like any other
            character, as the last one - deciding what it means belongs to the
            caller, not here.
        """
        chars = ""
        for _ in range(count):
            if interrupted is not None and interrupted():
                break
            char = self.input_char(blocking=True)
            if not char:
                break                       # end of input
            chars += char
            if char == '\x03':
                break                       # let the caller act on it
        return chars

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
