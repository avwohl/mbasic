# Code vs Comment Fixes - Applied Changes

## Summary

**Date**: 2025-11-05
**Source**: docs/dev/parsed_inconsistencies.json (from docs_inconsistencies_report-v7.md)
**Total Issues**: 173 code_vs_comment type issues
**Completed**: 22 issues in src/interpreter.py
**Remaining**: 151 issues across 34 other files

## Files Modified

### src/interpreter.py - 22 fixes applied

All fixes in this file improve comment/docstring clarity to match actual code behavior.

#### Fix 1: InterpreterState execution state priority (Lines 40-43)
**Issue**: Docstring didn't clarify priority when checking multiple states
**Fix**: Added explicit priority order (error_info FIRST, input_prompt SECOND, halted LAST)
```python
# OLD:
Primary execution states (check these to determine current status):
- runtime.halted: True if stopped (paused/done/at breakpoint)
- input_prompt: Non-None if waiting for input
- error_info: Non-None if an error occurred

# NEW:
Primary execution states (check these to determine current status):
- error_info: Non-None if an error occurred (check FIRST - highest priority)
- input_prompt: Non-None if waiting for input (check SECOND)
- runtime.halted: True if stopped (paused/done/at breakpoint) (check LAST)
```

#### Fix 2: skip_next_breakpoint_check behavior (Lines 56-58)
**Issue**: Comment said "prevents re-triggering immediately" but didn't explain when it's set/cleared
**Fix**: Clarified it's set when halting, allows one step past, then clears
```python
# OLD:
skip_next_breakpoint_check: bool = False  # Allows execution past a breakpoint after stopping on it
                                           # (prevents re-triggering the same breakpoint immediately)

# NEW:
skip_next_breakpoint_check: bool = False  # Set when halting at a breakpoint.
                                           # On next execution, allows stepping past the breakpoint once,
                                           # then clears itself. Prevents re-halting on same breakpoint.
```

#### Fix 3: current_statement_char_end docstring (Line 98)
**Issue**: Docstring didn't mention line_text_map fallback for last statement
**Fix**: Added documentation of fallback behavior
```python
# OLD:
Uses max(char_end, next_char_start - 1) to handle string tokens correctly.

# NEW:
Uses max(char_end, next_char_start - 1) to handle string tokens correctly.
For the last statement on a line, uses line_text_map to get actual line length.
```

#### Fix 4: return_stmt boundary condition in execute_return (Lines 1071-1075)
**Issue**: Comment said "Valid range: 0 to len(statements) inclusive" which is ambiguous
**Fix**: Clarified that len(statements) is a special sentinel value
```python
# OLD:
# return_stmt is 0-indexed offset. Valid range: 0 to len(statements) (inclusive of len).
# return_stmt == len(statements) is valid: means "continue at next line" (GOSUB was last stmt)
# return_stmt > len(statements) is invalid: statement was deleted (validation error)

# NEW:
# return_stmt is 0-indexed offset into statements array.
# Valid range: 0 to len(statements) where len(statements) is a special sentinel value
# meaning "continue at next line" (GOSUB's last statement completed, resume after the line).
# Values > len(statements) indicate the statement was deleted (validation error).
```

#### Fix 5: execute_next variable processing (Lines 1135-1137)
**Issue**: Comment said "closes I first" which suggests stack popping, but code processes left-to-right
**Fix**: Changed "closes" to "processes" and explained behavior
```python
# OLD:
# Process variables in order: NEXT I, J, K closes I first, then J, then K

# NEW:
# Process variables left-to-right: NEXT I, J, K processes I first, then J, then K.
# Each variable is incremented; if it loops back to FOR, subsequent vars are skipped.
# If a variable's loop completes, it's popped and the next variable is processed.
```

#### Fix 6: return_stmt in _execute_next_single (Lines 1225-1227)
**Issue**: Similar to Fix 4, unclear about sentinel value
**Fix**: Clarified sentinel value meaning
```python
# OLD:
# return_stmt is 0-indexed offset. Valid range: 0 to len(statements) (inclusive of len).
# return_stmt == len(statements) means FOR was last statement (continue at next line).
# return_stmt > len(statements) is invalid (statement was deleted).

# NEW:
# return_stmt is 0-indexed offset into statements array. Valid indices are 0 to len(statements)-1.
# return_stmt == len(statements) is a special sentinel: FOR was last statement, continue at next line.
# return_stmt > len(statements) is invalid (statement was deleted).
```

