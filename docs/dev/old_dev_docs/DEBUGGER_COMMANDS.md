# MBASIC Debugger Commands Reference

## Quick Reference

When a breakpoint is hit, you have three options:

| Command | Key | Action |
|---------|-----|--------|
| **Continue** | `c` or `C` | Run until next breakpoint or end |
| **Step** | `s` or `S` | Execute one line, then stop |
| **End** | `e` or `E` or `ESC` | Stop execution |

## Setting Breakpoints

### Before Running
1. Position cursor on the line you want to break at
2. Press `b`
3. A `●` symbol appears next to the line number
4. Press `b` again to toggle off

### Visual Indicator
```
 10 PRINT "No breakpoint"
●20 PRINT "Breakpoint here"
 30 PRINT "No breakpoint"
```

## Running with Breakpoints

### Start Execution
- Press `Ctrl+R` to run the program
- Execution begins normally
- Stops when it hits a breakpoint

### At a Breakpoint
Status line shows:
```
BREAKPOINT at line 20 - Press 'c' continue, 's' step, 'e' end
```

Your options:

#### Continue (`c`)
- **What it does**: Resumes normal execution
- **When it stops**: At the next breakpoint (or program end)
- **Use case**: Skip over code you know is working
- **Example**:
  ```basic
  ●10 PRINT "Start"        ← Press c here
   20 FOR I = 1 TO 100
   30   PRINT I            (all 100 lines execute)
   40 NEXT I
  ●50 PRINT "End"          ← Stops here
  ```

#### Step (`s`)
- **What it does**: Executes exactly one line
- **When it stops**: At the very next line
- **Use case**: Carefully inspect each line's execution
- **Example**:
  ```basic
  ●10 PRINT "Start"        ← Press s here
  ●20 FOR I = 1 TO 5       ← Stops here (line 11 ran)
  ●30   PRINT I            ← Press s, stops here
  ●40 NEXT I               ← Press s, stops here
  ●20 FOR I = 1 TO 5       ← Stops here (loop continues)
  ```

#### End (`e`, `ESC`, or `Ctrl+C`)
- **What it does**: Stops execution immediately
- **Program state**: Partial output may be visible
- **Use case**: You've seen enough or found the bug

## Typical Debugging Workflows

### Workflow 1: Jump Between Checkpoints
```basic
●10 PRINT "Phase 1 start"
 20 REM ... 50 lines of code ...
 70 PRINT "Phase 1 done"
●80 PRINT "Phase 2 start"
 90 REM ... 50 lines of code ...
140 PRINT "Phase 2 done"
●150 PRINT "Final phase"
```
**Strategy**: Set breakpoints at phase boundaries, use `c` to jump between them

### Workflow 2: Zoom Into Problem Area
```basic
 10 X = 100
 20 Y = 200
●30 Z = X + Y
 40 PRINT Z
```
**Strategy**:
1. Breakpoint at suspicious line (30)
2. Press `c` to get there
3. Once there, use `s` to step through carefully
4. Press `e` when done investigating

### Workflow 3: Loop Debugging
```basic
●10 FOR I = 1 TO 10
  20   IF I = 5 THEN PRINT "Middle"
  30   PRINT I
  40 NEXT I
```
**Strategy**:
- First time through: Press `s` to watch iteration 1
- Second time: Press `s` a few more times to verify pattern
- When confident: Press `c` to finish all remaining iterations

## Execution Flow

```
[Start Program]
       ↓
   Execute line 10
       ↓
   Execute line 20
       ↓
● Hit breakpoint at line 30
       ↓
   [Wait for user]
       ↓
   Press 'c' ────→ Continue normally
       ↓               ↓
   Press 's' ────→ Step: execute line 30 only
       ↓               ↓
   Press 'e' ────→ STOP: Show partial results
```

## Advanced Usage

### Selective Execution
Set breakpoints strategically to execute only the code you want to test:
```basic
  10 PRINT "Always runs"
● 20 REM Breakpoint - press 'e' here to skip rest
  30 PRINT "Won't execute if you press 'e' at line 20"
```

### Skip Initialization Code
```basic
  10 REM Initialize
  20 DIM A(100)
  30 FOR I = 1 TO 100: A(I) = I: NEXT I
● 40 REM Start of actual logic
  50 PRINT "Processing..."
```
**Strategy**: Press `c` at line 40 to skip past initialization you know works

### Verify Loop Correctness
```basic
● 10 FOR I = 1 TO 5
  20   PRINT "I="; I
  30 NEXT I
```
**First iteration**: Press `s` multiple times to watch loop mechanics
**Remaining iterations**: Press `c` to let them complete

## Tips

1. **Start with 'c', switch to 's' when needed**: Use continue to get to the problem area, then switch to step for detailed inspection

2. **Set breakpoints liberally**: You can always skip them with 'c', but you can't add them while running

3. **Watch the output window**: It shows what executed between breakpoints

4. **Use 'e' to restart**: If you overshoot, press 'e', set new breakpoints, and run again

5. **Step mode persists**: Once you press 's', every line stops until you press 'c'

## Keyboard Shortcuts Summary

### Setting Breakpoints (Edit Mode)
- `b` - Toggle breakpoint on current line

### Running (Edit Mode)
- `Ctrl+R` - Run program (stops at first breakpoint)

### At Breakpoint (Debug Mode)
- `c` - Continue to next breakpoint
- `s` - Step one line
- `e` - End execution

### Always Available
- `Ctrl+Q` - Quit IDE
- `Ctrl+P` - Help

## Implementation Notes

- Breakpoints are **line-level**: They trigger when that line number is reached
- Step mode checks **before** executing each line
- Continue mode only checks at explicit breakpoint lines
- The main screen stays visible during debugging (no screen switching)
- Output accumulates in the output window as program executes

## See Also

- `CONTINUE_FEATURE.md` - Detailed continue feature documentation
- `BREAKPOINT_SUMMARY.md` - Overall breakpoint system overview
- `test_continue_manual.sh` - Interactive test to practice these commands
