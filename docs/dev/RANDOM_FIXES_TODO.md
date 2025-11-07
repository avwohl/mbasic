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

**Status:** Partially done - web UI cleared, need to verify others

---

## SYSTEM Command Security (Multi-User Web UI)

**Issue:** Multiple users connected to web UI - one user running SYSTEM shouldn't exit the entire server

**Current behavior:** `execute_system()` in `src/interpreter.py` line 2007 calls `sys.exit(0)` which would kill the entire server

**Files:**
- `src/interpreter.py` (line 2007-2014)
- `src/ui/web/nicegui_backend.py`

**Fix needed:**
- Web UI should disconnect/reset session, not exit server
- Only CLI/Curses/Tk should actually exit the process
- Need session-level isolation for SYSTEM command

---

## Consolidate cmd_ Functions Across UIs

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

**Related:** Part of cmd_ consolidation issue above

---

## Notes

These issues were identified during docs_inconsistencies_report-v12 review on 2025-11-07.

Priority: Medium - not blocking, but affects UX and maintainability
