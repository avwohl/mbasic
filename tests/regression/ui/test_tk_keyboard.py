#!/usr/bin/env python3
"""
Test that a program running in the Tk UI has a keyboard of its own.

INKEY$ and INPUT$ read through the I/O handler (docs/dev/KEY_INPUT_ROUTING.md).
What the Tk backend had behind that seam was a modal dialog asking the user to
type a character and press OK - one per character - and nothing at all for
INKEY$, which returned "" forever. Measured against the previous commit:

    INPUT$(1)            a modal "Enter a single character:" dialog
    INPUT$(3)            three of them
    INKEY$               "" every time; a polling program never saw a key

The first half of the file drives TkKeyboard directly. It imports no tkinter,
on purpose, so the queue, the special-key translation and the interrupt
handling are testable with no display at all.

The second half builds the real UI and injects key events into it, which is
the only way to prove the wiring: the bindings that take a key before the
editor inserts it, the event-loop pump that keeps Tk alive while INPUT$ blocks
inside an after() callback, and Run > Stop ending a blocked read. It needs a
display, and says so and skips if there is none.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
# The Tk UI imports several modules flat (resource_limits, editing), which
# works because mbasic puts src/ on the path. A test that skips mbasic_main
# has to do the same.
sys.path.insert(0, str(PROJECT_ROOT / 'src'))

from src.ui.tk_keyboard import TkKeyboard, KEYSYM_TO_ANSI, INTERRUPT_CHAR

results = []


def check(condition, label):
    """Record one check; print pass/fail immediately."""
    results.append(bool(condition))
    print(f"{'PASS' if condition else 'FAIL'}: {label}")


class FakeEvent:
    def __init__(self, char='', keysym=''):
        self.char = char
        self.keysym = keysym


class FakeRoot:
    """A root that counts pumps and can deliver keys while one is waiting."""

    def __init__(self, keyboard=None, deliver_after=None):
        self.updates = 0
        self.keyboard = keyboard
        self.deliver_after = deliver_after

    def update(self):
        self.updates += 1
        if (self.deliver_after is not None
                and self.updates >= self.deliver_after
                and self.keyboard is not None):
            self.keyboard.push('K')


def test_key_events_become_characters():
    """A <Key> event with a character queues that character."""
    print("\nordinary keys are queued as themselves")
    print("-" * 60)
    keyboard = TkKeyboard(get_root=lambda: None)
    check(keyboard.push_from_event(FakeEvent(char='A', keysym='A')),
          "the event was taken")
    keyboard.push_from_event(FakeEvent(char='b', keysym='b'))
    keyboard.push_from_event(FakeEvent(char='\r', keysym='Return'))

    got = keyboard.input_chars(3)
    check(got == 'Ab\r', f"in order, Enter as CHR$(13) (got {got!r})")


def test_special_keys_arrive_as_escape_sequences():
    """MBASIC has no named keys - an arrow is what a terminal would send."""
    print("\nspecial keys are translated to terminal sequences")
    print("-" * 60)
    keyboard = TkKeyboard(get_root=lambda: None)
    keyboard.push_from_event(FakeEvent(char='', keysym='Up'))
    got = keyboard.input_chars(3)
    check(got == '\x1b[A', f"Up arrives as ESC [ A (got {got!r})")

    keyboard = TkKeyboard(get_root=lambda: None)
    keyboard.push_from_event(FakeEvent(char='', keysym='F1'))
    check(keyboard.input_chars(3) == '\x1bOP', "F1 arrives as ESC O P")


def test_the_two_special_key_tables_agree():
    """This table and the Windows one must not drift apart.

    Both answer the same question - what does a terminal send for a key MBASIC
    has no name for - so a program that reads INKEY$ gets the same bytes
    whichever backend it runs under.
    """
    print("\nthe Tk and Windows special-key tables agree")
    print("-" * 60)
    from src.win_console import _WIN_KEY_TO_ANSI

    tk_sequences = set(KEYSYM_TO_ANSI.values())
    win_sequences = set(_WIN_KEY_TO_ANSI.values())
    check(tk_sequences == win_sequences,
          f"same sequences on both platforms "
          f"(only in Tk: {sorted(tk_sequences - win_sequences)}, "
          f"only in Windows: {sorted(win_sequences - tk_sequences)})")


def test_modifiers_are_not_keys():
    """Shift on its own is not a keypress a program should see."""
    print("\nmodifier keys are ignored")
    print("-" * 60)
    keyboard = TkKeyboard(get_root=lambda: None)
    for keysym in ('Shift_L', 'Control_R', 'Alt_L', 'Caps_Lock'):
        check(not keyboard.push_from_event(FakeEvent(char='', keysym=keysym)),
              f"{keysym} was not queued")
    check(keyboard.pending() == 0, "nothing queued at all")


def test_unknown_special_keys_are_dropped():
    """A key with no character and no translation cannot be delivered."""
    print("\nan untranslatable key is dropped rather than guessed at")
    print("-" * 60)
    keyboard = TkKeyboard(get_root=lambda: None)
    check(not keyboard.push_from_event(FakeEvent(char='', keysym='Menu')),
          "not taken")
    check(keyboard.pending() == 0, "and nothing queued")


def test_stop_ends_a_blocking_read_as_ctrl_c():
    """Run > Stop is the only way out of a blocked INPUT$ in a GUI.

    It clears the backend's running flag; the read reports that as CHR$(3),
    which INPUT$ already treats as a break, so the program stops with
    "Break in nn" instead of hanging.
    """
    print("\nRun > Stop reaches a blocked read as Ctrl+C")
    print("-" * 60)
    running = [True]
    root = FakeRoot()
    keyboard = TkKeyboard(get_root=lambda: root,
                          still_running=lambda: running[0],
                          pump_seconds=0)

    # The user reaches Run > Stop while the read is pumping the event loop,
    # which is the only time they can: it is the pump that keeps the menu
    # alive at all.
    pump = root.update

    def stop_during_pump():
        pump()
        running[0] = False

    root.update = stop_during_pump

    got = keyboard.input_chars(3)
    check(got == INTERRUPT_CHAR,
          f"the read came back as Ctrl+C (got {got!r})")
    check(root.updates >= 1, "and it really did wait first")


def test_interrupted_callback_ends_the_wait():
    """A SIGINT-style interrupt must not wait for a key that never comes."""
    print("\nthe interrupted callback ends a blocking read")
    print("-" * 60)
    root = FakeRoot()
    keyboard = TkKeyboard(get_root=lambda: root, pump_seconds=0)
    calls = []

    def interrupted():
        calls.append(1)
        return len(calls) > 2

    got = keyboard.input_chars(3, interrupted=interrupted)
    check(got == "", f"gave up with nothing (got {got!r})")
    check(len(calls) >= 1, "and the callback was consulted")


def test_a_pumped_key_completes_the_read():
    """The read returns as soon as pumping the loop delivers a key."""
    print("\npumping the event loop is what delivers the key")
    print("-" * 60)
    root = FakeRoot(deliver_after=2)
    keyboard = TkKeyboard(get_root=lambda: root, pump_seconds=0)
    root.keyboard = keyboard

    got = keyboard.input_chars(1)
    check(got == 'K', f"the key arrived (got {got!r})")
    check(root.updates >= 2, f"after pumping the loop (got {root.updates})")


def test_no_root_does_not_hang():
    """Before the window exists there is nothing to wait for."""
    print("\na read with no window returns instead of blocking")
    print("-" * 60)
    keyboard = TkKeyboard(get_root=lambda: None)
    check(keyboard.input_chars(2) == "", "empty")
    check(keyboard.input_char(blocking=False) == "", "and INKEY$ says no key")


def test_on_wait_runs_once_and_only_when_waiting():
    """The program's prompt must be on screen before the user is asked."""
    print("\non_wait fires once, before the wait")
    print("-" * 60)
    flushes = []
    root = FakeRoot(deliver_after=1)
    keyboard = TkKeyboard(get_root=lambda: root,
                          on_wait=lambda: flushes.append(1), pump_seconds=0)
    root.keyboard = keyboard
    keyboard.input_chars(1)
    check(len(flushes) == 1, f"flushed once (got {len(flushes)})")

    flushes.clear()
    keyboard = TkKeyboard(get_root=lambda: root,
                          on_wait=lambda: flushes.append(1), pump_seconds=0)
    keyboard.push('Q')
    keyboard.input_chars(1)
    check(not flushes, "and not at all when a key is already queued")


