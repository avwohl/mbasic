---
title: MBASIC Tkinter GUI Help
type: guide
ui: tk
description: Complete guide to the MBASIC graphical user interface
keywords: [help, tk, tkinter, gui, graphical, interface, editor, debugger]
---

# MBASIC Tkinter GUI - Complete Guide

The Tkinter GUI provides a full-featured graphical development environment for MBASIC 5.21 programming with an integrated editor, debugger, and variable inspector.

## Quick Start

**Start the GUI:**
```bash
python3 mbasic.py --backend tk [filename.bas]
```

**Your First Program:**
1. Type: `10 PRINT "HELLO, WORLD!"`
2. Press **{{kbd:run_program}}** to run
3. See output in the lower pane

## Interface Overview

```
┌────────────────────────────────────────────────────┐
│ Menu Bar: File, Edit, Run, View, Help             │
├─────────┬──────────────────────────────────────────┤
│ Line #  │  Editor Window                           │
│  Gutter │  - Write your BASIC program here         │
│         │  - Line numbers in left gutter           │
│  10     │  - Breakpoints marked with ●             │
│  20  ●  │  - Syntax errors marked with ?           │
│  30  ?  │  - Current execution line highlighted    │
│         │                                           │
├─────────┴──────────────────────────────────────────┤
│ Output Window                                      │
│ - Program output appears here                      │
│ - Error messages and status                        │
└────────────────────────────────────────────────────┘
```

### Optional Windows

- **Variables Window** ({{kbd:toggle_variables}}) - Shows all variables and their values
- **Resources Window** ({{kbd:toggle_resources}}) - Shows FILES open, memory usage
- **Execution Stack** ({{kbd:toggle_stack}}) - Shows FOR loops and GOSUB calls

## Essential Features

### 1. Smart Insert ({{kbd:smart_insert}})

**The fastest way to add code between existing lines!**

You have:
```basic
10 PRINT "START"
20 PRINT "END"
```

Want to add something between them?

1. Click on line 10
2. Press {{kbd:smart_insert}}
3. A blank line 15 is automatically inserted!

Result:
```basic
10 PRINT "START"
15 [cursor here - ready to type]
20 PRINT "END"
```

**No more mental math!** Smart Insert calculates the midpoint for you.

**If lines are consecutive** (like 10, 11, 12), Smart Insert offers to renumber the program automatically to make room.

### 2. Syntax Checking

The editor continuously checks your syntax as you type (with a 100ms delay to avoid disruption).

**Syntax Error Markers:**
- Red **?** appears in line number gutter
- Error message appears in output pane
- Fix the syntax → **?** disappears automatically

**Common errors caught:**
- Missing quotes in strings
- Missing THEN in IF statements
- Typos in keywords
- Invalid operators

### 3. Breakpoints and Debugging

**Set breakpoints:**
- **Mouse**: Click line number in gutter
- **Keyboard**: Position cursor, press {{kbd:toggle_breakpoint}}
- **Visual**: Blue ● appears in gutter

**Debug controls:**
- {{kbd:run_program}} - Run program from start
- {{kbd:step_statement}} - Execute next statement (steps INTO subroutines)
- {{kbd:step_line}} - Execute next line (steps OVER subroutines)
- {{kbd:continue_execution}} - Continue running until next breakpoint
- {{kbd:stop_program}} - Stop execution

**During debugging:**
- Current execution point highlighted in yellow
- Variables window updates in real-time
- Execution stack shows active loops and GOSUB calls

### 4. Statement Highlighting

When stepping through code, MBASIC highlights **what will execute next**, not what just executed.

**Example:**
```basic
10 PRINT "A"
20 PRINT "B"  ← Highlighted when paused here
30 PRINT "C"
```

At a breakpoint on line 20, you see line 20 highlighted BEFORE it executes, letting you:
- See what's about to happen
- Check variable values before execution
- Decide whether to step or continue

**Multi-statement lines:**
```basic
10 PRINT "A": X=5: GOSUB 100: PRINT "B"
```

Use {{kbd:step_statement}} to step through each statement individually.
Use {{kbd:step_line}} to execute the entire line at once.

