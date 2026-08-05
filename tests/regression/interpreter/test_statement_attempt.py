#!/usr/bin/env python3
"""
Test that a statement retried after pausing for a key leaves nothing behind.

A handler that cannot wait for a keypress raises KeyInputPending, and the
interpreter runs the statement again once a key arrives
(docs/dev/WEB_PROGRAM_KEYBOARD.md). Anything the abandoned attempt already did
would otherwise happen twice.

Most of a statement is safe to repeat. `execute_print` collects its output and
writes at the end, so an attempt that pauses mid-expression has printed
nothing - the duplicated output this was first documented as causing does not
happen, measured. The keys it read are given back by KeyReadTransaction.

What is left is what an *expression* can change, and there are two:

    10 X$=STR$(RND)+INPUT$(1)      draws a random number per attempt
    10 X$=INPUT$(1,1)+INPUT$(1)    reads a file byte per attempt

The first silently skips the generator forward - and a sequence is the only
thing a random number generator is for. The second leaves the file further on
than the program ever saw, so the next read is a byte short. Both are recorded
by StatementAttempt and put back.

None of this runs on a terminal: those block for their key instead of pausing,
so their statements are never retried, and `defers_key_reads` keeps the whole
mechanism switched off. There is a check for that here, because a regression
that turned it on everywhere would be invisible.
"""

import os
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.interpreter import Interpreter
from src.iohandler.base import IOHandler, KeyInputPending
from src.lexer import Lexer
from src.parser import Parser
from src.runtime import Runtime
from src.mbasic_rnd import MbasicRandom
from src.statement_attempt import StatementAttempt

results = []


def check(condition, label):
    """Record one check; print pass/fail immediately."""
    results.append(bool(condition))
    print(f"{'PASS' if condition else 'FAIL'}: {label}")


class DeferringHandler(IOHandler):
    """A handler that pauses instead of waiting, like the web UI's."""

    defers_key_reads = True

    def __init__(self, keys=''):
        self.queue = list(keys)
        self.taken = []
        self.lines = []

    # -- the keyboard ---------------------------------------------------
    def input_char(self, blocking=True):
        if not blocking:
            return self._take(1) if self.queue else ""
        return self.input_chars(1)

    def input_chars(self, count, interrupted=None):
        if len(self.queue) < count:
            raise KeyInputPending(f"{count} wanted, {len(self.queue)} queued")
        return self._take(count)

    def _take(self, count):
        taken, self.queue = self.queue[:count], self.queue[count:]
        self.taken.extend(taken)
        return ''.join(taken)

    def begin_key_transaction(self):
        self.taken = []

    def rollback_key_transaction(self):
        self.queue[:0] = self.taken
        self.taken = []

    # -- the rest -------------------------------------------------------
    def output(self, text, end='\n'):
        self.lines.append(str(text) + end)

    def input(self, prompt=''):
        return ""

    def input_line(self, prompt=''):
        return ""

    def clear_screen(self):
        pass

    def error(self, message):
        self.lines.append(f"Error: {message}\n")

    def debug(self, message):
        pass

    def text(self):
        return ''.join(self.lines)


def run_program(source, handler, keys_per_tick=(), ticks=10):
    """Run a program, feeding a key after each tick that pauses."""
    ast = Parser(Lexer(source).tokenize()).parse()
    runtime = Runtime({line.line_number: line for line in ast.lines})
    interpreter = Interpreter(runtime, handler)
    interpreter.start()
    feed = list(keys_per_tick)
    for _ in range(ticks):
        state = interpreter.tick(mode='run', max_statements=1000)
        if not state.waiting_for_key:
            return state
        if feed:
            handler.queue.extend(feed.pop(0))
    return state


# ---------------------------------------------------------------------------
# StatementAttempt on its own
# ---------------------------------------------------------------------------

class FakeRuntime:
    def __init__(self):
        self.rnd = MbasicRandom()
        self.files = {}


