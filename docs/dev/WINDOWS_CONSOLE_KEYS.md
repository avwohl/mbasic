# Windows key decoding, LOCATE, and the POSIX bug found underneath them

**Created:** 2026-08-04
**Status:** Fixed
**Code:** `src/win_console.py`
**Regression tests:** `tests/regression/ui/test_win_console.py`,
`tests/regression/interpreter/test_inkey_posix.py`

Three things, in ascending order of how much they mattered.

## 1. INKEY$ on POSIX could not read a key at all

This is the one that affected real users on the platform mbasic is developed on,
and it was found only while researching the Windows half.

`INKEY$` used `select()` to check for a keystroke and then:

	tty.setraw(fd)                # TCSAFLUSH by default
	char = sys.stdin.read(1)

Both lines are wrong, and each is sufficient on its own to break it:

- `tty.setraw()` defaults to **`TCSAFLUSH`**, documented as "all input that has
  been received but not read will be discarded before the change is made" -
  which is precisely the keystroke `select()` had just reported.
- `sys.stdin.read(1)` goes through a `TextIOWrapper`, which pulls **every**
  available byte into its own decode buffer. The kernel queue empties, so the
  next `select()` reports "no key" while the rest of an escape sequence sits
  invisible in userspace.

Together they did not merely lose the key - they **hung the interpreter**. The
flush threw the bytes away, then the buffered read blocked forever waiting for
a character that no longer existed. Measured under a pty with `ICANON` off:
*any* keypress, arrow or plain letter, never returned.

Fixed with `TCSANOW` and `os.read()`, decoded `latin-1` so a byte is a byte.
`TCSANOW` rather than `TCSADRAIN` because the latter blocks until the output
queue drains, which is wrong inside a poll that is contractually non-blocking.

An arrow key now arrives as the three characters the terminal actually sent -
`CHR$(27)`, `"["`, `"A"` - one per call. That is confirmed to be what **real
MBASIC 5.21 does**: driven under `cpmemu`, the original `mbasic.com` returns
`ASC` 27, 91, 65 on three successive `INKEY$` calls with `LEN(A$)=1` each time.

Still true, and untouched: raw mode is entered only *after* `select()` reports
data and dropped again immediately, so the tty is canonical between polls. A
bare `10 A$=INKEY$: IF A$="" THEN 10` still sees nothing until Enter unless
something else has put the terminal in cbreak. That is a separate, older
limitation.

## 2. Windows key decoding

Three sites did:

	msvcrt.getch().decode('utf-8', errors='ignore')

Windows delivers a special key as **two** `getch()` calls: a prefix byte
(`0x00` or `0xE0`) then a scan code. `0xE0` is not valid UTF-8, so
`errors='ignore'` produced `""` - `INKEY$` reported "no key" having already
eaten the prefix, and the scan code surfaced as a letter on the next call. Up
arrow looked like `"H"`.

`src/win_console.py` now resolves the pair and returns the same escape sequence
a POSIX terminal would send, one character per call - so `INKEY$` behaves
identically on both platforms and `LEN(INKEY$)` stays 0 or 1, which is what
MBASIC 5.21 requires (`bistrs.mac` hardcodes the result length to one).

Three findings worth keeping, all from the UCRT sources:

**Do not use `getwch()`.** It looks like the obvious fix for the codepage
problem, and it is a trap. Its pushback buffer is a `static wint_t wchbuf` in
`ucrt/conio/getwch.cpp`, a *different translation unit* from the buffer
`_kbhit_nolock` peeks. So after `getwch()` returns a prefix, `kbhit()` reports
**false** with the scan code still pending, and that scan code leaks out of the
next call - reintroducing the very desync being fixed. `getch()`'s pushback
*is* the buffer `kbhit()` checks, which is what makes the gated second read
safe and non-blocking.

**Key on the (prefix, scan code) pair, not the scan code.** The two number
spaces are not disjoint. From the dispatch tables, Ctrl+PgUp is `(0xE0, 134)`
and F12 is *also* `(0xE0, 134)` - genuinely indistinguishable at this API, so
F12 wins. Keying on the scan code alone would additionally have decoded stray
bytes as navigation keys.