### 5. Variables Window ({{kbd:toggle_variables}})

Shows all program variables with:
- **Name** - Variable name as you typed it (case preserved!)
- **Value** - Current value
- **Type** - integer, float, string, array

**Features:**
- Click column headers to sort (Name, Value, Type)
- Filter box to search for specific variables
- Updates automatically during debugging
- Case-preserved display (TargetAngle, not TARGETANGLE)

**Example:**
```basic
10 TargetAngle = 45
20 Distance = 100.5
30 Name$ = "ROBOT"
40 DIM Scores(10)
```

Variables window shows:
```
Name         | Value  | Type
-------------|--------|--------
TargetAngle  | 45     | integer
Distance     | 100.5  | float
Name$        | ROBOT  | string
Scores       | (array)| array
```

### 6. Execution Stack ({{kbd:toggle_stack}})

Shows active control structures:

**Example program:**
```basic
10 FOR I = 1 TO 3
20   FOR J = 1 TO 2
30     GOSUB 100
40   NEXT J
50 NEXT I
100 PRINT I; J
110 RETURN
```

**Stack display at line 100:**
```
FOR I=1 TO 3 STEP 1  [I=2]
  FOR J=1 TO 2 STEP 1  [J=1]
    GOSUB from line 30
```

Perfect for understanding:
- Nested loop state
- Subroutine call chains
- Current loop variable values
- Return addresses

### 7. Renumber Program ({{kbd:renumber}})

Reorganize line numbers while automatically updating all GOTO/GOSUB references!

**Before:**
```basic
10 X=1
15 Y=2
17 GOTO 10
21 END
```

Press {{kbd:renumber}}, set Start=100, Increment=10:

**After:**
```basic
100 X=1
110 Y=2
120 GOTO 100  ← Automatically updated!
130 END
```

**Updates these references:**
- GOTO line_number
- GOSUB line_number
- ON expr GOTO line1, line2, ...
- ON expr GOSUB line1, line2, ...
- IF condition THEN line_number
- ON ERROR GOTO line_number
- RESTORE line_number
- RESUME line_number
- ERL comparisons in expressions

### 8. Find and Replace ({{kbd:find_replace}})

Search and replace text across your program:

1. Press {{kbd:find_replace}}
2. Enter find text: "OLDVAR"
3. Enter replace text: "NEWVAR"
4. Click "Replace All" or step through with "Find Next"

**Search options:**
- Case sensitive/insensitive
- Whole word matching
- Regular expression support (advanced)

## File Operations

### Save and Load

**Save:** {{kbd:save_file}} or File → Save
**Save As:** File → Save As...
**Open:** {{kbd:open_file}} or File → Open
**New:** {{kbd:new_program}} or File → New

**Supported formats:**
- `.bas` - ASCII text BASIC programs (recommended)
- `.txt` - Plain text files
- All files - Any text file

### Auto-Save

The editor does NOT auto-save. Remember to save often with {{kbd:save_file}}!

**Best practice:** Save after each successful test run.

## Keyboard Shortcuts

### Essential Shortcuts

| Shortcut | Action |
|----------|--------|
| {{kbd:run_program}} | Run program from start |
| {{kbd:save_file}} | Save current file |
| {{kbd:open_file}} | Open file |
| {{kbd:new_program}} | New program |
| {{kbd:smart_insert}} | Insert blank line between existing lines |
| {{kbd:renumber}} | Renumber program |

### Debugging Shortcuts

| Shortcut | Action |
|----------|--------|
| {{kbd:toggle_breakpoint}} | Toggle breakpoint on current line |
| {{kbd:step_statement}} | Step to next statement |
| {{kbd:step_line}} | Step to next line |
| {{kbd:continue_execution}} | Continue execution (go) |
| {{kbd:stop_program}} | Stop execution |

### Window Shortcuts

| Shortcut | Action |
|----------|--------|
| {{kbd:toggle_variables}} | Show/hide Variables window |
| {{kbd:toggle_resources}} | Show/hide Resources window |
| {{kbd:toggle_stack}} | Show/hide Execution Stack |

### Editing Shortcuts

