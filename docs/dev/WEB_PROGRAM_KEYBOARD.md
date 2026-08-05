# The web UI gives a running program its own keyboard

**Created:** 2026-08-05
**Status:** Fixed - `src/ui/web/web_keyboard.py` (new),
`src/ui/web/nicegui_backend.py`, `src/iohandler/base.py`, `src/interpreter.py`
**Regression test:** `tests/regression/ui/test_web_keyboard.py`

The last backend behind the seam from
[KEY_INPUT_ROUTING.md](KEY_INPUT_ROUTING.md), after
[CURSES_PROGRAM_KEYBOARD.md](CURSES_PROGRAM_KEYBOARD.md) and
[TK_PROGRAM_KEYBOARD.md](TK_PROGRAM_KEYBOARD.md). What was there:

	def input_char(self, blocking: bool = True) -> str:
	    """Get single character (not implemented for web)."""
	    return ""

So `INKEY$` never saw a key, and `INPUT$` returned an empty string without
waiting - which is worse than it looks, because a program then does `ASC(A$)`
on it and dies with "Illegal function call" instead of pausing for input.

## The constraint that makes this backend different

The other two solve waiting by waiting. The curses UI reads its screen directly
while the event loop is stopped; the Tk UI pumps its loop by hand. Neither is
available here, and the reason is not style: a keypress arrives from the
browser over a **websocket served by the same asyncio loop that ticks the
interpreter**. Blocking that loop for a key means the key can never arrive. It
is not slow - it is a deadlock, and it takes every other session on the server
with it.

There is no third thread to move to either, not without making every UI update
from the interpreter cross a thread boundary that nicegui does not expect.

So the web keyboard does not wait. It raises.

## Not-yet, instead of waiting

`WebKeyboard.input_chars()` raises `KeyInputPending` (new, in
`src/iohandler/base.py`) when the queue is short. The interpreter treats it as
"not yet":

	except KeyInputPending:
	    self.state.waiting_for_key = True
	    return self.state

The PC is left exactly where it is, so when the backend ticks again the *same
statement* runs from the start - and by then a key is queued. `_execute_tick`
sees `state.waiting_for_key`, cancels the tick timer rather than re-running the
statement every 10ms, and `WebKeyboard`'s `on_key` callback starts the timer
again when a key actually arrives. In this UI a keypress is the only event that
can change the answer, so it is the only thing that needs to wake the program.

Re-running a statement is not a new idea here: it is exactly what `CONT` does
after a Ctrl+C break in `INPUT$`, which
[INPUT_DOLLAR_RAW_READ.md](INPUT_DOLLAR_RAW_READ.md) already relies on and
tests.

Two rules fall out of it, and both are silent when broken, so both are tested:

- **Nothing may be consumed on the way out.** `INPUT$(3)` with two keys queued
  takes *neither* and raises, or the retry would read the third character into
  a variable missing the first two. Take all of them or none.
- **`INKEY$` must never raise.** "No key pending" is an answer it can always
  give, and a polling loop that paused the program would never poll again.

A Ctrl+C in the queue ends a short read immediately rather than waiting for the
rest - the user asked to interrupt, and `INPUT$` turns `CHR$(3)` into a break.

## Browser keys

`ui.keyboard(on_key=..., ignore=[])` at the top level of the page, not on a
pane: while a program runs it owns the console, the way it does on a real
terminal. `ignore=[]` is what lets it hear keys typed with the editor or the
immediate line focused; `_program_owns_keyboard` is what stops it stealing
them - it is False when nothing is running, at a breakpoint, or while the
`INPUT` statement's inline field is waiting for its answer.

Only `keydown` is taken. The browser reports press *and* release, and a program
polling `INKEY$` would otherwise see every key twice.

Translation:

- A one-character `KeyboardEvent.key` is itself.
- **Ctrl+letter becomes the control character** - a browser will not send
  `CHR$(3)` on its own, so without this a web user could not interrupt an
  `INPUT$` at all.
- `Enter` is `CHR$(13)`, as a CP/M console sends; `Tab`, `Backspace` and
  `Escape` likewise.
- Arrows and F-keys become the escape sequences a terminal transmits, from
  `BROWSER_KEY_TO_ANSI`. That is now the **third** table answering that
  question, after Tk's `KEYSYM_TO_ANSI` and the Windows scan-code table, so
  the test asserts all three hold the same 22 sequences rather than trusting
  three comments to stay in step.
- Anything else - `Shift`, `Meta`, dead keys - is not a keypress a program
  should see.

## Immediate mode

`PRINT INPUT$(1)` typed at the web UI's immediate line used to reach
`ConsoleKeyboardMixin`, which reads the *server's* terminal: a browser user
could block the machine running the server on a keypress nobody was there to
type. The immediate handler now gets the session's keyboard too, so at worst
the read pauses.

## Verifying

	python3 tests/regression/ui/test_web_keyboard.py

41 checks, no browser and no nicegui import: the queue and the pause/resume
contract are the substance, and both are reachable without either. Ten cover
`WebKeyboard` (translation, Ctrl+letter, the three-table agreement, consuming
nothing when it raises, `INKEY$` never raising, the wake-up callback); four
drive the real interpreter through a program that pauses, resumes, and reads
`INPUT$(3)` fed one key at a time; two build a bare backend to check who owns
the keyboard.

	python3 tests/playwright/test_web_keyboard_browser.py

6 more in a real browser, for the part only a browser can show: nicegui's
`ui.keyboard` delivering the event shape this code expects, and the tick timer
being cancelled when a program parks and recreated when a key arrives. It runs
the server, presses `q` at a paused `INPUT$` and `z` at a polling `INKEY$`, and
reads the output pane. About 20 seconds, so it lives in `tests/playwright/`
rather than under `tests/regression/`, whose runner allows a test 30 - and
discards its output when one runs over. Needs `pip install nicegui playwright`
and `playwright install chromium`; skips with exit 2 if any of those is
missing.

## Known limitations

**A statement that pauses runs again from its start.** `A$=INPUT$(1)` is
idempotent, but `PRINT "A";INPUT$(1)` prints `A` once per key that fails to be
there. This is inherited from the CONT resume model rather than introduced
here - the same thing happens after a Ctrl+C break in the CLI - but the web is
the first place it can happen without the user asking for a break. Fixing it
properly means making the expression evaluator resumable, which is a much
larger change than a keyboard.

**Nothing stops a program that never reads a key.** The curses and Tk UIs have
a stop key that reaches a blocked read. Here a program parked on
`waiting_for_key` is not blocking anything - the UI is fully responsive and Stop
works normally - but a program spinning in a tight loop without reading is
still only interruptible through the menu.