def test_clear_drops_queued_keys():
    """Keys typed at one program are not input for the next."""
    print("\nclear() empties the queue between programs")
    print("-" * 60)
    keyboard = TkKeyboard(get_root=lambda: None)
    keyboard.push('XY')
    keyboard.clear()
    check(keyboard.pending() == 0, "nothing left queued")


# ---------------------------------------------------------------------------
# The real UI, with a display
# ---------------------------------------------------------------------------

def build_backend():
    from src.ui.tk_ui import TkBackend, TkIOHandler
    from src.editing import ProgramManager
    from src.parser import TypeInfo

    def_type_map = {c: TypeInfo.SINGLE for c in 'abcdefghijklmnopqrstuvwxyz'}
    return TkBackend(TkIOHandler(lambda text: None),
                     ProgramManager(def_type_map))


def drive(program, steps, settle_ms=3500):
    """Run the real UI, script it from the event loop, return what it showed.

    start() builds the window and then blocks in mainloop, so the script is
    hung off a one-shot patch of mainloop - there is no other point at which
    the widgets exist but the loop has not taken over.
    """
    import tkinter as tk

    backend = build_backend()
    captured = {}

    def script():
        root = backend.root
        backend.editor_text.text.delete('1.0', 'end')
        backend.editor_text.text.insert('1.0', '\n'.join(program) + '\n')
        for delay, action in steps:
            root.after(delay, lambda a=action: a(backend))

        def finish():
            try:
                captured['output'] = backend.output_text.get('1.0', 'end')
                captured['editor'] = backend.editor_text.text.get('1.0', 'end')
            except Exception as exc:
                captured['output'] = f'<{exc}>'
                captured['editor'] = ''
            root.quit()

        root.after(settle_ms, finish)

    real_mainloop = tk.Tk.mainloop

    def patched(self, *args, **kwargs):
        tk.Tk.mainloop = real_mainloop          # only hook the first call
        script()
        return real_mainloop(self, *args, **kwargs)

    tk.Tk.mainloop = patched
    try:
        backend.start()
    finally:
        tk.Tk.mainloop = real_mainloop
        try:
            backend.root.destroy()
        except Exception:
            pass
    return captured.get('output', ''), captured.get('editor', '')


