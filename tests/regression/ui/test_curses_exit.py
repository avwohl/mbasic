#!/usr/bin/env python3
"""
Test that the curses UI exits cleanly, without error output.

Covers both documented ways out:
  - ^C, which arrives as SIGINT and is handled by the signal handler
  - QUIT_ALT_KEY (^Q by default, from src/ui/curses_keybindings.json)

This test previously spawned `python3 mbasic.py`, which has never existed. The
child died instantly, so `isalive()` was False and the test reported "exited
cleanly" - it would have passed against any nonexistent command. The assertion
that the UI is genuinely running *before* the exit key is sent is what keeps
this test honest.
"""

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

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
    """Stop the pty eating ^Q as an XON flow-control character.

    Without this the byte never reaches the application and a ^Q test would
    fail for a reason that has nothing to do with the keybinding.
    """
    import termios
    attrs = termios.tcgetattr(child.child_fd)
    attrs[0] &= ~termios.IXON
    termios.tcsetattr(child.child_fd, termios.TCSANOW, attrs)


def check_exit(child, label):
    """Verify the process ended and printed no error output."""
    if child.isalive():
        print(f"✗ {label}: process did not exit")
        child.terminate(force=True)
        return False
    print(f"✓ {label}: process exited")

    output = child.before or ""
    for marker in ('traceback', 'exception', 'error'):
        if marker in output.lower():
            print(f"✗ {label}: {marker} in output:\n{output[-500:]}")
            return False
    print(f"✓ {label}: no error output")
    return True


def run_exit_test(label, send, clear_ixon=False):
    """Start the UI, confirm it is really running, then exit it."""
    print(f"\n=== {label} ===")
    child = spawn_ui()
    try:
        time.sleep(1.5)

        # The assertion that makes this test non-vacuous: if the UI failed to
        # start, everything below would "pass" for the wrong reason.
        if not child.isalive():
            print(f"✗ {label}: UI did not start\n{child.before or ''}")
            return False
        print("✓ UI started")

        if clear_ixon:
            disable_ixon(child)

        child.send(send)
        time.sleep(1.5)
        return check_exit(child, label)

    except Exception as e:
        print(f"✗ {label}: {type(e).__name__}: {e}")
        if child.isalive():
            child.terminate(force=True)
        return False


if __name__ == '__main__':
    print("Testing Curses UI Exit Behavior")
    print("=" * 60)

    ctrl_c = run_exit_test("^C exit", '\x03')
    ctrl_q = run_exit_test("^Q exit (QUIT_ALT_KEY)", '\x11', clear_ixon=True)

    print("\n" + "=" * 60)
    print(f"  ^C exit: {'PASS' if ctrl_c else 'FAIL'}")
    print(f"  ^Q exit: {'PASS' if ctrl_q else 'FAIL'}")
    print("=" * 60)

    sys.exit(0 if (ctrl_c and ctrl_q) else 1)
