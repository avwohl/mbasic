#!/usr/bin/env python3
"""
Test that INKEY$ and INPUT$ read through the I/O handler, not process stdin.

Both builtins used to go straight to sys.stdin. `BuiltinFunctions` was built
with only the runtime, so no backend could intercept them - measured before the
change: with a CapturingIOHandler whose input_char() returns "", INPUT$(1)
still returned a byte piped to the process. Under the curses, web and Tk UIs
that meant the two builtins read the server or launching terminal instead of
the UI, from inside that UI's own event-loop callback.

`IOHandler.input_char()` was the intended seam all along - three separate
comments described ConsoleIOHandler.input_char as "the INPUT$ reader" while
nothing called it - so this wires them to it rather than inventing anything.

INPUT$(n) needs more than n calls to input_char(): a terminal has to hold one
mode for the whole read, or the characters after the first are echoed and it
waits for Enter. That is `input_chars(count, interrupted=...)`, which the base
class implements by looping so that a backend only overrides it if it cares.

No terminal and no pty here: this is about which object gets asked.
"""

import os
import sys

# Add project root to path (3 levels up from tests/regression/*/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.interpreter import Interpreter, BreakException
from src.iohandler.base import IOHandler
from src.runtime import Runtime

results = []


def check(condition, label):
    """Record one check; print pass/fail immediately."""
    results.append(bool(condition))
    print(f"{'PASS' if condition else 'FAIL'}: {label}")


class ExplodingStdin:
    """A stdin that fails the test if anything reads it."""

    def __init__(self):
        self.touched = []

    def _boom(self, *_args, **_kwargs):
        self.touched.append(True)
        raise AssertionError("the builtins read process stdin")

    read = fileno = isatty = readline = _boom


class DuckHandler:
    """A handler with only input_char - like src/ui/capturing_io_handler.py.

    Not an IOHandler subclass, on purpose: several handlers in this codebase
    are plain classes, so the fallback loop has to cope with one.
    """

    def __init__(self, keys=''):
        self.pending = list(keys)
        self.calls = 0

    def input_char(self, blocking=True):
        self.calls += 1
        return self.pending.pop(0) if self.pending else ""


class BulkHandler(IOHandler):
    """A handler that overrides input_chars, as ConsoleIOHandler does."""

    def __init__(self, keys=''):
        self.pending = list(keys)
        self.bulk_calls = 0
        self.char_calls = 0

    def input_chars(self, count, interrupted=None):
        self.bulk_calls += 1
        taken, self.pending = self.pending[:count], self.pending[count:]
        return ''.join(taken)

    # The rest of the abstract surface, unused here.
    def output(self, text, end='\n'):
        pass

    def input(self, prompt=''):
        return ""

    def input_line(self, prompt=''):
        return ""

    def input_char(self, blocking=True):
        self.char_calls += 1
        return self.pending.pop(0) if self.pending else ""

    def clear_screen(self):
        pass

    def error(self, message):
        pass

    def debug(self, message):
        pass


def interpreter_with(handler):
    """An interpreter with no program - only the builtins are exercised."""
    return Interpreter(Runtime({}), io_handler=handler)


def without_stdin(fn):
    """Run fn with a stdin that raises if it is read."""
    guard = ExplodingStdin()
    saved, sys.stdin = sys.stdin, guard
    try:
        return fn(), guard
    finally:
        sys.stdin = saved


def test_inkey_asks_the_handler():
    """INKEY$ must come from the handler, not the process's terminal."""
    print("\nINKEY$ reads through the I/O handler")
    print("-" * 60)
    handler = DuckHandler('XY')
    interp = interpreter_with(handler)

    (got, _), guard = without_stdin(
        lambda: (interp.builtins.INKEY(), interp.builtins.INKEY()))

    check(got == 'X', f"the handler's character came back (got {got!r})")
    check(handler.calls == 2, f"one call per INKEY$ (got {handler.calls})")
    check(not guard.touched, "and stdin was never touched")


def test_inkey_reports_no_key_as_empty():
    """An empty handler means "no key pending", which is what INKEY$ says."""
    print("\nINKEY$ with nothing pending")
    print("-" * 60)
    interp = interpreter_with(DuckHandler(''))
    got, _ = without_stdin(lambda: interp.builtins.INKEY())
    check(got == "", f"INKEY$ returned empty (got {got!r})")


def test_input_dollar_asks_the_handler():
    """INPUT$(n) must come from the handler too."""
    print("\nINPUT$(n) reads through the I/O handler")
    print("-" * 60)
    handler = DuckHandler('ABCD')
    interp = interpreter_with(handler)

    got, guard = without_stdin(lambda: interp.builtins.INPUT(3))

    check(got == 'ABC', f"three characters, in order (got {got!r})")
    check(handler.calls == 3,
          f"one input_char per character, since this handler has no "
          f"input_chars (got {handler.calls})")
    check(not guard.touched, "and stdin was never touched")


