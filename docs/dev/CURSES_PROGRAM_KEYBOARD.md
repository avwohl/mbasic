# The curses UI gives a running program its own keyboard

**Created:** 2026-08-05
**Status:** Fixed - `src/ui/urwid_keyboard.py` (new), `src/ui/curses_ui.py`,
`src/ui/capturing_io_handler.py`
**Regression test:** `tests/regression/ui/test_curses_keyboard.py`

The first backend to implement the seam from
[KEY_INPUT_ROUTING.md](KEY_INPUT_ROUTING.md). Until now the curses UI had no
keyboard of its own, so `INKEY$` and `INPUT$` fell through to
`ConsoleKeyboardMixin` and read the process's terminal - the same file
descriptor urwid was reading.

Measured against the previous commit, same probe, same programs:

	                                        before   after
	INPUT$ prompt visible before waiting      no      yes
	INPUT$ receives the typed key             yes     yes
	INKEY$ sees a key typed during a run      no      yes
	stop key ends a blocked INPUT$            no      yes

`INPUT$` "worked" by stealing the next key out from under urwid. The other
three are what a keyboard has to fix.

## Why INPUT$ blocks at all

`INPUT` the statement suspends: `tick()` returns with `state.input_prompt` set,
the UI opens a dialog, and `provide_input()` resumes. `INPUT$` cannot do that.
It is an *expression*, evaluated deep inside `execute_statement`, so there is
no point at which the interpreter can return to the event loop and come back
where it left off. It blocks inside the tick callback.

Everything below follows from that.

**The prompt was invisible.** A tick collects the program's output only after
it returns, so `10 PRINT "PRESS A KEY";: A$=INPUT$(1)` displayed nothing at all
and the UI looked hung. `UrwidKeyboard` calls back into the UI
(`on_wait` -> `_flush_program_output`) once, immediately before it settles in
to wait: drain the buffer into the output pane, repaint, then wait.

**Nothing else is reading the terminal.** That is what makes reading the screen
directly safe: `screen.get_input(True)` is the same call urwid itself makes,
and the main loop is stopped inside our callback, so there is no second reader
to race.

**The UI cannot act on its own stop key.** The event loop is not running, so
`^X` cannot reach `_handle_input`. The keyboard translates the UI's stop keys
into `CHR$(3)`, which `INPUT$` already treats as a break - so the program stops
with `Break in nn`, `CONT` still works, and the UI comes back. Without this a
program waiting on a key could not be stopped at all.

## Keys typed between ticks

The interpreter is ticked from an alarm every 10ms, so between ticks urwid is
reading the terminal and dispatching keys to the editor widget. A key meant for
a polling `INKEY$` was typed into the program listing instead - which is why
`INKEY$` could never see one.

`CursesBackend._filter_input` is installed as urwid's `input_filter`, and while
a program owns the keyboard it hands the raw bytes to `UrwidKeyboard` and
returns no keys for urwid to process. A running program owns the console, the
way it does on a real terminal.

"Owns the keyboard" is deliberately not `self.running`:

	if getattr(self, 'paused_at_breakpoint', False):
	    return False
	if loop is None or loop.widget is not self.base_widget:
	    return False
	if self.running:
	    return True
	pc = getattr(getattr(self, 'runtime', None), 'pc', None)
	return bool(pc is not None and pc.is_running())

`self.running` is set by the debug-run and CONT paths but **never by
`_run_program`**, so gating on it alone left an ordinary `RUN` with no keyboard
- the first version of this did exactly that, and `INKEY$` stayed broken. The
interpreter's own PC is the reliable answer.

The `loop.widget` test is what stops the filter from swallowing a dialog's
keys. The `INPUT` statement opens an overlay and waits for an answer; with the
filter diverting every key unconditionally, that answer never arrives and the
program hangs forever. Menus, help and settings are the same shape. There is a
test for the `INPUT` case specifically.

## Byte transparency

