# FOR Loop Handling: Compiler vs Interpreter

## Date
2025-11-13

## Summary

The **compiler** and **interpreter** handle FOR loops fundamentally differently when jumping out of loops and reusing variables.

## Compiler Backend (z88dk C code generation)

### How It Works

The compiler generates **lexically-scoped C for loops**:

```c
line_30:
    for (i = 1; i <= 10; i += 1) {
        // loop body
        if (condition) {
            goto line_100;  // Jump out
        }
    }

line_100:
    // Can reuse 'i' here
    for (i = 1; i <= 5; i += 1) {
        // new loop body
    }
```

**Key characteristics**:
- No runtime "loop stack" tracking
- Variables are just C variables (lexically scoped)
- Jumping out of a loop is just a C `goto`
- Reusing a variable in a new FOR loop is just reusing the C variable
- **Already works correctly** for Super Star Trek pattern

### Generated Code Example

From `tests/for_test3_jump_reuse.bas`:

```c
line_30:
    for (i = 1; i <= 10; i += 1) {
line_40:
        printf("I=%g\n", i);
line_50:
        if ((i == 3)) {
            goto line_100;
        }
line_60:
    }

line_100:
    printf("Jumped out at I=%g\n", i);
line_110:
    printf("Starting new FOR I loop...\n");
line_120:
    for (i = 1; i <= 5; i += 1) {  // Reuses same 'i' variable
line_130:
        printf("New I=%g\n", i);
line_140:
    }
```

### Test Results

✅ **Test 3** (jump-reuse): Compiles and runs correctly
✅ **Test 6** (Super Trek): Compiles and runs correctly

**Conclusion**: Compiler backend has **no issue** with this pattern. It's purely lexical scoping.

## Interpreter (Runtime execution)

### Current Implementation (Has Bug)

The interpreter uses a **runtime execution stack** that tracks active FOR loops:

```python
# src/runtime.py lines 83-88
self.execution_stack = []  # Mixed: GOSUB, FOR, WHILE entries
self.for_loop_vars = {}    # Quick lookup: var_name -> stack index
```

**Problem**: When pushing a new FOR loop with a variable that's already on the stack:
1. Checks if `var_name in self.for_loop_vars` (line 996)
2. Raises error: "FOR loop variable already active"
3. This prevents Super Star Trek pattern from working

**Issue**: Old FOR might be deep in stack (not on top):
```
Stack: [FOR I (index 0), GOSUB (index 1), WHILE (index 2)]
         ↑ Can't pop this without breaking structure
```

### Proposed Fix (Option 1: Separate FOR Stack)

Split FOR loops into a **separate stack** from GOSUB/WHILE:

```python
# Separate stacks
self.for_loop_stack = []      # Only FOR loops (can be circular)
self.execution_stack = []     # Only GOSUB and WHILE
self.for_loop_vars = {}       # var_name -> index in for_loop_stack
```

**Implementation**:
```python
def push_for_loop(self, var_name, ...):
    # If variable already active, replace it (implicit cleanup)
    if var_name in self.for_loop_vars:
        old_index = self.for_loop_vars[var_name]
        self.for_loop_stack[old_index] = new_entry  # Replace in place
    else:
        self.for_loop_stack.append(new_entry)
        self.for_loop_vars[var_name] = len(self.for_loop_stack) - 1
```

**Benefit**: When starting new FOR I, it just replaces the old FOR I in the separate stack.

### After Fix

Post-fix behavior will match real MBASIC 5.21:

✅ Test 3: Jump out of FOR I, start new FOR I → Works
✅ Test 5: Do this 9 times consecutively → Works
✅ Test 6: Super Star Trek pattern → Works
❌ Nested FOR with same var (both active) → Still errors (correct)

## Comparison Table

| Aspect | Compiler | Interpreter (Current) | Interpreter (After Fix) |
|--------|----------|----------------------|------------------------|
| FOR loop tracking | Lexical (C scope) | Runtime stack | Runtime stack (separate) |
| Variable reuse | Automatic (C var) | ❌ Error | ✅ Replaces old entry |
| Jump out behavior | C goto | Stack stays | Stack stays |
| Super Trek pattern | ✅ Works | ❌ Error | ✅ Works |
| Implementation | None needed | Unified stack | Separate FOR stack |
| Nested same var | C compiler error | ✅ Runtime error | ✅ Runtime error |

## Why They Differ

**Compiler**:
- Generates static C code
- Relies on C's lexical scoping rules
- No runtime loop tracking needed
- Variables are just C variables

**Interpreter**:
- Executes dynamically at runtime
- Must track active control flow for:
  - NEXT statement matching
  - GOSUB/RETURN pairing
  - Error detection (improper nesting)
- Variables exist in runtime variable storage
- Needs explicit loop stack management

## Notes for Future

### Potential Circular Buffer

Real MBASIC may have used an 8-entry circular FOR loop buffer. If desired, we could implement this:

```python
MAX_FOR_LOOPS = 8
self.for_loop_stack = [None] * MAX_FOR_LOOPS  # Fixed size
self.for_loop_head = 0  # Circular index
```

However, tests show real MBASIC 5.21 supports at least 10 nested loops, so a fixed 8-entry limit doesn't match behavior. More likely real MBASIC just had a generous limit.

### WHILE/WEND Behavior

Needs separate testing to determine if WHILE/WEND has the same "jump out and reuse" behavior as FOR loops.

If yes, may need `self.while_loop_stack` as well.

## Related Files

**Compiler**:
- `src/codegen_backend.py` - Lines 1094-1123 (FOR/NEXT generation)
- `test_compile/test_compile.py` - Compilation test harness

**Interpreter**:
- `src/runtime.py` - Lines 83-1045 (execution stack management)
- `src/interpreter.py` - Line 1021 (GOTO implementation)

**Tests**:
- `tests/for_test3_jump_reuse.bas` - Critical test (jump and reuse)
- `tests/for_test6_super_trek.bas` - Super Star Trek pattern

**Documentation**:
- `docs/dev/FOR_LOOP_STACK_FINDINGS.md` - Test results from real MBASIC
- `docs/dev/FOR_LOOP_STACK_IMPLEMENTATION_OPTIONS.md` - Analysis of 4 fix options
- `docs/dev/FOR_LOOP_JUMP_TODO.md` - Original issue description
