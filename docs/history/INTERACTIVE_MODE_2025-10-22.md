# MBASIC 5.21 Interactive Mode

**Date**: 2025-10-22
**Status**: ✓ Complete and working

---

## Overview

The MBASIC interpreter now supports full interactive mode, allowing you to:
- Enter and edit program lines
- Run programs
- Save and load programs
- Use direct commands (LIST, NEW, DELETE, RENUM, etc.)

---

## Usage

### Starting Interactive Mode

```bash
python3 mbasic
```

You'll see:
```
MBASIC 5.21 Interpreter
Ready

```

### Running a File Directly

```bash
python3 mbasic program.bas
```

---

## Interactive Commands

### Program Entry

**Numbered lines** - Add or replace program lines:
```basic
10 PRINT "Hello"
20 FOR I = 1 TO 10
30 PRINT I
40 NEXT I
50 END
```

**Delete a line** - Enter just the line number:
```basic
30
```
(Deletes line 30)

### Direct Commands

#### RUN
Execute the program in memory:
```
RUN
```

#### LIST [range]
List program lines:
```
LIST            ' List entire program
LIST 100        ' List line 100 only
LIST 100-200    ' List lines 100 through 200
LIST 100-       ' List from line 100 to end
LIST -200       ' List from start to line 200
```

#### NEW
Clear program from memory:
```
NEW
```
Response: `Ready`

#### SAVE "filename"
Save program to file:
```
SAVE "myprogram.bas"
```
- Adds `.bas` extension if not present
- Response: `Saved to myprogram.bas`

#### LOAD "filename"
Load program from file:
```
LOAD "myprogram.bas"
```
- Adds `.bas` extension if not present
- Clears current program first
- Response: `Loaded from myprogram.bas` then `Ready`

#### DELETE start-end
Delete a range of lines:
```
DELETE 100-200  ' Delete lines 100 through 200
DELETE 50-      ' Delete from line 50 to end
DELETE -100     ' Delete from start to line 100
```

#### RENUM [start][,increment]
Renumber program lines:
```
RENUM           ' Renumber starting at 10, increment 10
RENUM 100       ' Renumber starting at 100, increment 10
RENUM 100,20    ' Renumber starting at 100, increment 20
```
Response: `Renumbered`

#### SYSTEM (or BYE)
Exit to operating system:
```
SYSTEM
```
or
```
BYE
```
Response: `Goodbye`

#### AUTO [start][,increment]
Automatic line numbering mode:
```
AUTO            ' Auto number from 10, increment 10
AUTO 100        ' Start at 100, increment 10
AUTO 100,5      ' Start at 100, increment 5
AUTO ,20        ' Start at 10, increment 20
```

In AUTO mode:
- Type statements without line numbers
- AUTO adds the line number automatically
- Shows `*number` if line already exists (collision)
- Press Enter on empty line to exit AUTO mode
- Ctrl+C or Ctrl+D also exits

Example:
```
AUTO
10 PRINT "Hello"
20 FOR I = 1 TO 10
30 PRINT I
40 ← (press Enter to exit)
```

### Immediate Mode

Execute a statement without a line number:
```basic
PRINT 2 + 2
```
Output: ` 4`

---

## Example Session

```
$ python3 mbasic
MBASIC 5.21 Interpreter
Ready

10 REM Calculate factorial
20 INPUT "Enter a number"; N
30 F = 1
40 FOR I = 1 TO N
50 F = F * I
60 NEXT I
70 PRINT "Factorial of"; N; "is"; F
80 END
LIST
10 REM Calculate factorial
20 INPUT "Enter a number"; N
30 F = 1
40 FOR I = 1 TO N
50 F = F * I
60 NEXT I
70 PRINT "Factorial of"; N; "is"; F
80 END
SAVE "factorial.bas"
Saved to factorial.bas
RUN
Enter a number? 5
Factorial of 5  is 120
SYSTEM
Goodbye
```

---

## Implementation Details

### Files

- **src/interactive.py** (305 lines) - Interactive REPL implementation
- **mbasic** - Updated to support both file and interactive modes

### InteractiveMode Class

```python
class InteractiveMode:
    def __init__(self):
        self.lines = {}          # line_number -> line_text
        self.current_file = None

    def start(self):
        """Main REPL loop"""
        # Read input, process lines and commands

    def process_line(self, line):
        """Handle numbered lines or direct commands"""
        # Check if numbered line or command

    def execute_command(self, cmd):
        """Dispatch to command handler"""
        # RUN, LIST, NEW, SAVE, LOAD, etc.
```

### Command Implementation

Each command has a dedicated handler:

- `cmd_run()` - Parse and execute program
- `cmd_list(args)` - List with range support
- `cmd_new()` - Clear program
- `cmd_save(filename)` - Save to file
- `cmd_load(filename)` - Load from file
- `cmd_delete(args)` - Delete range
- `cmd_renum(args)` - Renumber lines
- `cmd_system()` - Exit
- `execute_immediate(stmt)` - Run statement directly

### Line Storage

Lines are stored in a dictionary:
```python
self.lines = {
    10: "10 PRINT \"Hello\"",
    20: "20 FOR I = 1 TO 10",
    30: "30 PRINT I",
    40: "40 NEXT I",
    50: "50 END"
}
```

When running or saving, lines are sorted and concatenated.

---

## Error Handling

### Graceful Error Messages

```
?Syntax error
?File not found: missing.bas
?NEXT without FOR
?Undefined line number: 9999
```

### Keyboard Interrupt

- **Ctrl+C** - Cancels current operation, prints `Break`
- **Ctrl+D** - Exits interactive mode (same as SYSTEM)

---

## MBASIC 5.21 Compatibility

### Supported Commands (from manual)

✓ RUN - Execute program
✓ LIST - List program
✓ NEW - Clear program
✓ SAVE - Save to file
✓ LOAD - Load from file
✓ DELETE - Delete range (MBASIC uses DELETE, not BASIC's DELETE)
✓ RENUM - Renumber lines
✓ SYSTEM - Exit

✓ AUTO - Auto line numbering mode

### Not Yet Implemented

⚠ EDIT - Line editor
⚠ LLIST - List to printer
⚠ MERGE - Merge program from file
⚠ CONT - Continue after STOP
⚠ TRON/TROFF - Trace mode
⚠ FILES - List disk files
⚠ KILL - Delete file
⚠ NAME - Rename file

---

## Testing

### Tests Performed

✓ Program entry (numbered lines)
✓ Line deletion
✓ RUN command
✓ LIST command (full and ranges)
✓ SAVE command
✓ LOAD command
✓ NEW command
✓ DELETE command
✓ RENUM command
✓ SYSTEM command
✓ Immediate mode PRINT
✓ FOR/NEXT loops
✓ GOSUB/RETURN
✓ Operator precedence

### Known Issues

None currently.

---

## Future Enhancements

1. **AUTO command** - Auto line numbering
2. **EDIT command** - Full-screen line editor
3. **MERGE command** - Merge programs
4. **CONT command** - Continue after STOP
5. **Command history** - Up/down arrow for previous commands
6. **Tab completion** - Complete commands and filenames
7. **Syntax highlighting** - Color-coded display

---

## Summary

The interactive mode provides a complete MBASIC 5.21 programming environment:

- ✓ Full REPL with line editing
- ✓ Program save/load
- ✓ Direct command execution
- ✓ Immediate mode expressions
- ✓ Error recovery
- ✓ Compatible with MBASIC 5.21 conventions

**Status**: Production ready for basic use.
