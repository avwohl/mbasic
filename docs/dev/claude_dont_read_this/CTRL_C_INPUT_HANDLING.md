# Ctrl+C Handling During INPUT

## Overview

When a user presses Ctrl+C (^C) during an INPUT or LINE INPUT statement, the interpreter now returns to command mode (or stops execution with a "Break" message), allowing the user to use CONT to resume or examine the program state.

## Implementation

### Changes Made

#### 1. Created BreakException class (src/interpreter.py:15-17)

```python
class BreakException(Exception):
    """Raised when user presses Ctrl+C to break execution"""
    pass
```

This custom exception signals that a user-initiated break occurred, distinguishing it from other errors.

#### 2. Modified execute_input() (src/interpreter.py:1024-1030)

```python
# Read input
try:
    line = input()
except KeyboardInterrupt:
    # User pressed Ctrl+C during input - break to command mode
    print()  # Newline after ^C
    raise BreakException()
```

When KeyboardInterrupt is caught during INPUT, it's converted to BreakException.

#### 3. Modified execute_lineinput() (src/interpreter.py:1124-1129)

Same handling for LINE INPUT statements:

```python
try:
    line = input()
except KeyboardInterrupt:
    # User pressed Ctrl+C during input - break to command mode
    print()  # Newline after ^C
    raise BreakException()
```

#### 4. Modified _run_loop() exception handling (src/interpreter.py:143-149)

```python
except BreakException:
    # User pressed Ctrl+C during INPUT - handle like break
    self.runtime.stopped = True
    self.runtime.stop_line = self.runtime.current_line
    self.runtime.stop_stmt_index = self.runtime.current_stmt_index
    print(f"Break in {self.runtime.current_line.line_number if self.runtime.current_line else '?'}")
    return
```

When BreakException is caught, the interpreter:
- Sets stopped = True (enables CONT)
- Saves the current line and statement position
- Prints "Break in {line}"
- Returns to command mode

## Behavior

### Interactive Mode

```basic
10 INPUT "Enter your name"; N$
20 PRINT "Hello, "; N$
RUN
```

**Interaction:**
```
Enter your name? ^C
Break in 10
Ok
CONT
Enter your name? Bob
Hello, Bob
Ok
```

### File Execution Mode

When running from a file with `python3 mbasic program.bas`, pressing Ctrl+C during INPUT will:
1. Print a newline
2. Print "Break in {line}"
3. Return control (program exits since there's no interactive prompt)

## Technical Details

### Why BreakException Instead of KeyboardInterrupt?

1. **Signal Handler Compatibility**: The interpreter sets up a SIGINT signal handler during execution that sets `break_requested = True`. However, Python's `input()` function is special - it will raise KeyboardInterrupt when Ctrl+C is pressed, even with a custom signal handler.

2. **Clean Error Handling**: Using a custom BreakException allows us to distinguish between:
   - User-initiated breaks (BreakException) - returns to command mode
   - Program errors (RuntimeError, etc.) - handled by ON ERROR GOTO if present
   - Other interrupts (KeyboardInterrupt) - would be caught by signal handler in other contexts

3. **Consistent with STOP Behavior**: BreakException is handled exactly like the STOP statement - setting stopped=True and saving execution position for CONT.

### Input() and Signals

Python's `input()` function behavior with signals:
- When Ctrl+C is pressed during `input()`, Python raises KeyboardInterrupt
- This happens even if a custom SIGINT handler is installed
- The custom signal handler is bypassed for `input()` specifically
- This is Python's design to ensure users can always interrupt input

## Compatibility

### What Works
- `INPUT var` - Break during input returns to command mode
- `INPUT "prompt"; var` - Break during prompted input
- `LINE INPUT "prompt", var$` - Break during line input
- CONT after break - Resumes at the same INPUT statement

### What Doesn't Work (By Design)
- Breaking during file INPUT (#n) - Not applicable since file I/O doesn't wait for user
- Breaking in non-interactive file execution - Program exits (no command mode to return to)

## Testing

### Manual Test

```basic
10 REM Test Ctrl+C during INPUT
20 PRINT "Press Ctrl+C at the INPUT prompt"
30 INPUT "Enter something"; A$
40 PRINT "You entered: "; A$
50 END
```

1. Run the program: `python3 mbasic`
2. Load it: `LOAD "tests/test_break_input.bas"`
3. Execute: `RUN`
4. At the INPUT prompt, press Ctrl+C
5. Expected: "Break in 30" appears, returns to Ok prompt
6. Type: `CONT`
7. Enter a value
8. Expected: Program continues and completes

## Future Enhancements

Potential improvements:
1. Handle Ctrl+C during PRINT statements (currently handled by outer break_requested check)
2. Configurable break behavior (e.g., END vs STOP behavior)
3. Break counter (show how many times user has broken)

## Related Files

- src/interpreter.py - BreakException class and INPUT handling
- src/runtime.py - stopped, stop_line, stop_stmt_index fields
- src/interactive.py - Command mode and CONT implementation
