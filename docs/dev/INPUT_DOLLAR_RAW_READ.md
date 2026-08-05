# INPUT$ read the keyboard cooked, and buffered it out of everyone's reach

**Created:** 2026-08-05
**Status:** Fixed - `src/basic_builtins.py`, `BuiltinFunctions.INPUT`
**Regression test:** `tests/regression/interpreter/test_input_dollar_posix.py`

The fourth and last of the stdin readers, deferred from
[EDIT_MODE_TYPEAHEAD.md](EDIT_MODE_TYPEAHEAD.md) because it changes how a BASIC
statement reads its input. The other three are covered by
[CLI_INPUT_HANDLING_FIXES.md](CLI_INPUT_HANDLING_FIXES.md) and
[WINDOWS_CONSOLE_KEYS.md](WINDOWS_CONSOLE_KEYS.md).

The whole keyboard path was:

	result = ""
	for i in range(num):
	    char = sys.stdin.read(1)
	    if not char:
	        break
	    result += char
	return result

No terminal handling of any kind. Measured under a pty, the terminal was in
full canonical mode while `INPUT$` waited - `lflag = ICANON|ECHO|ISIG|IEXTEN` -
which made it wrong four ways at once.

**It waited for Enter.** Typing `A` at `INPUT$(1)` produced nothing; typing
`ABC` at `INPUT$(3)` produced nothing. Both returned only once Enter was
pressed.

**It echoed.** The terminal echoed the keystroke, so a program that prints the
key itself printed it twice - `basic/games/hangman.bas:260` is
`L$=INPUT$(1):PRINT X5$L$`.

**It stranded the rest of what was typed.** `sys.stdin.read(1)` goes through a
`TextIOWrapper`, which pulls the whole canonical line into a userspace buffer
that nothing else can see. On a tty neither the REPL nor the `INPUT` statement
can reach it - both read at the file descriptor through readline - so the
keystroke looked lost. It was not lost. The *next* `INPUT$` got it:

	RUN            <- typed "AB" then Enter
	GOT65
	RUN            <- nothing typed at all
	GOT66
	RUN            <- nothing typed at all
	GOT10

Stale keystrokes crossed program runs. On piped input, where there is no
readline, the leftovers came back as REPL commands instead:
`?Parse error at line 1, column 3: Unknown statement or command: 'b'`.

**Ctrl+C could neither reach the program nor stop it.** `ISIG` turned it into a
SIGINT, and `Interpreter._setup_break_handler` only sets `break_requested` and
returns, so PEP 475 restarted the blocked read. The break was deferred until
some later keystroke ended the read - and that keystroke was then swallowed by
the break instead of being delivered:

	^C                             <- nothing happens
	Q                              <- meant for the program
	Break in PC(30.0)              <- 'Q' never reached line 30

## What real MBASIC does

From the BASIC-80 5.21 reference manual, section 3.17 (recoverable at
`git show cfa65e76^:doc/external/basic_ref.txt`):

	Returns a string of X characters, read from the terminal or from file
	number Y. If the terminal is used for input, no characters will be echoed
	and all control characters are passed through except Control-C, which is
	used to interrupt the execution of the INPUT$ function.

Checked against the real 5.21 binary under `cpmemu`, driven over a pty so the
echo question could be settled properly (`cpmemu` puts the tty in raw mode
itself, so any echo seen would have to come from MBASIC):

- No echo. Program lines typed at `Ok` were echoed back in the same session, so
  echo would have been visible had MBASIC produced it.
- No Enter. The two bytes `AB` with no newline satisfied two successive
  `INPUT$(1)` calls.
- Ctrl+C aborts the program at that line and returns to `Ok`. The program does
  not receive `CHR$(3)`. `CONT` is accepted afterwards and re-enters the
  `INPUT$`.
- Ctrl+C is the only exception: `CHR$(1)`, `CHR$(13)` and `CHR$(26)` all reach
  the program unchanged.

## The fix

The established idiom, with one difference: raw mode is entered **once for the
whole n-character read** rather than per character. Dropping back to cooked
mode between characters would echo the rest of what was typed and wait for
Enter before delivering it.

	tty.setraw(fd, termios.TCSANOW)
	while len(chars) < num:
	    data = os.read(fd, num - len(chars))
	    if not data:
	        break
	    chars += data.decode('latin-1')

`TCSANOW`, not `setraw()`'s `TCSAFLUSH` default, for the reason it matters
everywhere else here: `FLUSH` discards input that has arrived but has not been
read. Keys typed ahead of the statement were delivered before this change and
still are - there is a test for exactly that.

`os.read` and `latin-1` for byte transparency, so `ASC()` means the same thing
under `INPUT$`, under `INKEY$` and on Windows. Enter now arrives as `CHR$(13)`
rather than `CHR$(10)`, because raw mode turns off `ICRNL` - which is what a
CP/M console sends.

`TERMINAL_ERRORS` around `tcgetattr` selects the fallback: piped input, a file,
or a stdin replacement with no real `fileno()` has no terminal to put in raw
mode, and is read with `sys.stdin.read(1)` as before. That is deliberate rather
than lazy - with no tty there is no readline either, so the REPL and the
`INPUT` statement are going through that same `TextIOWrapper`, and matching
them is what keeps the characters in order. The fallback after a *failed* raw
read only re-reads if nothing was read yet, or a partial read would deliver its
characters twice.

Windows loops `win_read_key(blocking=True)`, where `""` means "there is no
console at all" rather than "no key" - see `src/win_console.py`.

## Ctrl+C