urwid's `input_filter` and `get_input(raw_keys=True)` both hand back the raw
byte values, and one byte becomes one character. `ASC()` therefore means the
same thing here as under the console handler and on Windows, and an arrow key
arrives as the three bytes the terminal sent - which is what a CP/M program
polling `INKEY$` would have seen.

The queue is cleared when a program starts (`_setup_program`): keys typed at
the previous program are not input for this one, and half of an escape sequence
left by a program that stopped mid-arrow certainly is not. This is the POSIX
equivalent of `win_flush_pending()`.

## Verifying

	python3 tests/regression/ui/test_curses_keyboard.py

33 checks in about 20 seconds. The first nine drive `UrwidKeyboard` directly
with a fake screen - it imports no urwid on purpose, so the queue, the byte
transparency, the stop-key mapping, the interrupt callback and the flush-once
rule are testable anywhere, including where the UI cannot run at all. The last
four drive the real UI over a pty, which is the only way to prove the wiring:
the prompt appearing before the wait, `INKEY$` seeing a key typed mid-run, the
stop key ending a blocked read, and the `INPUT` dialog still receiving its
answer.

The pty half skips loudly if `urwid` or `pexpect` is missing, and the unit half
still runs - verified by blocking both imports: 20 checks, still green.

### Never type at a UI that has not painted

urwid starts its screen with `tty.setcbreak()`, and `termios`' default for that
is `TCSAFLUSH` - which **discards** input that arrived first
(`urwid/display/_posix_raw_display.py`, `_start`). Anything typed before that
point is echoed by the still-cooked tty and then thrown away.

The pty harness used to sleep 1.2s and start typing. Startup measured 0.6-1.2s
here, so on a loaded box it lost the race, and the program that ran was missing
however many lines went in early: without line 10 it is `NEXT without FOR`,
without 10 through 40 what is left runs straight to its `END`. That surfaced as
`INKEY$` intermittently "not seeing" a key - about one run in twelve - and never
as a lost line, because the cooked tty's echo of a discarded line looks exactly
like the editor taking it.

So `UI.__init__` waits for the last text of the first paint, and then waits for
the editor to echo each program line before sending the next. Measured against
a UI launched behind `sleep 2`: the old harness lost 6 of 6 lines, the new one
none. Under nothing worse than a loaded box, the old harness lost 4 of 6.

`tests/regression/ui/test_curses_pexpect.py` and
`tests/regression/ui/test_curses_exit.py` slept 1.5s at the same spot and had
the same exposure; both now wait for the paint too, and wait for `EOF` rather
than sleeping at an exit. Behind `sleep 2` the old versions lost the typed
program and lost `^Q` respectively - the UI never exited - and the new ones do
neither. Waiting for `EOF` also gave `test_curses_exit.py` its "no error
output" check back: it read `child.before`, which no `expect` had ever set, so
it had been scanning `None`.

Any future pty test should wait for `PAINTED` before it types. The trap is
quiet, because the pty echoes what it discards: a lost keystroke looks exactly
like one the UI accepted.

Note that `python3 tests/run_regression.py` reports many more tests once urwid
is installed. Without it, 8 files fail on `ModuleNotFoundError` and 2 skip;
`pip install "mbasic[curses]"` turns that into 7 genuine pre-existing failures
(keyword case, settings, keybindings, position serializer, chain case).

## Known limitations

**The UI is frozen while `INPUT$` waits.** Nothing is redrawn, the menu does
not open, a resize is not handled until a key arrives. Only the stop key gets
out, and only because the keyboard translates it. Fixing this properly means
making `INPUT$` suspend the way the `INPUT` statement does, which needs the
expression evaluator to be resumable - a much larger change than a keyboard.

**A program owns every key except stop and quit while it runs.** That is right
for a BASIC console, but it means the menu and the editor are unreachable
during a long-running program that never reads a key. `^X` stops it.

**~~Tk and the web UI still have no keyboard.~~** Tk has one now - see
[TK_PROGRAM_KEYBOARD.md](TK_PROGRAM_KEYBOARD.md), which solves the same problem
with a pumped event loop instead of a direct screen read. The web backend still
returns "" from `SimpleWebIOHandler.input_char`.
