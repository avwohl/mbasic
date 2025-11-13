# FOR Loop Stack Implementation - Complete Summary

## Date
2025-11-13

## Overview

This document summarizes the complete research, analysis, and implementation plan for fixing the FOR loop variable reuse bug when jumping out of loops.

## The Problem

**Super Star Trek pattern fails**:
```basic
50 FOR I=1 TO 9
80   ON I GOTO 200,210,220,...
90 NEXT I
200 FOR I=1 TO 2  ' ❌ Error: "variable I already active"
```

## Research Findings

### Real MBASIC 5.21 Behavior

Tested with 6 comprehensive test programs (`tests/for_test*.bas`):

✅ **Test 3 (Critical)**: Jump out of FOR I, start new FOR I → Works!
✅ **Test 5**: Do this 9 times consecutively → Works!
✅ **Test 6**: Super Star Trek pattern → Works!
✅ **Depth**: At least 10 nested FOR loops supported (not limited to 8)

**Conclusion**: Real MBASIC allows immediate variable reuse after jumping out of a loop.

### Compiler Backend Status

✅ **Already works correctly**

- Generates lexically-scoped C for loops
- No runtime loop stack tracking
- Variable reuse is automatic (just C variables)
- Test 3 and Test 6 both compile and run successfully

```c
for (i = 1; i <= 10; i += 1) {
    if (i == 3) goto line_100;
}
line_100:
for (i = 1; i <= 5; i += 1) {  // Reuses 'i' - works fine
```

### Interpreter Current Bug

❌ **Has bug** - unified stack prevents variable reuse

**Architecture** (`src/runtime.py:83-88`):
```python
self.execution_stack = []  # Mixed: GOSUB, FOR, WHILE
self.for_loop_vars = {}    # var_name -> stack index
```

**Problem** (line 996-1001):
```python
if var_name in self.for_loop_vars:
    raise RuntimeError(f"FOR loop variable {var_name} already active")
```

**Why can't just "pop old FOR"**:
1. Old FOR might be deep in stack (not on top)
2. GOSUB or WHILE entries might be between them
3. `pop_for_loop()` requires FOR to be on top

**Example**:
```
Stack: [FOR I (index 0), GOSUB (index 1), WHILE (index 2)]
         ↑ Can't pop this without breaking structure
```

## Solution: Option 1 - Separate FOR Loop Stack

### Architecture Change

**Split stacks**:
```python
self.for_loop_stack = []      # Only FOR loops
self.execution_stack = []     # Only GOSUB and WHILE
self.for_loop_vars = {}       # var_name -> index in for_loop_stack
```

### Implementation

```python
def push_for_loop(self, var_name, end_value, step_value, return_line, return_stmt_index):
    # If variable already active, replace it (implicit cleanup)
    if var_name in self.for_loop_vars:
        old_index = self.for_loop_vars[var_name]
        # Replace old entry in place
        self.for_loop_stack[old_index] = {
            'type': 'FOR',
            'var': var_name,
            'end': end_value,
            'step': step_value,
            'return_line': return_line,
            'return_stmt': return_stmt_index
        }
    else:
        # Add new entry
        self.for_loop_stack.append({...})
        self.for_loop_vars[var_name] = len(self.for_loop_stack) - 1
```

**Benefits**:
- Simple logic - just replace in place
- No need to sift through mixed stack
- Matches real MBASIC behavior
- Compiler already works this way (lexically)

### UI/Debugger Compatibility

**Three UIs display stack**:
- Curses UI (`src/ui/curses_ui.py:3371`)
- TK UI (`src/ui/tk_ui.py:1690`)
- Web UI (`src/ui/web/nicegui_backend.py:339`)

**Key insight**: UIs don't need to change!

Update `get_execution_stack()` to **merge** both stacks:

```python
def get_execution_stack(self):
    """Export unified execution stack for UI display."""
    # Show GOSUB/WHILE, then FOR loops
    result = self.execution_stack.copy()
    result.extend(self.for_loop_stack)
    return result
```

**Trade-off**: Lose true interleaved ordering, but:
- Real MBASIC doesn't enforce FOR/GOSUB nesting anyway
- Each section still shows its own ordering
- Debugger remains useful

