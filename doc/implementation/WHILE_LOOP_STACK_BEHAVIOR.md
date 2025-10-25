# WHILE Loop Stack Behavior in MBASIC 5.21

**Date:** 2025-10-25
**Tested on:** Real MBASIC 5.21 via tnylpo CP/M emulator

## Executive Summary

Contrary to initial assumptions, **WHILE loops DO maintain a runtime stack** in MBASIC 5.21, similar to FOR loops. This was confirmed through testing on actual MBASIC 5.21.

## Key Findings

### 1. WHILE Loops Have a Stack ✅

**Test:** Jump into middle of WHILE loop (skip WHILE statement)
```basic
10 I = 0
20 GOTO 50
30 WHILE I < 3
40   I = I + 1
50   PRINT "I="; I
60 WEND
70 PRINT "Done"
80 SYSTEM
```

**Result:**
```
I= 0
WEND without WHILE in 60
```

**Proof:** The error "WEND without WHILE" proves that:
- WEND checks for a matching WHILE entry on a runtime stack
- Without executing WHILE first, the stack entry doesn't exist
- WEND cannot find its matching WHILE and reports an error

### 2. GOTO Does NOT Clean Up Loop Stacks ⚠️

**Test 1:** GOTO out of WHILE loop
```basic
10 I = 0
20 WHILE I < 10
30   I = I + 1
40   PRINT "I="; I
50   IF I = 3 THEN GOTO 100
60 WEND
70 PRINT "After WEND"
100 PRINT "After GOTO"
110 SYSTEM
```

**Result:**
```
I= 1
I= 2
I= 3
After GOTO
```

**Finding:** GOTO out of loop works. The WHILE stack entry remains (orphaned).

**Test 2:** GOTO out and back to WEND
```basic
10 I = 0
20 WHILE I < 3
30   I = I + 1
40   PRINT "Loop I="; I
50   IF I = 2 THEN GOTO 200
60 WEND
70 PRINT "After WHILE"
80 GOTO 300
200 PRINT "In GOTO I="; I
210 GOTO 60
300 PRINT "Done"
310 SYSTEM
```

**Result:**
```
Loop I= 1
Loop I= 2
In GOTO I= 2
Loop I= 3
After WHILE
Done
```

**Finding:**
- GOTO out leaves stack entry intact
- Returning to WEND via GOTO works because stack entry still exists
- WEND jumps back to WHILE (line 20) which re-evaluates condition

### 3. FOR and WHILE Intermix Freely ✅

**Test 1:** FOR containing WHILE
```basic
10 FOR I = 1 TO 2
20   J = 0
30   WHILE J < 2
40     J = J + 1
50     PRINT "I="; I; " J="; J
60   WEND
70 NEXT I
80 PRINT "Done"
90 SYSTEM
```

**Result:** Works correctly - both loops execute properly nested.

**Test 2:** WHILE containing FOR
```basic
10 I = 0
20 WHILE I < 2
30   I = I + 1
40   FOR J = 1 TO 2
50     PRINT "I="; I; " J="; J
60   NEXT J
70 WEND
80 PRINT "Done"
90 SYSTEM
```

**Result:** Works correctly - both loops execute properly nested.

**Finding:** FOR and WHILE maintain separate stacks that can be intermixed.

## Implementation Implications

### Current Implementation Status

**FOR loops (runtime.py:74):**
```python
self.for_loops = {}  # var_name -> {'end': val, 'step': val, 'return_line': line, 'return_stmt': idx}
```
- Dict keyed by variable name
- Python 3.7+ dict maintains insertion order
- Has `get_for_loop_stack()` method

**WHILE loops (runtime.py:75):**
```python
self.while_loops = []  # [{'while_line': line, 'while_stmt': idx}, ...]
```
- List (true stack)
- Has push/pop/peek methods
- **NO `get_while_loop_stack()` method** - asymmetry!

### Problem: Cannot Determine Interleaved Nesting Order

The current implementation cannot determine the true nesting order when FOR and WHILE are intermixed:

```basic
10 FOR I = 1 TO 3        ' Loop stack: [FOR I]
20   WHILE J < 5          ' Loop stack: [FOR I, WHILE J]
30     FOR K = 1 TO 2     ' Loop stack: [FOR I, WHILE J, FOR K]
40       ...
50     NEXT K              ' Loop stack: [FOR I, WHILE J]
60   WEND                  ' Loop stack: [FOR I]
70 NEXT I                  ' Loop stack: []
```

**Challenge:**
- `for_loops` is a dict - no timing info relative to WHILE loops
- `while_loops` is a list - has order info within itself
- No shared sequence/timestamp to interleave them

## Proposed Solutions

### Option 1: Add `get_while_loop_stack()` Only

Simple symmetric approach - just add the missing method:

```python
def get_while_loop_stack(self):
    """Export WHILE loop stack in nesting order."""
    return [{'line': loop['while_line']} for loop in self.while_loops]
```

**Pros:** Simple, matches existing pattern
**Cons:** Still can't see unified FOR/WHILE nesting

### Option 2: Unified `get_loop_stack()` with Sequence Tracking (RECOMMENDED)

Add a global sequence counter to track entry order of ALL loops:

