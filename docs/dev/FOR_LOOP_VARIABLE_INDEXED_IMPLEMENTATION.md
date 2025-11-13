# FOR Loop Variable-Indexed Implementation

## Date
2025-11-13

## Summary

Implemented variable-indexed FOR loop tracking instead of stack-based tracking. This allows jumping out of FOR loops and reusing the same variable (Super Star Trek pattern).

## The Approach

**Variable-Indexed FOR Loops:**
- Each variable is bound to at most one FOR loop at a time
- FOR loop state stored in `Runtime.for_loop_states` dict: `var_name -> {'pc': PC, 'end': value, 'step': value}`
- NEXT looks up the loop state by variable name (O(1) operation)
- Jumping out of a loop and starting a new FOR with the same variable just overwrites the binding

**Nested Loop Detection:**
When nested FOR loops use the same variable:
```basic
FOR I = 1 TO 10   ' Binds I to loop 1
  FOR I = 1 TO 5  ' Overwrites, binds I to loop 2
  NEXT I          ' Completes loop 2, unbinds I
NEXT I            ' Error: I not bound to any loop
```

The first NEXT clears the variable's binding. The second NEXT finds no binding and errors - exactly as desired.

## Changes Made

### Runtime (src/runtime.py)

1. **Added `for_loop_states` dict** (line 90):
   ```python
   # FOR loop state storage - maps variable name to loop state
   # var_name -> {'pc': PC object, 'end': end_value, 'step': step_value}
   self.for_loop_states = {}
   ```

2. **Removed `for_loop_vars` dict** - no longer needed

3. **Added helper methods**:
   - `bind_for_loop(var_name, pc, end_value, step_value)` - Bind variable to FOR loop
   - `get_for_loop_state(var_name)` - Get loop state
   - `unbind_for_loop(var_name)` - Unbind variable from loop

4. **Updated `push_for_loop()`** - Now binds variable to loop state (overwrites if already bound)

5. **Simplified `pop_for_loop()`** - Just unbinds variable

6. **Updated `get_for_loop()`** - Returns loop info from for_loop_states

7. **Updated `validate_stack()`** - Validates FOR loop states separately from execution stack

8. **Updated `has_active_loop()`** - Checks for_loop_states instead of for_loop_vars

9. **Updated clear method** - Clears for_loop_states

### Interpreter (src/interpreter.py)

1. **Simplified `_execute_next_single()`** - Removed stack validation logic (no longer needed)

2. **Added `_find_most_recent_for_variable()`** - Lexically scans backward to find FOR statement for NEXT without variable

3. **Updated `execute_next()`** - Handles NEXT without variable using lexical scoping

### Web UI (src/ui/web/nicegui_backend.py)

1. **Updated serialization** - Saves for_loop_states (pickled) instead of for_loop_vars

2. **Backwards compatibility** - Old saves without for_loop_states start with empty dict

## Benefits

1. **Super Star Trek Pattern Works**: Can jump out of FOR I and start new FOR I
2. **Simple Logic**: No stack searching, just dict lookup
3. **Correct Nesting Detection**: Automatically catches nested same-variable loops
4. **O(1) NEXT Operation**: Direct dict lookup instead of stack search
5. **Matches Real MBASIC**: Tested behavior matches MBASIC 5.21

## Test Results

✅ **test3 (Jump and Reuse)**: Works - jumps out of FOR I, starts new FOR I
✅ **test6 (Super Trek Pattern)**: Works - ON I GOTO handlers with FOR I loops
✅ **test1 (Deep Nesting)**: Works - 10 nested loops with different variables
✅ **Nested Same Variable**: Correctly errors on second NEXT

## Files Modified

- `src/runtime.py` - FOR loop state tracking
- `src/interpreter.py` - NEXT execution and lexical scanning
- `src/ui/web/nicegui_backend.py` - Session serialization

## References

- `docs/dev/FOR_LOOP_IMPLEMENTATION_SUMMARY.md` - Original plan (used separate stack approach)
- `docs/dev/FOR_LOOP_STACK_FINDINGS.md` - Real MBASIC test results
- User insight: "no stack, just tag variable with FOR loop PC"
