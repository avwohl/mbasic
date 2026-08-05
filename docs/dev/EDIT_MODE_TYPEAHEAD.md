# EDIT mode discarded type-ahead, and hung

**Created:** 2026-08-04
**Status:** Fixed - `src/interactive.py`, `_read_char()` and `cmd_edit()`
**Regression test:** `tests/regression/editor/test_edit_typeahead.py`

The third and last of the raw-mode readers, after `INKEY$` and
`ConsoleIOHandler.input_char` (see
[WINDOWS_CONSOLE_KEYS.md](WINDOWS_CONSOLE_KEYS.md)). `_read_char()` is the
per-keystroke reader for `EDIT`, and it did:

	tty.setraw(fd)              # TCSAFLUSH by default
	ch = sys.stdin.read(1)

`TCSAFLUSH` discards input that has arrived but has not been read. Since this
runs **once per keystroke** rather than once at entry, everything typed between
two calls - while the previous character was being processed and echoed - was
thrown away.

It was recorded as "type-ahead is discarded; being a blocking read it does not
hang." **That was wrong.** Measured under a pty with `ICANON`/`ECHO` cleared:
type `ABCDE` in one burst, then read five characters, and the reader never
returned at all. The flush discarded the five queued bytes and the read then
waited forever for a character that no longer existed. A single typed-ahead
character was enough. End to end, `mbasic --ui cli` fed a pasted
`10 PRINT "HI"` / `EDIT 10` / `  D` burst prints the `10` EDIT prompt and hangs
until killed.

Fixed the same way as the other two: `tty.setraw(fd, termios.TCSANOW)` and
`os.read(fd, 1)` decoded `latin-1`. All five characters now arrive in order.

`latin-1` matters here specifically: `EDIT` is driven by control characters and
its entry key is `^A` (0x01), so the reader must be byte-transparent. Every
comparison in the edit loop (`\r`, `\n`, space, `D I X H E Q L A C`) and in
`_read_until_escape` (`ESC`, `$`, `\x7f`, `\x08`) is ASCII, so splitting a
multi-byte character into bytes cannot fabricate a command - no trail byte of
UTF-8, Shift-JIS, Big5 or GBK is `0x24` or `0x1B`, and no high byte upper-cases
into an EDIT command letter.

## The second-order bug the fix exposed

Removing the flush revealed something it had been masking. `<CR>` is EDIT's
"save and exit" subcommand, and the terminator that submitted the `EDIT 10`
command line could still be queued when the edit loop started. So EDIT exited
immediately without editing, and the keystrokes meant for it fell through to the
REPL as commands:

	EDIT 10
	10PRINT "HI"
	?Parse error at line 1, column 3: Unknown statement or command: 'd'

This needs `\r\n` to reach the terminal - a paste, `pexpect`, `tmux send-keys` -
because `ICRNL` turns the CR into a second newline and readline consumes only
the first. A human pressing Enter once never sees it.

`cmd_edit()` now calls `_drop_leftover_newline()` at entry, which takes **at
most one byte, only if something is already queued, and keeps it unless it
really is a terminator** - a non-terminator is handed to the next `_read_char()`
through a one-character pushback rather than being eaten. Discarding input is
the bug being fixed; the cure must not reintroduce it in miniature.

Do not "simplify" this back into a flush inside the reader. A per-keystroke
flush is what caused the hang.

## Verifying

	python3 tests/regression/editor/test_edit_typeahead.py

8 checks: type-ahead delivery, `^A`/ESC byte transparency, high bytes, and one
end-to-end pty run of the real EDIT loop driven entirely with CRLF. Against the
code before the fix it reports 3 failures in ~16s - it fails rather than hanging
the runner, because the harness uses `select()` with a deadline instead of a
bare `os.read` on the pty master.

The non-tty paths of this same reader are covered separately by
`tests/regression/ui/test_cli_input_isolation.py`, so the piped case is not
repeated here.

## Still open

`BuiltinFunctions.INPUT` (`INPUT$` from the keyboard,
`src/basic_builtins.py`) is now the only stdin reader still using
`sys.stdin.read(1)`. Two separate problems, neither fixed here:

- It has **no raw mode at all**, so `INPUT$(1)` waits for Enter instead of
  returning on the first keystroke.
- More importantly, the `TextIOWrapper` drains the whole kernel queue into
  userspace, where the other three readers - all now on `os.read` - and
  readline cannot see it. Measured: after `INPUT$(1)` returned `A` from a typed
  `AB`, `FIONREAD` on the fd was 0, and the stranded `B` reappeared two commands
  later as if it had just been typed.

Fixing that means changing how a BASIC statement reads its input, which deserves
its own decision rather than being folded into a terminal-mode fix.
