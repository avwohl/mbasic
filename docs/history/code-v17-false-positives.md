# Code-v17 False Positives and Already Resolved Issues

Generated: 2025-11-09
Source: docs/history/code-v17.md

This document tracks issues from code-v17.md that were false positives or already resolved in the codebase.

---

## False Positives (Report was Incorrect)

### Inconsistent cursor positioning after delete line
**File:** `src/ui/curses_ui.py` _delete_current_line()
**Report Claimed:** Comment says "Always position at column 1" but else branch positions at end of previous line
**Reality:** The comment (lines 2309-2311) accurately describes the behavior:
```python
# Position cursor intelligently after deletion:
# - If not at last line: position at column 1 of the line that moved up
# - If was last line: position at end of the new last line
```
**Status:** No issue exists - comment matches code exactly

### Inconsistent code_start position handling
**File:** `src/ui/curses_ui.py` multiple methods
**Report Claimed:** _insert_line_after_current() hardcodes column 7, _toggle_breakpoint_current_line() uses both _parse_line_number AND hardcoded 7
**Reality:** Code correctly uses _parse_line_number() with defensive fallback:
- Line 2448: `_, code_start = self.editor._parse_line_number(lines[line_index])`
- Line 2450: `code_start = 7  # Fallback to column 7 if parsing fails`
- Line 2612: `code_area = line[code_start:]` (uses parsed value)
**Status:** No issue exists - code is already correct

### _refresh_editor() referenced but not defined
**File:** `src/ui/curses_ui.py`
**Report Claimed:** _refresh_editor() is referenced in cmd_delete and cmd_renum but not defined
**Reality:** _refresh_editor() IS defined at line 1496
**Status:** No issue exists - method exists and is properly defined

### _on_status_click() uses different regex than _parse_line_number()
**File:** `src/ui/tk_widgets.py`
**Report Claimed:** Two different patterns could cause inconsistent behavior
**Reality:** Already fixed in working tree (not yet committed at time of report)
**Status:** Already resolved

---

## No Change Needed (Working As Intended)

### Context menu dismiss binding may not work as intended
**File:** `src/ui/tk_help_browser.py` lines 645-658
**Report Claimed:** tk.Menu <FocusOut> and <Escape> bindings may not trigger reliably
**Reality:** Code comment (line 736) correctly explains that tk_popup() handles dismissal automatically and explicit bindings are unreliable
**Status:** Code and documentation are correct - no change needed

### Web help launcher open_help_in_browser() doesn't add .html extension
**File:** `src/ui/web_help_launcher.py`
**Report Claimed:** Migration guide says add .html but function doesn't
**Reality:** Migration guide explicitly says to use directory-style URLs (/path/) NOT .html files. Code correctly implements this (line 79)
**Status:** Code and documentation are consistent - no change needed

---

## Already Removed from Codebase

### identifier_table unused code
**File:** `src/case_string_handler.py`
**Report Claimed:** get_identifier_table() is implemented but comment says "not currently used"
**Reality:** The get_identifier_table() method has already been removed from the codebase
**Status:** Already resolved - issue is outdated

### _create_toolbar UNUSED method
**File:** `src/ui/curses_ui.py`
**Report Claimed:** Says "Can be safely removed if no plans to restore"
**Reality:** _create_toolbar() method does NOT exist in curses_ui.py - already removed
**Note:** Method still exists and is actively used in tk_ui.py (which is correct)
**Status:** Already resolved - issue is outdated

---

## Summary

- **False Positives:** 4 issues where the report was incorrect
- **No Change Needed:** 2 issues working as intended
- **Already Resolved:** 2 issues already fixed in codebase

**Total outdated issues:** 8 out of ~40 issues in code-v17.md

These issues should be ignored in future consistency checks.
