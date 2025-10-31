# MBASIC Tk UI - Quick Start Guide

## Starting the Tk UI

```bash
python3 mbasic --backend tk [filename.bas]
```

Or simply:
```bash
python3 mbasic [filename.bas]
```

The Tk UI is the default graphical interface for MBASIC.

## First Program - Hello World

1. Start the Tk UI: `python3 mbasic --backend tk`
2. In the editor window, type:
   ```basic
   10 PRINT "HELLO, WORLD!"
   20 END
   ```
3. Press **Ctrl+R** to run
4. See output in the lower pane

## Essential Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| **Ctrl+R** | Run program |
| **Ctrl+S** | Save file |
| **Ctrl+O** | Open file |
| **Ctrl+N** | New program |
| **Ctrl+I** | Smart insert blank line |
| **Ctrl+E** | Renumber program |
| **Ctrl+V** | Show/hide Variables window |
| **Ctrl+W** | Show/hide Variables & Resources window |
| **Ctrl+K** | Show/hide Execution Stack window |
| **Ctrl+T** | Step through code (next statement) |
| **Ctrl+L** | Step through code (next line) |
| **Ctrl+G** | Continue execution (go) |
| **Ctrl+B** | Toggle breakpoint |
| **Ctrl+H** | Find and replace |

## Screen Layout

```
┌────────────────────────────────────────────────────┐
│ Menu Bar                                           │
├─────────┬──────────────────────────────────────────┤
│ Line #  │  Editor Window                           │
│  Gutter │  - Write your BASIC program here         │
│         │  - Line numbers on left                  │
│  10     │  - Syntax errors marked with ?           │
│  20  ●  │  - Breakpoints marked with ●             │
│  30  ?  │                                           │
│         │                                           │
├─────────┴──────────────────────────────────────────┤
│ Output Window                                      │
│ - Program output appears here                      │
│ - Error messages shown here                        │
│ - Execution status displayed                       │
└────────────────────────────────────────────────────┘
```

## Smart Insert Workflow

**Smart Insert (Ctrl+I)** is the fastest way to add code between existing lines. No more mental math to figure out line numbers!

### Example 1: Basic Usage

You have this program:
```basic
10 PRINT "START"
20 PRINT "END"
```

Want to add a line between them?

1. Click on line 10 (or position cursor anywhere on that line)
2. Press **Ctrl+I**
3. A blank line 15 is automatically inserted!

Result:
```basic
10 PRINT "START"
15
20 PRINT "END"
```

The cursor is positioned right after the line number, ready to type.

### Example 2: No Gap - Auto Renumber

You have consecutive lines:
```basic
10 PRINT "ONE"
11 PRINT "TWO"
12 PRINT "THREE"
```

Position cursor on line 10, press **Ctrl+I**:

A dialog appears: "No room between lines 10 and 11. Would you like to renumber the program to make room?"

Click **Yes** → Lines 11 onwards are renumbered to 1000, 1010, 1020... creating plenty of room!

Result:
```basic
10 PRINT "ONE"
15
1000 PRINT "TWO"
1010 PRINT "THREE"
```

### Example 3: At End of Program

You have:
```basic
10 PRINT "START"
20 PRINT "MIDDLE"
30 PRINT "END"
```

Cursor on line 30, press **Ctrl+I**:

A blank line 40 is inserted (using standard increment of 10).

Result:
```basic
10 PRINT "START"
20 PRINT "MIDDLE"
30 PRINT "END"
40
```

### Smart Insert vs Manual Numbering

**Old way (manual):**
```
1. Look at line 10 and line 20
2. Calculate: (10 + 20) / 2 = 15
3. Type: "15 PRINT ..."
```

**New way (Smart Insert):**
```
1. Position on line 10
2. Press Ctrl+I
3. Start typing your code
```

**Time saved:** ~5-10 seconds per line insertion. Over a programming session, this adds up!

## Typical Workflows

### 1. Write New Program

```
1. Press Ctrl+N for new program
2. Type first line: 10 PRINT "START"
3. Press Enter
4. Type next line: 20 END
5. Press Ctrl+R to run
6. Check output in lower pane
7. Press Ctrl+S to save
```

### 2. Expand Existing Program

You have a working program and need to add functionality:

```
1. Find the spot where new code goes
2. Press Ctrl+I to insert blank line
3. Type your new code
4. Press Ctrl+R to test
5. Press Ctrl+S to save
```

**Example:**
```basic
Before:
10 INPUT "Enter number"; N
20 PRINT "You entered"; N
30 END

After (cursor on 10, Ctrl+I twice):
10 INPUT "Enter number"; N
15 IF N < 0 THEN PRINT "Must be positive" : GOTO 10
17 ' Validate input
20 PRINT "You entered"; N
30 END
```

### 3. Major Restructuring - Use Renumber

Your program has grown and line numbers are a mess:

```
1. Press Ctrl+E (Renumber dialog opens)
2. Set "Start at": 100
3. Set "Increment": 10
4. Click "Renumber"
5. All line numbers and GOTO/GOSUB references updated!
```

