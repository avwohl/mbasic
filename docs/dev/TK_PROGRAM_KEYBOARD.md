# The Tk UI gives a running program its own keyboard

**Created:** 2026-08-05
**Status:** Fixed - `src/ui/tk_keyboard.py` (new), `src/ui/tk_ui.py`
**Regression test:** `tests/regression/ui/test_tk_keyboard.py`

The second backend to implement the seam from
[KEY_INPUT_ROUTING.md](KEY_INPUT_ROUTING.md), after
[CURSES_PROGRAM_KEYBOARD.md](CURSES_PROGRAM_KEYBOARD.md). What was behind it
here was `TkIOHandler.input_char`, which opened a modal dialog:

	simpledialog.askstring("INPUT$ (Single Character)",
	                       "Enter a single character:", parent=self.root)

Measured against the previous commit, driving the real UI under Xvfb:

	                        before                          after
	INPUT$(1)               a modal "type a character        the key that was
	                        and press OK" dialog             typed
	INPUT$(3)               three of those dialogs           three keys
	INKEY$                  "" every time - a polling        the key typed
	                        program never saw a key          during the run

The `INPUT$` probe on the pre-change tree did not finish: the dialog is modal,
nothing in a "press any key" program can answer it, and the run had to be
killed. The `INKEY$` probe finished with an empty output pane.

## Why it blocks, and why that is survivable here

`INPUT$` is an expression, evaluated inside `execute_statement`, so unlike the
`INPUT` statement it cannot suspend the tick and resume - it blocks inside the
`root.after` callback that ticks the interpreter, with Tk's event loop stopped
behind it.

The way out is that Tk lets you run the loop by hand: `TkKeyboard._pump()`
calls `root.update()`, which delivers pending events - including the keypress
being waited for - and repaints. So unlike the curses UI, whose event loop
genuinely stops, **the Tk window stays alive while `INPUT$` waits**: it
repaints, the menus open, and Run > Stop works. That last one matters, because
it is the only way to end a blocking read from the UI: it clears
`self.running`, the keyboard reports that as `CHR$(3)`, and `INPUT$` turns it
into the break it already knows how to do (`Break in 20`).

Pumping the loop means callbacks can run - including a tick scheduled by
whatever the user just clicked. `TkIOHandler.input_chars` sets
`backend._waiting_for_program_key` for the duration and `_execute_tick` returns
immediately when it sees it, so the interpreter cannot be re-entered
underneath a tick that is already inside it.

## Keys go to the program first

`_on_program_key` is bound on the editor text, the immediate entry and the
output pane, **before** their other handlers, and returns `'break'` when it
takes a key - which stops the rest of the binding chain, including the widget's
own class binding that would otherwise type the character into the program
listing. Registration order is what puts it first; `add='+'` keeps the existing
handlers.

Ownership is `self.running and not self.paused_at_breakpoint`. Tk maintains
`self.running` properly - `_execute_tick` returns early without it - which is
the opposite of the curses UI, where it is set only by the debug paths and the
gate had to come from the interpreter's PC instead.

The `INPUT` statement needs no special case here: it sets `self.running = False`
while it waits for the immediate line, so the keys go where they should. There
is a test for that, because it is exactly the kind of thing a key filter
breaks.

## Special keys

Tk reports arrows and function keys by name (`event.keysym`) with no character.
MBASIC has no notion of a named key - a CP/M console is a byte stream, and an
arrow is whatever escape sequence the terminal transmits - so `KEYSYM_TO_ANSI`
translates them into the same sequences the POSIX console produces and the
Windows path already synthesises from scan codes (`_WIN_KEY_TO_ANSI` in
`src/win_console.py`).

Two tables answering the same question is exactly the drift this codebase has
been bitten by before, so the test asserts they contain the same 22 sequences
rather than trusting a comment to keep them honest.

Modifier keysyms are dropped: Shift on its own is not a keypress a program
should see.

## Verifying

	python3 tests/regression/ui/test_tk_keyboard.py

29 checks with a display, 23 without - and 0.6s without, because the eleven
that need no window are the ones that cover the queue, the special-key
translation, the modifier filtering, the interrupt handling and the
flush-once rule. `TkKeyboard` imports no tkinter, which is what makes that
possible.

The four windowed checks are the wiring: `INPUT$` receiving a typed key,
`INKEY$` seeing one typed mid-run, Run > Stop breaking a blocked read, and the
`INPUT` statement still getting its answer. They build the real `TkBackend` and
inject events with `event_generate`, driving everything from `root.after`
callbacks - a key cannot be sent from the test's own code, because while
`INPUT$` blocks, the test is not running.

No display is the normal case on a build machine, so that half skips loudly.
Locally: `xvfb-run -a python3 tests/regression/ui/test_tk_keyboard.py`.

## Known limitations

**A program owns every key while it runs.** The menus stay reachable with the
mouse and Run > Stop still works, but the editor cannot be typed into during a
program - which is right for a BASIC console and surprising for a GUI.

**The wait costs a 20ms poll.** Tk has no "wait for an event with a timeout",
so `_pump()` sleeps between `update()` calls. A tighter loop would spin a core
for no benefit; a looser one would feel sluggish.

**The modal dialog is still there** for a `TkIOHandler` built without a
backend, which is the only way to reach it now. It is the honest fallback for a
handler with no UI behind it.

**~~The web backend still has no keyboard.~~** It has one now - see
[WEB_PROGRAM_KEYBOARD.md](WEB_PROGRAM_KEYBOARD.md). It could neither block nor
pump, because its keys arrive on the same asyncio loop that runs the
interpreter, so it pauses the program instead and resumes it when a key
arrives.
