"""Console-based I/O handler for terminal/CLI use.

This module provides a console implementation of IOHandler that uses
standard Python input() and print() functions. This is the default
I/O handler for the command-line MBASIC interpreter.
"""

import contextlib
import os
import select
import signal
import sys

try:
    import tty
    import termios
except ImportError:
    # POSIX only. The guard has to wrap the import itself - putting ImportError
    # in a handler around the use never fires, because by then the import has
    # already propagated. On Windows there is no raw mode to set.
    tty = None
    termios = None

from .base import IOHandler
from src.debug_logger import debug_log
from src.terminal_errors import TERMINAL_ERRORS
from src.win_console import win_read_key, win_locate

#: Ctrl+C. On a terminal it only reaches a reader at all because raw mode
#: clears ISIG; in cooked mode the line discipline turns it into SIGINT. What
#: it MEANS is the caller's business - see BuiltinFunctions._raise_break.
INTERRUPT_CHAR = '\x03'

#: How often a blocking read looks up from the keyboard to see whether it has
#: been interrupted. Only costs a wakeup: select() returns the instant a key is
#: actually typed.
_INTERRUPT_POLL = 0.1


@contextlib.contextmanager
def _terminal_restored_if_killed(fd, old_settings):
    """Put the terminal back if the process is killed during the read.

    Raw mode is held for the whole blocking wait, and the restoring tcsetattr
    lives in a `finally` that a SIGTERM never reaches - so `timeout 5 python3
    mbasic ...`, a CI kill, or closing the window while a program sits at
    INPUT$ would leave the user's terminal with no echo and no Ctrl+C, needing
    `stty sane`. Neither SIGINT (raw mode has already turned it into a plain
    byte) nor SIGKILL (uncatchable) is involved here.

    A no-op off the main thread, where signal.signal() cannot be called.
    """
    previous = {}

    def restore_and_die(signum, _frame):
        try:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except TERMINAL_ERRORS:
            pass
        # Hand the signal back to whoever had it and re-raise, so the process
        # still dies exactly as it was told to.
        signal.signal(signum, previous.get(signum, signal.SIG_DFL))
        os.kill(os.getpid(), signum)

    for name in ('SIGTERM', 'SIGHUP'):
        number = getattr(signal, name, None)
        if number is None:
            continue
        try:
            previous[number] = signal.signal(number, restore_and_die)
        except (ValueError, OSError, RuntimeError):
            pass                # not the main thread, or not supported here
    try:
        yield
    finally:
        for number, handler in previous.items():
            try:
                signal.signal(number, handler)
            except (ValueError, OSError, RuntimeError):
                pass


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
        """
        if blocking:
            return self.input_chars(1)

        if sys.platform == 'win32':
            # Windows: resolve the two-call extended-key protocol and the
            # console codepage, neither of which survived the old
            # decode('utf-8', errors='ignore').
            return win_read_key(blocking=False)

        try:
            # isatty() inside the try because it raises on a closed or
            # substituted stdin, which is what TERMINAL_ERRORS is for. A pipe
            # is always "readable", so without this check a polling INKEY$ on
            # piped input would eat the script it is being fed.
            if not sys.stdin.isatty():
                return ""
            if not select.select([sys.stdin], [], [], 0.0)[0]:
                return ""
            # os.read rather than sys.stdin.read(1): the TextIOWrapper drains
            # the whole kernel queue into its decode buffer, leaving select()
            # blind to bytes still pending.
            data = os.read(sys.stdin.fileno(), 1)
            return data.decode('latin-1') if data else ""
        except TERMINAL_ERRORS:
            return ""

    def input_chars(self, count: int, interrupted=None) -> str:
        """Read up to count characters from the console. See IOHandler.

        Raw, unbuffered and byte-transparent, which is what MBASIC's INPUT$
        needs: nothing echoed, no Enter, every control character delivered.

        - ``sys.stdin.read(1)`` would go through a TextIOWrapper that pulls the
          whole kernel queue into a userspace buffer no other reader can see.
          Typing "AB" then Enter at INPUT$(1) gave the program "A" and
          stranded "B\\n" there, invisible to the REPL and to the INPUT
          statement, which both read at the file descriptor - and the next
          program's INPUT$ then picked it up as though freshly typed.
        - ``tty.setraw()`` defaults to TCSAFLUSH, which discards input that has
          arrived but not been read. Keys typed ahead of the read must survive,
          so this uses TCSANOW.

        Raw mode is entered once for the whole read rather than per character:
        dropping back to cooked mode between characters would echo the rest of
        what the user typed and wait for Enter before delivering it.
        """
        if count <= 0:
            return ""

        if sys.platform == 'win32':
            return self._read_windows(count)

        if termios is None or tty is None:
            # No POSIX terminal control, and not the Windows branch either -
            # there is no raw mode to be had, so stdin had better be a pipe.
            return self._read_cooked(count)

        try:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
        except TERMINAL_ERRORS:
            # Not a terminal: piped input, a file, or a stdin replacement with
            # no real fd. termios.error is why that tuple exists - it is not an
            # OSError subclass, so "this is not a terminal" escaped the
            # handlers that used to be written as except OSError.
            return self._read_cooked(count)

        chars = ""
        raw_failed = False
        try:
            with _terminal_restored_if_killed(fd, old_settings):
                tty.setraw(fd, termios.TCSANOW)
                while len(chars) < count:
                    # A SIGINT that arrived before setraw() - the window
                    # between a program's prompt and this line - interrupts
                    # nothing by itself, and PEP 475 restarts the read
                    # underneath it. Polling is what turns that into an
                    # abandoned read rather than a wait that then swallows
                    # whatever key finally ends it.
                    if interrupted is not None and interrupted():
                        break
                    if not select.select([fd], [], [], _INTERRUPT_POLL)[0]:
                        continue
                    # One byte at a time, deliberately. Reading the whole
                    # remainder in one call would consume anything typed after
                    # a Ctrl+C along with it, and a caller that treats Ctrl+C
                    # as a break would then destroy keystrokes that should have
                    # stayed queued.
                    data = os.read(fd, 1)
                    if not data:
                        break               # EOF - the terminal went away
                    # latin-1 keeps this byte-transparent, so ASC() means the
                    # same here as it does under INKEY$ and on Windows.
                    char = data.decode('latin-1')
                    chars += char
                    if char == INTERRUPT_CHAR:
                        break
        except TERMINAL_ERRORS:
            # Falling back is only safe if nothing was read. Reading again
            # after a partial read would deliver those characters twice.
            raw_failed = not chars
            if not raw_failed:
                debug_log(f"console read failed after {len(chars)} of {count} "
                          f"characters; returning a short string")
        finally:
            try:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            except TERMINAL_ERRORS:
                # The characters are already in hand; a failure to put the
                # terminal back must not lose them or read a second time.
                pass

        if raw_failed:
            return self._read_cooked(count)
        return chars

    def _read_windows(self, count: int) -> str:
        """Read count characters through the Windows console."""
        try:
            redirected = not sys.stdin.isatty()
        except TERMINAL_ERRORS:
            redirected = True
        if redirected:
            # msvcrt.getch() reads CONIN$ - the physical console - not stdin,
            # so under `mbasic prog.bas < in.txt` it would ignore the
            # redirection completely and block on a keypress that is never
            # coming. POSIX gets this check for free, because tcgetattr fails
            # on a pipe; Windows has to ask.
            return self._read_cooked(count)

        chars = ""
        while len(chars) < count:
            # The shared helper resolves prefix+scan-code pairs and returns one
            # character per call.
            ch = win_read_key(blocking=True)
            if not ch:
                # "" from a *blocking* read means there is no console at all -
                # msvcrt missing, or a detached process such as pythonw.exe
                # where CONIN$ cannot be opened - not "no key pending".
                # WARNING: the fallback reads a whole line and waits for Enter,
                # which defeats single-character input.
                import warnings
                warnings.warn(
                    "no console available for input_chars() - falling back to "
                    "input() (waits for Enter, not single characters)",
                    RuntimeWarning
                )
                # A whole line for a single-character request, so keep it out
                # of the command history like every other program read.
                line = input_without_history()
                return chars + (line[:count - len(chars)] if line else "")
            chars += ch
            if ch == INTERRUPT_CHAR:
                break
        return chars

    @staticmethod
    def _read_cooked(count: int) -> str:
        """Read without raw mode: piped input, or no terminal control at all.

        Deliberately still sys.stdin rather than os.read. With no tty there is
        no readline either, so the REPL and the INPUT statement are reading
        through this same TextIOWrapper - matching them is what keeps the
        characters in order.
        """
        chars = ""
        try:
            for _ in range(count):
                ch = sys.stdin.read(1)
                if not ch:
                    break                   # EOF
                chars += ch
                if ch == INTERRUPT_CHAR:
                    # Stop here, so whatever follows stays in the buffer for
                    # the next reader rather than being consumed by a read the
                    # caller is about to abandon.
                    break
        except TERMINAL_ERRORS:
            # This is the end of the line for a keyboard read, so it degrades
            # rather than raising: under pythonw.exe sys.stdin is None
            # (AttributeError), and a closed or substituted stdin gives the
            # other two. The read comes back short, as it does at EOF.
            pass
        return chars

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

        Does nothing when the output is not an interactive console. The escape
        is a control language addressed to a terminal; written into a
        redirected file it is just corruption of the output.
        """
        try:
            row = max(1, int(row))
            col = max(1, int(col))
        except (TypeError, ValueError):
            return

        if sys.platform == 'win32':
            # conhost does not interpret ANSI unless asked, so writing the
            # escape blind put literal garbage on the screen. win_locate()
            # turns on ENABLE_VIRTUAL_TERMINAL_PROCESSING once per process and
            # returns False when stdout is not a console, or when the console
            # is too old to support it (Windows 8, Windows 10 before 1511).
            if not win_locate(row, col):
                return
        else:
            try:
                if not sys.stdout.isatty():
                    return
            except (AttributeError, ValueError):
                return      # stdout replaced by something odd, or closed

        try:
            print(f'\033[{row};{col}H', end='')
            sys.stdout.flush()
        except (OSError, ValueError):
            pass

    def get_cursor_position(self) -> tuple[int, int]:
        """Get current cursor position.

        Note: This is difficult to implement portably in console.
        Returns (1, 1) by default.
        """
        # Getting cursor position in console is complex and platform-specific
        # Return default position
        return (1, 1)


class ConsoleKeyboardMixin:
    """Keyboard reads for a handler that captures output but has no input.

    INKEY$ and INPUT$ go through the interpreter's I/O handler now, so a
    handler without them raises AttributeError where it used to be bypassed
    entirely - the builtins read ``sys.stdin`` directly and nobody noticed
    which handler was installed.

    Mixing this in keeps that behavior, deliberately: it reads the process's
    own terminal, which is exactly what those builtins were doing before. It
    is a placeholder, not a design. A backend with a real keyboard - curses,
    Tk, the web UI - should implement ``input_char``/``input_chars`` itself and
    stop reading the launching terminal from inside its own event loop.
    """

    def input_char(self, blocking: bool = True) -> str:
        return self._console_keyboard().input_char(blocking=blocking)

    def input_chars(self, count: int, interrupted=None) -> str:
        return self._console_keyboard().input_chars(count,
                                                    interrupted=interrupted)

    def _console_keyboard(self):
        handler = getattr(self, '_console_keyboard_handler', None)
        if handler is None:
            handler = ConsoleIOHandler()
            self._console_keyboard_handler = handler
        return handler
