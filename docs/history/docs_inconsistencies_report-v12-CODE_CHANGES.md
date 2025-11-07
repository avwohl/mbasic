# Code Changes - Inconsistencies Report v12

**Generated from:** docs_inconsistencies_report-v12.md
**Date:** 2025-11-07
**Total Issues:** 22

⚠️ **WARNING:** These are issues where the **CODE should be changed** (not the documentation).
**REQUIRES HUMAN REVIEW** before implementing to avoid reimplementing removed code.

---

## High Severity Code Changes (8 issues)

### 1. ⚠️ UI integration contract validation
**Files:** `src/immediate_executor.py`
**Issue:** Cannot verify if UI provides required methods; potential integration violations
**Lines:** 103-169
**Details:**
- Comment describes UI integration requirements:
  - `interpreter.interactive_mode` must reference UI object
  - `UI.program` must have `add_line()` and `delete_line()` methods
  - `UI._refresh_editor()` and `UI._highlight_current_statement()` optional
- Code implements checks but without UI code files, cannot verify contract is met
- Risk: Integration may be violated in practice

**Recommended Fix:** Verify UI implementations provide required interface, add integration tests

---

### 2. ⚠️ CONT after line edits may crash
**Files:** `src/interactive.py`
**Issue:** `process_line()` doesn't call `clear_execution_state()` but CONT expects it
**Lines:** 186-207, 289-299
**Details:**
- CONT docstring (lines 289-299): "CONT will fail with '?Can't continue' if the program has been edited because editing clears the GOSUB/RETURN and FOR/NEXT stacks"
- But `process_line()` adds/deletes lines WITHOUT calling `clear_execution_state()`:
  - Line 195: `del self.lines[line_num]` (no clear)
  - Line 203: `self.line_asts[line_num] = line_ast` (no clear)
- Only `cmd_new()` and `cmd_renum()` call `clear_execution_state()`
- Risk: CONT could crash with invalid return addresses after line edits

**Recommended Fix:**
```python
# In process_line(), after modifying lines:
if line_num in self.lines:
    del self.lines[line_num]
    self.clear_execution_state()  # ADD THIS
```

---

### 3. ⚠️ FOR loop malformed handling creates dummy variable
**Files:** `src/parser.py`
**Issue:** Creates dummy variable 'I' without warning, could silently corrupt programs
**Details:**
- When FOR loop variable is malformed, parser creates `VariableNode("I", TypeInfo.INTEGER)`
- No error message, warning, or indication to user
- Could silently change program behavior

**Recommended Fix:** Raise parse error instead of creating dummy variable

---

### 4. ⚠️ cmd_delete/cmd_renum missing _sync_program_to_runtime
**Files:** `src/ui/curses_ui.py`
**Issue:** Runtime out of sync after these commands
**Details:**
- Comments claim sync occurs automatically
- Timing analysis shows sync happens BEFORE command, not after
- After delete/renum, runtime may have stale line references

**Recommended Fix:** Call `_sync_program_to_runtime()` after delete/renum operations

---

### 5. ⚠️ QUIT_ALT_KEY semantic error
**Files:** `src/ui/keybindings.py`
**Issue:** Loads from wrong JSON key ('editor.continue' instead of quit-related key)
**Details:**
- `QUIT_ALT_KEY` loads from `'editor.continue'` JSON key
- Semantic mismatch - quit key loading from continue configuration

**Recommended Fix:** Create proper quit JSON key or document the intentional mapping

---

### 6. ⚠️ 'not self.running' check redundant
**Files:** `src/ui/tk_ui.py`
**Issue:** Either `can_execute_immediate()` is insufficient or check is redundant
**Details:**
- Code checks both `can_execute_immediate()` and `not self.running`
- Suggests either:
  - `can_execute_immediate()` doesn't check running state (bug)
  - Redundant check (code smell)

**Recommended Fix:** Investigate and remove redundancy or fix `can_execute_immediate()`

---

### 7. ⚠️ Empty program inconsistent handling
**Files:** `src/ui/web/nicegui_backend.py`
**Issue:** RUN doesn't clear output but STEP does
**Details:**
- When program is empty:
  - RUN: Does not clear output
  - STEP: Clears output
- Inconsistent user experience