#### Fix 7: RESUME 0 vs RESUME (Lines 1328-1329)
**Issue**: Comment said "identical meaning" without clarifying parser treats them differently
**Fix**: Explained parser difference vs semantic equivalence
```python
# OLD:
# RESUME or RESUME 0 - retry the statement that caused the error
# Both forms are valid BASIC syntax with identical meaning

# NEW:
# RESUME or RESUME 0 - retry the statement that caused the error
# Parser treats them differently (None vs 0) but semantically they're identical
```

#### Fix 8: OPTION BASE comment (Lines 1540-1543)
**Issue**: Comment said "implicit BASE 0" which could mean implicit array creation or implicit base value
**Fix**: Clarified it applies to both explicit DIM and implicit creation
```python
# OLD:
# MBASIC 5.21 gives 'Duplicate Definition' if:
# 1. OPTION BASE has already been executed, OR
# 2. Any arrays have been created (even with implicit BASE 0)

# NEW:
# MBASIC 5.21 gives 'Duplicate Definition' if:
# 1. OPTION BASE has already been executed, OR
# 2. Any arrays have been created (both explicitly via DIM and implicitly via first use like A(5)=10)
#    This applies regardless of the current array base (0 or 1).
```

#### Fix 9: OLD EXECUTION METHODS version clarification (Lines 583-584)
**Issue**: Referenced v1.0.300 without explaining relationship to MBASIC 5.21
**Fix**: Clarified these are different versioning schemes
```python
# OLD:
# OLD EXECUTION METHODS REMOVED (v1.0.300)

# NEW:
# OLD EXECUTION METHODS REMOVED (internal version v1.0.300 - this is the mbasic implementation
# version, not the MBASIC 5.21 language version)
```

#### Fix 10: WEND loop popping behavior
**Issue**: Comment didn't explain what happens if error occurs during WHILE re-evaluation
**Fix**: Added note about error handling and stack state
```python
# Added:
# Note: If an error occurs during WHILE condition evaluation, the loop is already popped,
# which is correct (error handling should not leave partial loop state).
```

#### Fix 11: execute_input state variables (Lines 1585-1588)
**Issue**: Comment mentioned state transition but didn't document which state vars are set
**Fix**: Listed all state variables involved
```python
# OLD:
In tick-based execution mode, this may transition to 'waiting_for_input' state
instead of blocking. When input is provided via provide_input(), execution
resumes from the input buffer.

# NEW:
In tick-based execution mode, this may transition to 'waiting_for_input' state
instead of blocking. Sets: input_prompt (prompt text), input_variables (var list),
input_file_number (file # or None). When input is provided via provide_input(),
execution resumes and these state vars are read then cleared.
```

#### Fix 12: CLEAR file close error handling
**Issue**: Comment said "Close all open files" but didn't mention silent error handling
**Fix**: Documented that errors are silently ignored
```python
# OLD:
# Close all open files

# NEW:
# Close all open files
# Note: Errors during file close are silently ignored (bare except: pass below)
```

#### Fix 13: MID$ assignment length parameter (Lines 2518-2519)
**Issue**: Docstring showed syntax but didn't clarify if length is required
**Fix**: Added note that length is required in our implementation
```python
# OLD:
Syntax: MID$(string_var, start, length) = value

# NEW:
Syntax: MID$(string_var, start, length) = value
(length is required in our implementation; parser should enforce this)
```

#### Fix 14: CONT Break limitation
**Issue**: Comment said "Break doesn't set stopped flag" without explaining where this is handled
**Fix**: Clarified this function only checks stopped flag, Break handling is elsewhere
```python
# OLD:
Note: Ctrl+C (Break) does not set stopped flag, so CONT cannot resume after Break.

# NEW:
Note: This function only checks the stopped flag. Ctrl+C (Break) interrupts execution
without setting stopped=True, so CONT cannot resume after Break. This is handled elsewhere
in the execution flow (Break sets halted but not stopped).
```

