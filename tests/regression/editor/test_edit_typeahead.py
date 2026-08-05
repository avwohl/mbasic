#!/usr/bin/env python3
"""
Test that EDIT mode does not discard type-ahead.

InteractiveMode._read_char() is called once per keystroke by the EDIT loop, and
it did:

    tty.setraw(fd)              # TCSAFLUSH by default
    ch = sys.stdin.read(1)

TCSAFLUSH discards input that has arrived but has not been read, so everything
typed between two calls was thrown away. And because the read then waited for a
character that had just been discarded, typing ahead and stopping left EDIT
hanging rather than merely losing keys.

Measured before the fix: type "ABCDE" in one burst, then read five characters -
the reader never returned at all. After (TCSANOW + os.read): all five arrive.

This is the third and last of the raw-mode readers to be fixed this way.
INKEY$ is covered by tests/regression/interpreter/test_inkey_posix.py; the
non-tty paths of this same reader are covered by
tests/regression/ui/test_cli_input_isolation.py, which is why the piped case is
not repeated here. ConsoleIOHandler.input_char's POSIX hunk has only its
Windows routing tested (tests/regression/ui/test_win_console.py) - nothing
calls it, so it has no pty test.

Needs a pty, so it exits 2 (SKIP) where one cannot be allocated.
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

# Runs in the pty child. Clears ICANON/ECHO the way a full-screen reader would,
# then calls _read_char repeatedly with a pause between calls - that pause is
# the window in which a flush eats whatever was typed.
CHILD = '''
import sys, termios, time
sys.path.insert(0, {root!r})
from src.interactive import InteractiveMode

fd = sys.stdin.fileno()
attrs = termios.tcgetattr(fd)
attrs[3] &= ~(termios.ECHO | termios.ICANON)
termios.tcsetattr(fd, termios.TCSANOW, attrs)

time.sleep({delay})
got = []
for _ in range({calls}):
    got.append(InteractiveMode._read_char(None))
    time.sleep(0.05)
print("RESULT:" + repr(got), flush=True)
'''

results = []


def check(condition, label):
    """Record one check; print pass/fail immediately."""
    results.append(bool(condition))
    print(f"{'PASS' if condition else 'FAIL'}: {label}")


def read_chars(keystrokes, calls, delay=0.5, timeout=3):
    """Type keystrokes into a pty in one burst; return what _read_char saw.

    None means the child never answered - which is the symptom being tested,
    since the unfixed reader blocks forever on discarded input.
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
                break
            # select() first: os.read() on the master blocks indefinitely when
            # the child hangs, which would stall the run instead of failing.
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
        for cleanup in (lambda: os.close(fd),
                        lambda: os.kill(pid, 9),
                        lambda: os.waitpid(pid, 0)):
            try:
                cleanup()
            except (OSError, ChildProcessError, ProcessLookupError):
                pass

    for line in output.decode('latin-1').splitlines():
        if 'RESULT:' in line:
            marker = line[line.index('RESULT:') + len('RESULT:'):]
            try:
                return ast.literal_eval(marker)
            except (ValueError, SyntaxError):
                return None
    return None


def test_typeahead_survives():
    """Five characters typed in one burst must all be delivered."""
    print("\nEDIT mode keeps everything typed ahead")
    print("-" * 60)
    got = read_chars(b'ABCDE', calls=5)
    check(got is not None,
          "the reader returned at all (None means it hung - the original bug)")
    if got is None:
        return
    check(got == ['A', 'B', 'C', 'D', 'E'],
          f"all five characters arrive in order (got {got!r})")


def test_control_character_is_byte_transparent():
    """EDIT mode is driven by control characters - ^A must stay 0x01."""
    print("\nControl characters survive unchanged")
    print("-" * 60)
    got = read_chars(b'\x01\x1b', calls=2)
    check(got is not None, "the reader returned at all")
    if got is None:
        return
    check(got == ['\x01', '\x1b'],
          f"^A and ESC come through as themselves (got {got!r})")


def test_high_byte_is_preserved():
    """A byte above 127 must not be mangled or dropped."""
    print("\nBytes above 127 survive")
    print("-" * 60)
    got = read_chars(b'\x81\x82', calls=2)
    check(got is not None, "the reader returned at all")
    if got is None:
        return
    check(got == ['\x81', '\x82'], f"both high bytes survive (got {got!r})")


def test_edit_loop_survives_crlf_line_endings():
    """Drive the real EDIT loop over a pty with CRLF, end to end.

    Removing the per-keystroke flush exposed a second-order problem: sending
    "\\r\\n" leaves a spare newline queued (ICRNL turns the CR into one too),
    and <CR> is EDIT's "save and exit" subcommand - so EDIT quit before the
    user's first keystroke and the rest leaked to the REPL as commands.
    cmd_edit now drops exactly one leftover terminator.

    Everything above tests the reader in isolation; this is the only case that
    runs the EDIT command loop itself.
    """
    print("\nEDIT driven with CRLF edits the line instead of quitting")
    print("-" * 60)
    pid, fd = pty.fork()
    if pid == 0:
        try:
            env_script = os.path.join(PROJECT_ROOT, 'mbasic')
            os.environ.pop('MBASIC_DEBUG', None)
            os.chdir(PROJECT_ROOT)
            os.execv(sys.executable, [sys.executable, env_script, '--ui', 'cli'])
        finally:
            os._exit(1)

    output = b''

    def pump(seconds):
        nonlocal output
        end = time.time() + seconds
        while time.time() < end:
            if not select.select([fd], [], [], max(0, end - time.time()))[0]:
                break
            try:
                chunk = os.read(fd, 4096)
            except OSError:
                break
            if not chunk:
                break
            output += chunk

    try:
        time.sleep(1.0)
        pump(0.8)
        # Every line CRLF-terminated, which is what a paste or an expect
        # script sends. "  D" skips two characters and deletes the third,
        # turning PRINT into PRNT - a visible, unambiguous edit.
        for keys, wait in ((b'10 PRINT "HI"\r\n', 0.5), (b'EDIT 10\r\n', 0.6),
                           (b'  D\r', 0.5), (b'LIST\r\n', 0.5),
                           (b'SYSTEM\r\n', 0.6)):
            os.write(fd, keys)
            time.sleep(wait)
            pump(0.5)
    finally:
        for cleanup in (lambda: os.close(fd),
                        lambda: os.kill(pid, 9),
                        lambda: os.waitpid(pid, 0)):
            try:
                cleanup()
            except (OSError, ChildProcessError, ProcessLookupError):
                pass

    text = output.decode('latin-1')
    check('10 PRNT "HI"' in text,
          "LIST shows the edited line, so EDIT consumed the keystrokes")
    check("'d'" not in text,
          "the D subcommand did not leak to the REPL as a command")


if __name__ == "__main__":
    print("EDIT mode type-ahead")
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

    test_typeahead_survives()
    test_control_character_is_byte_transparent()
    test_high_byte_is_preserved()
    test_edit_loop_survives_crlf_line_endings()

    failed = results.count(False)
    print("\n" + "=" * 60)
    print(f"Results: {results.count(True)} passed, {failed} failed")

    if failed:
        print("❌ Some tests failed")
        sys.exit(1)
    print("✅ All tests passed!")
    sys.exit(0)
