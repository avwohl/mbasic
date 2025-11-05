# Curses UI - Complete Feature Reference

This document covers all 36 features available in the Curses UI.

## File Operations (8 features)

### New Program (Ctrl+N)
Clear the current program and start fresh.

### Open/Load File (Ctrl+O)
Load a BASIC program from disk. Opens a file browser to select the file.

### Save File (Ctrl+V)
Save the current program to disk. If no filename is set, prompts for one.
Note: Uses Ctrl+V because Ctrl+S is reserved for terminal flow control.

### Save As (Shift+Ctrl+V)
Save the current program with a new filename.

### Recent Files (Ctrl+Shift+O)
View and load from a list of recently opened files.

### Auto-Save
The Curses UI automatically saves your work periodically to prevent data loss.

### Delete Lines (Ctrl+D)
Delete the current line in the editor.

### Merge Files
Merge another BASIC program into the current one. Useful for combining code modules.

## Execution & Control (6 features)

### Run Program (Ctrl+R)
Execute the current BASIC program from the beginning.

### Stop/Interrupt (Ctrl+X)
Stop a running program immediately.

### Continue (Ctrl+G)
Resume execution after hitting a breakpoint or stepping.

### List Program (Menu only)
Display the program listing in the editor. Access through the menu bar.

### Renumber (Ctrl+E)
Renumber all program lines with consistent increments. Opens a dialog to specify start line and increment.

### Auto Line Numbers
Automatically generate line numbers when entering new lines. Toggle on/off as needed.

## Debugging (6 features)

### Breakpoints (Ctrl+B)
Toggle a breakpoint on the current line. Execution will pause when reaching this line.
- Set: Click margin or press Ctrl+B
- Indicated by: ● symbol in line number margin

### Step Statement (Ctrl+T)
Execute one BASIC statement and pause. Useful for debugging complex lines with multiple statements.

### Step Line (Ctrl+K)
Execute the next line of code and pause. Advances one line number at a time.

### Clear All Breakpoints (Ctrl+Shift+B)
Remove all breakpoints from the program at once.

### Multi-Statement Debug
When stepping, the debugger highlights individual statements on lines with multiple statements (separated by :).

### Current Line Highlight
The currently executing line is highlighted with a cyan background during program execution.

## Variable Inspection (6 features)

### Variables Window (Ctrl+W)
Open/close the variables inspection window showing all program variables and their current values.

### Edit Variable Value (Limited - Not fully implemented)
⚠️ Variable editing is currently limited in Curses UI. You cannot directly edit values in the variables window. Use immediate mode commands to modify variable values instead.

### Variable Filtering (f key in variables window)
Filter the variables list to show only variables matching a search term.

### Variable Sorting (s key in variables window)
Cycle through different sort orders:
- **Accessed**: Most recently accessed (read or written) - newest first
- **Written**: Most recently written to - newest first
- **Read**: Most recently read from - newest first
- **Name**: Alphabetically by variable name

Press 'd' to toggle sort direction (ascending/descending).

### Execution Stack (Menu only)
View the call stack showing:
- Active GOSUB calls
- FOR/NEXT loops
- WHILE loops
Helps understand program flow and nesting levels.

**How to access:**
1. Press Ctrl+U to open the menu bar
2. Navigate to the Debug menu
3. Select "Execution Stack" option

Note: There is no dedicated keyboard shortcut to avoid conflicts with editor typing.

### Resource Usage
Monitor memory and variable usage in the status bar.

## Editor Features (6 features)

### Line Editing
Edit BASIC code line-by-line with full cursor navigation.

### Multi-Line Edit
Edit multiple lines at once in the full-screen editor.

### Cut/Copy/Paste (Not implemented)
Standard clipboard operations are not available in the Curses UI.
Note: Ctrl+X is used for Stop/Interrupt, Ctrl+C exits the program, and Ctrl+V is used for Save.
Use your terminal's native copy/paste functions instead (typically Shift+Ctrl+C/V or mouse selection).

### Find/Replace (Not yet implemented)
Find and Replace functionality is not yet available in Curses UI.
See [Find/Replace](find-replace.md) (available via menu) for workarounds and alternatives.

### Smart Insert (Ctrl+I)
Insert a new line number at the midpoint between the current line and the next line.
Example: Between lines 10 and 20, inserts line 15.

### Sort Lines
Lines are automatically kept in numerical order. Manual sorting is available if needed.

### Syntax Checking
Real-time syntax validation as you type. Syntax errors are marked with a '?' symbol in the line number margin.

## Help System (4 features)

### Help Command (?)
Display the main help screen with keyboard shortcuts and feature overview. Press ? to open help.

### Integrated Docs
Complete MBASIC language reference and UI guide built into the help system.

### Search Help
Search the help system for specific topics, commands, or keywords.

### Context Help
Press ? with cursor on a BASIC keyword to get help for that specific command.

## Quick Reference

### Most Used Shortcuts
| Shortcut | Action |
|----------|--------|
| Ctrl+N | New Program |
| Ctrl+O | Open File |
| Ctrl+V | Save File |
| Ctrl+R | Run Program |
| Ctrl+X | Stop Program |
| Ctrl+B | Toggle Breakpoint |
| Ctrl+T | Step Statement |
| Ctrl+K | Step Line |
| Ctrl+G | Continue |
| Ctrl+W | Variables Window |
| Menu only | Execution Stack |
| ? | Help |

### Status Bar Indicators
- **●** - Breakpoint set on line
- **?** - Syntax error on line
- **Cyan highlight** - Currently executing line

---

*See also: [Keyboard Shortcuts](../../../user/keyboard-shortcuts.md), [Getting Started](getting-started.md)*