Raw mode clears `ISIG`, so the 0x03 byte is delivered to the reader instead of
becoming a SIGINT. That makes the policy this interpreter's to choose for the
first time, and it now breaks, as the manual describes and as the real binary
does: `BreakException`, "Break in nn", `CONT` re-enters the `INPUT$`.

The alternative - handing `CHR$(3)` to the program, which is what
`docs/help/common/language/functions/input_dollar.md` used to claim already
happened - was rejected because raw mode is held for the whole blocking wait.
A program sitting in `INPUT$` would have become impossible to interrupt from
the keyboard at all.

Two deliberate differences from 5.21, both noted in the help page:

- 5.21 returns silently to `Ok`; this prints `Break in nn`, matching what STOP
  and Ctrl+C during `INPUT` already print here.
- `INKEY$` is left alone. It only enters raw mode once `select()` has already
  reported a key, so on POSIX the terminal is cooked while a program polls it
  and Ctrl+C usually becomes a SIGINT before `INKEY$` can see the byte -
  measured: `Break in 10`, not `CHR$(3)`. It also never blocks, so it cannot
  trap the user the way a pending `INPUT$` would.

`BreakException` had never actually been raised anywhere in `src/` - it was
defined and caught, and that was all. Raising it exposed two things in the
handler that had never run:

- The message was `f"Break in {pc}"`, which prints the debugging repr:
  `Break in PC(30.0)`. Both break sites now use `pc.line_num`, as
  `execute_stop()` already did.
- Immediate mode (`PRINT INPUT$(1)` at the `Ok` prompt) had no arm for it, so
  the break would have been reported as `?BreakException`. Both immediate-mode
  paths - `InteractiveMode.execute_immediate` for the CLI and
  `ImmediateExecutor.execute` for the visual UIs - now report `Break`, the way
  `execute_stop()` reports a STOP with no line number.

## Verifying

	python3 tests/regression/interpreter/test_input_dollar_posix.py

23 checks in under 3 seconds: single keystroke with no Enter and no echo,
`INPUT$(3)` in one burst, no stale keystroke into the next RUN, type-ahead
typed before the statement, `CHR$(1)`/`CHR$(13)`/high bytes passed through,
Ctrl+C breaking and `CONT` resuming, Ctrl+C in immediate mode, and the piped
path. Against the code before the fix it reports 12-13 failures in about a
minute (the count varies with where the stranded bytes land), naming each of
the four symptoms plus `Break in PC(30.0)`.

Speed comes from `drain(..., until=marker)`: without it every step pays its
full timeout, since a quiet interpreter and a hung one look identical until the
deadline expires. Every read of the pty master is `select()`-gated against a
deadline, so a hang fails the test instead of hanging the runner.

Tests that type at an `INPUT$` prompt wait for the program to print a marker
and then pause `RAW_MODE_SETTLE` (0.2s). The marker is flushed a few hundred
microseconds before `tty.setraw()` runs, and typing inside that window is a
race a human cannot win: the keystroke lands in the cooked queue, gets echoed,
and an Enter is rewritten to LF by `ICRNL` on the way in.

## Known limitations

**A key typed before `INPUT$` starts carries the cooked terminal's
translations.** It is still delivered - that is what `TCSANOW` protects - but
it passed through the line discipline on the way in, so an early Enter arrives
as `CHR$(10)` where one typed at the prompt arrives as `CHR$(13)`. Fixing that
would mean holding the terminal in cbreak for the whole program run, which is
the same underlying gap that stops a bare `10 A$=INKEY$` loop from seeing
keystrokes (see [WINDOWS_CONSOLE_KEYS.md](WINDOWS_CONSOLE_KEYS.md)).

**Leftover type-ahead now goes back to the REPL.** Typing `AB` and Enter at
`INPUT$(1)` leaves `B` and the terminator in the tty queue, where the REPL
reads them and reports `Unknown statement or command: 'b'`. That is the honest
outcome - the same as typing ahead at the `Ok` prompt - and it is what stops
the byte from surfacing two RUNs later. It is not silently discarded, because
discarding input is the bug this family of fixes exists to remove.

## Not fixed here

**`IOHandler.input_char()` is dead API.** Eight implementations exist and
nothing in `src/` calls any of them; `src/iohandler/base.py`,
`src/terminal_errors.py` and `CLI_INPUT_HANDLING_FIXES.md` all describe
`ConsoleIOHandler.input_char` as "the `INPUT$` reader", and it never was - the
comments have been corrected. `BuiltinFunctions` is constructed with only the
runtime (`src/interpreter.py`), so `INPUT$` and `INKEY$` cannot reach the
interpreter's I/O handler at all.

The consequence is that under the curses, web and Tk backends both builtins
read the *server or launching terminal's* `sys.stdin` rather than the backend's
input. Measured with a `CapturingIOHandler` whose `input_char` returns `""`:
`INPUT$(1)` still returned the byte piped to the process. Since each of those
UIs ticks the interpreter from inside its own event loop, a blocking `INPUT$`
freezes the UI - for the web backend, every session on the server. Routing the
two builtins through the I/O handler would fix that, and is a change to the
interpreter's construction rather than to a terminal-mode read.

**Immediate-mode `INPUT`** (the statement, not the function) still does not
work - see the same note in
[CLI_INPUT_HANDLING_FIXES.md](CLI_INPUT_HANDLING_FIXES.md).

**The compiler backends have no `INPUT$` reader.** The C backend emits
`/* unsupported function */`; the JS backend passes the name through and emits
literal `input$(...)`. Nothing here changes that.
