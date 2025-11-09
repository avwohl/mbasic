# Docs-v17 False Positives and Already Correct Issues

Generated: 2025-11-09
Source: docs/history/docs-v17.md processing

This document tracks issues from docs-v17.md that were false positives or already correct in the codebase.

---

## False Positives (Documentation Was Already Correct)

### Settings widget keybindings not documented in JSON
**Issue #79**
**File:** `src/ui/curses_settings_widget.py`, `src/ui/curses_keybindings.json`
**Report Claimed:** Widget implements ESC, ENTER, Apply, Reset keys but curses_keybindings.json has no settings entries
**Reality:** Dialog-specific keys are intentionally hardcoded in keybindings.py (Python constants) and documented in code comments, not in JSON file. This is by design - the JSON is for main UI keybindings, not widget-internal navigation.
**Status:** No change needed - intentional design

### Broken internal documentation links
**Issue #290**
**Files:** `docs/help/index.md`, `docs/help/common/ui/cli/index.md`, etc.
**Report Claimed:** Multiple references to non-existent files (edit.md, auto.md, delete.md, renum.md)
**Reality:** All links verified to be correct - issue was a false positive
**Status:** No change needed - links are correct

### Variable inspection methods contradiction
**Issue #332**
**Files:** `docs/help/ui/curses/variables.md`, `docs/help/ui/cli/variables.md`
**Report Claimed:** Variables Window described as Curses-only but CLI doc mentions it too
**Reality:** Documentation correctly states CLI doesn't have Variables Window while Curses does. The CLI variables.md file describes the VARS command (different from Variables Window).
**Status:** No change needed - documentation is correct

### Toolbar buttons documentation contradictory
**Issue #420**
**Files:** `docs/help/ui/web/getting-started.md`, `docs/help/ui/web/web-interface.md`
**Report Claimed:** getting-started lists toolbar, web-interface doesn't mention it
**Reality:** Both documents consistently describe the toolbar with Run, Stop, Step, Stmt, Cont buttons
**Status:** No change needed - documentation is consistent

---

## No Change Needed (Working As Intended)

### Multiple keybinding systems with unclear relationships
**Issue #171**
**Status:** FIXED by creating comprehensive documentation in docs/dev/KEYBINDING_SYSTEMS.md
**Note:** Not a false positive - documentation was missing but now added

### Module docstring describes two scopes but three implemented
**File:** `src/settings.py`
**Report Claimed:** Docstring mentions global and project, but FILE scope exists in code
**Reality:** FILE scope is reserved for future use and intentionally not documented yet
**Status:** Fixed in docs-v17 processing - added note that FILE scope is reserved

---

## Already Fixed in Previous Sessions

### DEFINT example shows incorrect type mismatch
**File:** `docs/help/common/language/statements/defint-sng-dbl-str.md`
**Report Claimed:** Comment says AMOUNT is string variable but assigns numeric 100
**Reality:** Already fixed in previous session - now uses "100" (string)
**Status:** Already resolved

### STACK command not in keybindings
**Files:** `src/ui/cli_debug.py`, `src/ui/cli_keybindings.json`
**Report Claimed:** cmd_stack() implemented but not in JSON
**Reality:** Already added in previous session (lines 68-72 of cli_keybindings.json)
**Status:** Already resolved

---

## Summary

- **False Positives:** 4 issues where documentation was already correct
- **No Change Needed:** 2 issues working as intended (1 fixed with new docs)
- **Already Fixed:** 2 issues resolved in previous sessions

**Total outdated issues:** 8 out of ~300 issues in docs-v17.md

These issues should be ignored in future consistency checks.
