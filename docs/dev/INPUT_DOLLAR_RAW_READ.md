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
	    if self._take_break_request():
	        self._raise_break()
	    if not select.select([fd], [], [], self._BREAK_POLL)[0]:
	        continue
	    data = os.read(fd, 1)
	    if not data:
	        break
	    char = data.decode('latin-1')
	    if char == self._BREAK_CHAR:
	        self._raise_break()
	    chars += char

`TCSANOW`, not `setraw()`'s `TCSAFLUSH` default, for the reason it matters
everywhere else here: `FLUSH` discards input that has arrived but has not been
read. Keys typed ahead of the statement were delivered before this change and
still are - there is a test for exactly that.

`os.read` and `latin-1` for byte transparency, so `ASC()` means the same thing
under `INPUT$`, under `INKEY$` and on Windows. Enter now arrives as `CHR$(13)`
rather than `CHR$(10)`, because raw mode turns off `ICRNL` - which is what a
CP/M console sends.

One byte per `os.read`, and the break checked as each byte arrives. Reading the
whole remainder at once would swallow anything typed *after* a Ctrl+C in the
same chunk, and the break would then destroy keystrokes that should have stayed
queued for whoever reads next. Checking the finished string instead of each
byte was worse still - see "What the review caught".

The `select()` poll is there for the Ctrl+C that arrives *before* raw mode
does. In that window ISIG is still set, so it becomes a SIGINT, and
`_setup_break_handler` only sets `break_requested` and returns - PEP 475 then
restarts the read underneath it. Without the poll the read stays blocked and
the next key typed is consumed into the variable and thrown away by a break
reported against the following line, which is exactly the behavior this fix
exists to remove.

`TERMINAL_ERRORS` around `tcgetattr` selects the fallback: piped input, a file,
or a stdin replacement with no real `fileno()` has no terminal to put in raw
mode, and is read with `sys.stdin.read(1)` as before. That is deliberate rather
than lazy - with no tty there is no readline either, so the REPL and the
`INPUT` statement are going through that same `TextIOWrapper`, and matching
them is what keeps the characters in order. The fallback after a *failed* raw
read only re-reads if nothing was read yet, or a partial read would deliver its
characters twice.

Windows checks `isatty()` first and then loops `win_read_key(blocking=True)`,
where `""` means "there is no console at all" rather than "no key" - see
`src/win_console.py`. The `isatty()` test is what POSIX gets for free from
`tcgetattr` failing on a pipe: `msvcrt.getch()` reads CONIN$, the physical
console, *not* stdin, so without it `mbasic prog.bas < in.txt` would ignore the
redirection completely and block on a keypress that is never coming.

A Windows Ctrl+C never arrives as a byte - the console turns it into a
CTRL_C_EVENT and CPython raises `KeyboardInterrupt` out of `getch()`, which
being a `BaseException` would sail past the tick loop and abandon the program
with no message. It is caught and turned into the same break.

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

A keyboard only. The cooked path does not check for it, so `INPUT$(n)` still
returns `CHR$(3)` from redirected input exactly as it did before any of this -
nobody pressed anything there, and a pipe has no ISIG to reclaim, which is the
whole argument above. `INPUT$(n,#f)` from a file was never in question.

Three deliberate differences from 5.21, the first two noted in the help page:

- 5.21 returns silently to `Ok`; this prints `Break in nn`, matching what STOP
  and Ctrl+C during `INPUT` already print here.
- Real 5.21 under cpmemu breaks on a 0x03 in *piped* input too, because piped
  input is the only console it has. Here it is not one, so that byte stays
  data.
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

## What the review caught

An adversarial review of the first commit (8bf32024) found six real defects,
each reproduced against both trees; they are fixed in the follow-up. Worth
recording, because most of them are the *cure* misbehaving rather than the
original bug:

- **Ctrl+C did nothing to `INPUT$(3)` until two more keys were typed.** The
  break was checked on the completed string, so the 0x03 sat in the buffer
  while the read kept blocking - and raw mode had already taken ISIG away, so
  no SIGINT could fire either. Strictly worse than the cooked read it replaced.
  Now checked per byte, as it is read.
- **A key typed after the Ctrl+C was destroyed with it**, because one `os.read`
  could return `A\x03B` and the break discarded the lot. Now one byte per read,
  so anything after the 0x03 stays in the tty queue.