def test_the_generator_is_snapshotted_once():
    """The state to go back to is the one before the FIRST draw."""
    print("\nthe random generator is restored to where the attempt found it")
    print("-" * 60)
    runtime = FakeRuntime()
    attempt = StatementAttempt()

    reference = MbasicRandom()
    expected = [reference.next() for _ in range(3)]

    attempt.note_random(runtime)
    drawn = [runtime.rnd.next()]
    attempt.note_random(runtime)        # a second draw in the same attempt
    drawn.append(runtime.rnd.next())
    attempt.rollback(runtime)

    check(drawn == expected[:2], "two numbers were drawn")
    after = [runtime.rnd.next() for _ in range(3)]
    check(after == expected,
          "and the sequence starts again from the beginning, not the middle")


def test_rollback_restores_the_whole_generator_state():
    """RND(0) returns the last number, and the counters pick the next
    constants, so seed and counters all have to go back together."""
    print("\nthe seed and all three counters are restored")
    print("-" * 60)
    runtime = FakeRuntime()
    for _ in range(5):
        runtime.rnd.next()
    before = runtime.rnd.state()
    attempt = StatementAttempt()
    attempt.note_random(runtime)
    for _ in range(3):
        runtime.rnd.next()
    check(runtime.rnd.state() != before, "the state moved")
    attempt.rollback(runtime)
    check(runtime.rnd.state() == before,
          f"and came back ({runtime.rnd.state()} vs {before})")


def test_file_positions_are_restored():
    """A file read in an abandoned attempt must be re-readable."""
    print("\nfile positions are rewound")
    print("-" * 60)
    path = tempfile.mktemp(suffix='.dat')
    with open(path, 'w') as handle:
        handle.write('ABCDEF')
    try:
        with open(path, 'rb') as handle:
            runtime = FakeRuntime()
            runtime.files = {1: {'handle': handle}}
            attempt = StatementAttempt()

            attempt.note_file_position(1, handle)
            first = handle.read(2)
            attempt.rollback(runtime)
            second = handle.read(2)

            check(first == b'AB', f"the attempt read AB (got {first!r})")
            check(second == b'AB',
                  f"and the retry reads the same bytes (got {second!r})")
    finally:
        os.unlink(path)


def test_reset_forgets_the_previous_attempt():
    """A committed statement is not undone by the next one's rollback."""
    print("\nreset() drops the previous attempt's record")
    print("-" * 60)
    runtime = FakeRuntime()
    attempt = StatementAttempt()
    attempt.note_random(runtime)
    drawn = runtime.rnd.next()
    attempt.reset()                     # the statement finished
    attempt.rollback(runtime)           # a later statement pauses
    check(runtime.rnd.next() != drawn,
          "the generator was not wound back to the finished statement")


# ---------------------------------------------------------------------------
# Through the interpreter
# ---------------------------------------------------------------------------

def test_rnd_is_not_advanced_by_a_pause():
    """The value a program gets must not depend on how often it waited."""
    print("\nRND in a paused statement does not skip the sequence")
    print("-" * 60)
    source = '10 X$=STR$(RND)+INPUT$(1)\n20 PRINT X$\n'

    # No seeding needed: MBASIC's generator starts from a fixed seed and each
    # run resets it, so the two runs are comparable by construction.
    paused = DeferringHandler()
    run_program(source, paused, keys_per_tick=['', '', '', 'Q'])

    direct = DeferringHandler('Q')
    run_program(source, direct)

    check('Q' in paused.text(), f"the paused run finished ({paused.text()!r})")
    check(paused.text() == direct.text(),
          f"and drew the same number as the run that never paused "
          f"({paused.text().strip()!r} vs {direct.text().strip()!r})")


def test_a_file_read_is_not_repeated_by_a_pause():
    """The file must end up exactly as far on as the program read."""
    print("\na file read in a paused statement is not repeated")
    print("-" * 60)
    path = tempfile.mktemp(suffix='.dat')
    with open(path, 'w') as handle:
        handle.write('ABCDEF')
    try:
        handler = DeferringHandler()
        run_program(
            f'10 OPEN "I",1,"{path}"\n'
            '20 X$=INPUT$(1,1)+INPUT$(1)\n'
            '30 PRINT "GOT";X$\n'
            '40 Y$=INPUT$(1,1)\n'
            '50 PRINT "NEXT";Y$\n',
            handler, keys_per_tick=['', '', 'Q'])

        text = handler.text()
        check('GOTAQ' in text.replace(' ', ''),
              f"the statement paired the first byte with the key ({text!r})")
        check('NEXTB' in text.replace(' ', ''),
              f"and the next read got the second byte, not the third ({text!r})")
    finally:
        os.unlink(path)


