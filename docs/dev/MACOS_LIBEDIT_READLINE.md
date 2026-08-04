# macOS libedit and the CLI history file

**Created:** 2026-08-04
**Status:** Fixed - `src/interactive.py`, `_setup_readline()`
**Reported by:** rolandkirsche, GitHub PR #3
**Regression test:** `tests/regression/ui/test_cli_readline_history.py`

`mbasic --ui cli` crashed at startup on macOS with:

	PermissionError: [Errno 1] Operation not permitted: '/Users/.../.mbasic_history'

on a file the user owned, mode 0600 - and it kept crashing on a file that
`readline.write_history_file()` had just written moments earlier in the same
process. That is not a permission problem at all, and the reason matters enough
that it is written down here: the obvious "clean up" of the fix reintroduces the
crash.

## Why it happens

Python's `readline` module is a thin wrapper over whichever C library the
interpreter was built against. macOS system Python (Xcode Command Line Tools)
links **libedit**, not GNU readline. The two do not agree on what
`read_history()` returns.

CPython's `Modules/readline.c` treats the return value as an errno - identical
code in every version from 3.8 through 3.14:

	errno = read_history(PyBytes_AS_STRING(filename_bytes));
	if (errno)
	    return PyErr_SetFromErrno(PyExc_OSError);

GNU readline honours that contract: 0, or a real errno from `open`/`read`.
Apple's libedit does not. It is a 2012 NetBSD snapshot - the file header reads
`$NetBSD: readline.c,v 1.106 2012/10/12 23:35:02 christos Exp $` - and its
`read_history()` ends:

	return (!(history_length > 0));	/* return 0 if all is okay */

It returns a **boolean "loaded nothing" flag**. So a history file that reads
perfectly but holds zero entries returns 1, CPython assigns 1 to `errno`, and
Python renders `EPERM` as `PermissionError: [Errno 1] Operation not permitted`.

That explains the write-then-fail-to-read sequence exactly, and it was
self-inflicted: libedit's `write_history()` on an empty history writes a
13-byte file containing just `_HiStOrY_V2_\n`. A session in which the user
typed nothing produced exactly that file, and the next run choked on it. Run
mbasic, type nothing, quit, run it again - that was the repro.

A second libedit path produces a similar symptom by a different route:
`history_load()` returns -1 when the file does not begin with the magic line
`_HiStOrY_V2_`, and Apple's `read_history()` does not clear `errno` first, so it
returns whatever stale errno was lying around - measured as `EINVAL` (22) for an
empty file and for a GNU-format cookie-less one, but it is genuinely whatever
was left over. A history file written by a GNU-readline Python and then read by
a libedit one lands here.

**Both defects are fixed in current upstream libedit** - NetBSD trunk now clears
`errno` before the load and ends with `return 0;` - and the fix is live in, for
instance, Debian's libedit 3.1-20251016, where a zero-entry history file reads
back cleanly. Apple still ships the 2012 code. So this is a bug in *Apple's*
libedit, not in libedit, and a future reader who checks upstream will find
working source.

## What the fix does, and what must not be "simplified"

**1. The read catches `OSError`, not just `FileNotFoundError`.**
Do not narrow this back. `FileNotFoundError` alone is insufficient even on
Linux with GNU readline: a *directory* at `~/.mbasic_history` raises a bare
`OSError [Errno 22]` (not `IsADirectoryError` - GNU rejects non-regular files
before it ever reads them), which crashed startup here too. Enumerating
subclasses does not work either, because libedit's errno is arbitrary. Only the
`OSError` base class covers the space. Both handlers are kept because the order
is load-bearing and the split documents "first run" versus "something is wrong";
`FileNotFoundError` is itself an `OSError` subclass.

**2. The exit-time save is guarded, and is no longer a bare `atexit.register`.**
`write_history_file()` fails the same ways the read does. An exception escaping
an `atexit` callback prints

	Exception ignored in atexit callback <built-in function write_history_file>:
	PermissionError: [Errno 13] Permission denied

after the user has already typed `SYSTEM`. Reproduced on Linux with a read-only
`$HOME`. Fixing only the read would have moved the traceback from startup to
exit rather than removing it. CPython's own `site.py` guards this same call.
The handler catches `Exception`, not just `OSError`, on the principle that an
`atexit` hook has no business raising anything at all.