| Shortcut | Action |
|----------|--------|
| {{kbd:find_replace}} | Find and replace |
| {{kbd:undo}} | Undo last edit |
| {{kbd:redo}} | Redo last undo |
| {{kbd:cut}} | Cut selected text |
| {{kbd:copy}} | Copy selected text |
| {{kbd:paste}} | Paste from clipboard |

See [Keyboard Shortcuts](keyboard-shortcuts.md) for complete list.

## Settings and Configuration

Control program behavior using the settings system:

### Variable Case Handling

```basic
' View current setting
SHOW SETTINGS "variables.case_conflict"

' Change policy
SET "variables.case_conflict" "first_wins"   ' Default: first case wins
SET "variables.case_conflict" "error"        ' Strict: flag conflicts as errors
SET "variables.case_conflict" "prefer_upper" ' Prefer UPPERCASE
SET "variables.case_conflict" "prefer_lower" ' Prefer lowercase
SET "variables.case_conflict" "prefer_mixed" ' Prefer CamelCase

' Get help on a setting
HELP SET "variables.case_conflict"
```

**Example - Error mode catches typos:**
```basic
SET "variables.case_conflict" "error"
10 TotalCount = 0
20 TotalCont = 1  ' ERROR: Typo detected (TotalCont vs TotalCount)!
```

### Keyword Case Handling

```basic
' View current setting
SHOW SETTINGS "keywords.case_style"

' Change keyword display
SET "keywords.case_style" "force_lower"      ' print, for, if (default)
SET "keywords.case_style" "force_upper"      ' PRINT, FOR, IF
SET "keywords.case_style" "force_capitalize" ' Print, For, If (modern)
SET "keywords.case_style" "first_wins"       ' First occurrence wins
SET "keywords.case_style" "preserve"         ' Keep as typed
```

**Example - Modern capitalized style:**
```basic
SET "keywords.case_style" "force_capitalize"
10 Print "Hello"   ' Displayed as: Print (not PRINT or print)
20 For I = 1 To 10 ' Displayed as: For...To (not FOR...TO)
```

### All Settings

View all settings:
```basic
SHOW SETTINGS
```

View settings in a category:
```basic
SHOW SETTINGS "variables"
SHOW SETTINGS "keywords"
SHOW SETTINGS "editor"
```

## Common Workflows

### 1. Write New Program

1. Press {{kbd:new_program}}
2. Type: `10 PRINT "START"`
3. Press Enter
4. Type: `20 END`
5. Press {{kbd:run_program}}
6. Check output in lower pane
7. Press {{kbd:save_file}} when done

### 2. Expand Existing Program

You have a working program and need to add functionality:

1. Find the insertion point
2. Press {{kbd:smart_insert}} to insert blank line
3. Type your new code
4. Press {{kbd:run_program}} to test
5. Press {{kbd:save_file}} when done

### 3. Debug with Breakpoints

1. Click line number gutter to set breakpoint (● appears)
2. Press {{kbd:toggle_variables}} to open Variables window
3. Press {{kbd:run_program}}
4. Program stops at breakpoint
5. Check variable values
6. Press {{kbd:step_statement}} to step through code
7. Watch variables update in real-time
8. Press {{kbd:continue_execution}} to continue

### 4. Fix Syntax Errors

1. Look for red **?** in line number gutter
2. Read error message in output pane
3. Fix the syntax on that line
4. **?** disappears automatically (100ms delay)
5. Press {{kbd:run_program}} to test

### 5. Renumber Before Sharing

Your development version has messy line numbers:
```basic
10 PRINT "START"
15 X=1
17 Y=2
21 GOTO 50
50 END
```

Make it clean:
1. Press {{kbd:renumber}}
2. Set Start=10, Increment=10
3. Click "Renumber"

Result:
```basic
10 PRINT "START"
20 X=1
30 Y=2
40 GOTO 50
50 END
```

## Tips and Tricks

### Smart Insert for Rapid Development

**Scenario:** You have a skeleton and need to flesh it out:
```basic
10 REM Initialize
100 REM Process
200 REM Output
300 END
```

Use {{kbd:smart_insert}} to add details under each section without calculating line numbers!