def test_a_handler_can_take_the_whole_read():
    """input_chars() lets a handler hold its input device for the whole read.

    ConsoleIOHandler overrides it because a terminal cannot do INPUT$(3) as
    three separate raw reads without echoing the last two.
    """
    print("\nINPUT$(n) uses input_chars when the handler provides it")
    print("-" * 60)
    handler = BulkHandler('ABCD')
    interp = interpreter_with(handler)

    got, _ = without_stdin(lambda: interp.builtins.INPUT(3))

    check(got == 'ABC', f"three characters, in order (got {got!r})")
    check(handler.bulk_calls == 1,
          f"asked for all three at once (got {handler.bulk_calls} calls)")
    check(handler.char_calls == 0,
          f"and not one at a time (got {handler.char_calls})")


def test_short_read_is_not_padded():
    """A handler with less than asked for ends the read, as EOF does."""
    print("\nINPUT$(n) accepts a short answer")
    print("-" * 60)
    interp = interpreter_with(DuckHandler('A'))
    got, _ = without_stdin(lambda: interp.builtins.INPUT(3))
    check(got == 'A', f"what there was, and no more (got {got!r})")


def test_ctrl_c_from_a_handler_breaks():
    """CHR$(3) is a break wherever it comes from - the policy lives here.

    The handler returns it like any other character; deciding what it means is
    the builtin's business, so a backend does not have to know about
    BreakException.
    """
    print("\nCtrl+C from a handler breaks the program")
    print("-" * 60)
    for label, handler in (('input_char', DuckHandler('A\x03B')),
                           ('input_chars', BulkHandler('A\x03B'))):
        interp = interpreter_with(handler)
        try:
            got = without_stdin(lambda: interp.builtins.INPUT(3))[0]
            raised = None
        except BreakException as exc:
            got, raised = None, exc
        check(isinstance(raised, BreakException),
              f"{label}: a returned CHR$(3) raised BreakException "
              f"(got {got!r})")

    # And a handler that never yields one just returns characters.
    interp = interpreter_with(DuckHandler('AB'))
    got, _ = without_stdin(lambda: interp.builtins.INPUT(2))
    check(got == 'AB', f"an ordinary read still returns (got {got!r})")


def test_handler_swapped_after_construction_is_honoured():
    """The curses UI assigns interpreter.io after building the interpreter.

    src/ui/curses_ui.py does exactly this, so a builtin that captured the
    handler it was constructed with would go on reading the replaced one.
    """
    print("\nreplacing interpreter.io redirects the builtins")
    print("-" * 60)
    first = DuckHandler('AAA')
    interp = interpreter_with(first)
    second = DuckHandler('ZZZ')
    interp.io = second

    got, _ = without_stdin(lambda: interp.builtins.INPUT(1))

    check(got == 'Z', f"the read went to the new handler (got {got!r})")
    check(first.calls == 0, f"and not the old one (got {first.calls} calls)")


def test_file_reads_are_untouched():
    """INPUT$(n,#f) is file I/O and has nothing to do with the handler."""
    print("\nINPUT$(n,#f) still reads the file")
    print("-" * 60)
    import tempfile

    handler = DuckHandler('XXXX')
    interp = interpreter_with(handler)
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.dat',
                                     delete=False) as fh:
        fh.write('HELLO')
        path = fh.name
    try:
        with open(path, 'r') as opened:
            interp.runtime.files[1] = {'handle': opened, 'mode': 'I',
                                       'filename': path}
            got = interp.builtins.INPUT(3, 1)
    finally:
        interp.runtime.files.pop(1, None)
        os.unlink(path)

    check(got == 'HEL', f"the file's characters came back (got {got!r})")
    check(handler.calls == 0,
          f"the keyboard handler was not consulted (got {handler.calls})")


if __name__ == "__main__":
    print("INKEY$ / INPUT$ routing through the I/O handler")
    print("=" * 60)

    test_inkey_asks_the_handler()
    test_inkey_reports_no_key_as_empty()
    test_input_dollar_asks_the_handler()
    test_a_handler_can_take_the_whole_read()
    test_short_read_is_not_padded()
    test_ctrl_c_from_a_handler_breaks()
    test_handler_swapped_after_construction_is_honoured()
    test_file_reads_are_untouched()

    failed = results.count(False)
    print("\n" + "=" * 60)
    print(f"Results: {results.count(True)} passed, {failed} failed")

    if failed:
        print("❌ Some tests failed")
        sys.exit(1)
    print("✅ All tests passed!")
    sys.exit(0)
