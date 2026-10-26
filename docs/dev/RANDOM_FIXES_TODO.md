# Random Fixes TODO

Collection of miscellaneous fixes and improvements identified during documentation review.

## Output Clearing

**Issue:** Need to verify all `_clear_output()` calls have been removed from all UIs

**Files to check:**
- `src/ui/curses_ui.py`
- `src/ui/tk_ui.py`
- `src/ui/web/nicegui_backend.py`
- `src/ui/cli.py`

**Goal:** Continuous scrolling output like ASR33 teletype (no auto-clearing)

**Status:** Done. No UI clears the output on its own now. Checked by reading the
code: the CLI has no clear call; curses clears only on the menu item `Clear Output`
(and replaces the output with the syntax errors while the program has some, which
is a feature of the syntax check); the web UI clears only on `Run > Clear Output`;
Tk cleared the output at RUN, LIST and NEW, and the three calls are removed. Only
the menu item `Run > Clear Output` is left in Tk.

---

## SYSTEM Command Security (Multi-User Web UI)

**Issue:** Multiple users connected to web UI - one user running SYSTEM shouldn't exit the entire server

**Old behavior:** `execute_system()` ended with `sys.exit(0)`. The web UI later got
`SandboxedFileIO.system_exit()`, which raised `IOError`, so `SYSTEM` was an error in a
web session.

**Files:**
- `src/interpreter.py` (`execute_system`)
- `src/file_io.py` (`SandboxedFileIO.system_exit`)
- `src/ui/web/nicegui_backend.py` (`cmd_system`)

**Status:** Done. In the web UI `SYSTEM` prints `Goodbye` and halts the program of
that session only (the pc is halted and `CONT` does nothing). The server and the
other sessions are not touched. The CLI, curses and Tk UIs still exit the process.
Tests: `tests/regression/ui/test_web_immediate_commands.py` (a mock replaces `nicegui`).
Not fixed, found on the way: `File > Exit` in the web UI calls `app.shutdown()`, which
stops the whole server (see `docs/dev/WEB_UI_NICEGUI_BACKEND.md`).

---

## Consolidate cmd_ Functions Across UIs

**Status:** Open. This is a refactor and not a bug, so it was left alone.

**Issue:** All UIs have their own `cmd_` function implementations for things like LIST that could be done in a program. Implementation should be common, with UI-specific hooks if needed for updates.

**Files with cmd_ functions:**
- `src/ui/curses_ui.py`
- `src/ui/tk_ui.py`
- `src/ui/web/nicegui_backend.py`
- `src/ui/cli.py`
- `src/interactive.py` (base implementations)

**Problems:**
- Duplicated logic across UIs
- Inconsistent behavior
- Hard to maintain

**Proposal:**
- Move common cmd_ logic to shared location (interactive.py or new module)
- UIs provide hooks for UI updates (refresh display, etc.)
- UI-specific code only handles visual updates, not logic

**Examples of commands to consolidate:**
- LIST
- DELETE
- RENUM
- FILES
- SAVE
- LOAD
- MERGE
- NEW

---

## CLI LIST Command Does Nothing

**Issue:** In CLI UI, the LIST command does nothing (no output)

**File:** `src/ui/cli.py`

**Expected:** Should list the program like other UIs

**Current:** Silent failure or no implementation

**Status:** Not a bug. `LIST` in `python3 mbasic --ui cli` prints the program (tested
by typing two lines and `LIST`). No change.

**Related:** Part of cmd_ consolidation issue above

---

## Notes

These issues were identified during docs_inconsistencies_report-v12 review on 2025-11-07.

Priority: Medium - not blocking, but affects UX and maintainability

---

## Web UI Guide Is Out of Date

**Issue:** `docs/dev/WEB_UI_NICEGUI_BACKEND.md` (moved out of `src/ui/web/README.md` on 2026-09-30) still describes an early web UI. For example, the guide says INPUT is a placeholder and that programs using INPUT hang. The guide is built into the published docs site.

**Files:**
- `docs/dev/WEB_UI_NICEGUI_BACKEND.md`
- `src/ui/web/nicegui_backend.py` (the current behaviour to check the guide against)

**Goal:** Check each status claim in the guide against the code and update the guide, or mark the guide as historical and move the guide to `docs/history/`.

**Status:** Done. The guide was rewritten from the current code: INPUT works inline,
the editor holds the whole program, and File, Edit, Run, Debug and Help menus,
the debugger and the immediate line exist. The guide also lists what is still
true: Recent Files is not restored after a reload, and `File > Exit` stops the
server.
