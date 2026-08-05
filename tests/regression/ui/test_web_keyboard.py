#!/usr/bin/env python3
"""
Test that a program running in the web UI has a keyboard of its own.

INKEY$ and INPUT$ read through the I/O handler (docs/dev/KEY_INPUT_ROUTING.md).
`SimpleWebIOHandler.input_char` returned "" and nothing else, so INKEY$ never
saw a key and INPUT$ silently returned an empty string.

The web UI is the one backend that cannot fix this by waiting. Its keys arrive
from the browser over a websocket served by the same asyncio loop that ticks
the interpreter, so blocking for a keypress means the keypress can never
arrive - a deadlock that takes every other session on the server with it. The
curses UI reads its stopped screen directly and the Tk UI pumps its own loop;
neither is available here.

So `WebKeyboard` raises `KeyInputPending` instead of waiting, the interpreter
leaves the statement where it is and pauses, and the backend ticks again when a
key arrives - re-running the statement, which is the same resume model CONT
uses after a Ctrl+C break in INPUT$.

Two things that follow, and are tested below because getting either wrong is
silent: nothing may be consumed when it raises, or the retry reads into a
variable that is missing the characters already taken; and INKEY$ must never
raise, because "no key pending" is an answer it can always give.

No browser and no nicegui here - the queue and the pause/resume contract are
what matter, and both are testable without either.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.interpreter import Interpreter
from src.iohandler.base import IOHandler, KeyInputPending
from src.lexer import Lexer
from src.parser import Parser
from src.runtime import Runtime
from src.ui.web.web_keyboard import WebKeyboard, BROWSER_KEY_TO_ANSI

results = []


def check(condition, label):
    """Record one check; print pass/fail immediately."""
    results.append(bool(condition))
    print(f"{'PASS' if condition else 'FAIL'}: {label}")


# ---------------------------------------------------------------------------
# WebKeyboard on its own
# ---------------------------------------------------------------------------

def test_ordinary_keys_are_queued():
    print("\nordinary browser keys are queued as characters")
    print("-" * 60)
    keyboard = WebKeyboard()
    check(keyboard.push_browser_key('A'), "'A' was taken")
    keyboard.push_browser_key('b')
    check(keyboard.input_chars(2) == 'Ab', "both came back in order")


def test_named_keys_become_the_bytes_a_terminal_sends():
    print("\nnamed keys are translated")
    print("-" * 60)
    keyboard = WebKeyboard()
    keyboard.push_browser_key('Enter')
    check(keyboard.input_chars(1) == '\r',
          "Enter is CHR$(13), as a CP/M console sends")

    keyboard = WebKeyboard()
    keyboard.push_browser_key('ArrowUp')
    check(keyboard.input_chars(3) == '\x1b[A', "Up is ESC [ A")

    keyboard = WebKeyboard()
    keyboard.push_browser_key('Escape')
    check(keyboard.input_chars(1) == '\x1b', "Escape is CHR$(27)")


def test_ctrl_letter_becomes_a_control_character():
    """A browser will not send CHR$(3) on its own."""
    print("\nCtrl+letter reaches the program as a control character")
    print("-" * 60)
    keyboard = WebKeyboard()
    keyboard.push_browser_key('c', ['ctrl'])
    check(keyboard.input_chars(1) == '\x03',
          "Ctrl+C is CHR$(3), which INPUT$ treats as a break")

    keyboard = WebKeyboard()
    keyboard.push_browser_key('a', ['ctrl'])
    check(keyboard.input_chars(1) == '\x01', "Ctrl+A is CHR$(1)")

    keyboard = WebKeyboard()
    keyboard.push_browser_key('c')
    check(keyboard.input_chars(1) == 'c', "and a plain 'c' is still 'c'")


def test_keys_with_no_character_are_dropped():
    print("\nmodifiers and unknown keys are not keypresses")
    print("-" * 60)
    keyboard = WebKeyboard()
    for key in ('Shift', 'Control', 'Meta', 'Dead', ''):
        check(not keyboard.push_browser_key(key), f"{key!r} was not queued")
    check(keyboard.pending() == 0, "nothing queued at all")


def test_the_three_special_key_tables_agree():
    """Web, Tk and Windows all answer the same question.

    A program reading INKEY$ must get the same bytes for an arrow key
    whichever backend it happens to be running under.
    """
    print("\nthe web, Tk and Windows special-key tables agree")
    print("-" * 60)
    from src.ui.tk_keyboard import KEYSYM_TO_ANSI
    from src.win_console import _WIN_KEY_TO_ANSI

    web = set(BROWSER_KEY_TO_ANSI.values())
    tk = set(KEYSYM_TO_ANSI.values())
    win = set(_WIN_KEY_TO_ANSI.values())
    check(web == tk, f"web and Tk agree (differences: {web ^ tk})")
    check(web == win, f"web and Windows agree (differences: {web ^ win})")


def test_inkey_never_raises():
    """"No key pending" is an answer INKEY$ can always give."""
    print("\nINKEY$ reports no key rather than pausing the program")
    print("-" * 60)
    keyboard = WebKeyboard()
    try:
        got = keyboard.input_char(blocking=False)
        raised = None
    except KeyInputPending as exc:
        got, raised = None, exc
    check(raised is None, "no KeyInputPending from a non-blocking read")
    check(got == "", f"just an empty string (got {got!r})")


def test_a_short_queue_pauses_and_consumes_nothing():
    """The retry must find the queue exactly as it was."""
    print("\nan unsatisfiable read consumes nothing")
    print("-" * 60)
    keyboard = WebKeyboard()
    keyboard.push('AB')

    try:
        got = keyboard.input_chars(3)
        raised = None
    except KeyInputPending as exc:
        got, raised = None, exc

    check(isinstance(raised, KeyInputPending),
          f"INPUT$(3) with two queued raised KeyInputPending (got {got!r})")
    check(keyboard.pending() == 2,
          f"and took neither of them (queue has {keyboard.pending()})")

    keyboard.push('C')
    check(keyboard.input_chars(3) == 'ABC',
          "the retry reads all three, in order")


def test_ctrl_c_does_not_wait_for_the_rest():
    """An interrupt is not worth waiting on the rest of a read for."""
    print("\nCtrl+C ends a short read immediately")
    print("-" * 60)
    keyboard = WebKeyboard()
    keyboard.push('A\x03')
    got = keyboard.input_chars(5)
    check(got == 'A\x03',
          f"the read came back at the Ctrl+C (got {got!r})")


def test_on_key_fires_so_a_paused_program_can_resume():
    """Nothing else can wake a program parked on KeyInputPending."""
    print("\nqueueing a key notifies the backend")
    print("-" * 60)
    woken = []
    keyboard = WebKeyboard(on_key=lambda: woken.append(1))
    keyboard.push_browser_key('X')
    check(len(woken) == 1, f"the callback fired once (got {len(woken)})")
    keyboard.push_browser_key('Shift')
    check(len(woken) == 1, "and not for a key that was not queued")


def test_clear_drops_queued_keys():
    print("\nclear() empties the queue between programs")
    print("-" * 60)
    keyboard = WebKeyboard()
    keyboard.push('XY')
    keyboard.clear()
    check(keyboard.pending() == 0, "nothing left queued")


# ---------------------------------------------------------------------------
# The interpreter's half of the contract
# ---------------------------------------------------------------------------

class PendingHandler(IOHandler):
    """An I/O handler with a WebKeyboard and a list for its output."""

    def __init__(self, keyboard):
        self.keyboard = keyboard
        self.lines = []

    def output(self, text, end='\n'):
        self.lines.append(str(text) + end)

    def input(self, prompt=''):
        return ""

    def input_line(self, prompt=''):
        return ""

    def input_char(self, blocking=True):
        return self.keyboard.input_char(blocking=blocking)

    def input_chars(self, count, interrupted=None):
        return self.keyboard.input_chars(count, interrupted=interrupted)

    def clear_screen(self):
        pass

    def error(self, message):
        self.lines.append(f"Error: {message}\n")

    def debug(self, message):
        pass

    def text(self):
        return ''.join(self.lines)


def run_program(source, keyboard):
    """Start a program and return (interpreter, handler)."""
    ast = Parser(Lexer(source).tokenize()).parse()
    runtime = Runtime({line.line_number: line for line in ast.lines})
    handler = PendingHandler(keyboard)
    interpreter = Interpreter(runtime, handler)
    interpreter.start()
    return interpreter, handler


def test_the_interpreter_pauses_instead_of_failing():
    """KeyInputPending must pause the program, not become a BASIC error."""
    print("\nthe interpreter pauses on KeyInputPending")
    print("-" * 60)
    keyboard = WebKeyboard()
    interpreter, handler = run_program(
        '10 PRINT "ASK"\n20 A$=INPUT$(1)\n30 PRINT "GOT";ASC(A$)\n', keyboard)

    state = interpreter.tick(mode='run', max_statements=100)

    check(state.waiting_for_key,
          "the state says it is waiting for a key")
    check(state.error_info is None,
          f"and it is not an error (got {state.error_info})")
    check('ASK' in handler.text(),
          "the output before the read still happened")
    check('GOT' not in handler.text(),
          "and the read itself did not complete")


def test_the_program_resumes_when_a_key_arrives():
    """The paused statement runs again and finishes."""
    print("\nthe program resumes on the next tick once a key is queued")
    print("-" * 60)
    keyboard = WebKeyboard()
    interpreter, handler = run_program(
        '10 A$=INPUT$(1)\n20 PRINT "GOT";ASC(A$)\n', keyboard)

    interpreter.tick(mode='run', max_statements=100)
    keyboard.push('Q')
    state = interpreter.tick(mode='run', max_statements=100)

    check(not state.waiting_for_key, "no longer waiting")
    check('GOT 81' in handler.text() or 'GOT81' in handler.text(),
          f"the program read the key (output: {handler.text().strip()!r})")


def test_a_multi_character_read_resumes_intact():
    """INPUT$(3) fed one key at a time must still return all three."""
    print("\nINPUT$(3) survives being fed a key at a time")
    print("-" * 60)
    keyboard = WebKeyboard()
    interpreter, handler = run_program(
        '10 A$=INPUT$(3)\n20 PRINT "LEN";LEN(A$);ASC(A$)\n', keyboard)

    for char in 'AB':
        interpreter.tick(mode='run', max_statements=100)
        keyboard.push(char)
    interpreter.tick(mode='run', max_statements=100)
    keyboard.push('C')
    state = interpreter.tick(mode='run', max_statements=100)

    text = handler.text()
    check(not state.waiting_for_key, "the read completed")
    check('3' in text and '65' in text,
          f"all three characters arrived (output: {text.strip()!r})")


def test_inkey_does_not_pause_a_program():
    """A polling loop must keep running when no key is pending."""
    print("\nINKEY$ leaves a program running")
    print("-" * 60)
    keyboard = WebKeyboard()
    interpreter, handler = run_program(
        '10 FOR I=1 TO 5\n20 A$=INKEY$\n30 NEXT I\n40 PRINT "DONE"\n',
        keyboard)

    state = interpreter.tick(mode='run', max_statements=1000)

    check(not state.waiting_for_key, "never waited")
    check('DONE' in handler.text(),
          f"and ran to the end (output: {handler.text().strip()!r})")



# ---------------------------------------------------------------------------
# The backend's half: who owns the keyboard, and what wakes a paused program
# ---------------------------------------------------------------------------

class FakeKeyName:
    """nicegui reports event.key as an object with a .name."""

    def __init__(self, name):
        self.name = name


class FakeModifiers:
    def __init__(self, ctrl=False, alt=False, shift=False, meta=False):
        self.ctrl, self.alt, self.shift, self.meta = ctrl, alt, shift, meta


class FakeKeyEvent:
    def __init__(self, name, ctrl=False):
        self.key = FakeKeyName(name)
        self.modifiers = FakeModifiers(ctrl=ctrl)
        self.action = type('Action', (), {'keydown': True})()


def bare_backend(keyboard, running=True, waiting_for_input=False):
    """A backend with only the attributes the keyboard path touches.

    Built with __new__ because a real one needs a browser session; the logic
    under test is the gate and the event translation, not the UI.
    """
    from src.ui.web.nicegui_backend import NiceGUIBackend

    backend = NiceGUIBackend.__new__(NiceGUIBackend)
    backend.program_keyboard = keyboard
    backend.running = running
    backend.waiting_for_input = waiting_for_input
    backend.paused_at_breakpoint = False
    return backend


def test_the_backend_gives_a_running_program_its_keys():
    print("\nthe backend routes browser keys to a running program")
    print("-" * 60)
    keyboard = WebKeyboard()
    backend = bare_backend(keyboard)

    check(backend._handle_program_key(FakeKeyEvent('A')), "the key was taken")
    check(keyboard.pending() == 1, "and queued")

    backend._handle_program_key(FakeKeyEvent('c', ctrl=True))
    check(keyboard.input_chars(2) == 'A\x03',
          "Ctrl+C arrived as CHR$(3) through the backend too")


def test_the_ui_keeps_its_keys_when_no_program_is_running():
    print("\nthe UI keeps its keys when nothing is running")
    print("-" * 60)
    keyboard = WebKeyboard()
    check(not bare_backend(keyboard, running=False)._handle_program_key(
        FakeKeyEvent('A')), "not taken while stopped")

    # The INPUT statement's inline field is being typed into - those
    # keystrokes are its answer, not a program's INKEY$.
    check(not bare_backend(keyboard, waiting_for_input=True)._handle_program_key(
        FakeKeyEvent('A')), "not taken while INPUT is waiting")
    check(keyboard.pending() == 0, "nothing was queued in either case")


if __name__ == "__main__":
    print("The web UI's keyboard")
    print("=" * 60)

    test_ordinary_keys_are_queued()
    test_named_keys_become_the_bytes_a_terminal_sends()
    test_ctrl_letter_becomes_a_control_character()
    test_keys_with_no_character_are_dropped()
    test_the_three_special_key_tables_agree()
    test_inkey_never_raises()
    test_a_short_queue_pauses_and_consumes_nothing()
    test_ctrl_c_does_not_wait_for_the_rest()
    test_on_key_fires_so_a_paused_program_can_resume()
    test_clear_drops_queued_keys()

    test_the_interpreter_pauses_instead_of_failing()
    test_the_program_resumes_when_a_key_arrives()
    test_a_multi_character_read_resumes_intact()
    test_inkey_does_not_pause_a_program()

    test_the_backend_gives_a_running_program_its_keys()
    test_the_ui_keeps_its_keys_when_no_program_is_running()

    failed = results.count(False)
    print("\n" + "=" * 60)
    print(f"Results: {results.count(True)} passed, {failed} failed")

    if failed:
        print("❌ Some tests failed")
        sys.exit(1)
    print("✅ All tests passed!")
    sys.exit(0)