**Before renumber:**
```basic
10 X=1
15 Y=2
17 GOTO 10
21 END
```

**After renumber (start=100, increment=10):**
```basic
100 X=1
110 Y=2
120 GOTO 100
130 END
```

Notice: GOTO 10 automatically became GOTO 100!

### 4. Debug with Breakpoints and Variables

```
1. Click line number gutter to set breakpoint (● appears)
2. Press Ctrl+V to open Variables window
3. Press Ctrl+R to run
4. Program stops at breakpoint
5. Check variable values in Variables window
6. Press Ctrl+T to step through code
7. Watch variables update in real-time
8. Press Ctrl+G to continue running
```

**Variables Window Features:**
- Click column headers to sort (Name, Value, Type)
- Shows all variables and their current values
- **Displays variables with original case** (TargetAngle, not targetangle)
- Updates automatically as you step
- Types displayed (integer, float, string, array)
- Filter box to search for specific variables

### 5. Advanced Editing - Find and Replace

Large program with repeated code?

```
1. Press Ctrl+H (Find and Replace)
2. Enter find text: "OLDVAR"
3. Enter replace text: "NEWVAR"
4. Click "Replace All"
5. All occurrences updated
```

## Common Tasks

### Load, Edit, Save

```bash
# Start with existing file
python3 mbasic --backend tk myprogram.bas

# Or load from menu
1. Press Ctrl+O
2. Browse to file
3. Click Open
4. Edit in editor
5. Press Ctrl+S to save
```

### Create Program Template

```basic
10 REM Program: [Name]
20 REM Author: [Your Name]
30 REM Date: [Date]
40 REM Purpose: [Description]
50 REM
100 ' Initialize variables
110
200 ' Main program
210
900 ' Subroutines
910
1000 END
```

Use **Ctrl+I** to fill in sections!

### Fix Syntax Errors

Red **?** markers appear in line number gutter for syntax errors:

```
1. Look for ? in gutter
2. Read error in output pane
3. Fix the syntax
4. ? disappears automatically (100ms delay)
5. Press Ctrl+R to run
```

**Common errors:**
- Missing quotes: `PRINT HELLO` → `PRINT "HELLO"`
- Missing THEN: `IF X=1 GOTO 100` → `IF X=1 THEN GOTO 100`
- Typos: `PIRNT` → `PRINT`

### Work with Arrays

```basic
10 DIM A(10)
20 FOR I = 1 TO 10
30   A(I) = I * 10
40 NEXT I
50 PRINT A(5)
60 END
```

Run with **Ctrl+R**, then check Variables window (**Ctrl+V**) to see array contents!

## Variable Case Preservation (New in October 2025)

MBASIC now preserves the original case of your variables while maintaining case-insensitive behavior!

### How It Works

```basic
10 TargetAngle = 45
20 targetangle = 90  ' Same variable, different case
30 PRINT TargetAngle  ' Displays "TargetAngle = 90"
```

**What you see:**
- Variables window shows: `TargetAngle = 90` (using first case seen)
- All references use the same display case
- Lookups remain case-insensitive (BASIC compatibility)

### Configure Case Behavior

Use the settings system to control how case conflicts are handled:

```basic
' View current setting
SHOW SETTINGS "case"

' Change policy
SET "variables.case_conflict" "error"        ' Strict: flag conflicts
SET "variables.case_conflict" "first_wins"   ' Default: first case wins
SET "variables.case_conflict" "prefer_upper" ' Prefer UPPERCASE
SET "variables.case_conflict" "prefer_lower" ' Prefer lowercase
SET "variables.case_conflict" "prefer_mixed" ' Prefer CamelCase

' Get help on a setting
HELP SET "variables.case_conflict"
```

### Example: Catching Typos with Error Mode

```basic
SET "variables.case_conflict" "error"
10 TotalCount = 0
20 FOR I = 1 TO 10
30   TotalCont = TotalCont + I  ' ERROR: Typo detected!
40 NEXT I
```

With error mode enabled, MBASIC catches the typo at line 30 immediately!

**Learn more:** See `docs/user/SETTINGS_AND_CONFIGURATION.md` for complete settings guide.

---

## Improved Debugging Features (October 2025)

The TK UI now provides enhanced debugging with intuitive statement highlighting.

### Next-Statement Highlighting

When stepping through code or hitting a breakpoint, MBASIC highlights **what will execute next**, not what just executed.

**Example:**
```basic
10 PRINT "A"
20 PRINT "B"  ' ← Highlighted when you pause here
30 PRINT "C"
```

When you hit a breakpoint on line 20, you see line 20 highlighted BEFORE it executes. This lets you:
- See what's about to happen
- Examine variable values before the statement runs
- Decide whether to step or continue

### Control Flow Visualization

The highlight automatically jumps to show where execution is going during GOSUB, RETURN, GOTO, NEXT, etc.

**Example:**
```basic
10 PRINT "Start"
20 GOSUB 100
30 PRINT "End"   ' ← Highlights here after RETURN
40 END
100 PRINT "Sub"
110 RETURN
```

