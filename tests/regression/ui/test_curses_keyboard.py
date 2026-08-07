#!/usr/bin/env python3
"""
Test that a program running in the curses UI has a keyboard of its own.

INKEY$ and INPUT$ read through the I/O handler (docs/dev/KEY_INPUT_ROUTING.md).
Before the curses backend put anything behind that seam, they fell back to
reading the process's terminal - the same file descriptor urwid was reading -
which meant:

- `INPUT$` worked only by stealing the next key out from under urwid, freezing
  the whole UI while it waited, and showing nothing: the program's prompt sits
  in an output buffer that the tick only drains after it returns.
- `INKEY$` could not see a key at all. Between ticks urwid is reading the
  terminal itself, so a key typed at a polling program was dispatched to the
  editor widget and typed into the program listing instead.

The first half of the file exercises UrwidKeyboard directly - it imports no
urwid, on purpose, so the queue and the interrupt mapping are testable
anywhere. The second half drives the real UI over a pty, which is the only way
to prove the wiring: the input_filter, the flush before waiting, and the stop
key reaching a program that is blocked while the event loop is not running.

Nothing in the pty half waits on a clock for something it can wait on
directly. It types nothing until the UI has painted (urwid throws typed-ahead
keys away - see UI.__init__), and it types no program line without seeing the
editor take it, so a program that fails to load says so instead of failing a
check three steps later for a reason nothing on screen names.
"""

import io
import os
import re
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.ui.urwid_keyboard import UrwidKeyboard

results = []


def check(condition, label):
    """Record one check; print pass/fail immediately."""
    results.append(bool(condition))
    print(f"{'PASS' if condition else 'FAIL'}: {label}")


# ---------------------------------------------------------------------------
# UrwidKeyboard on its own - no urwid, no terminal
# ---------------------------------------------------------------------------

class FakeScreen:
    """Enough of an urwid screen to answer get_input()."""

    started = True

    def __init__(self, batches=()):
        self.batches = list(batches)
        self.timeouts = []

    def set_input_timeouts(self, max_wait=None, **_kwargs):
        self.timeouts.append(max_wait)

    def get_input(self, raw_keys=False):
        raw = self.batches.pop(0) if self.batches else []
        keys = [chr(b) for b in raw]
        return (keys, raw) if raw_keys else keys


class FakeLoop:
    def __init__(self, screen):
        self.screen = screen


def keyboard_for(batches=(), stop_chars=(), on_wait=None):
    return UrwidKeyboard(get_loop=lambda: FakeLoop(FakeScreen(batches)),
                         on_wait=on_wait, stop_chars=stop_chars)


def test_queued_keys_are_delivered_in_order():
    """Keys the input_filter diverted are waiting when the program asks."""
    print("\nkeys diverted from urwid are queued for the program")
    print("-" * 60)
    keyboard = keyboard_for()
    keyboard.push_raw([ord('A'), ord('B'), ord('C')])

    check(keyboard.pending() == 3, f"three queued (got {keyboard.pending()})")
    check(keyboard.input_chars(2) == 'AB', "INPUT$(2) took the first two")
    check(keyboard.input_char(blocking=False) == 'C', "INKEY$ took the third")
    check(keyboard.input_char(blocking=False) == "",
          "and reports no key once the queue is empty")


def test_bytes_are_not_decoded():
    """One byte, one character - ASC() must mean what it does elsewhere."""
    print("\nraw bytes survive as characters")
    print("-" * 60)
    keyboard = keyboard_for()
    keyboard.push_raw([0x1b, ord('['), ord('A'), 0x81])

    got = keyboard.input_chars(4)
    check(got == '\x1b[A\x81',
          f"an arrow key arrives as the bytes the terminal sent (got {got!r})")


def test_divert_keys_returns_nothing_to_the_ui():
    """The filter's return value is what urwid still processes."""
    print("\ndivert_keys hands the UI nothing back")
    print("-" * 60)
    keyboard = keyboard_for()
    left = keyboard.divert_keys(['a'], [ord('a')])
    check(left == [], f"urwid gets an empty key list (got {left!r})")
    check(keyboard.pending() == 1, "and the byte went to the program")


