# INKEY$ and INPUT$ read through the I/O handler now

**Created:** 2026-08-05
**Status:** Fixed - `src/basic_builtins.py`, `src/iohandler/base.py`,
`src/iohandler/console.py`, `src/interpreter.py`
**Regression test:** `tests/regression/interpreter/test_key_input_routing.py`

Both keyboard builtins went straight to `sys.stdin`. `BuiltinFunctions` was
built with only the runtime:

	self.builtins = BuiltinFunctions(runtime)

so no backend could intercept them, whatever handler the interpreter had been
given. Measured before the change: with a `CapturingIOHandler` whose
`input_char()` returns `""`, `INPUT$(1)` still returned a byte piped to the
process.

`IOHandler.input_char()` was the seam all along, and it was dead - three
separate comments described `ConsoleIOHandler.input_char` as "the `INPUT$`
reader" while nothing called it. This wires the builtins to it rather than
inventing anything new:

	def INKEY(self):
	    return self._io().input_char(blocking=False)

## Why INPUT$ needed a second method

`INPUT$(n)` cannot be n calls to `input_char()`. On a terminal that means
entering and leaving raw mode n times, and between two of them the terminal is
cooked again - so everything after the first character is echoed, and the read
waits for Enter before delivering it. The raw mode has to span the whole read.

So `IOHandler` gains:

	def input_chars(self, count, interrupted=None) -> str

with a concrete default that loops `input_char()`, because that is right for
every backend that has no terminal to put in a mode. `ConsoleIOHandler`
overrides it. A handler only has to know about this if it cares.

Two things are deliberately *not* in the interface:

- **Ctrl+C is returned, not interpreted.** The handler hands back `CHR$(3)`
  like any other character, and `BuiltinFunctions._raise_break` decides that it
  means a break. A backend does not need to know `BreakException` exists.
- **`interrupted` is a callback, not state.** The console read polls it to
  notice a SIGINT that arrived before the terminal was in raw mode. The
  interpreter's break flag stays in the interpreter.

## What moved

`ConsoleIOHandler` absorbed the terminal machinery from
[INPUT_DOLLAR_RAW_READ.md](INPUT_DOLLAR_RAW_READ.md) - TCSANOW, `os.read` a
byte at a time, latin-1, the cooked fallback, the Windows `isatty()` gate and
prefix/scan-code protocol, and the SIGTERM handler that puts the terminal back
if the process is killed mid-read. `input_char(blocking=True)` is now
`input_chars(1)`, so the single- and multi-character reads cannot drift apart
the way the four copies of this code did before `src/terminal_errors.py`
existed.

`basic_builtins.py` no longer imports `tty`, `termios`, `os`, `sys` or
`win_console` at all. What is left there is BASIC semantics: how many
characters, what `CHR$(3)` means, and that `INPUT$(n,#f)` is a file read.

## The handler is resolved per call

	self.builtins = BuiltinFunctions(runtime, io_provider=lambda: self.io)

A callable, not the handler, because `src/ui/curses_ui.py` assigns
`interpreter.io` *after* construction - twice, in two different places. A
builtin holding the handler it was built with would go on reading the one being
replaced. There is a test for exactly this.

## What each backend gets now

- **CLI** - unchanged, and this is the one with real behavior to preserve. All
  33 checks in `test_input_dollar_posix.py` still pass.
- **curses/urwid** and the visual UIs' immediate mode - `CapturingIOHandler`
  and `OutputCapturingIOHandler` mix in `ConsoleKeyboardMixin`, which reads the
  process's own terminal. That is precisely what the builtins were doing before
  by accident, so nothing changes; the difference is that it is now a stated
  choice in one place instead of an accident in two. It is still wrong - a
  urwid UI owns that terminal and should be handing over its own keys - but it
  is wrong on purpose and in a single overridable method. *(Since overridden:
  the curses UI passes a real keyboard, see
  [CURSES_PROGRAM_KEYBOARD.md](CURSES_PROGRAM_KEYBOARD.md). The mixin remains
  the fallback for the immediate-mode handler.)*
- **Tk** - `TkIOHandler.input_char` opens a modal "INPUT$ (Single Character)"
  dialog, written for this and unreachable until now. It already returns `""`
  for a non-blocking read, so a polling `INKEY$` does not open dialogs.
- **web (nicegui)** - `SimpleWebIOHandler.input_char` returns `""`. Previously
  these builtins read the *server's* stdin from inside the asyncio loop, which
  would have blocked every session on the machine; now they cannot.

## Verifying

	python3 tests/regression/interpreter/test_key_input_routing.py

18 checks, no pty and no terminal - the point is which object gets asked, so
stdin is replaced with one that fails the test if anything reads it. Covers
both handler shapes (`input_char` only, and `input_chars`), the short read, a
`CHR$(3)` from either shape raising `BreakException`, the handler being swapped
after construction, and `INPUT$(n,#f)` still reading its file.

	python3 tests/regression/interpreter/test_input_dollar_posix.py

The terminal behavior it all has to keep: 33 checks, unchanged by the move.

## Not fixed here

**~~No backend implements a real keyboard yet.~~** The curses UI does now -
see [CURSES_PROGRAM_KEYBOARD.md](CURSES_PROGRAM_KEYBOARD.md), which is what
this seam was for. Tk and the web UI still answer from `input_char` alone (a
modal dialog per character, and `""` respectively); each is one method away
from a real implementation, and none of it touches the interpreter.

**`WebIOHandler` and `CursesIOHandler` are still dead** (`src/iohandler/web_io.py`,
`src/iohandler/curses_io.py`) - neither is instantiated in production. They
implement `input_char`, so they would work if wired up.