```python
class Runtime:
    def __init__(self):
        self.loop_sequence = 0  # Global counter for all loops

    def push_for_loop(self, var_name, end_value, step_value, return_line, return_stmt_index):
        """Register a FOR loop"""
        self.for_loops[var_name] = {
            'end': end_value,
            'step': step_value,
            'return_line': return_line,
            'return_stmt': return_stmt_index,
            'sequence': self.loop_sequence  # ADD THIS
        }
        self.loop_sequence += 1

    def push_while_loop(self, while_line, while_stmt_index):
        """Register a WHILE loop"""
        self.while_loops.append({
            'while_line': while_line,
            'while_stmt': while_stmt_index,
            'sequence': self.loop_sequence  # ADD THIS
        })
        self.loop_sequence += 1

    def get_loop_stack(self):
        """Return all loops (FOR and WHILE) in true nesting order."""
        all_loops = []

        # Collect FOR loops
        for var_name, loop_info in self.for_loops.items():
            all_loops.append({
                'type': 'FOR',
                'var': var_name,
                'current': self.variables.get(var_name, 0),
                'end': loop_info['end'],
                'step': loop_info['step'],
                'line': loop_info['return_line'],
                'sequence': loop_info['sequence']
            })

        # Collect WHILE loops
        for loop_info in self.while_loops:
            all_loops.append({
                'type': 'WHILE',
                'line': loop_info['while_line'],
                'sequence': loop_info['sequence']
            })

        # Sort by sequence number (entry order)
        all_loops.sort(key=lambda x: x['sequence'])

        # Remove sequence from output (internal detail)
        for loop in all_loops:
            del loop['sequence']

        return all_loops
```

**Example output:**
```python
[
    {'type': 'FOR', 'var': 'i', 'current': 2, 'end': 3, 'step': 1, 'line': 10},
    {'type': 'WHILE', 'line': 20},
    {'type': 'FOR', 'var': 'k', 'current': 1, 'end': 2, 'step': 1, 'line': 30}
]
```

**Pros:**
- Shows true nesting order of all loop types
- More useful for debugging complex nested loops
- Minimal overhead (one integer counter)

**Cons:**
- Slightly more complex than Option 1
- Requires modifying both push_for_loop and push_while_loop

## GOTO Behavior Summary

| Scenario | Behavior | Stack State |
|----------|----------|-------------|
| GOTO out of FOR | Works, orphans stack entry | FOR entry remains |
| GOTO out of WHILE | Works, orphans stack entry | WHILE entry remains |
| GOTO back to NEXT (FOR) | Works if stack entry exists | Uses existing entry |
| GOTO back to WEND (WHILE) | Works if stack entry exists | Uses existing entry |
| GOTO into FOR (skip FOR) | Works but dangerous | No stack entry, NEXT may fail |
| GOTO into WHILE (skip WHILE) | **ERROR: "WEND without WHILE"** | No stack entry, WEND fails |

**Key difference:**
- FOR: Can partially work without stack entry (but broken)
- WHILE: Explicitly checks for stack entry, errors if missing

## FOR Loop Behavior (for comparison)

FOR loops also maintain a stack (dictionary), but behavior differs:

**Test:** GOTO out of FOR
```basic
10 FOR I = 1 TO 5
20   PRINT "I="; I
30   IF I = 3 THEN GOTO 100
40 NEXT I
50 PRINT "After FOR"
100 PRINT "After GOTO, I="; I
110 SYSTEM
```

**Result:**
```
I= 1
I= 2
I= 3
After GOTO, I= 3
```

**Finding:** FOR loop entry remains in `for_loops` dict, orphaned but harmless.

## Recommendations for Compiler Backend

### 1. Stack Management

When compiling WHILE/WEND:
- Maintain a WHILE loop stack at runtime (already implemented)
- Each WHILE pushes entry: `{while_line, while_stmt, sequence}`
- Each WEND pops entry and jumps back to WHILE
- WEND must validate stack entry exists (error if missing)

### 2. GOTO Handling

**DO NOT** clean up loop stacks on GOTO:
- This matches authentic MBASIC 5.21 behavior
- Allows GOTO back to middle of loop (rare but valid)
- Orphaned entries are harmless

### 3. Unified Loop Stack for Debugging

For debugging/inspection purposes:
- Implement `get_loop_stack()` with sequence tracking
- Shows true nesting order of FOR and WHILE loops intermixed
- Essential for visual debuggers and IDE integration

### 4. Validation

WHILE/WEND validation should happen at:
- **Parse time:** Ensure lexical pairing (WHILE has matching WEND)
- **Runtime:** WEND checks stack for matching WHILE, errors if missing

## Testing Methodology

All tests run using:
```bash
cd /home/wohl/cl/mbasic/tests
(cat test.bas && echo "RUN") | timeout 10 tnylpo ../com/mbasic
```

See `tests/HOW_TO_RUN_REAL_MBASIC.md` for details.

Test files created:
- `test_while_goto.bas` - GOTO out of WHILE
- `test_goto_into_while.bas` - GOTO into WHILE (error case)
- `test_while_goto_return.bas` - GOTO out and back to WEND
- `test_for_while_mix.bas` - FOR containing WHILE
- `test_while_for_mix.bas` - WHILE containing FOR
- `test_for_goto.bas` - GOTO out of FOR (comparison)

## Conclusion

WHILE loops in MBASIC 5.21:
1. ✅ **Have a runtime stack** (proven by "WEND without WHILE" error)
2. ✅ **Do NOT clean up on GOTO** (entries remain, can return to WEND)
3. ✅ **Can intermix with FOR loops** (separate stacks)
4. ⚠️ **Need sequence tracking** for unified loop stack view

This behavior should be preserved in the compiler backend for authentic MBASIC 5.21 compatibility.
