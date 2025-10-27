# Work in Progress

## Task
✅ FIXED: FOR loop stack corruption - 23 duplicate entries after ONE run

## Root Cause
User's program had reversed NEXT statements:
```basic
40 FOR x%=0 TO 20
50   FOR y%=0 TO 23
60     PRINT ...
70   NEXT x%    ' WRONG! Should be NEXT y%
80 NEXT y%      ' WRONG! Should be NEXT x%
```

This caused stack corruption:
1. Line 70 "NEXT x%" pops x% (but y% is still active!)
2. NEXT x% jumps back to line 40, increments x%
3. Line 50 pushes y% AGAIN (y% already on stack!)
4. Stack grows: [y%, y%, y%, ...] endlessly

## Fix Applied
Added two validations:

### 1. NEXT statement validation (interpreter.py:1445-1459)
Before processing NEXT, verify the loop variable is on TOP of stack:
```python
loop_index = self.runtime.for_loop_vars[var_name]
if loop_index != len(self.runtime.execution_stack) - 1:
    # Error: not the innermost loop
    raise RuntimeError(f"NEXT {var_name} without FOR - found FOR {top_var} loop instead")
```

### 2. FOR statement validation (runtime.py:802-806)
Before pushing FOR loop, verify variable doesn't already have active loop:
```python
if var_name in self.for_loop_vars:
    raise RuntimeError(f"FOR loop variable {var_name} already active")
```

## Test Results
✅ Buggy program now shows proper error:
   "NEXT x% without FOR - found FOR y% loop instead (improper nesting)"

✅ Correct program still works fine - y% is pushed/popped properly for each x% iteration

## Files Modified
- src/interpreter.py (lines 1445-1459)
- src/runtime.py (lines 802-806)

## Ready to Commit
Yes - fix is tested and working