### Variables Window for Arrays

When working with arrays, keep Variables window open:
```basic
10 DIM Scores(5)
20 FOR I = 1 TO 5
30   INPUT "Score"; Scores(I)
40 NEXT I
```

Run with {{kbd:toggle_variables}} window open - see each array element as it fills!

### Execution Stack for Nested Loops

Press {{kbd:toggle_stack}} while stepping through nested loops:
```basic
10 FOR I = 1 TO 3
20   FOR J = 1 TO 2
30     PRINT I; J
40   NEXT J
50 NEXT I
```

The stack shows current state of both loops!

### Quick Testing Cycle

Fastest workflow for iterative development:
```
Type → {{kbd:run_program}} → Check → Edit → {{kbd:run_program}} → Check → ...
```

No need to save between test runs! Save with {{kbd:save_file}} only when happy.

### Use Comments Liberally

MBASIC supports two comment styles:
```basic
10 REM This is a remark statement
20 ' This is also a comment (shorter!)
```

Add comments while developing with {{kbd:smart_insert}}.

## Common Mistakes to Avoid

❌ **Manually calculating line numbers** → Use {{kbd:smart_insert}} instead
❌ **Running without saving first** → Save with {{kbd:save_file}}
❌ **Ignoring ? markers** → Fix syntax errors before running
❌ **Not using Variables window** → You're debugging blind!
❌ **Stepping through entire program** → Set breakpoints, use {{kbd:continue_execution}}

## Advanced Features

### Control Flow Visualization

The highlight automatically jumps to show where execution is going:

```basic
10 PRINT "Start"
20 GOSUB 100
30 PRINT "End"   ← Highlights here after RETURN
40 END
100 PRINT "Sub"
110 RETURN
```

**What you see:**
1. Step at line 20 → Highlights GOSUB 100
2. Step again → Highlight jumps to line 100
3. Step through 100, 110
4. Step at RETURN → Highlight jumps to line 30

This makes control flow visible and easy to follow!

### Edit-at-Breakpoint Safety

**What happens:** You hit a breakpoint in a FOR loop, edit the loop, and continue.

**MBASIC protects you:**
- Validates all active loop return addresses
- If edit breaks loop structure, shows warning
- Prevents crashes from editing code mid-execution

**Safe:** Edit unrelated code while paused
**Warning:** Edit code currently on the execution stack

### Resource Monitoring

Press {{kbd:toggle_resources}} to see:
- Open files (OPEN statement)
- File handles in use
- Memory usage (future)

Useful for debugging file I/O programs!

## Getting Help

- **In-app help**: Press {{kbd:help_topics}} or Help → Help Topics
- **Online docs**: See `docs/` directory
- **Quick start guide**: `docs/user/TK_UI_QUICK_START.md`
- **Examples**: Check `basic/` directory
- **Issues**: Report at GitHub repository

## BASIC Language Reference

Complete BASIC-80 language documentation:

- [Language Overview](../../common/language/index.md) - Introduction to BASIC-80
- [Operators](../../common/language/operators.md) - Arithmetic, logical, relational
- **Statements** - All 63 BASIC-80 statements
  - [Statements Index](../../common/language/statements/index.md)
  - Organized by category: input-output, control-flow, file-io
- **Functions** - All 40 BASIC-80 functions
  - [Functions Index](../../common/language/functions/index.md)
  - Organized by category: mathematical, string, type-conversion
- **Appendices** - Reference materials
  - [Error Codes](../../common/language/appendices/error-codes.md)
  - [ASCII Table](../../common/language/appendices/ascii-codes.md)

## About MBASIC

- [MBASIC Index](../../mbasic/index.md) - Overview and navigation
- [Getting Started](../../mbasic/getting-started.md) - Your first BASIC program
- [Features](../../mbasic/features.md) - What's implemented
- [Compatibility](../../mbasic/compatibility.md) - MBASIC 5.21 differences
- [Architecture](../../mbasic/architecture.md) - How MBASIC works

---

**Welcome to MBASIC Tk UI!** Start with simple programs, use {{kbd:smart_insert}} to build them up, and explore the debugging features. You'll be productive in minutes!
