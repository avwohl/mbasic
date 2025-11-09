# Code Behavior Changes from Inconsistencies Report v17

Generated: 2025-11-09
Source: docs_inconsistencies_report-v17.md

This file contains issues that require changes to what the code actually does, not just documentation updates. These may include bugs, logic errors, missing implementations, or behavior that contradicts intended design.

---

## High Severity Code Issues

### _sync_program_to_runtime preserves PC claim vs actual behavior
**File:** `src/ui/curses_ui.py` _sync_program_to_runtime method
**Issue:** Docstring claims "preserves current PC/execution state" but code resets PC to halted when paused_at_breakpoint=True
**Current behavior:**
```python
if self.running and not self.paused_at_breakpoint:
    # Execution is running - preserve execution state
    self.runtime.pc = old_pc
    self.runtime.halted = old_halted
else:
    # No execution in progress or paused at breakpoint - ensure halted
    self.runtime.pc = PC.halted_pc()
    self.runtime.halted = True
```
**Decision needed:** Is pausing at breakpoint the correct behavior (update docstring) or should PC be preserved when paused (update code)?
**Recommendation:** If intentional to prevent accidental resumption, update docstring. If breakpoint pause should preserve PC, fix code.

### Stop/Interrupt shortcut conflicts with Cut operation
**File:** `docs/help/ui/tk/feature-reference.md`
**Issue:** {{kbd:cut:tk}} assigned to both Stop Program and Cut text - serious conflict
**Impact:** Users cannot perform both operations
**Fix required:** Assign different shortcuts to Stop and Cut operations
**Recommendation:** Follow standard conventions (Ctrl+X for Cut, Escape or Ctrl+Break for Stop)

---

## Medium Severity Code Issues

### EDIT command doesn't call clear_execution_state()
**File:** `src/interactive.py` cmd_edit() line ~860
**Issue:** CONT docstring says editing clears execution state, but EDIT command doesn't call clear_execution_state() while other edit operations do
**Current behavior:**
- process_line() calls clear_execution_state() when adding/deleting lines (lines ~150, ~157)
- cmd_renum() calls clear_execution_state() after renumbering
- cmd_edit() updates statement_table but does NOT call clear_execution_state()
**Fix:** Add clear_execution_state() call in cmd_edit() after line modification, OR document why EDIT is special

### Inconsistent cursor positioning after delete line
**File:** `src/ui/curses_ui.py` _delete_current_line() line ~920
**Issue:** Comment says "Always position at column 1" but else branch positions at end of previous line
**Current behavior:**
```python
if line_index < len(lines):
    new_cursor_pos = sum(len(lines[i]) + 1 for i in range(line_index)) + 1  # Column 1
else:
    # Was last line, position at end of previous line
    new_cursor_pos = sum(len(lines[i]) + 1 for i in range(len(lines) - 1)) + len(lines[-1])
```
**Fix:** Either always position at column 1, or update comment to describe actual behavior

### Inconsistent handling of code_start position
**File:** `src/ui/curses_ui.py` multiple methods
**Issue:** _insert_line_after_current() hardcodes column 7, _toggle_breakpoint_current_line() uses _parse_line_number for variable width
**Locations:**
- _insert_line_after_current(): `new_cursor_pos = 7  # Column 7 is start of code area`
- _toggle_breakpoint_current_line(): `line_number, code_start = self.editor._parse_line_number(line)` AND `code_area = line[7:]`
**Fix:** If line number width is variable, use _parse_line_number() consistently. If fixed at 7, document assumptions about line number format.

### Inconsistent program state synchronization
**File:** `src/ui/curses_ui.py` multiple methods
**Issue:** Multiple sync methods with unclear relationships and _refresh_editor() referenced but not defined
**Methods:**
1. _parse_editor_content() - parses editor text into self.editor_lines
2. _sync_program_to_runtime() - syncs self.program to runtime
3. _sync_program_to_editor() - syncs self.program to editor
4. _refresh_editor() - referenced in cmd_delete and cmd_renum but not defined
**Fix:** Define _refresh_editor() or update calls to use correct method

