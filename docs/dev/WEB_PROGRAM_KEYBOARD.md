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

- **A single read consumes nothing on the way out.** `INPUT$(3)` with two keys
  queued takes *neither* and raises, or the retry would read the third
  character into a variable missing the first two. Take all of them or none.
- **`INKEY$` must never raise.** "No key pending" is an answer it can always
  give, and a polling loop that paused the program would never poll again.

A Ctrl+C in the queue ends a short read immediately rather than waiting for the
rest - the user asked to interrupt, and `INPUT$` turns `CHR$(3)` into a break.

## A statement can read more than once

Taking all or nothing is enough for one read per statement. It is not enough
for two:

	10 X$=INPUT$(1)+INPUT$(1)

The first read succeeds and takes a character. The second raises. The retry
runs the first read *again* and takes another. Measured before the fix: four
keys queued, four keys consumed, line 20 never reached - the program ate every
key it was given and never finished. `10 X$=INKEY$+INPUT$(2)` did the same.

So an attempt is bracketed. `KeyReadTransaction` in `src/iohandler/base.py`
adds two methods and a flag; the interpreter calls them around each statement:

	deferring = getattr(self.io, 'defers_key_reads', False)
	if deferring:
	    self.io.begin_key_transaction()
	try:
	    self.execute_statement(stmt)
	except KeyInputPending:
	    if deferring:
	        self.io.rollback_key_transaction()

`WebKeyboard` records what each attempt reads - including `INKEY$`, which never
pauses but does consume - and puts it back at the front of the queue, in order.
The retry then starts from exactly the state the abandoned attempt did.

`defers_key_reads` is what keeps this off everywhere else. A terminal handler
blocks instead of raising, so it never needs a rollback - and could not do one
anyway, since its characters came out of the kernel and cannot be pushed back.
The CLI, curses and Tk paths do not execute a line of this.

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

**A statement that pauses runs again from its start**, so anything in it that
is not a keyboard read happens once per attempt. In practice that is narrower
than it sounds, and it was originally documented here as worse than it is:

- Output does *not* duplicate. `PRINT "A";INPUT$(1)` prints `A` once. Measured:
  `execute_print` evaluates its expressions into a list and writes at the end,
  so an attempt that pauses mid-expression has written nothing.
- Keyboard reads do not duplicate either, since the fix above.
- `RND` does. `PRINT RND;INPUT$(1)` advances the generator once per attempt,
  so a program that pauses skips forward in the sequence. The printed value is
  correct - it is the one from the attempt that finished - but the sequence a
  later `RND` continues from is not the one it would have been. This is the
  only side effect left that a BASIC program can observe, and covering it would
  mean a transactional runtime rather than a transactional read.

**Terminals cannot roll back.** The same double-read shape exists in the CLI
after a Ctrl+C break: `X$=INPUT$(1)+INPUT$(1)`, interrupted after one
character, loses that character when `CONT` re-runs the statement. Its
characters came from the kernel and there is nowhere to put them back. The web
can only do better because its keys are already in a queue of its own.

**Nothing stops a program that never reads a key.** The curses and Tk UIs have
a stop key that reaches a blocked read. Here a program parked on
`waiting_for_key` is not blocking anything - the UI is fully responsive and Stop
works normally - but a program spinning in a tight loop without reading is
still only interruptible through the menu.