def test_stop_key_arrives_as_ctrl_c():
    """The UI's stop key has to be able to end a blocked INPUT$.

    While INPUT$ blocks, the event loop is not running and the UI cannot act on
    its own stop key - this keyboard is the only thing reading. Delivering it
    as CHR$(3) reuses the break INPUT$ already understands.
    """
    print("\nthe UI stop key reaches the program as Ctrl+C")
    print("-" * 60)
    keyboard = keyboard_for(stop_chars={'\x18'})
    keyboard.push_raw([ord('A'), 0x18, ord('B')])

    got = keyboard.input_chars(3)
    check(got == 'A\x03',
          f"the read ends at the stop key, delivered as CHR$(3) (got {got!r})")
    check(keyboard.pending() == 1,
          "and what was typed after it stays queued for the next reader")


def test_interrupt_char_ends_a_read():
    """A real Ctrl+C ends the read too, and keeps what follows."""
    print("\nCtrl+C ends the read")
    print("-" * 60)
    keyboard = keyboard_for()
    keyboard.push_raw([ord('A'), 0x03, ord('B')])
    got = keyboard.input_chars(3)
    check(got == 'A\x03', f"stopped at the Ctrl+C (got {got!r})")
    check(keyboard.pending() == 1, "the 'B' typed after it survived")


def test_clear_drops_queued_keys():
    """Keys typed at one program are not input for the next."""
    print("\nclear() empties the queue between programs")
    print("-" * 60)
    keyboard = keyboard_for()
    keyboard.push_raw([ord('X'), ord('Y')])
    keyboard.clear()
    check(keyboard.pending() == 0, "nothing left queued")
    check(keyboard.input_char(blocking=False) == "", "and INKEY$ says no key")


def test_interrupted_callback_ends_the_wait():
    """A SIGINT while blocked must not wait for a keypress that never comes."""
    print("\nthe interrupted callback ends a blocking read")
    print("-" * 60)
    keyboard = keyboard_for()          # empty screen: nothing will ever arrive
    calls = []

    def interrupted():
        calls.append(1)
        return len(calls) > 1

    got = keyboard.input_chars(3, interrupted=interrupted)
    check(got == "", f"the read gave up (got {got!r})")
    check(len(calls) >= 1, "and the callback was actually consulted")


def test_no_screen_does_not_hang():
    """With no loop yet there is nothing to wait for."""
    print("\na read with no screen returns instead of blocking")
    print("-" * 60)
    keyboard = UrwidKeyboard(get_loop=lambda: None)
    start = time.time()
    got = keyboard.input_chars(2)
    check(got == "", f"empty (got {got!r})")
    check(time.time() - start < 2, "and promptly")


def test_on_wait_runs_once_before_waiting():
    """The program's prompt has to be flushed before the user is asked."""
    print("\non_wait fires before the read settles in to wait")
    print("-" * 60)
    flushes = []
    keyboard = keyboard_for(batches=[[ord('K')]],
                            on_wait=lambda: flushes.append(1))
    got = keyboard.input_chars(1)
    check(got == 'K', f"the key came back (got {got!r})")
    check(len(flushes) == 1, f"flushed exactly once (got {len(flushes)})")

    # Nothing to wait for: the key is already queued, so no flush is needed.
    flushes.clear()
    keyboard = keyboard_for(on_wait=lambda: flushes.append(1))
    keyboard.push_raw([ord('Q')])
    keyboard.input_chars(1)
    check(not flushes, "and not at all when a key is already waiting")


# ---------------------------------------------------------------------------
# The real UI, over a pty
# ---------------------------------------------------------------------------

RUN_BYTE = STOP_BYTE = PAINTED = None
pexpect = None


def strip_ansi(text):
    return re.sub(r'\x1b\[[0-9;?]*[a-zA-Z]|\x1b\][^\x07]*\x07|\x1b[()][A-B0]',
                  '', text)