### _on_status_click() uses different regex than _parse_line_number()
**File:** `src/ui/tk_widgets.py`
**Issue:** Two different patterns for extracting line numbers could cause inconsistent behavior
**Current:**
- _parse_line_number(): `match = re.match(r'^(\d+)(?:\s|$)', line_text)`  # Requires whitespace OR end
- _on_status_click(): `match = re.match(r'^\s*(\d+)', line_text)`  # Allows anything after
**Impact:** _on_status_click() matches '10REM' as line 10, _parse_line_number() rejects it
**Fix:** Use same pattern in both methods, or document why they differ

### Comment claims identifier_table infrastructure not used but it's implemented
**File:** `src/case_string_handler.py` lines 28-61
**Issue:** Comment says "not currently used" but get_identifier_table() is fully implemented
**Current:**
```python
@classmethod
def get_identifier_table(cls, policy: str = "force_lower") -> CaseKeeperTable:
    """Get or create the identifier case keeper table."""
    if cls._identifier_table is None:
        cls._identifier_table = CaseKeeperTable(policy=policy)
```
**Fix:** Either remove unused code or update comment if it's actually used elsewhere

### Comment about original_negative line number reference outdated
**File:** `src/basic_builtins.py` line 274
**Issue:** Comment says "captured at line 272 before rounding" but actually captured at line 270
**Fix:** Update line number reference or use relative reference like "captured above before rounding"

### Comment about leading sign padding contradicts code structure
**File:** `src/basic_builtins.py` lines 337-346
**Issue:** Comment says "only spaces, not asterisks for leading sign" but code structure doesn't enforce this
**Current:**
```python
# Comment: 'but only spaces, not asterisks for leading sign'
if spec['asterisk_fill']:
    result_parts.append('*' * max(0, padding_needed))
else:
    result_parts.append(' ' * max(0, padding_needed))
```
**Fix:** Verify behavior matches comment intent, update code or comment as needed

### Comment says add_line expects complete line but passes line_num separately
**File:** `src/immediate_executor.py`
**Issue:** API design passes line number twice
**Current:**
```python
complete_line = f"{line_num} {line_content}"
success, error = ui.program.add_line(line_num, complete_line)
```
**Fix:** Either remove redundant line_num parameter or update comment to explain why it's needed

### Comment about ERL renumbering describes deviation without clear resolution
**File:** `src/interactive.py` line ~580
**Issue:** Comment says "INTENTIONAL DEVIATION" but also mentions "Known limitation: ...will incorrectly renumber"
**Decision needed:** Is this a bug to fix or accepted behavior to document better?

### Comment about program_runtime persistence suggests unusual behavior
**File:** `src/interactive.py` execute_immediate
**Issue:** Comment says "program_runtime persists until NEW/LOAD/next RUN" which may indicate cleanup not happening
**Fix:** Verify runtime cleanup happens appropriately or document why persistence is needed

### Comment about error_info timing is imprecise
**File:** `src/interpreter.py` lines 667-669
**Issue:** Says error_info set "just before" _invoke_error_handler but there's conditional logic between
**Fix:** Update comment to reflect actual flow

### Comment about latin-1 encoding and CP437/CP850 conversion
**File:** `src/interpreter.py` line ~1430
**Issue:** Says "Conversion may be needed" but doesn't specify where/how
**Fix:** Add conversion functionality or document it as user responsibility

### Comment about MID$ assignment start_idx contradicts typical behavior
**File:** `src/interpreter.py` execute_midassignment()
**Issue:** `start_idx == len(current_value)` is out of bounds, preventing append
**Fix:** Verify this matches MBASIC 5.21 behavior, document clearly

### input_line() implementations have inconsistent space preservation limitations
**Files:** `src/iohandler/base.py`, `src/iohandler/console.py`, `src/iohandler/curses_io.py`, `src/iohandler/web_io.py`
**Issue:** base.py says Python input() strips "trailing newline/spaces", console.py says "leading/trailing spaces", descriptions don't match
**Fix:** Test actual behavior, document consistently

### print() method backward compatibility comment backwards
**File:** `src/iohandler/web_io.py`
**Issue:** Comment suggests print() is alias but implementation shows print() calls output()
**Fix:** Clarify which is primary method and which is alias

### at_end_of_line() vs at_end_of_statement() used inconsistently
**File:** `src/parser.py`
**Issue:** Code uses at_end_of_line() where at_end_of_statement() should be used (e.g., parse_print())
**Fix:** Review all uses and apply correct method based on context

### Incomplete comment about function name normalization
**File:** `src/parser.py` parse_deffn() line ~2110
**Issue:** Comment cut off mid-sentence: "ensures function"
**Fix:** Complete the sentence