**What you see:**
1. Step at line 20 → Highlights GOSUB 100
2. Step again → Highlight jumps to line 100 (subroutine entry)
3. Step through 100, 110
4. Step at RETURN → Highlight jumps to line 30 (statement AFTER the GOSUB)

This makes control flow visible and easy to follow!

### Mid-Line Statement Stepping

For lines with multiple statements (colon-separated), stepping shows exactly which statement will execute:

```basic
10 PRINT "A": X=5: GOSUB 100: PRINT "B": END
```

Use **Ctrl+T** (step statement) to move through each part:
1. `PRINT "A"` ← First
2. `X=5` ← Second
3. `GOSUB 100` ← Third (jumps to subroutine)
4. After RETURN: `PRINT "B"` ← Resumes here (not at start of line)
5. `END` ← Last

Use **Ctrl+L** (step line) to execute the entire line at once.

### Execution Stack Window

Press **Ctrl+K** to see the execution stack showing active loops and subroutine calls:

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
- Nested loops
- Subroutine call chains
- Current loop variable values
- Return addresses

---

## Tips and Tricks

### 1. Smart Insert for Rapid Development

**Scenario:** You have a skeleton program and need to flesh it out.

```basic
10 REM Initialize
100 REM Process
200 REM Output
300 END
```

Use Smart Insert (Ctrl+I) to add details under each section header without worrying about line numbers!

### 2. Renumber Before Sharing

Your development version might have messy line numbers:
```basic
10 PRINT "START"
15 X=1
17 Y=2
21 GOTO 50
50 END
```

Before sharing, make it clean:
1. Press **Ctrl+E**
2. Start=10, Increment=10
3. Result:
```basic
10 PRINT "START"
20 X=1
30 Y=2
40 GOTO 50
50 END
```

### 3. Use Comments Liberally

MBASIC supports two comment styles:
```basic
10 REM This is a remark statement
20 ' This is also a comment (shorter!)
```

Add comments while developing with Smart Insert:
```basic
10 X = 5
' Ctrl+I here creates line 15
15 ' Calculate result
20 Y = X * 10
```

### 4. Variables Window for Arrays

When working with arrays, keep Variables window open:

```basic
10 DIM SCORES(5)
20 FOR I = 1 TO 5
30   INPUT "Score"; SCORES(I)
40 NEXT I
```

Run this with **Ctrl+V** window open - you'll see each array element as it's filled!

### 5. Execution Stack for Loops

Press **Ctrl+K** to see Execution Stack while stepping through nested loops:

```basic
10 FOR I = 1 TO 3
20   FOR J = 1 TO 2
30     PRINT I; J
40   NEXT J
50 NEXT I
```

The stack shows:
```
FOR I=1 TO 3 STEP 1  [I=1]
  FOR J=1 TO 2 STEP 1  [J=1]
```

Perfect for debugging complex loop logic!

### 6. Quick Testing Cycle

Fastest workflow for iterative development:

```
Type → Ctrl+R → Check → Edit → Ctrl+R → Check → ...
```

No need to save between test runs! Save with **Ctrl+S** only when you're happy with results.

### 7. Breakpoint Shortcuts

**Mouse:** Click line number to toggle breakpoint
**Keyboard:** Position cursor, press **Ctrl+B**

Try both and use whichever feels faster!

## Next Steps

### Learn More About...

- **Debugging**: See [Debugging Features](../help/common/debugging.md)
- **Keyboard Shortcuts**: See [Tk Keyboard Shortcuts](../help/ui/tk/keyboard-shortcuts.md)
- **BASIC Language**: See [Language Reference](../help/common/language/index.md)
- **Editor Features**: See [Editor Commands](../help/common/editor-commands.md)

### Try These Sample Programs

Start with simple examples in `basic/` directory:

```bash
python3 mbasic --backend tk basic/hello.bas
python3 mbasic --backend tk basic/loops.bas
python3 mbasic --backend tk basic/arrays.bas
```

### Master These Skills

In order of importance:

1. **Smart Insert (Ctrl+I)** - Essential for efficient editing
2. **Run/Step/Continue (Ctrl+R/T/G)** - Core debugging workflow
3. **Variables Window (Ctrl+V)** - See what your program is doing
4. **Renumber (Ctrl+E)** - Keep code organized
5. **Breakpoints (Ctrl+B)** - Stop at critical points
6. **Save Often (Ctrl+S)** - Protect your work

### Common Mistakes to Avoid

❌ **Manually calculating line numbers** → Use Smart Insert instead
❌ **Running without saving** → Save first with Ctrl+S
❌ **Ignoring ? markers** → Fix syntax errors before running
❌ **Not using Variables window** → You're debugging blind!
❌ **Stepping through entire program** → Set breakpoints, use Continue

## Getting Help

- **In-app help**: Press **F1** or use Help menu
- **Online docs**: See `docs/` directory
- **Examples**: Check `basic/` directory
- **Issues**: Report at GitHub repository

---

**Welcome to MBASIC!** Start with simple programs, use Smart Insert to build them up, and explore the debugging features. You'll be productive in minutes!