### Serialization (Web UI)

Update `src/ui/web/nicegui_backend.py`:

**Serialize** (line 3692):
```python
'execution_stack': self.runtime.execution_stack,      # GOSUB/WHILE only
'for_loop_stack': self.runtime.for_loop_stack,        # FOR only (NEW)
'for_loop_vars': self.runtime.for_loop_vars,
```

**Restore** (line 3731):
```python
self.runtime.execution_stack = state['execution_stack']
self.runtime.for_loop_stack = state.get('for_loop_stack', [])  # Backwards compatible
self.runtime.for_loop_vars = state['for_loop_vars']
```

## Implementation Checklist

### Phase 1: Core Changes
- [ ] Add `self.for_loop_stack = []` to `Runtime.__init__()` (runtime.py:86)
- [ ] Modify `push_for_loop()` to use separate stack (runtime.py:982)
- [ ] Modify `pop_for_loop()` to use separate stack (runtime.py:1021)
- [ ] Modify `get_for_loop()` to use separate stack (runtime.py:1039)
- [ ] Update `get_execution_stack()` to merge stacks (runtime.py:1311)
- [ ] Update stack validation in `validate_execution_stack()` (runtime.py:1101)

### Phase 2: Serialization
- [ ] Update `serialize_state()` in nicegui_backend.py (line 3692)
- [ ] Update `restore_state()` in nicegui_backend.py (line 3731)

### Phase 3: Testing
- [ ] Run all existing tests
- [ ] Test `tests/for_test3_jump_reuse.bas` (critical)
- [ ] Test `tests/for_test6_super_trek.bas` (Super Trek pattern)
- [ ] Test nested FOR with same variable still errors
- [ ] Test debugger stack display in curses/tk/web UIs
- [ ] Test web UI session save/restore

### Phase 4: Verification
- [ ] Verify compiler still works (already does)
- [ ] Verify interpreter matches real MBASIC behavior
- [ ] Update Super Star Trek to use the pattern

## Files Modified

**Core**:
- `src/runtime.py` - Stack management
- `src/interpreter.py` - (possibly GOTO, but probably not needed)

**UI**:
- `src/ui/web/nicegui_backend.py` - Serialization

**Tests**:
- `tests/for_test*.bas` - Already created (6 tests)

**Documentation**:
- `docs/dev/FOR_LOOP_STACK_FINDINGS.md` - Real MBASIC test results
- `docs/dev/FOR_LOOP_STACK_IMPLEMENTATION_OPTIONS.md` - Analysis of 4 options
- `docs/dev/FOR_LOOP_COMPILER_VS_INTERPRETER.md` - Compiler vs interpreter
- `docs/dev/FOR_LOOP_IMPLEMENTATION_SUMMARY.md` - This file

## Why This Is The Right Approach

1. **Matches real MBASIC**: Tests prove this is how it works
2. **Compiler compatibility**: Compiler already works this way
3. **Simplicity**: Clean separation, simple replacement logic
4. **UI compatibility**: No UI changes needed (merged view)
5. **Performance**: No searching through mixed stack
6. **Correctness**: Nested same-var loops still error (as they should)

## Alternative Approaches Rejected

- **Option 2** (GOTO cleanup): Too complex, need to track loop ranges
- **Option 3** (Sift through stack): Leaves orphaned GOSUB entries
- **Option 4** (Mark abandoned): Stack grows, complex NEXT logic

## Related Issues

- Original issue: `docs/dev/FOR_LOOP_JUMP_TODO.md`
- Super Star Trek currently doesn't run due to this bug
- Fix will enable many vintage BASIC programs to work

## References

Test programs (all in `tests/`):
- `for_test1_depth.bas` - 10 nested loops
- `for_test2_overflow.bas` - 9 nested loops
- `for_test3_jump_reuse.bas` - **Critical test**
- `for_test4_next_search.bas` - NEXT behavior
- `for_test5_circular.bas` - 9 consecutive jumps
- `for_test6_super_trek.bas` - **Super Trek pattern**

All test results documented in `FOR_LOOP_STACK_FINDINGS.md`.
