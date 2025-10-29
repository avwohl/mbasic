# Curses UI - Complete Feature Reference

This document covers all 37 features available in the Curses UI.

## File Operations (8 features)

### New Program (Ctrl+N)
Clear the current program and start fresh.

### Open/Load File (Ctrl+O)
Load a BASIC program from disk. Opens a file browser to select the file.

### Save File (Ctrl+S)
Save the current program to disk. If no filename is set, prompts for one.

### Save As (Ctrl+Shift+S)
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

### List Program (Ctrl+L)
Display the program listing in the editor.

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

### Step Line (Ctrl+L when paused)
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

### Edit Variable Value (e key in variables window)
Modify a variable's value during debugging. Select a variable and press 'e' to edit.

### Variable Filtering (f key in variables window)
Filter the variables list to show only variables matching a search term.

### Variable Sorting (s key in variables window)
Cycle through different sort orders:
- By name (alphabetical)
- By type (Integer, Single, Double, String)
- By value
- By last modified

Press 'd' to reverse sort direction.

### Execution Stack (Ctrl+K)
View the call stack showing:
- Active GOSUB calls
- FOR/NEXT loops
- WHILE loops
Helps understand program flow and nesting levels.

### Resource Usage
Monitor memory and variable usage in the status bar.

## Editor Features (7 features)

### Line Editing
Edit BASIC code line-by-line with full cursor navigation.

### Multi-Line Edit
Edit multiple lines at once in the full-screen editor.

### Cut/Copy/Paste
Standard clipboard operations using system clipboard:
- Cut: Ctrl+X
- Copy: Ctrl+C
- Paste: Ctrl+V

### Find/Replace (Ctrl+F / Ctrl+H)
Search for text in your program and optionally replace it.
- Case-sensitive or insensitive search
- Whole word matching
- Replace single or replace all

### Smart Insert (Ctrl+I)
Insert a new line number at the midpoint between the current line and the next line.
Example: Between lines 10 and 20, inserts line 15.

### Sort Lines
Lines are automatically kept in numerical order. Manual sorting is available if needed.

### Syntax Checking
Real-time syntax validation as you type. Syntax errors are marked with a '?' symbol in the line number margin.

## Help System (4 features)

### Help Command (Ctrl+H)
Display the main help screen with keyboard shortcuts and feature overview.

### Integrated Docs
Complete MBASIC language reference and UI guide built into the help system.

### Search Help
Search the help system for specific topics, commands, or keywords.

### Context Help
Press Ctrl+H with cursor on a BASIC keyword to get help for that specific command.

## Quick Reference

### Most Used Shortcuts
| Shortcut | Action |
|----------|--------|
| Ctrl+N | New Program |
| Ctrl+O | Open File |
| Ctrl+S | Save File |
| Ctrl+R | Run Program |
| Ctrl+X | Stop Program |
| Ctrl+B | Toggle Breakpoint |
| Ctrl+T | Step Statement |
| Ctrl+L | Step Line |
| Ctrl+G | Continue |
| Ctrl+W | Variables Window |
| Ctrl+K | Execution Stack |
| Ctrl+H | Help |

### Status Bar Indicators
- **●** - Breakpoint set on line
- **?** - Syntax error on line
- **Cyan highlight** - Currently executing line

---

*See also: [Keyboard Commands](keyboard-commands.md), [Getting Started](getting-started.md)*