**A blocking read must not return `""` for a key it cannot express.**
Ctrl+Left has no terminal equivalent. Returning `""` for it looked harmless
until you notice `ConsoleIOHandler.input_char` reads `""` from a *blocking*
read as "there is no console" and degrades to line `input()`. A blocking read
now loops, and `""` from it means only "no console".

## 3. LOCATE

`ConsoleIOHandler.locate()` printed the ANSI cursor escape unconditionally.
Windows conhost does not interpret ANSI without
`ENABLE_VIRTUAL_TERMINAL_PROCESSING`, so it appeared as literal garbage -
while `clear_screen()` directly below it did branch on the platform.

`win_locate()` now enables VT processing once per process (cached, building on
the existing mode so other flags survive, and reading the mode back rather than
trusting the return value) and reports whether the escape can be written.
POSIX gained an `isatty()` guard: a cursor escape written into a redirected
file is corruption of the output, not cursor control.

**`LOCATE` is not a statement this interpreter supports** - the parser rejects
it, and nothing calls `io.locate()`. Real MBASIC 5.21 answers `Syntax error`
too. This fix is about the `IOHandler` contract being correct, not about a live
user-visible bug.

Deliberately **not** implemented: the `SetConsoleCursorPosition` fallback for
Windows 8 and pre-1511 Windows 10. It needs a `COORD` passed by value and three
independent coordinate conversions (1-based to 0-based, row/column order,
viewport-relative to buffer-absolute), none of which can be exercised without a
Windows machine - and a fake can only prove that the fake agrees with itself.
Without it, down-level Windows gets "the cursor does not move", which is still
better than literal garbage.

## What the tests do and do not prove

	python3 tests/regression/ui/test_win_console.py        # 37 checks
	python3 tests/regression/interpreter/test_inkey_posix.py   # 11 checks

The Windows tests inject a fake `msvcrt` modelled on the UCRT pushback
behaviour and a fake `kernel32` seeded into the api cache, and the last group
patches `sys.platform` so the real call sites execute - without that group the
suite stayed green against a tree where the fix was never wired in.

The POSIX tests are real: a `pty`, a real arrow key, the real `INKEY$`.

**Shipping with zero coverage, because it cannot be had here:** the entire
ctypes/kernel32 binding block (so argtypes and handle widths on 64-bit are
unverified); `msvcrt.get_osfhandle`; whether conhost actually moves the cursor
once VT is on; real scan codes from real hardware; DBCS and `chcp 65001`
consoles; Ctrl+C arriving as `0x03` versus `KeyboardInterrupt`; ConPTY versus
legacy conhost; and `pythonw.exe`.

## Known limitations on Windows

- **Multi-byte console codepages confuse the prefix test.** The UCRT pushes
  bytes 2..n of a multi-byte character into the *same* buffer `kbhit()` peeks,
  so on a DBCS or UTF-8 console a lead byte of `0x00`/`0xE0` is
  indistinguishable from a key prefix. An unmapped pair is now handed back as
  its two bytes rather than dropped, so nothing is lost silently, but a Shift-JIS
  character whose bytes happen to be `E0 48` will still read as an Up arrow.
  Fixing this properly means `ReadConsoleInputW` instead of `getch()`.
- **`ENABLE_VIRTUAL_TERMINAL_PROCESSING` is not restored on exit.** The mode
  belongs to the inherited console screen buffer, so it outlives the process.
  Benign on Windows 10+, but it is an unrestored global side effect.
- **Redirected stdin does not feed `INKEY$`.** `kbhit`/`getch` open `CONIN$`
  directly and are structurally blind to redirection, so `mbasic < prog.txt`
  reads the physical keyboard on Windows where POSIX returns `""`.
- **`src/interactive.py` `_read_char()`** (EDIT mode) still uses the
  `TCSAFLUSH` default. Being a blocking read it does not hang, but type-ahead
  is discarded. Left alone as a separate change.