class UI:
    """The curses UI on a pty, driven a keystroke at a time."""

    def __init__(self, program=()):
        self.log = io.StringIO()
        self.child = pexpect.spawn(
            f'{sys.executable} mbasic --ui curses',
            encoding='latin-1', timeout=10, dimensions=(24, 80),
            cwd=str(PROJECT_ROOT))
        self.child.logfile_read = self.log

        # Wait for the UI to be up, not for a clock. urwid starts its screen
        # with tty.setcbreak(), whose termios default is TCSAFLUSH - which
        # *discards* input that arrived first. Anything typed before that point
        # is echoed by the still-cooked tty and then thrown away, and the
        # program that runs is missing whichever lines lost the race: without
        # line 10 it is "NEXT without FOR", without 10 through 40 what is left
        # runs straight to its END and prints NONE. Startup here measures
        # 0.6-1.2s against the 1.2s this used to sleep, so it lost that race
        # about once in twelve - as an INKEY$ failure, never as a lost line.
        # PAINTED is the last text of the first full paint, so by the time it
        # arrives the flush is behind us.
        trouble = "" if self.saw(PAINTED, timeout=30) else "it never painted"

        lost = []
        if not trouble:
            for line in program:
                self.child.send(line + '\r')
                # The editor echoes the line it took, which is the only proof
                # that it took it. Matching the whole line means program lines
                # have to fit the editor pane - about 76 columns - because a
                # wrapped one is not contiguous in the stream.
                if not self.saw_exact(line, timeout=10):
                    lost.append(line)
            if lost:
                trouble = f"the editor never showed {lost}"

        check(not trouble, "the UI came up with the program loaded"
                           + (f" - {trouble}" if trouble else ""))

    def run(self):
        self.child.send(RUN_BYTE)
        time.sleep(0.5)

    def send(self, data, pause=0.4):
        self.child.send(data)
        time.sleep(pause)

    def saw(self, pattern, timeout=5):
        try:
            self.child.expect(pattern, timeout=timeout)
            return True
        except Exception:       # TIMEOUT, EOF - both mean "never appeared"
            return False

    def saw_exact(self, text, timeout=5):
        """saw() for text that is not a pattern - program lines are full of
        $, (, ) and " and mean them literally."""
        try:
            self.child.expect_exact(text, timeout=timeout)
            return True
        except Exception:
            return False

    def screen(self):
        return strip_ansi(self.log.getvalue())

    def alive(self):
        return self.child.isalive()

    def close(self):
        try:
            self.child.terminate(force=True)
        except Exception:
            pass

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        self.close()
        return False


# Output built with CHR$ so the expected text cannot match the echo of the
# typed program. MBASIC's PRINT puts a space before a number, and the pane may
# render it either way, hence 'GOT ?81'.
ASK_AND_READ = ['10 PRINT CHR$(80)+CHR$(82)+CHR$(69)+CHR$(83)+CHR$(83);',
                '20 A$=INPUT$(1)',
                '30 PRINT CHR$(71)+CHR$(79)+CHR$(84);ASC(A$)']


def test_input_dollar_in_the_ui():
    """INPUT$ shows its prompt, waits, and gets the key that is typed."""
    print("\nINPUT$ in the curses UI")
    print("-" * 60)
    with UI(ASK_AND_READ) as ui:
        ui.run()
        # The prompt is printed by line 10 and would still be sitting in the
        # output buffer if the keyboard did not flush before waiting.
        check(ui.saw('PRESS', timeout=5),
              "the prompt appears before the key is typed")
        ui.send('Q')
        check(ui.saw('GOT ?81', timeout=5),
              "the typed key reached the program")