def test_input_dollar_from_a_file_is_a_string():
    """INPUT$(n,#f) used to return bytes, so ASC() read the repr.

    Mode 'I' files are opened 'rb' so EOF can spot a ^Z. PRINT showed b'ABC',
    and the help page's own example - PRINT HEX$(ASC(INPUT$(1,#1))) - answered
    98 for the 'b' of the repr instead of 65 for the 'A'. The '#' form did not
    parse at all, so that example failed twice over.
    """
    print("\nINPUT$ from a file returns characters, not a bytes repr")
    print("-" * 60)
    path = tempfile.mktemp(suffix='.dat')
    with open(path, 'w') as handle:
        handle.write('ABCDEF')
    try:
        handler = DeferringHandler()
        run_program(
            f'10 OPEN "I",1,"{path}"\n'
            '20 X$=INPUT$(3,#1)\n'
            '30 PRINT "GOT";X$\n'
            '40 PRINT "ASC";ASC(X$)\n',
            handler)
        text = handler.text().replace(' ', '')
        check('GOTABC' in text, f"the characters came back ({handler.text()!r})")
        check('ASC65' in text,
              f"and ASC() sees the first one, not a repr ({handler.text()!r})")
    finally:
        os.unlink(path)


def test_the_help_pages_own_example_runs():
    """docs/help/common/language/functions/input_dollar.md, Example 1.

    It hex-dumps a file with INPUT$(1, #1). Neither half of it worked: the '#'
    was a parse error, and ASC() of the bytes repr gave the wrong number.
    """
    print("\nthe help page's INPUT$ example produces the right hex dump")
    print("-" * 60)
    path = tempfile.mktemp(suffix='.dat')
    with open(path, 'w') as handle:
        handle.write('HI!')
    try:
        handler = DeferringHandler()
        run_program(
            f'10 OPEN "I", 1, "{path}"\n'
            '20 IF EOF(1) THEN 50\n'
            '30 PRINT HEX$(ASC(INPUT$(1, #1)));\n'
            '40 GOTO 20\n'
            '50 PRINT\n'
            '60 END\n',
            handler, ticks=40)
        text = handler.text().replace(' ', '').replace('\n', '')
        check(text == '484921',
              f"HI! dumps as 48 49 21 (got {handler.text()!r})")
    finally:
        os.unlink(path)


def test_a_terminal_never_gets_an_attempt():
    """The mechanism must stay off for handlers that block."""
    print("\nno attempt is created for a handler that does not defer")
    print("-" * 60)

    class BlockingHandler(DeferringHandler):
        defers_key_reads = False

        def input_chars(self, count, interrupted=None):
            return ''.join(self.queue[:count] or ['Z'] * count)

    handler = BlockingHandler('Z')
    ast = Parser(Lexer('10 X$=INPUT$(1)\n20 PRINT "GOT";X$\n').tokenize()).parse()
    runtime = Runtime({line.line_number: line for line in ast.lines})
    interpreter = Interpreter(runtime, handler)
    interpreter.start()
    interpreter.tick(mode='run', max_statements=100)

    check(runtime.statement_attempt is None,
          "the runtime was never given a statement attempt")
    check('GOT' in handler.text(), f"and the program ran ({handler.text()!r})")


if __name__ == "__main__":
    print("Undo for a retried statement")
    print("=" * 60)

    test_the_generator_is_snapshotted_once()
    test_rollback_restores_the_whole_generator_state()
    test_file_positions_are_restored()
    test_reset_forgets_the_previous_attempt()

    test_rnd_is_not_advanced_by_a_pause()
    test_a_file_read_is_not_repeated_by_a_pause()
    test_input_dollar_from_a_file_is_a_string()
    test_the_help_pages_own_example_runs()
    test_a_terminal_never_gets_an_attempt()

    failed = results.count(False)
    print("\n" + "=" * 60)
    print(f"Results: {results.count(True)} passed, {failed} failed")

    if failed:
        print("❌ Some tests failed")
        sys.exit(1)
    print("✅ All tests passed!")
    sys.exit(0)