#### Fix 15: execute_stop npc comment
**Issue**: Comment referenced 'npc' without defining it
**Fix**: Added explanation of what npc is and where it's set
```python
# OLD:
# Save PC position for CONT
# npc is set by statement execution flow to point to next statement

# NEW:
# Save PC position for CONT
# runtime.npc (next program counter) is set by tick() to point to the next statement
# to execute after the current one completes
```

#### Fix 16: MID$ min calculation
**Issue**: Comment described calculation but not semantic meaning of each component
**Fix**: Added semantic explanation of why each component is needed
```python
# OLD:
# Calculate how many characters to actually replace
# This is the minimum of: length parameter, length of new_value, and available space in string

# NEW:
# Calculate how many characters to actually replace
# min(length, len(new_value), available_space) where:
#   length = requested replacement length (from MID$ stmt)
#   len(new_value) = chars available in replacement string
#   available_space = chars from start_idx to end of string (prevents overrun)
```

#### Fix 17: CLEAR preserved state
**Issue**: Comment only mentioned common_vars but code preserves more
**Fix**: Documented all preserved state
```python
# OLD:
# Note: We preserve runtime.common_vars for CHAIN compatibility
# Note: We ignore string_space and stack_space parameters (Python manages memory automatically)

# NEW:
# Note: Preserved state for CHAIN compatibility:
#   - runtime.common_vars (COMMON variables)
#   - runtime.files (open file handles)
#   - runtime.field_buffers (random access file buffers)
#   - runtime.user_functions (DEF FN functions)
# Note: We ignore string_space and stack_space parameters (Python manages memory automatically)
```

#### Fix 18: LSET/RSET non-field variable behavior (Lines 2510-2512)
**Issue**: Comment said "just do normal assignment" without explaining this is a compatibility extension
**Fix**: Clarified this is not strict MBASIC 5.21 behavior
```python
# OLD:
# If not a field variable, just do normal assignment

# NEW:
# If not a field variable, fall back to normal assignment.
# Note: In strict MBASIC 5.21, LSET/RSET are only for field variables.
# This fallback is a compatibility extension.
```

#### Fix 19: get_variable_for_debugger usage (Lines 2891-2893)
**Issue**: Comment said "saving state, not actually reading for use" which is misleading
**Fix**: Clarified purpose is to avoid access tracking, not about value usage
```python
# OLD:
# Note: We use get_variable_for_debugger here because we're saving state, not actually reading for use

# NEW:
# Note: Use get_variable_for_debugger to avoid triggering variable access tracking.
# We ARE using the value (to save/restore), but this is implementation detail,
# not program-level variable access.
```

#### Fix 20: debugger_set parameter purpose (Lines 2906-2907)
**Issue**: Comment used inconsistent terminology with Fix 19
**Fix**: Unified explanation of debugger_set purpose
```python
# OLD:
# Use debugger_set=True since this is implementation detail, not actual program assignment

# NEW:
# Use debugger_set=True to avoid tracking this as program-level assignment.
# This is function call implementation (save/restore params), not user code.
```

#### Fixes 21-22: Verified as correct
- Issue about OPEN error message: Code already correct (includes mode value in error)
- Issue about file EOF detection: Code behavior already correct

## Impact

All fixes are documentation-only changes that improve code maintainability:
- **No functional changes** - code behavior unchanged
- **Improved clarity** - comments now accurately describe code
- **Better maintenance** - future developers will understand intent
- **Reduced confusion** - eliminated misleading terminology

## Testing

No testing required as these are comment-only changes. However, verified:
1. All files still parse correctly (no syntax errors introduced)
2. Comments accurately reflect adjacent code behavior
3. No contradictions between comments and implementation

## Next Steps

See `CODE_COMMENT_FIXES_REMAINING.md` for:
- 151 remaining issues across 34 files
- Prioritization by severity and file
- Common patterns and recommended fix approach

---

Generated: 2025-11-05