def test_inkey_sees_a_key_typed_mid_run():
    """A key typed at a polling program must not go to the editor instead."""
    print("\nINKEY$ during a run")
    print("-" * 60)
    # Line 5 is the program saying it has started, so the key is typed at a
    # program that is demonstrably polling rather than after a guessed pause.
    # The loop itself is 30000 iterations, about 26 seconds of ticks, so it
    # cannot run out from under the check - NONE means the program was wrong,
    # not that the test was slow.
    with UI(['5 PRINT CHR$(80)+CHR$(79)+CHR$(76)+CHR$(76)',
             '10 FOR I=1 TO 30000',
             '20 A$=INKEY$',
             '30 IF A$<>"" THEN 60',
             '40 NEXT I',
             '50 PRINT CHR$(78)+CHR$(79)+CHR$(78)+CHR$(69):END',
             '60 PRINT CHR$(71)+CHR$(79)+CHR$(84);ASC(A$)']) as ui:
        ui.run()
        check(ui.saw('POLL', timeout=10), "the program is running and polling")
        ui.send('Z')
        check(ui.saw('GOT ?90', timeout=10),
              "INKEY$ returned the key typed while the program was running")


def test_stop_key_breaks_a_blocked_input_dollar():
    """The UI must be recoverable from a program waiting on a key."""
    print("\nthe stop key ends a blocked INPUT$")
    print("-" * 60)
    with UI(ASK_AND_READ) as ui:
        ui.run()
        ui.saw('PRESS', timeout=5)
        ui.send(STOP_BYTE)
        check(ui.saw('Break', timeout=5), "the read broke")
        check(ui.alive(), "the UI survived")
        ui.run()
        check(ui.saw('PRESS', timeout=5), "and can run the program again")


def test_the_input_statement_dialog_still_gets_its_answer():
    """The filter must not swallow the keys a dialog is waiting for.

    The INPUT statement suspends the tick and opens an overlay; if a running
    program were given every key unconditionally, the dialog would never
    receive an answer and the program would hang forever.
    """
    print("\nthe INPUT statement's dialog still receives typing")
    print("-" * 60)
    with UI(['10 INPUT "NAME";N$',
             '20 PRINT CHR$(72)+CHR$(73);N$']) as ui:
        ui.run()
        check(ui.saw('Input Required', timeout=5), "the dialog opened")
        ui.send('BOB\r')
        check(ui.saw('HI ?BOB', timeout=5), "and its answer reached the program")


if __name__ == "__main__":
    print("The curses UI's keyboard")
    print("=" * 60)

    test_queued_keys_are_delivered_in_order()
    test_bytes_are_not_decoded()
    test_divert_keys_returns_nothing_to_the_ui()
    test_stop_key_arrives_as_ctrl_c()
    test_interrupt_char_ends_a_read()
    test_clear_drops_queued_keys()
    test_interrupted_callback_ends_the_wait()
    test_no_screen_does_not_hang()
    test_on_wait_runs_once_before_waiting()

    # The pty half needs the UI's own dependencies. Missing ones skip that
    # half loudly rather than failing, and the checks above still stand.
    missing = None
    try:
        import pexpect            # noqa: F811
    except ImportError:
        missing = "pexpect not installed (pip install pexpect)"
    if missing is None:
        try:
            import urwid          # noqa: F401
        except ImportError:
            missing = 'urwid not installed (pip install "mbasic[curses]")'

    if missing:
        print(f"\nSKIPPING the pty half: {missing}")
    else:
        from src.ui.keybindings import (RUN_KEY, STOP_KEY,
                                        STATUS_BAR_SHORTCUTS, key_to_char)
        RUN_BYTE = key_to_char(RUN_KEY)
        STOP_BYTE = key_to_char(STOP_KEY)
        # The head of the status bar - row 24, and the last text the first full
        # paint writes. Taken from the UI's own constant so that renaming it
        # cannot leave this waiting for something that is never coming.
        PAINTED = STATUS_BAR_SHORTCUTS.split(' - ')[0]

        test_input_dollar_in_the_ui()
        test_inkey_sees_a_key_typed_mid_run()
        test_stop_key_breaks_a_blocked_input_dollar()
        test_the_input_statement_dialog_still_gets_its_answer()

    failed = results.count(False)
    print("\n" + "=" * 60)
    print(f"Results: {results.count(True)} passed, {failed} failed")

    if failed:
        print("❌ Some tests failed")
        sys.exit(1)
    print("✅ All tests passed!")
    sys.exit(0)
