---
title: Debugging Features
type: guide
description: Complete guide to debugging BASIC programs with breakpoints, stepping, and statement-level execution
keywords: [debug, debugger, breakpoint, step, statement, highlighting, variables, stack, execution]
---

# Debugging Features

MBASIC includes a full-featured debugger with breakpoints, single-stepping, variable inspection, and statement-level execution tracking.

## Overview

The debugger helps you:
- Find and fix bugs in your programs
- Understand how your code executes
- Inspect variable values during execution
- Step through code line by line or statement by statement
- Track subroutine calls and loop state

## Breakpoints

### What are Breakpoints?

Breakpoints pause program execution at specific lines, allowing you to inspect the program state.

### Setting Breakpoints

| UI | Method | Indicator |
|----|--------|-----------|
| **Tk UI** | Click line number gutter, or **Ctrl+B** on line | **●** indicator |
| **Curses UI** | Position cursor on line and press **b** | **●** indicator |
| **Web UI** | Click line number or use toolbar "Breakpoint" button | **●** indicator + pink background |

### Removing Breakpoints

- Click/press again on the same line to remove the breakpoint
- The **●** indicator will disappear

### Priority Indicators

Line number indicators follow this priority:
1. **? (Question mark)** - Parse error (highest priority)
2. **● (Bullet)** - Breakpoint
3. **(Space)** - Normal line

If a line has both an error and a breakpoint, the **?** error indicator is shown.

## Stepping Through Code

### Step Types

**Step Line** - Execute one entire line, then pause
- Even if the line has multiple statements (separated by `:`), all statements execute
- Useful for quick navigation through code
- Shortcuts: Tk/Curses/Web: **Ctrl+T** or Step button

**Step Statement** - Execute one statement, then pause
- If a line has multiple statements (e.g., `A=1 : B=2 : C=3`), each statement executes separately
- Allows fine-grained control for debugging complex lines
- The current statement is highlighted (see Statement Highlighting below)
- Shortcuts: Same as Step Line, but advances statement-by-statement

### Using Step Commands

1. **Set a breakpoint** or start execution
2. When paused at a breakpoint:
   - Press **Ctrl+T** or click **Step** to advance one statement
   - Press **Ctrl+G** or click **Continue** to run to next breakpoint
   - Press **Ctrl+Q** or click **Stop** to halt execution

## Statement Highlighting

### What is Statement Highlighting?

BASIC allows multiple statements on one line, separated by colons:
```basic
100 A = 1 : B = 2 : PRINT A + B
```

Statement highlighting shows exactly which statement is currently executing within a multi-statement line.

### How It Works

When stepping through code, the debugger:
1. Highlights the current line being executed
2. If the line has multiple statements, highlights the specific statement
3. Updates the highlight as you step through each statement

### Visual Indicators by UI

**Tk UI:**
- Current statement highlighted with **yellow background**
- Highlight covers just the executing statement, not the whole line
- Auto-scrolls to keep the statement visible

**Curses UI:**
- Shows statement index in status bar: `Line 100 statement 2`
- Current statement passed to editor for highlighting
- Compact display for terminal environment

**Web UI:**
- Shows statement index in status label: `Paused at line 100 statement 2`
- Status updates as you step through statements
- Also shows `[stmt N]` during continuous execution

### Example

```basic
10 REM Multi-statement line example
20 A = 5 : B = 10 : C = A + B : PRINT "C="; C
30 END
```

When you step through line 20:
1. First step: `A = 5` highlighted
2. Second step: `B = 10` highlighted
3. Third step: `C = A + B` highlighted
4. Fourth step: `PRINT "C="; C` highlighted
5. Fifth step: Advances to line 30

## Continue Execution

After pausing at a breakpoint:
- Press **Ctrl+G** or click **Continue**
- Program runs until:
  - Next breakpoint is hit
  - Program ends
  - Runtime error occurs

## Variables Window

### Opening Variables Window

**Tk UI:** Debug → Variables or **Ctrl+V**
**Curses UI:** **Ctrl+V** during execution
**Web UI:** Debug → Variables Window or Variables button

### What It Shows

- All variables currently defined in your program
- Variable names, types, and current values
- Array elements with subscript access tracking
- Last modified timestamp

### Variable Types