### apply_keyword_case_policy 'preserve' fallback ambiguity
**File:** `src/position_serializer.py`
**Issue:** Comment says "shouldn't normally execute in correct usage" but provides fallback
**Fix:** Clarify if this is defensive code or error condition

### Deprecation date format error
**File:** `src/runtime.py` get_loop_stack()
**Issue:** "Deprecated since: 2025-10-25" is in the future
**Fix:** Correct date to 2024-10-25 or verify dating convention

### register_keyword() exists for compatibility but with unused parameters
**File:** `src/simple_keyword_case.py`
**Issue:** Takes line_num and column parameters marked unused, comment says "for compatibility" without explaining with what
**Fix:** Remove unused parameters or document what requires them

### RedisSettingsBackend initialization documentation incomplete
**File:** `src/settings_backend.py`
**Issue:** Docstring doesn't explain when default_settings is None vs provided, or how to force reload
**Fix:** Document initialization logic more completely

### Module docstring describes two scopes but three implemented
**File:** `src/settings.py`
**Issue:** Docstring mentions global and project, but FILE scope exists in code
**Fix:** Add FILE scope to module docstring even if not yet used

### Context menu dismiss binding may not work as intended
**File:** `src/ui/tk_help_browser.py` lines 645-658
**Issue:** tk.Menu <FocusOut> and <Escape> bindings may not trigger reliably
**Fix:** Test and verify bindings work, or use alternative dismiss approach

### _on_status_click() showinfo called but docstring says "confirmation message"
**File:** `src/ui/tk_widgets.py`
**Issue:** Uses showinfo() for breakpoint but docstring says "confirmation message"
**Fix:** Change to actual confirmation dialog or update docstring

### Comment about CP/M EOF marker references missing file loading code
**File:** `src/ui/web/nicegui_backend.py`
**Issue:** Claims consistency with file loading but doesn't reference where
**Fix:** Add reference or verify consistency

### Web help launcher open_help_in_browser() doesn't add .html extension
**File:** `src/ui/web_help_launcher.py`
**Issue:** Migration guide says add .html but function doesn't
**Fix:** Either add .html in function or update migration guide

### Typo example in curses editing docs contradictory
**File:** `docs/help/common/ui/curses/editing.md`
**Issue:** Says '1O PRINT' creates "variable 1O (syntax error)!" - can't be both variable creation and syntax error
**Fix:** Clarify what actually happens (likely syntax error, not variable creation)

### DEFINT example shows incorrect type mismatch
**File:** `docs/help/common/language/statements/defint-sng-dbl-str.md`
**Issue:** Comment says AMOUNT is string variable but assigns numeric 100 (would cause type mismatch error)
**Fix:** Correct example to use AMOUNT$ or assign string value "100"

---

## Low Severity Code Issues

### PREFIX stripping comment overly defensive
**File:** `src/ui/curses_settings_widget.py` _create_setting_widget()
**Issue:** Comment defends against removing 'force_' elsewhere in string, but this isn't a real concern
**Fix:** Simplify comment or remove defensive explanation

### STACK command not in keybindings
**File:** `src/ui/cli_debug.py`, `src/ui/cli_keybindings.json`
**Issue:** cmd_stack() implemented but not in JSON
**Fix:** Add to JSON or document why it's excluded

### Comment about target_column default doesn't match variable line numbers
**File:** `src/ui/curses_ui.py` keypress() method
**Issue:** Assumes fixed 5-digit line numbers but line numbers are variable width
**Fix:** Update comment to reflect actual line number width handling

### Comment about line 0 edge case unclear
**File:** `src/ui/curses_ui.py` _update_syntax_errors()
**Issue:** Line 0 would be invalid in BASIC but comment suggests it's valid edge case
**Fix:** Clarify if line 0 is supported or should be rejected

### Bug fix comment about next_auto_line_num doesn't mention increment location
**File:** `src/ui/curses_ui.py` _update_display()
**Issue:** Says DON'T increment here but doesn't mention incrementing DOES happen in keypress()
**Fix:** Add reference to where increment actually happens

### Comment about _create_toolbar says UNUSED but provides detailed explanation
**File:** `src/ui/curses_ui.py` line ~260
**Issue:** Says "Can be safely removed if no plans to restore" - decision item not comment
**Fix:** Either remove method or document plans to restore