def press(keysym):
    return lambda backend: backend.editor_text.text.event_generate(
        '<Key>', keysym=keysym)


#: Announce, read one key, report its code. Built with CHR$ so nothing
#: expected can match the program text itself.
ASK_AND_READ = ['10 PRINT CHR$(80)+CHR$(82)+CHR$(69)+CHR$(83)+CHR$(83);',
                '20 A$=INPUT$(1)',
                '30 PRINT CHR$(71)+CHR$(79)+CHR$(84);ASC(A$)']


def test_input_dollar_in_the_ui():
    """INPUT$ shows its prompt, waits, and receives the key that is typed."""
    print("\nINPUT$ in the Tk UI")
    print("-" * 60)
    out, _ = drive(ASK_AND_READ,
                   [(300, lambda b: b._menu_run()), (1200, press('Q'))],
                   settle_ms=3500)
    check('PRESS' in out, f"the prompt was displayed (got {out.strip()[:80]!r})")
    check('81' in out and 'GOT' in out,
          f"the typed key reached the program (got {out.strip()[:80]!r})")


def test_inkey_sees_a_key_typed_mid_run():
    """A key typed at a polling program must not go to the editor instead."""
    print("\nINKEY$ during a run")
    print("-" * 60)
    out, _ = drive(['10 FOR I=1 TO 200000',
                    '20 A$=INKEY$',
                    '30 IF A$<>"" THEN 60',
                    '40 NEXT I',
                    '50 PRINT CHR$(78)+CHR$(79)+CHR$(78)+CHR$(69):END',
                    '60 PRINT CHR$(71)+CHR$(79)+CHR$(84);ASC(A$)'],
                   [(300, lambda b: b._menu_run()), (1200, press('Z'))],
                   settle_ms=4000)
    check('90' in out and 'GOT' in out,
          f"INKEY$ returned the key typed while running (got {out.strip()[:80]!r})")