- **Integer (%):** Whole numbers (e.g., `COUNT%`)
- **Single (!):** Single-precision floating point (default for numbers)
- **Double (#):** Double-precision floating point (e.g., `PI#`)
- **String ($):** Text values (e.g., `NAME$`)

### Editing Variables

You can change variable values during debugging:

**Tk UI:**
- Double-click variable in the table
- Enter new value in the dialog
- Click OK to update

**Curses UI:**
- Press **e** or **Enter** on selected variable
- Type new value
- Press Enter to confirm

**Web UI:**
- Click "Edit Selected" button
- Or double-click the variable row
- Enter new value in the dialog
- Click OK to update

### Array Variables

Arrays show with their dimensions:
- `A(10)` - One-dimensional array, 10 elements
- `B(5,5)` - Two-dimensional array, 5×5
- Last accessed subscript tracked
- Can edit individual array elements

### Sorting Variables

Click column headers to sort by:
- Name (alphabetical)
- Type (grouped by %, !, #, $)
- Value (numerical/alphabetical)
- Modified (most recent first)

## Execution Stack Window

### Opening Stack Window

**Tk UI:** Debug → Execution Stack or **Ctrl+K**
**Curses UI:** **Ctrl+K** during execution
**Web UI:** Debug → Stack Window or Stack button

### What It Shows

The execution stack tracks:
- Active FOR loops (variable, current value, target, step)
- GOSUB subroutine calls (return address)
- Nested loop state
- Call hierarchy

### Stack Display

**FOR Loops:**
```
FOR I = 1 TO 10 STEP 2
  Variable: I
  Current: 5
  To: 10
  Step: 2
```

**GOSUB Calls:**
```
GOSUB 1000
  Return to: 500
```

**Nested Items:**
- Innermost items at top
- Outer items below
- Shows full nesting structure

## Common Debugging Workflows

### Finding a Bug

1. **Reproduce the error** - Run the program and see it fail
2. **Set breakpoints** - Put breakpoints near where you think the bug is
3. **Run to breakpoint** - Let the program run until it pauses
4. **Inspect variables** - Check variable values in the Variables window
5. **Step through code** - Use Step Statement to see each operation
6. **Fix and retest** - Modify the code and try again

### Understanding Complex Code

1. **Set breakpoint at start** - Put a breakpoint on the first line
2. **Step statement-by-statement** - Use Step Statement to see each operation
3. **Watch the variables** - Keep Variables window open
4. **Track the flow** - Follow execution through GOTOs and GOSUBs
5. **Check the stack** - Use Execution Stack for loops and subroutines

### Testing a Subroutine

1. **Set breakpoint at GOSUB** - Pause before calling the subroutine
2. **Step into subroutine** - Use Step to enter the GOSUB
3. **Watch the stack** - See the return address in Execution Stack
4. **Inspect changes** - Check what the subroutine modifies
5. **Verify return** - Ensure it returns to the right place

## Tips and Tricks

### Multi-Statement Lines

- Use **Step Statement** instead of **Step Line** for fine control
- Watch the statement highlighting to see what's executing
- Set breakpoints before multi-statement lines to pause at the start

### Infinite Loops

- Press **Ctrl+C** or **Stop** button to interrupt
- Set a breakpoint inside the loop to inspect state
- Check loop counters in the Variables window

### Variable Inspection

- Edit variables to test "what if" scenarios
- Watch array subscripts to see access patterns
- Sort by "Modified" to see what changed recently

### GOTO/GOSUB Tracking

- Use breakpoints to catch unexpected jumps
- Check Execution Stack to see where you came from
- Verify GOSUB/RETURN pairs match up

## Error Markers

### Parse Errors

Lines with syntax errors show with a **?** marker:
- Appears in line number gutter
- Takes priority over breakpoint markers
- Red color/background in Tk and Web UIs
- Shown on all lines that fail to parse

### Fixing Errors

1. **Identify error lines** - Look for **?** markers
2. **Read error message** - Check the output window for details
3. **Fix the syntax** - Correct the BASIC code
4. **Verify fix** - The **?** marker disappears when syntax is valid

### Background Validation

**Tk UI:** Validates syntax automatically as you type (100ms delay after cursor movement)
**Web UI:** Validates when you load files, sort, or renumber
**Curses UI:** Validates when you save or run

## Keyboard Shortcuts Summary

### All UIs

| Action | Shortcut | Notes |
|--------|----------|-------|
| Run program | **Ctrl+R** | Start from beginning |
| Step | **Ctrl+T** | One statement at a time |
| Continue | **Ctrl+G** | Run to next breakpoint |
| Stop | **Ctrl+Q** | Halt execution |

### Tk UI Only

| Action | Shortcut | Notes |
|--------|----------|-------|
| Toggle breakpoint | **Ctrl+B** | On current line |
| Variables window | **Ctrl+V** | Show/hide variables |
| Stack window | **Ctrl+K** | Show/hide stack |

### Curses UI Only

| Action | Shortcut | Notes |
|--------|----------|-------|
| Toggle breakpoint | **b** | On current line |
| Variables window | **Ctrl+V** | During execution |
| Stack window | **Ctrl+K** | During execution |
| Edit variable | **e** or **Enter** | In variables window |

### Web UI

Most actions use buttons or menus. Execution shortcuts (Ctrl+R, Ctrl+T, Ctrl+G, Ctrl+Q) work.

## See Also

- [Keyboard Shortcuts](shortcuts.md) - Complete shortcut reference
- [Editor Commands](editor-commands.md) - Editing features
- [Getting Started](getting-started.md) - Your first program
- [Language Reference](language/index.md) - BASIC-80 language

## Testing Statement Highlighting

Try this test program:

```basic
10 REM Multi-statement test
20 PRINT "A"; : PRINT "B"; : PRINT "C"
30 A = 1 : B = 2 : C = A + B
40 PRINT "A="; A; " B="; B; " C="; C
50 FOR I = 1 TO 3 : PRINT I; : NEXT I
60 END
```

Set a breakpoint on line 20 and use **Step Statement** to see each statement highlight individually.

---

**Pro tip:** Master the Step Statement command and Variables window - they're your most powerful debugging tools!
