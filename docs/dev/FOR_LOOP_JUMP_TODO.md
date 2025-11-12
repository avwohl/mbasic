# FOR Loop Jump Behavior TODO

## Issue

MBASIC interpreter raises error when jumping out of a FOR loop without completing it, then starting a new FOR loop with the same variable elsewhere.

**Error**: `FOR loop variable {var_name} already active - nested FOR loops with same variable not allowed`

## Reproduction Case

Super Star Trek lines 2080-2160:

```basic
2080 FOR I=1 TO 9:IF LEFT$(A$,3)<>MID$(A1$,3*I-2,3)THEN 2160
2140 ON I GOTO 2300,1980,4000,4260,4700,5530,5690,7290,6270
2160 NEXT I
```

When user enters a command, code loops through options. If match found, jumps via ON...GOTO to handler code. Some handler routines also use variable I for their own FOR loops.

**Common Pattern**: Early BASIC and FORTRAN code commonly reused I, J, K for loop variables across different parts of the program due to FORTRAN's implicit typing rules (I-N = integers).

## Current Behavior

Runtime error raised when:
1. FOR I loop starts at line 2080
2. Code jumps out via ON...GOTO (e.g., to line 4000)
3. Target line starts new FOR I loop
4. Error: "FOR loop variable I already active"

## Expected Behavior (Real MBASIC)

Need to investigate how real MBASIC 5.21 handles this:
- Does jumping out of a FOR loop automatically close it?
- Can you start a new FOR loop with same variable after jumping out?
- What happens to the loop stack?

## Possible Implementation Detail

User recalls reading that real MBASIC used a **circular 8-level buffer for FOR loops**.

This could explain the behavior:
- Fixed-size circular buffer (8 nested loops max)
- When jumping out of a loop, the buffer entry might be marked as inactive but not removed
- Starting a new FOR loop with same variable would overwrite the old entry in the buffer
- This would naturally allow variable reuse after jumping out

Need to verify this implementation detail and whether it affects the behavior.

## Investigation Steps

1. **Test with real MBASIC**: Use `tests/HOW_TO_RUN_REAL_MBASIC.md` to run Super Star Trek
   - Enter commands that trigger the jump
   - Observe whether error occurs
   - Check variable I value after jump

2. **Check MBASIC documentation**: Look for formal specification on:
   - FOR loop exit behavior
   - GOTO/ON GOTO interaction with FOR loops
   - Loop stack management
   - Circular 8-level buffer implementation (if documented)

3. **Test edge cases**:
   - Jump out of FOR loop, never return, start new FOR with same variable
   - Jump out of nested FOR loops
   - GOSUB from inside FOR loop that starts new FOR with same variable

## Likely Solution

Jumping out of a FOR loop (via GOTO, ON GOTO, etc.) should probably:
- Remove that loop from the active FOR loop stack
- Allow the loop variable to be reused elsewhere

This would match the common pattern in 1970s-80s BASIC code where loop variables were freely reused.

## Files to Check

- `src/runtime.py` - FOR loop stack management (line with error message)
- `src/interpreter.py` - GOTO/ON GOTO implementation
- `src/statements/control_flow.py` - FOR/NEXT implementation

## Related Issues

This is separate from nested FOR loops with same variable (which should remain an error):
```basic
10 FOR I=1 TO 10
20   FOR I=1 TO 5  ' ERROR - nested with same variable
30   NEXT I
40 NEXT I
```

But jumping out should be allowed:
```basic
10 FOR I=1 TO 10
20   IF I=5 THEN GOTO 100
30 NEXT I
100 FOR I=1 TO 5  ' Should be OK - previous loop exited
110 NEXT I
```