**3. Nothing is written when there is nothing to save.**
`write_history_file()` rewrites the file wholesale from the in-memory list, so a
failed read followed by a successful write would destroy a history file we
merely could not parse. The save is skipped when the in-memory history is empty,
which covers that and one more thing: it stops mbasic manufacturing the empty
history file that trips libedit on the next run. Piping a program into
`--ui cli` used to leave a 0-byte `~/.mbasic_history` behind; now it leaves
nothing. Once the user has actually typed commands the file is written and, on
macOS, self-heals into a format libedit can read.

What is *not* preserved: a GNU-format history read on a libedit Python fails,
and the first command the user types will overwrite it in libedit format. You
cannot keep what you cannot read, and every other libedit application behaves
the same way - but someone alternating between Homebrew python and
`/usr/bin/python3` may notice.

**4. `parse_and_bind()` speaks two different languages.**
GNU readline takes inputrc syntax; libedit takes `editrc(5)` syntax. Each
silently ignores the other's strings - no exception, no return value, the
binding simply never happens. (Return codes are useless for detecting this:
libedit returns "success" for `tab: complete` because the colon makes it look
like a program-name prefix.) So on macOS `'Control-a: self-insert'` had never
done anything, and the `^A` EDIT-mode key the startup banner advertises was
dead on that platform. The backend is detected once and the equivalent editrc
commands are issued instead:

	bind -e
	bind ^I rl_complete
	bind ^A ed-insert

`ed-insert` is libedit's spelling of `self-insert`; it inserts the character
that triggered the binding, so `^A` puts a real 0x01 in the buffer and the
`line[0] == '\x01'` test in `start()` sees what it expects.

Two ordering traps, both pinned by the regression test:

- **`bind -e` must come first.** It calls `map_init_emacs()`, a full keymap
  reinitialization; anything bound before it is discarded.
- **`bind ^I rl_complete` is required, not belt-and-braces.** Tab completion
  was in fact *already working* on macOS, because libedit's own
  `rl_initialize()` binds `^I` to `rl_complete` at import time. But `bind -e`
  wipes that. Dropping or reordering that line would take macOS Tab completion
  from working to broken.

On the GNU side, `set editing-mode emacs` likewise moved ahead of
`tab: complete` for the same reason. That is a small fix in its own right: with
`set editing-mode vi` in a user's `~/.inputrc`, the old order bound Tab into the
vi keymap and then switched away from it, so Tab inserted a literal tab.

Detection is `readline.backend` (Python 3.13+) falling back to a `libedit`
substring test on `readline.__doc__`, which is the documented pre-3.13 method
and the one that actually runs on macOS system Python (3.9). The `or ''` guard
is there because a non-CPython or pure-Python `readline` shim can have no
docstring - *not* because of `python -OO`, which strips docstrings from Python
bytecode but not from a C extension's.

## Verifying

	python3 tests/regression/ui/test_cli_readline_history.py

The test installs a fake `readline` module in `sys.modules` - `_setup_readline()`
does a function-local `import readline`, which resolves at call time - so every
libedit failure mode is reproducible on Linux. On the code before the fix it
reports 16 failures; after, 34 checks pass.

One failure mode reproduces end to end without a Mac. This used to exit 1 with
an `OSError [Errno 22]` traceback and now prints `Goodbye` and exits 0:

	H=$(mktemp -d); mkdir "$H/.mbasic_history"
	printf 'PRINT "HI"\nSYSTEM\n' | HOME="$H" python3 mbasic --ui cli

The read-only `$HOME` case shows the `atexit` half of the fix - the
`Exception ignored in atexit callback` line disappears - but it is not a clean
run either way, because mbasic separately fails to create its `~/.mbasic`
settings directory:

	H=$(mktemp -d); chmod 500 "$H"
	printf 'PRINT "HI"\nSYSTEM\n' | HOME="$H" python3 mbasic --ui cli

Read failures are reported through `debug_log()`, so they are visible with
`MBASIC_DEBUG=1` instead of being invisible.

## Not fixed here

Which Python you install on macOS decides whether any of this applies:
Homebrew's python links GNU readline, pyenv does when Homebrew's readline is
present at build time, and Apple's system Python does not. Nothing above changes
that - it makes mbasic behave on either.

Left alone deliberately, and worth separate reports:

- `src/interactive.py` `_read_char()` catches `(AttributeError, OSError,
  ImportError)` and its comment claims that covers `termios.error`. It does not:
  `issubclass(termios.error, OSError)` is `False`.
- Program `INPUT` responses go through a bare `input()` in
  `src/iohandler/console.py`, so they are recorded in `~/.mbasic_history`
  alongside commands. `readline.set_auto_history(False)` around those reads is
  the fix.
- A read-only `$HOME` still produces a `?PermissionError` for the `~/.mbasic`
  settings directory, unrelated to history.