def test_stop_breaks_a_blocked_input_dollar():
    """The UI must be recoverable from a program waiting on a key."""
    print("\nRun > Stop ends a blocked INPUT$")
    print("-" * 60)
    out, _ = drive(ASK_AND_READ,
                   [(300, lambda b: b._menu_run()),
                    (1400, lambda b: b._menu_stop())],
                   settle_ms=3800)
    check('Break' in out or 'stopped' in out.lower(),
          f"the read was broken (got {out.strip()[:120]!r})")
    check('GOT' not in out, "and the program did not get a character")


def test_the_input_statement_still_gets_its_answer():
    """The key bindings must not swallow what the INPUT statement is owed."""
    print("\nthe INPUT statement still receives its answer")
    print("-" * 60)

    def answer(backend):
        backend.immediate_entry.focus_force()
        backend.immediate_entry.delete(0, 'end')
        backend.immediate_entry.insert(0, 'BOB')
        backend._execute_immediate()

    out, _ = drive(['10 INPUT "NAME";N$', '20 PRINT CHR$(72)+CHR$(73);N$'],
                   [(300, lambda b: b._menu_run()), (1400, answer)],
                   settle_ms=3800)
    check('BOB' in out and 'HI' in out,
          f"the answer reached the program (got {out.strip()[:120]!r})")


if __name__ == "__main__":
    print("The Tk UI's keyboard")
    print("=" * 60)

    test_key_events_become_characters()
    test_special_keys_arrive_as_escape_sequences()
    test_the_two_special_key_tables_agree()
    test_modifiers_are_not_keys()
    test_unknown_special_keys_are_dropped()
    test_stop_ends_a_blocking_read_as_ctrl_c()
    test_interrupted_callback_ends_the_wait()
    test_a_pumped_key_completes_the_read()
    test_no_root_does_not_hang()
    test_on_wait_runs_once_and_only_when_waiting()
    test_clear_drops_queued_keys()

    # The half that needs a window. No display is the normal case on a build
    # machine, so it skips loudly and the checks above still stand.
    missing = None
    try:
        import tkinter
        probe = tkinter.Tk()
        # withdraw() keeps the probe off the screen; update() is load-bearing.
        # On Tcl/Tk 9.0 + Aqua, a root destroyed before it has ever processed
        # an event leaves the toolkit in a state where the NEXT root aborts
        # the process (SIGTRAP) the moment it enters mainloop - so this probe
        # for a display was itself killing every windowed test below it.
        # Reproducible with no mbasic code at all:
        #     p = tkinter.Tk(); p.destroy()
        #     r = tkinter.Tk(); r.after(300, r.quit); r.mainloop()   # SIGTRAP
        # Full create/mainloop/destroy cycles nest and repeat fine, which is
        # why drive() can build a window per test; only the never-ran root is
        # poisonous.
        probe.withdraw()
        probe.update()
        probe.destroy()
    except ImportError:
        missing = "tkinter not installed"
    except Exception as exc:                # TclError: no display
        missing = f"no display available ({exc})"

    if missing:
        print(f"\nSKIPPING the windowed half: {missing}")
    else:
        test_input_dollar_in_the_ui()
        test_inkey_sees_a_key_typed_mid_run()
        test_stop_breaks_a_blocked_input_dollar()
        test_the_input_statement_still_gets_its_answer()

    failed = results.count(False)
    print("\n" + "=" * 60)
    print(f"Results: {results.count(True)} passed, {failed} failed")

    if failed:
        print("❌ Some tests failed")
        sys.exit(1)
    print("✅ All tests passed!")
    sys.exit(0)
