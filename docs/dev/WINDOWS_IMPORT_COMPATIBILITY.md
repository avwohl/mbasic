# Windows: three bugs that stopped mbasic importing at all

**Created:** 2026-08-04
**Status:** Fixed
**Regression test:** `tests/regression/integration/test_windows_imports.py`

mbasic advertises Windows support - `Operating System :: OS Independent` in
`pyproject.toml`, a Windows section in `docs/user/INSTALL.md`, a `%APPDATA%`
settings path in the code. It could not be imported on Windows at all. Three
separate bugs, each fatal on its own.

None of them needs a Windows machine to reproduce, because none of them is
about Windows *behavior* - they are about the environment being different.

## 1. `tty` and `termios` imported at module scope

`src/basic_builtins.py` opened with:

	import tty
	import termios

Neither module exists in the Windows standard library. `INKEY$` needs them, but
only inside the branch that is skipped when `sys.platform == 'win32'`, so the
imports were paying a cost the code never intended. Importing
`src.basic_builtins` raised `ModuleNotFoundError`, and since `src.interpreter`
imports it, so did `src.interpreter`, `src.interactive`,
`src.immediate_executor` and `src.ui`. That is the whole interpreter.

Guarded now, with the names set to `None` and an explicit check in the `INKEY$`
POSIX branch. The check goes *before* `sys.stdin.isatty()` deliberately: with no
terminal layer there is no reason to touch stdin at all, and `isatty()` itself
raises on a closed or substituted stdin.

## 2. `curses` imported unconditionally by the I/O package

`src/iohandler/__init__.py` did `from .curses_io import CursesIOHandler`, and
`curses_io.py` does `import curses`. `curses` is POSIX-only in the standard
library, so importing *any* I/O handler - including the plain console one -
failed on Windows.

Guarded exactly the way `src/ui/__init__.py` already guards its optional Tk and
curses UI backends: `CursesIOHandler` becomes `None` and `_has_curses_io`
becomes `False`. Nothing in the tree consumes the package-level name, so this
costs nothing; `tests/test_breakpoint_simple.py` imports the submodule directly
and still gets a clear `ImportError`.

## 3. A shipped JSON read in the locale's codepage

This is the subtle one, and the reason it is worth writing down.

`src/ui/keybindings.py` read its config at **module scope**:

	with open(_config_path, 'r') as f:      # no encoding=
	    _config = json.load(f)

Without `encoding=`, Python decodes using the locale's preferred encoding - on
Windows the ANSI codepage. `src/ui/curses_keybindings.json` ships twelve
non-ASCII bytes: the arrows U+2191 and U+2193, as UTF-8. On any Windows whose
codepage is not UTF-8 - cp932 (Japanese), cp936, cp949, cp950, cp874 - that
decode fails:

	UnicodeDecodeError: 'cp932' codec can't decode byte 0x91 in position 2461

`UnicodeDecodeError` is a `ValueError`, **not** an `OSError`, so it also slipped
past the `except (ImportError, OSError)` guard in `src/ui/__init__.py` that
exists precisely to keep an unusable optional backend from taking down the CLI.
The result: on a Japanese Windows with urwid installed, `mbasic --ui cli` died
before printing anything.

Two fixes, because either alone leaves a trap:

- every read of a file **we ship** now names `encoding='utf-8'` - the two
  readers in `src/ui/keybindings.py` and `src/ui/keybinding_loader.py`, and the
  help-file readers in `src/ui/help_widget.py` and `src/ui/tk_help_browser.py`
  (68 of the shipped help documents contain non-ASCII);
- the guards in `src/ui/__init__.py` now catch `ValueError` too, so a data file
  that will not decode can never again take the CLI down with it.

Note `src/ui/keybinding_loader.py` wraps its read in `except Exception: pass`,
so the codepage mismatch there did not crash - it silently returned *no
keybindings at all*. Quieter, and worse.

## Reproducing without Windows

The regression test simulates both environmental differences directly:

	python3 tests/regression/integration/test_windows_imports.py

- **Missing modules:** a `sys.meta_path` hook installed through a temporary
  `sitecustomize.py` refuses `termios`, `tty`, `curses`, `fcntl`, `pty`, `grp`,
  `pwd`, `resource`, `readline` and `msvcrt`, raising `ModuleNotFoundError` the
  way Python really does.
- **Non-UTF-8 default encoding:** `LC_ALL=C` with `PYTHONUTF8=0` and
  `PYTHONCOERCECLOCALE=0` makes `open()` default to ASCII. Both of those
  variables are needed - Python otherwise coerces the C locale to C.UTF-8
  (PEP 538) or turns on UTF-8 mode (PEP 540) and the bug hides.

By hand:

	LC_ALL=C PYTHONCOERCECLOCALE=0 PYTHONUTF8=0 python3 -c "import src.ui.keybindings"

34 checks, against 18 failures on the code before the fix. It runs the real
`mbasic` under each simulation and under both at once.

**What the test does not do** is simulate Windows. `sys.platform` stays
`'linux'`, so every `if sys.platform == 'win32'` branch - the `msvcrt` paths,
the `%APPDATA%` settings directory, `cls` in `clear_screen` - is never executed.
It pins the import dimension, which is what was broken. Do not read a passing
run as "mbasic works on Windows".

## Also changed: the declared Python floor

`pyproject.toml` said `requires-python = ">=3.8"`, which was never achievable.
`src/parser.py` and `src/input_sanitizer.py` - both on the unconditional startup
path - annotate with PEP 585 builtin generics (`tuple[str, bool]`). Those are
evaluated at import time and cannot be subscripted before 3.9, and there is no
`from __future__ import annotations` anywhere in the tree. A 3.8 install would
have succeeded and then failed on first run. Now `>=3.9`, with the 3.8
classifier dropped.

## Still broken on Windows (runtime, not imports)

Fixing the imports gets mbasic to start. It does not make it work well:

- ~~**`INKEY$` and `INPUT$` swallow special keys.**~~ and ~~**`LOCATE` prints
  garbage.**~~ Both fixed - see
  [WINDOWS_CONSOLE_KEYS.md](WINDOWS_CONSOLE_KEYS.md), which also covers the
  POSIX `INKEY$` bug found underneath them.
- **No line editing or history.** `readline` is absent; `pyreadline3` is the
  usual remedy and is not offered in any extra in `pyproject.toml`.
- **`SAVE` writes CRLF and mangles high-bit program text**, because
  `src/editing/manager.py` opens user files in text mode with no `encoding=`.
  That one is deliberately untouched here: it changes how user data is written,
  and `docs/user/FILE_FORMAT_COMPATIBILITY.md` makes claims about it that need
  deciding on purpose rather than in passing.
- **The state directory is split.** `src/settings.py` correctly uses
  `%APPDATA%/mbasic`, but `src/ui/auto_save.py` and `src/ui/recent_files.py` use
  `Path.home()/'.mbasic'`.
- **`--compile-c` cannot work**: `src/codegen_backend.py` shells out to
  `/usr/bin/env`.
