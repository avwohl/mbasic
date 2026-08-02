#!/usr/bin/env python3
"""
End-to-end test of the curses UI over a real pty.

Verifies that a program typed into the editor actually runs and that its output
reaches the output pane - the full path through urwid that in-process tests
cannot exercise.

Two traps this test is written to avoid:
  - It used to spawn `python3 mbasic.py`, which has never existed, and to import
    HELP_CHAR / QUIT_CHAR, which have never existed either. Both functions then
    returned True unconditionally and __main__ never called sys.exit(1), so the
    file could only ever report success.
  - The pty echoes typed keystrokes, so expecting a literal that appears in the
    typed program text matches the echo rather than the program's output. The
    program below builds its output with CHR$ so the expected text cannot
    appear in the keystrokes.
"""

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

# Exit code 2 tells tests/run_regression.py the test could not run. Exiting 0
# instead would score a green tick on completely untested code.
SKIP = 2

try:
    import pexpect
except ImportError:
    print("SKIP: pexpect not installed (pip install pexpect)")
    sys.exit(SKIP)

try:
    import urwid  # noqa: F401  - the curses UI cannot start without it
except ImportError:
    print("SKIP: urwid not installed (pip install \"mbasic[curses]\")")
    sys.exit(SKIP)

from src.ui.keybindings import RUN_KEY, QUIT_ALT_KEY, key_to_char

# key_to_char is documented as the single source of truth for key character
# codes; deriving the bytes here instead would silently go out of sync, and a
# hand-rolled ctrl-only table would raise KeyError if a non-ctrl key were bound.
RUN_BYTE = key_to_char(RUN_KEY)
QUIT_BYTE = key_to_char(QUIT_ALT_KEY)

# 'JKL' via CHR$ so the expected output never appears in the typed keystrokes.
PROGRAM = '10 PRINT CHR$(74)+CHR$(75)+CHR$(76)'
EXPECTED = 'JKL'


def spawn_ui():
    """Start the curses UI on a pty, using the interpreter running this test."""
    return pexpect.spawn(
        f'{sys.executable} mbasic --ui curses',
        encoding='utf-8',
        timeout=10,
        dimensions=(24, 80),
        cwd=str(PROJECT_ROOT),
    )


def disable_ixon(child):
    """Stop the pty eating ^Q as an XON flow-control character."""
    import termios
    attrs = termios.tcgetattr(child.child_fd)
    attrs[0] &= ~termios.IXON
    termios.tcsetattr(child.child_fd, termios.TCSANOW, attrs)


def quit_ui(child):
    """Exit via QUIT_ALT_KEY, falling back to ^C (SIGINT), then SIGKILL."""
    if child.isalive():
        disable_ixon(child)
        child.send(QUIT_BYTE)
        time.sleep(1.5)
    if child.isalive():
        child.send('\x03')
        time.sleep(1.5)
    if child.isalive():
        child.terminate(force=True)
        return False
    return True


def test_program_runs():
    """Type a program, run it with RUN_KEY, and confirm its output appears."""
    print("=== Program execution in the curses UI ===")
    child = spawn_ui()
    try:
        time.sleep(1.5)

        # Without this, a UI that failed to start would let everything below
        # "succeed" for the wrong reason.
        if not child.isalive():
            print(f"✗ UI did not start\n{child.before or ''}")
            return False
        print("✓ UI started")

        child.send(f'{PROGRAM}\r')
        time.sleep(0.4)
        child.send('20 END\r')
        time.sleep(0.4)

        child.send(RUN_BYTE)
        try:
            child.expect(EXPECTED, timeout=5)
            print(f"✓ program output {EXPECTED!r} appeared")
        except (pexpect.TIMEOUT, pexpect.EOF) as e:
            print(f"✗ program output {EXPECTED!r} never appeared ({type(e).__name__})")
            return False

        return True

    except Exception as e:
        print(f"✗ {type(e).__name__}: {e}")
        return False
    finally:
        quit_ui(child)


def test_quit_key():
    """Confirm QUIT_ALT_KEY alone terminates the UI."""
    print("\n=== Quit via QUIT_ALT_KEY ===")
    child = spawn_ui()
    try:
        time.sleep(1.5)
        if not child.isalive():
            print(f"✗ UI did not start\n{child.before or ''}")
            return False
        print("✓ UI started")

        disable_ixon(child)
        child.send(QUIT_BYTE)
        time.sleep(1.5)

        if child.isalive():
            print("✗ UI still running after QUIT_ALT_KEY")
            child.terminate(force=True)
            return False
        print("✓ UI exited")
        return True

    except Exception as e:
        print(f"✗ {type(e).__name__}: {e}")
        if child.isalive():
            child.terminate(force=True)
        return False


if __name__ == '__main__':
    print(f"Curses UI pexpect tests (RUN_KEY={RUN_KEY!r}, QUIT_ALT_KEY={QUIT_ALT_KEY!r})")
    print("=" * 60)

    ran = test_program_runs()
    quit_ok = test_quit_key()

    print("\n" + "=" * 60)
    print(f"  Program execution: {'PASS' if ran else 'FAIL'}")
    print(f"  Quit key:          {'PASS' if quit_ok else 'FAIL'}")
    print("=" * 60)

    sys.exit(0 if (ran and quit_ok) else 1)