**Recommended Fix:** Make behavior consistent (both don't clear)

---

### 8. ⚠️ Inconsistent command key documentation
**Files:** `docs/help/common/debugging.md`, `docs/help/common/editor-commands.md`
**Issue:** Need to determine correct shortcuts
**Details:**
- Different keyboard shortcuts documented in different places
- Can't determine which is actually implemented

**Recommended Fix:** Verify actual implementation and update all docs consistently

---

## Medium Severity Code Changes (9 issues)

### 9. Step command behavior inconsistent
**Files:** `src/ui/auto_save.py`, `src/ui/cli_debug.py`, `src/ui/curses_keybindings.json`
**Issue:** Inconsistent granularity implementation across UIs
**Recommended Fix:** Standardize step behavior (line vs statement)

---

### 10. CapturingIOHandler duplication
**Files:** `src/ui/curses_ui.py`
**Issue:** Should extract to shared location
**Recommended Fix:** Extract to `src/ui/capturing_io_handler.py` or similar

---

### 11. HelpMacros and KeybindingLoader duplication
**Files:** `src/ui/help_macros.py`, `src/ui/keybinding_loader.py`
**Issue:** Nearly identical loading code
**Recommended Fix:** Extract shared keybinding loading function

---

### 12. LIST_KEY naming wrong
**Files:** `src/ui/keybindings.py`
**Issue:** Should be `STEP_LINE_KEY` based on actual action
**Recommended Fix:** Rename variable to match its purpose

---

### 13. immediate_history AttributeError risk
**Files:** `src/ui/tk_ui.py`
**Issue:** `_setup_immediate_context_menu()` would fail if `immediate_history` is None
**Details:**
- Method accesses `self.immediate_history` without None check
- Comments suggest it might be None in some cases

**Recommended Fix:** Add None check or ensure it's never None

---

### 14. Dual input mechanism unclear
**Files:** `src/ui/web/nicegui_backend.py`
**Issue:** Unclear control flow trying both input paths
**Recommended Fix:** Clarify which path is used when and why both exist

---

### 15. Internal inconsistency - empty programs
**Files:** `src/ui/web/nicegui_backend.py`
**Issue:** Different output clearing behavior for RUN vs STEP on empty programs
**Recommended Fix:** Standardize behavior (same as issue #7)

---

### 16. Settings dialog not exposed
**Files:** `src/ui/web/web_settings_dialog.py`
**Issue:** Fully implemented but no UI/keyboard access
**Details:**
- Dialog widget exists and works
- No menu item or keyboard shortcut to access it

**Recommended Fix:** Add menu item or keyboard shortcut to open settings

---

### 17. Unrelated doc in sequential-files.md
**Files:** `docs/user/SETTINGS_AND_CONFIGURATION.md`, `docs/user/sequential-files.md`
**Issue:** File I/O mixed with settings documentation
**Recommended Fix:** Separate or reorganize content

---

## Low Severity Code Changes (5 issues)

### 18. ConsoleIOHandler fallback broken
**Files:** `src/iohandler/console.py`
**Issue:** Windows without msvcrt returns broken behavior silently
**Details:**
- Falls back to readline-like behavior on Windows without msvcrt
- May not work correctly but no error/warning

**Recommended Fix:** Raise error or log warning when fallback used

---

### 19. Menu vs help_widget keybinding inconsistency
**Files:** `src/ui/interactive_menu.py`, `src/ui/help_widget.py`
**Issue:** Architectural inconsistency in keybinding handling
**Recommended Fix:** Use consistent keybinding mechanism

---

### 20. Error message formatting inconsistent
**Files:** `src/ui/curses_ui.py`
**Issue:** Box width varies between error types
**Details:**
- Some errors shown in narrow boxes
- Others in wide boxes
- Inconsistent visual appearance

**Recommended Fix:** Standardize error box formatting

---

### 21. _close_all_files missing
**Files:** `src/ui/web/nicegui_backend.py`
**Issue:** Method referenced but not shown in code
**Details:**
- Method is called but definition not in provided code
- May be missing or in different file

**Recommended Fix:** Verify method exists or remove call

---

### 22. Path normalization duplication
**Files:** `src/ui/tk_help_browser.py`
**Issue:** Multiple approaches should consolidate
**Recommended Fix:** Use single consistent path normalization function

---

## Summary by Category

**Integration Issues (3):**
- UI contract validation (#1)
- Runtime sync missing (#4)
- Dual input mechanism (#14)

**State Management Issues (3):**
- CONT doesn't clear state (#2)
- Empty program inconsistency (#7, #15)
- immediate_history None check (#13)

**Naming/Organization Issues (5):**
- QUIT_ALT_KEY semantic error (#5)
- LIST_KEY wrong name (#12)
- Code duplication (#10, #11, #22)

**User-Facing Issues (4):**
- FOR loop dummy variable (#3)
- Step behavior inconsistent (#9)
- Settings dialog hidden (#16)
- Error formatting (#20)

**Validation Issues (4):**
- Redundant checks (#6)
- Missing methods (#21)
- Fallback broken (#18)
- Command key docs (#8)

**Architectural Issues (3):**
- Keybinding inconsistency (#19)
- Documentation organization (#17)

---

## Recommended Priority Order

### Critical (Do First):
1. **Issue #2:** CONT after line edits - potential crash
2. **Issue #3:** FOR loop dummy variable - silent corruption
3. **Issue #4:** Runtime sync missing - state corruption

### High Priority:
4. **Issue #1:** UI integration validation
5. **Issue #5:** QUIT_ALT_KEY semantic error
6. **Issue #7:** Empty program consistency

### Medium Priority:
7. **Issue #13:** immediate_history None check
8. **Issue #10:** CapturingIOHandler duplication
9. **Issue #11:** Keybinding loader duplication
10. **Issue #16:** Settings dialog exposure

### Low Priority (Cleanup):
11-22: Remaining naming, formatting, and minor issues

---

## Pre-Implementation Checklist

Before implementing ANY of these fixes:

- [ ] Review git history for related code
- [ ] Check if code was intentionally removed/disabled
- [ ] Verify current behavior is actually wrong
- [ ] Look for related test cases
- [ ] Check if "bug" is actually feature parity with MBASIC 5.21
- [ ] Consult with user about expected behavior
- [ ] Review impact on other UIs (CLI, Curses, Tk, Web)
- [ ] Check if issue already fixed in recent commits

**Remember:** Past runs at this stage resulted in reimplementing removed code!