- **A SIGINT arriving before raw mode still hung the read** and still swallowed
  whatever key ended it - the original bug, in the window the fix did not
  cover. Now polled, see above.
- **A 0x03 byte from a *pipe* raised a break.** Nobody pressed anything there;
  it is data, as it always was. The break check is now on the keyboard paths
  only.
- **The SIGINT handler was never restored** on the new break path, so after a
  Ctrl+C in `INPUT$` the REPL's own Ctrl+C - including three-presses-to-quit -
  was dead for the rest of the session. Restored on both break arms.
- **Windows read the physical console even when stdin was redirected**, so
  `mbasic prog.bas < in.txt` would have blocked on a keypress that never comes.
  `isatty()` first, now.

Two test defects came out of the same review: the `RDY` sync marker matched the
echo of the source line that printed it (`10 PRINT "RDY";`), which flaked 2 runs
in 13 under load, and a failing run took ~58s - past `run_regression.py`'s 30s
timeout, whose handler discards the captured output, so a future regression
would have reported nothing at all.

## Verifying

	python3 tests/regression/interpreter/test_input_dollar_posix.py

32 checks in about 7 seconds: single keystroke with no Enter and no echo,
`INPUT$(3)` in one burst, no stale keystroke into the next RUN, type-ahead
typed before the statement, `CHR$(1)`/`CHR$(13)`/high bytes passed through,
Ctrl+C breaking and `CONT` resuming, one Ctrl+C ending a three-character read,
type-ahead surviving a break, the terminal surviving a SIGTERM mid-read,
Ctrl+C in immediate mode, and both piped cases. Against the code before the fix
it reports 18 failures in ~22s, naming each of the four symptoms plus
`Break in PC(30.0)`.

Speed comes from `drain(..., until=marker)`: without it every step pays its
full timeout, since a quiet interpreter and a hung one look identical until the
deadline expires. Every read of the pty master is `select()`-gated against a
deadline, so a hang fails the test instead of hanging the runner - and every
deadline is additionally clamped to a whole-file budget (`BUDGET_SECONDS`, 20s)
so that a *failing* run still finishes inside the 30s the runner allows and
prints its failure list.

Tests that type at an `INPUT$` prompt wait for the program to print a `CHR$(6)`
marker and then pause `RAW_MODE_SETTLE` (0.2s). The marker is a control byte on
purpose: the CLI echoes a typed-ahead program line twice, once by the line
discipline and once by readline, so a printable marker matches the echo of its
own source line and the sync lands before the program has run. The pause covers
the few hundred microseconds between the marker being flushed and
`tty.setraw()` - typing inside that window is a race a human cannot win, and
the keystroke would be echoed and, if it is Enter, rewritten to LF by `ICRNL`.

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

**A terminal read returns bytes; a piped read returns characters.** The raw
path decodes `latin-1`, so `INPUT$(n)` is n bytes from a tty. The cooked path
is still `sys.stdin.read(1)`, which is n *decoded characters* - so typing
e-acute at `INPUT$(1)` gives `CHR$(195)` (the first UTF-8 byte, the second left
in the queue) while piping the same two bytes gives `CHR$(233)`. Reading
`sys.stdin.buffer` instead would fix the type at the cost of desynchronising
from the wrapper the REPL and `INPUT` read through, which is the stranding bug
in reverse - a worse trade for input that is almost always ASCII.

**Windows: a bare 0xFF keypress with nothing behind it looks like "no
console".** `win_read_key` cannot tell them apart (its own comment concedes
this), and `INPUT$` is now the only live blocking caller. On a misfire the read
falls through to the cooked path - a line read, waiting for Enter - rather than
failing. Untypeable in practice; recorded because the heuristic is now
reachable.

**Windows: half a special key can be left in `_win_pending`.** An arrow expands
to three characters and `INPUT$(1)` takes one, leaving the rest in a
module-level list that only the next builtin read sees. POSIX leaves the same
remainder in the tty queue, where the REPL reports it. Pre-existing in
`INKEY$`'s design; `Interpreter.start()` clears it between programs.

## Not fixed here

**`IOHandler.input_char()` is dead API.** Seven implementations exist behind
one `@abstractmethod`, and nothing reaches any of them: the only call site in
`src/` is `web_io.py`'s own deprecated `get_char()` alias, which has no callers
either. `src/iohandler/base.py`,
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
