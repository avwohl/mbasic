# Continue Feature - Breakpoint Debugger

## Overview

The MBASIC IDE curses interface includes a full breakpoint debugger with **continue** functionality. When a breakpoint is hit during program execution, you can:
- **Continue (c)** - Resume execution until the next breakpoint or program end
- **Step (s)** - Execute one line and stop again
- **End (e)** - Stop execution immediately

## How to Use Continue

### Setting Breakpoints
1. Open a BASIC program in the curses IDE:
   ```bash
   python3 mbasic --ui curses yourprogram.bas
   ```

2. Set breakpoints on the lines where you want to pause:
   - Move cursor to the desired line
   - Press **'b'** or **b**
   - A **●** symbol appears before the line number

3. You can set multiple breakpoints throughout your program

### Running with Continue

1. Press **Ctrl+R** to run the program

2. When execution hits the first breakpoint:
   ```
   BREAKPOINT at line 20 - Press 'c' continue, 's' step, 'e' end
   ```

3. Press **'c'** to **continue** execution:
   - Program resumes running normally
   - Stops at the next breakpoint (if any)
   - If no more breakpoints, runs to completion

4. Repeat step 3 at each breakpoint

### Example Session

```basic
10 PRINT "Starting..."
20 FOR I = 1 TO 5          ← Set breakpoint here
30   PRINT "I ="; I
40 NEXT I
50 PRINT "Done!"           ← Set breakpoint here
```

**Execution flow:**
1. Set breakpoints on lines 20 and 50
2. Press Ctrl+R - stops at line 20
3. Press 'c' - loop executes, stops at line 50
4. Press 'c' - program completes

## Commands at Breakpoint

When stopped at a breakpoint:

| Key | Action | Description |
|-----|--------|-------------|
| **c** or **C** | Continue | Resume until next breakpoint or end |
| **s** or **S** | Step | Execute current line, stop at next line |
| **e** or **E** | End | Stop execution immediately |
| **ESC** | End | Stop execution immediately |
| **Ctrl+C** | End | Stop execution immediately |

## Continue vs. Step

**Continue ('c')**:
- Runs at full speed
- Only stops at explicitly set breakpoints
- Best for: Skipping over known-good code sections
- Use when: You want to jump between key points in your program

**Step ('s')**:
- Executes one line at a time
- Stops after every single line
- Best for: Detailed inspection of program flow
- Use when: You want to watch every line execute

## Visual Feedback

During breakpoint pause:
- **Status line** at top shows: `BREAKPOINT at line XX - Press 'c' continue, 's' step, 'e' end`
- **Main screen** stays visible - you can see your code
- **Output window** shows output generated so far

After pressing 'c':
- Status line clears
- Execution resumes immediately
- Output continues to accumulate

## Tips

1. **Strategic breakpoints**: Set breakpoints at key points (loop starts, function calls, decision points)
2. **Combine with output**: Watch the output window to see what happened between breakpoints
3. **Remove breakpoints**: Press 'b' again on a line to toggle the breakpoint off
4. **Multiple breakpoints**: Set as many as you need - continue will stop at each one in order

## Testing

Run the manual test:
```bash
./test_continue_manual.sh
```

This launches an interactive test program where you can practice:
- Setting multiple breakpoints
- Using 'c' to continue between them
- Observing program state at each stop

## Implementation Details

The continue feature is implemented in:
- **src/ui/curses_ui.py** - `_breakpoint_hit()` method handles user input
- **src/interpreter.py** - Checks `self.step_mode` flag and breakpoint set
- When 'c' is pressed:
  - `self.step_mode = False` (disable step mode)
  - Returns `True` (continue execution)
  - Interpreter only stops at explicit breakpoints

## Known Limitations

- Cannot set breakpoints while program is running
- Breakpoints are line-level only (can't break within compound statements on same line)
- No variable inspection yet (planned feature)
- Input during debugging not fully supported

## Future Enhancements

Planned features:
- [ ] Variable watch window
- [ ] Expression evaluation at breakpoint
- [ ] Conditional breakpoints
- [ ] Breakpoint hit counts
- [ ] Call stack display
