#!/usr/bin/env python3
"""
Test that INKEY$ can actually read a keystroke on POSIX.

Two bugs made the POSIX path unable to deliver a key that select() had just
reported as waiting:

1. `tty.setraw(fd)` defaults to TCSAFLUSH, which DISCARDS input that has
   arrived but not yet been read - precisely the keystroke select() detected.
2. `sys.stdin.read(1)` goes through a TextIOWrapper, which pulls every
   available byte into its own decode buffer. The kernel queue then looks
   empty, so the next select() reports "no key" while the rest of an escape
   sequence sits invisible in userspace.

Together they did not merely lose the key - they HUNG the interpreter: the
flush threw the bytes away and the buffered read then blocked forever waiting
for a character that no longer existed. Pressing an arrow key at an INKEY$ loop
froze mbasic.

Fixed with TCSANOW and os.read(). An arrow key now arrives as the three
characters the terminal actually sent - ESC, '[', 'A' - one per call, which is
all INKEY$ can return: MBASIC 5.21 hardcodes the result to a single character.

Needs a pty, so it is skipped where one cannot be allocated.
"""

import ast
import os
import pty
import select
import sys
import time

# Add project root to path (3 levels up from tests/regression/*/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))

# Runs in the pty child: put the terminal in the state a program polling
# INKEY$ would want (no echo, no line buffering), then poll.
CHILD = '''
import sys, termios, time
sys.path.insert(0, {root!r})
from src.basic_builtins import BuiltinFunctions

fd = sys.stdin.fileno()
attrs = termios.tcgetattr(fd)
attrs[3] &= ~(termios.ECHO | termios.ICANON)
termios.tcsetattr(fd, termios.TCSANOW, attrs)

builtins = BuiltinFunctions.__new__(BuiltinFunctions)
time.sleep({delay})
got = [BuiltinFunctions.INKEY(builtins) for _ in range({calls})]
print("RESULT:" + repr(got), flush=True)
'''

results = []


def check(condition, label):
    """Record one check; print pass/fail immediately."""
    results.append(bool(condition))
    print(f"{'PASS' if condition else 'FAIL'}: {label}")


def read_inkey(keystrokes, calls=6, delay=0.5, timeout=5):
    """Send bytes to a pty and return what successive INKEY$ calls saw.

    Returns None if the child produced nothing - which is itself the symptom
    of the bug being tested, since the old code blocked indefinitely.
    """
    source = CHILD.format(root=PROJECT_ROOT, delay=delay, calls=calls)
    pid, fd = pty.fork()
    if pid == 0:
        try:
            os.execv(sys.executable, [sys.executable, '-c', source])
        finally:
            os._exit(1)

    output = b''
    try:
        time.sleep(delay / 2)
        os.write(fd, keystrokes)
        deadline = time.time() + timeout
        while True:
            remaining = deadline - time.time()
            if remaining <= 0:
                break       # the child hung - the symptom of the original bug
            # select() first: os.read() on the pty master blocks indefinitely
            # when the child never writes, which would hang the whole run
            # rather than reporting a failure.
            if not select.select([fd], [], [], remaining)[0]:
                break
            try:
                chunk = os.read(fd, 1024)
            except OSError:
                break
            if not chunk:
                break
            output += chunk
            if b'RESULT:' in output:
                break
    finally:
        try:
            os.close(fd)
        except OSError:
            pass
        try:
            os.kill(pid, 9)
        except (ProcessLookupError, PermissionError):
            pass
        try:
            os.waitpid(pid, 0)
        except (ChildProcessError, OSError):
            pass

    for line in output.decode('latin-1').splitlines():
        if 'RESULT:' in line:
            marker = line[line.index('RESULT:') + len('RESULT:'):]
            try:
                return ast.literal_eval(marker)
            except (ValueError, SyntaxError):
                return None
    return None


def test_arrow_key():
    """An arrow key must arrive as the escape sequence the terminal sent."""
    print("\nINKEY$ delivers an arrow key")
    print("-" * 60)
    got = read_inkey(b'\x1b[A')
    check(got is not None,
          "INKEY$ returned at all (None means it hung - the original bug)")
    if got is None:
        return
    check(got[:3] == ['\x1b', '[', 'A'],
          f"Up arrow arrives as ESC, '[', 'A' (got {got[:3]!r})")
    check(all(len(ch) <= 1 for ch in got),
          "every INKEY$ result is at most one character, as MBASIC 5.21 requires")
    check(got[3:] == [''] * len(got[3:]),
          f"nothing extra is emitted afterwards (got {got[3:]!r})")


def test_ordinary_key():
    """The simple case must keep working."""
    print("\nINKEY$ delivers an ordinary keypress")
    print("-" * 60)
    got = read_inkey(b'Z', calls=3)
    check(got is not None, "INKEY$ returned at all")
    if got is None:
        return
    check(got[0] == 'Z', f"the character comes back unchanged (got {got[0]!r})")
    check(got[1:] == [''] * len(got[1:]), "and only once")


def test_no_key_pending():
    """With nothing typed, INKEY$ must return empty rather than block."""
    print("\nINKEY$ returns empty when no key is waiting")
    print("-" * 60)
    got = read_inkey(b'', calls=3, delay=0.3)
    check(got is not None, "INKEY$ returned promptly with no input available")
    if got is None:
        return
    check(got == ['', '', ''], f"all calls report no key (got {got!r})")


def test_high_byte_is_preserved():
    """Byte transparency: ASC() must mean the same on both platforms."""
    print("\nINKEY$ preserves a byte above 127")
    print("-" * 60)
    got = read_inkey(b'\x81', calls=3)
    check(got is not None, "INKEY$ returned at all")
    if got is None:
        return
    check(got[0] == '\x81',
          f"the high byte survives rather than being dropped (got {got[0]!r})")


if __name__ == "__main__":
    print("INKEY$ key reading on POSIX")
    print("=" * 60)

    try:
        pid, fd = pty.fork()
        if pid == 0:
            os._exit(0)
        os.close(fd)
        os.waitpid(pid, 0)
    except OSError as exc:
        print(f"SKIP: cannot allocate a pty here ({exc})")
        sys.exit(2)

    test_arrow_key()
    test_ordinary_key()
    test_no_key_pending()
    test_high_byte_is_preserved()

    failed = results.count(False)
    print("\n" + "=" * 60)
    print(f"Results: {results.count(True)} passed, {failed} failed")

    if failed:
        print("❌ Some tests failed")
        sys.exit(1)
    print("✅ All tests passed!")
    sys.exit(0)