### Comment about toolbar removal doesn't explain why menu is better
**File:** `src/ui/curses_ui.py` line ~262
**Issue:** Claims "better keyboard navigation" without justification
**Fix:** Explain why menu provides better navigation or remove claim

### Comment about main widget storage in _activate_menu() is wrong
**File:** `src/ui/curses_ui.py` _activate_menu()
**Issue:** Claims _show_help closes overlays first but it doesn't
**Fix:** Correct comment to match actual behavior

### Comment about statement-level precision uses inconsistent terminology
**File:** `src/ui/curses_ui.py` _update_stack_window()
**Issue:** Uses 'return_stmt' for GOSUB but 'stmt' for FOR/WHILE
**Fix:** Standardize variable naming

### Comment in _show_keymap says "same approach" but implementations differ
**File:** `src/ui/curses_ui.py` _show_keymap()
**Issue:** _show_keymap has toggle behavior, _show_help doesn't
**Fix:** Update comment to note differences

### Comment mentions duplicated CapturingIOHandler but it's already extracted
**File:** `src/ui/curses_ui.py` _execute_immediate
**Issue:** Comment outdated - extraction already done
**Fix:** Update comment to reflect current state

### Comment in _on_autosave_recovery_response says "blank lines" but filters lines with no code
**File:** `src/ui/curses_ui.py`
**Issue:** "Blank lines" vs "lines with line numbers but no code"
**Fix:** Use precise terminology

### _expand_kbd parameter format documentation could be clearer
**File:** `src/ui/help_widget.py` lines ~107-119
**Issue:** Format description accurate but example could confuse
**Fix:** Add clarifying example showing both formats

### Link tag prefixes comment incomplete
**File:** `src/ui/tk_help_browser.py` line 632
**Issue:** Comment identifies two prefixes but _on_link_click() only checks "link_" not "result_link_"
**Fix:** Verify all prefixes handled consistently

### Inline help display design choice not documented
**File:** `src/ui/tk_settings_dialog.py` line 169
**Issue:** Design decision (inline label vs tooltip) only in code comment
**Fix:** Document in module docstring or user docs

### Modal behavior comment uses non-standard terminology
**File:** `src/ui/tk_settings_dialog.py` line 48
**Issue:** Uses 'modal' to mean "modeless with grab" which is confusing
**Fix:** Use standard terminology

### Comment about variable region types incomplete
**File:** `src/ui/tk_ui.py` _on_variable_double_click()
**Issue:** Explains 'tree' and 'cell' but not other possible values
**Fix:** Document all possible region values or note these are the only ones checked

### Comment "return 'break'" redundant after first occurrence
**File:** `src/ui/tk_ui.py` _on_enter()
**Issue:** Same comment appears 3+ times in same function
**Fix:** Remove redundant comments

### Dead code comment for _setup_immediate_context_menu() references dead code methods
**File:** `src/ui/tk_ui.py`
**Issue:** Dead code retained with vague "potential future use" rationale
**Fix:** Remove dead code or document specific restoration plans

### cycle_sort_mode() claims to match Tk UI without verification
**File:** `src/ui/variable_sorting.py`
**Issue:** No mechanism to ensure implementations stay in sync
**Fix:** Add test to verify sync or cross-reference implementation

### serialize_expression() ERR/ERL special handling rationale incomplete
**File:** `src/ui/ui_helpers.py`
**Issue:** Doesn't explain why ERR/ERL are FunctionCallNode if they're system variables
**Fix:** Reference parser design decision

### Module comment references missing _enable_inline_input() method
**File:** `src/ui/web/nicegui_backend.py` line ~70
**Issue:** Method not in provided code
**Fix:** Verify method exists or update comment

### Comment about MBASIC version clarifications suggests past confusion
**File:** `src/ui/web/nicegui_backend.py` multiple locations
**Issue:** Repeated clarifications about 5.21 being language version
**Fix:** Simplify or consolidate comments

### open_help_in_browser() docstring doesn't clarify platform-dependent behavior
**File:** `src/ui/web_help_launcher.py`
**Issue:** webbrowser.open() returns vary by platform
**Fix:** Document platform-dependent behavior

---

## Summary

Issues requiring code changes: ~40
Issues requiring verification: ~25
Issues requiring design decisions: ~10

Note: Many issues require testing against MBASIC 5.21 to determine correct behavior before implementing fixes.
