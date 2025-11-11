# Remaining Code vs Comment Fixes

## Summary

**Total Issues**: 173
**Completed**: 22 (src/interpreter.py - all fixes applied)
**Remaining**: 151 across 34 files

## Progress by Severity

- **HIGH**: 7 remaining (out of 10 total)
- **MEDIUM**: 62 remaining (out of 74 total)
- **LOW**: 82 remaining (out of 89 total)

## Completed Files

### src/interpreter.py - 22 issues ✓ DONE

All 22 issues fixed:
1. ✓ Clarified return_stmt boundary condition (lines 1071-1075)
2. ✓ Clarified OPTION BASE implicit array handling (lines 1540-1543)
3. ✓ OPEN error message already correct in code
4. ✓ Clarified skip_next_breakpoint_check behavior (lines 56-58)
5. ✓ Fixed NEXT comment wording ('processes' not 'closes') (lines 1135-1137)
6. ✓ Clarified version numbers (lines 583-584)
7. ✓ Clarified _execute_next_single return_stmt (lines 1225-1227)
8. ✓ Clarified RESUME 0 vs RESUME handling (lines 1328-1329)
9. ✓ Added WEND loop popping explanation
10. ✓ Documented INPUT state variables (lines 1585-1588)
11. ✓ Documented CLEAR file close error handling
12. ✓ Documented MID$ length parameter (lines 2518-2519)
13. ✓ Clarified CONT Break limitation
14. ✓ Clarified execute_stop npc
15. ✓ Clarified MID$ min calculation semantic meaning
16. ✓ Documented InterpreterState priority (lines 41-43)
17. ✓ Added current_statement_char_end docstring (line 98)
18. ✓ Documented CLEAR preserved state
19. ✓ File EOF detection (code behavior correct)
20. ✓ Clarified LSET/RSET non-field behavior (lines 2510-2512)
21. ✓ Clarified get_variable_for_debugger usage (lines 2891-2893)
22. ✓ Clarified debugger_set parameter purpose (lines 2906-2907)

## Remaining Files (sorted by issue count)

### High Priority (most issues or high severity)

1. **src/ui/curses_ui.py**: 21 issues (1 HIGH, 11 MEDIUM, 9 LOW)
2. **src/ui/tk_ui.py**: 21 issues (1 HIGH, 7 MEDIUM, 13 LOW)
3. **src/ui/web/nicegui_backend.py**: 21 issues (2 HIGH, 8 MEDIUM, 11 LOW)
4. **src/parser.py**: 13 issues (0 HIGH, 6 MEDIUM, 7 LOW)
5. **src/runtime.py**: 10 issues (0 HIGH, 5 MEDIUM, 5 LOW)
6. **src/interactive.py**: 8 issues (1 HIGH, 4 MEDIUM, 3 LOW)
7. **src/position_serializer.py**: 7 issues (1 HIGH, 3 MEDIUM, 3 LOW)

### Medium Priority (4-6 issues)

8. **src/immediate_executor.py**: 6 issues (0 HIGH, 2 MEDIUM, 4 LOW)
9. **src/ui/tk_widgets.py**: 5 issues (0 HIGH, 3 MEDIUM, 2 LOW)
10. **src/ui/keybindings.py**: 4 issues (1 HIGH, 0 MEDIUM, 3 LOW)
11. **src/basic_builtins.py**: 4 issues (0 HIGH, 1 MEDIUM, 3 LOW)

### Low Priority (1-3 issues each, 23 files)

12. src/resource_limits.py: 3 issues
13. src/ui/ui_helpers.py: 3 issues
14. src/lexer.py: 2 issues
15. src/ui/help_widget.py: 2 issues
16. src/settings_definitions.py: 2 issues
17. src/ui/tk_settings_dialog.py: 2 issues
18-34. 17 files with 1 issue each

## Common Fix Patterns

Based on interpreter.py fixes, most issues fall into these categories:

### 1. Boundary Condition Clarifications
- Make explicit what valid ranges are (e.g., "0 to len(array)-1" vs "0 to len(array)")
- Document sentinel values (e.g., len(array) meaning "continue at next line")
- Example: return_stmt comments in execute_return()

### 2. Missing Context Documentation
- Document all state variables that are set/read
- Explain error handling behavior (especially silent errors)
- Example: INPUT state machine variables

### 3. Misleading Terminology
- Use precise language ("processes" not "closes" when order matters)
- Distinguish "implementation detail" from "user code"
- Example: NEXT variable processing order

### 4. Documentation of Limitations
- Make clear when features are not implemented vs ignored
- Explain why certain checks are/aren't made
- Example: CONT cannot resume after Break

### 5. Defensive Code Explanations
- When code handles cases "that shouldn't happen"
- When fallbacks exist for compatibility
- Example: LSET/RSET on non-field variables

## High Severity Issues Remaining (7 total)

1. **src/interactive.py**: Docstring for cmd_edit() claims count prefixes not implemented but doesn't show if they're parsed or rejected
2. **src/ui/curses_ui.py**: Comment says "Don't call interpreter.start()" but then manipulates state
3. **src/ui/tk_ui.py**: Comment in cmd_cont() describes behavior but implementation doesn't match
4. **src/ui/web/nicegui_backend.py** (2 issues):
   - Comment says "reuse interpreter" but creates new IO handler
   - Comment about "Don't sync editor from AST" contradicts TODO
5. **src/position_serializer.py**: apply_keyword_case_policy "preserve" policy contradiction
6. **src/ui/keybindings.py**: Comment about stack window vs step_line key confusion

## Recommended Approach

For systematic completion:

1. **Phase 1** (HIGH priority): Fix all 7 HIGH severity issues
2. **Phase 2** (by file count): Process files with most issues first
   - curses_ui.py, tk_ui.py, nicegui_backend.py (63 total)
   - parser.py, runtime.py (23 total)
3. **Phase 3** (by severity): Fix all remaining MEDIUM (62 issues)
4. **Phase 4** (cleanup): Fix all LOW issues (82 issues)

Alternatively, process by file (complete each file fully before moving to next):
1. interactive.py (8 issues - includes 1 HIGH)
2. position_serializer.py (7 issues - includes 1 HIGH)
3. Then proceed through remaining files

## Fix Application Method

Most fixes are straightforward comment/docstring updates:
1. Read the affected section
2. Determine if comment or code is correct
3. Update the incorrect one (usually update comment to match code)
4. For ambiguous cases, add clarifying comments

Use the Edit tool for targeted fixes:
```python
Edit(
    file_path="/home/wohl/cl/mbasic/src/file.py",
    old_string="old comment text",
    new_string="clarified comment text"
)
```

## Reference

Full issue details in: `/home/wohl/cl/mbasic/docs/dev/parsed_inconsistencies.json`

Section: `issues_by_severity` → filter by `"type": "code_vs_comment"`

---

Generated: 2025-11-05
Based on: docs/history/docs_inconsistencies_report-v7.md
