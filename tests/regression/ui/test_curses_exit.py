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

It waits for the UI to paint rather than sleeping at it, because a key sent
before urwid has started its screen is discarded and never arrives - see
wait_until_painted().
"""

import sys
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

from src.ui.keybindings import STATUS_BAR_SHORTCUTS

# The head of the status bar - row 24, and the last text the UI's first full
# paint writes. Taken from the UI's own constant so that renaming it cannot
# leave this waiting for something that is never coming.
PAINTED = STATUS_BAR_SHORTCUTS.split(' - ')[0]


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


def wait_until_painted(child, timeout=30):
    """Wait for the UI to be up, rather than for a clock.

    urwid starts its screen with tty.setcbreak(), whose termios default is
    TCSAFLUSH - which *discards* input that arrived first, so a key sent before
    that point is thrown away and the UI never sees it. This used to sleep 1.5s
    and hope; startup measures 0.6-1.2s here, which is not the margin it looks
    like on a loaded box. Once PAINTED arrives the flush is behind us.
    """
    try:
        child.expect(PAINTED, timeout=timeout)
        return True
    except Exception:       # TIMEOUT, EOF - both mean "never came up"
        return False


def wait_for_exit(child, timeout=15):
    """Wait for the child to actually go, rather than for a clock."""
    try:
        child.expect(pexpect.EOF, timeout=timeout)
        child.wait()        # reap it, so isalive() below is the truth
    except Exception:       # TIMEOUT - check_exit reports it; already reaped
        pass


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
        # The assertion that makes this test non-vacuous: if the UI failed to
        # start, everything below would "pass" for the wrong reason. Waiting
        # for the paint is the stronger form of it - a live process is not yet
        # a UI that can receive a keystroke.
        if not wait_until_painted(child):
            alive = "still running" if child.isalive() else "already dead"
            print(f"✗ {label}: UI did not come up ({alive})\n{child.before or ''}")
            if child.isalive():
                child.terminate(force=True)
            return False
        print("✓ UI started")

        if clear_ixon:
            disable_ixon(child)

        child.send(send)
        wait_for_exit(child)
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
