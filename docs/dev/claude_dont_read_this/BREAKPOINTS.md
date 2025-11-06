# Breakpoint System

The curses IDE includes a visual breakpoint debugger.

## Setting Breakpoints

There are three ways to set a breakpoint:

1. **Press 'b' key** - Toggle breakpoint on the current line (where cursor is)
2. **Press b** - Toggle breakpoint on the current line
3. **Mouse click** - Click on the ● symbol or space at the start of a line

When a breakpoint is set, you'll see a ● symbol appear before the line number:

```
●10 PRINT "This line has a breakpoint"
 20 PRINT "This line does not"
```

## Using Breakpoints

1. Set one or more breakpoints using any of the methods above
2. Press **Ctrl+R** to run your program
3. When execution reaches a breakpoint, a status message appears at the top:
   ```
   BREAKPOINT at line 10 - Press 'c' continue, 's' step, 'e' end
   ```
4. Choose your action:
   - **'c'** - Continue to next breakpoint or end of program
   - **'s'** - Step to next line (stops at every line)
   - **'e'** - End execution and return to editor
5. The main IDE screen stays visible during debugging

## Example Session

```basic
10 FOR I = 1 TO 5
20 PRINT "Count: "; I
30 NEXT I
```

1. Position cursor on line 20
2. Press 'b' to set breakpoint (● appears)
3. Press Ctrl+R to run
4. Program pauses at line 20 each time through the loop
5. Press 'c' to continue to next iteration
6. Press 's' to stop debugging

## Tips

- Breakpoints are preserved during the session
- Toggle a breakpoint off by pressing 'b' again on that line
- You can set multiple breakpoints
- The ● indicator shows which lines have breakpoints
