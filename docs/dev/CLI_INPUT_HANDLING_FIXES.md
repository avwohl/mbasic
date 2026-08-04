# Two CLI input bugs: termios.error and INPUT history

**Created:** 2026-08-04
**Status:** Fixed
**Found:** while triaging GitHub PR #3 (see
[MACOS_LIBEDIT_READLINE.md](MACOS_LIBEDIT_READLINE.md), which listed both as
deferred)
**Regression test:** `tests/regression/ui/test_cli_input_isolation.py`

Neither of these is macOS-specific. They were found while reading the readline
code for PR #3 and are recorded separately because they are general POSIX and
general CLI bugs.

## 1. `termios.error` is not an `OSError`

`EDIT` on piped input died:

	$ printf '10 PRINT "HI"\nEDIT 10\n\nSYSTEM\n' | python3 mbasic --ui cli
	Ready
	10?error: (25, 'Inappropriate ioctl for device')

Reading one keystroke means putting the terminal in raw mode, and
`termios.tcgetattr()` fails when stdin is a pipe or a file. The handler was
written to cope with that - it just could not, because:

	>>> issubclass(termios.error, OSError)
	False

`termios.error` is a direct subclass of `Exception`. `except OSError` never
catches "this is not a terminal", so the failure escaped as a BASIC error.

Three places do this raw-mode read, and each had drifted to its own idea of
what to catch:

- `src/interactive.py` `_read_char()` - EDIT mode. Caught `(AttributeError,
  OSError, ImportError)`. This is the one users hit. Its `ImportError` arm was
  also dead code: `import tty, termios` sat *outside* the `try`, so on Windows
  the import raised before the handler could see it.
- `src/iohandler/console.py` `input_char()` - `INPUT$`. No `try` at all.
- `src/basic_builtins.py` - `INKEY$`. Caught `(OSError, IOError)`, and `IOError`
  is merely an alias of `OSError`, so it added nothing. Guarded by an `isatty()`
  check, so this one was close to unreachable in practice.

Three copies of one idea, drifting, is what produced the bug, so the fix is one
shared tuple in `src/terminal_errors.py`:

	TERMINAL_ERRORS = (AttributeError, ValueError, OSError) + _TERMIOS_ERRORS

`ValueError` is in there because `fileno()` on a closed file raises it, which is
a third way for the setup to fail that none of the three sites covered. The
`termios` import in that module is itself guarded, so the tuple is also the one
place that has to know `termios` is POSIX-only.

Two things worth keeping in mind if this code is touched again:

- **Do not re-read in the fallback if the character was already read.** The
  restoring `tcsetattr()` runs in a `finally`, so it can fail *after* a
  successful read. Falling through to a plain read at that point consumes a
  second character and returns the wrong one. Both sites now track whether the
  read happened.
- **The failure must stay loud enough to diagnose.** The raw-mode path is
  unchanged when stdin really is a terminal - verified by comparing the full
  `termios` struct before and after, and by driving `EDIT` under a pty.

## 2. Program `INPUT` answers were recorded as commands

	10 INPUT "AGE"; A

The answer to that prompt was read with a bare `input()`. readline files
everything `input()` returns into the command history, so the answer was
recorded next to the commands the user typed and then written to
`~/.mbasic_history` on exit. Pressing Up at the `Ok` prompt scrolled back
through whatever programs had asked for - passwords included, if a program asked
for one.

Before and after, same session, from a pty:

	before:  10 INPUT "AGE"; A | 20 PRINT A | RUN | SECRET42 | SYSTEM
	after:   10 INPUT "AGE"; A | 20 PRINT A | RUN | SYSTEM

The fix is `input_without_history()` in `src/iohandler/console.py`, wrapping the
read in `readline.set_auto_history(False)` / `(True)`. That flag lives in
CPython's readline module rather than in the C library, so it behaves the same
on GNU readline and on libedit - which matters, since libedit is the whole
reason PR #3 existed.

Four sites read program input and all four now use it: `ConsoleIOHandler.input`,
two tick loops in `src/interactive.py` (`cmd_run` with a start line, and
`cmd_cont`), and one in `src/interpreter.py`.

The REPL's own command reader in `start()` is deliberately **not** changed - it
is a bare `input()` and must stay one, or command history stops working
entirely. `AUTO` mode's prompt is left alone for the same reason: it reads
program source lines, which belong in history.

`INPUT$` and `INKEY$` never reached history - they read single characters
without readline. The curses, Tk and web backends do not use readline at all.

## Verifying

	python3 tests/regression/ui/test_cli_input_isolation.py

24 checks. Against the code before the fix it reports 11 failures, naming both
bugs: `error: (25, 'Inappropriate ioctl for device')` from both raw-mode sites,
and the INPUT answer present in the history file. The pty half skips cleanly if
`pexpect` is not installed.

Two of its checks are controls that pass either way, on purpose: one pins the
premise (`termios.error` is not an `OSError`), and one asserts commands *are*
still in the history file, so an over-broad fix that disabled history altogether
would be caught.

## Not fixed here

- **The Windows import failures** noted here (`tty`/`termios` at module scope in
  `src/basic_builtins.py`, `import curses` via `src/iohandler/__init__.py`) have
  since been fixed, along with a third one nobody had spotted - see
  [WINDOWS_IMPORT_COMPATIBILITY.md](WINDOWS_IMPORT_COMPATIBILITY.md).
- **Immediate-mode `INPUT`** (`INPUT "NAME"; N$` typed at the `Ok` prompt) does
  not work: `execute_immediate()` calls the interpreter directly and never
  drives the input state machine, so the prompt prints, control returns to the
  REPL, and the user's answer is parsed as a command. The shared helper cannot
  help - the statement needs wiring into the state machine.
