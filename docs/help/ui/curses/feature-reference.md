# Curses UI - Complete Feature Reference

This document covers all features available in the Curses UI, organized by category.

## File Operations (7 features)

### New Program ({{kbd:new:curses}})
Clear the current program and start fresh.

### Open/Load File ({{kbd:open:curses}})
Load a BASIC program from disk. Opens a file browser to select the file.

### Save File ({{kbd:save:curses}})
Save the current program to disk. If no filename is set, prompts for one.
Note: Uses {{kbd:save:curses}} because {{kbd:save:curses}} is reserved for terminal flow control.

### Save As (Shift+{{kbd:save:curses}})
Save the current program with a new filename.

### Recent Files ({{kbd:save:curses}}hift+O)
View and load from a list of recently opened files.

### Auto-Save
The Curses UI automatically saves your work periodically to prevent data loss.

### Merge Files
Merge another BASIC program into the current one. Useful for combining code modules.

## Execution & Control (6 features)

### Run Program ({{kbd:run:curses}})
Execute the current BASIC program from the beginning.

### Stop/Interrupt ({{kbd:stop:curses}})
Stop a running program immediately.

### Continue ({{kbd:goto_line:curses}})
Resume execution after hitting a breakpoint or stepping.

### List Program (Menu only)
Display the program listing in the editor. Access through the menu bar.

### Renumber (Ctrl+E)
Renumber all program lines with consistent increments. Opens a dialog to specify start line and increment.

### Auto Line Numbers
Automatically generate line numbers when entering new lines. Toggle on/off as needed.

## Debugging (6 features)

### Breakpoints ({{kbd:toggle_breakpoint:curses}})
Toggle a breakpoint on the current line. Execution will pause when reaching this line.
- Set: Click margin or press {{kbd:toggle_breakpoint:curses}}
- Indicated by: ● symbol in line number margin

### Step Statement ({{kbd:step:curses}})
Execute one BASIC statement and pause. Useful for debugging complex lines with multiple statements.

### Step Line ({{kbd:step_line:curses}})
Execute the next line of code and pause. Advances one line number at a time.

### Clear All Breakpoints ({{kbd:save:curses}}hift+B)
Remove all breakpoints from the program at once.

### Multi-Statement Debug
When stepping, the debugger highlights individual statements on lines with multiple statements (separated by :).

### Current Line Highlight
The currently executing line is highlighted with a cyan background during program execution.

## Variable Inspection (6 features)

**Note:** The Curses UI provides a dedicated Variables Window. In CLI mode, variable inspection uses the PRINT statement instead. See [CLI Variables](../cli/variables.md) for details.

### Variables Window (Ctrl+W)
Open/close the variables inspection window showing all program variables and their current values.

### Edit Variable Value (Not implemented)
⚠️ Variable editing is not available in Curses UI. You cannot directly edit values in the variables window. Use immediate mode commands to modify variable values instead.

### Variable Filtering (f key in variables window)
Filter the variables list to show only variables matching a search term.

### Variable Sorting (s key in variables window)
Cycle through different sort orders:
- **Accessed**: Most recently accessed (read or written) - newest first
- **Written**: Most recently written to - newest first
- **Read**: Most recently read from - newest first
- **Name**: Alphabetically by variable name

Press 'd' to toggle sort direction (ascending/descending).

### Execution Stack
View the call stack showing:

**Access methods:**
- Via menu: Ctrl+U → Debug → Execution Stack
- Via command: Type `STACK` in immediate mode (same as CLI)
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

## Editor Features (7 features)

### Line Editing
Edit BASIC code line-by-line with full cursor navigation.

### Multi-Line Edit
Edit multiple lines at once in the full-screen editor.

### Delete Lines (Ctrl+D)
Delete the current line in the editor.

### Cut/Copy/Paste (Not implemented)
Standard clipboard operations are not available in the Curses UI due to keyboard shortcut conflicts:
- **{{kbd:stop:curses}}** - Used for Stop/Interrupt (cannot be used for Cut)
- **{{kbd:continue:curses}}** - Terminal signal to exit program (cannot be used for Copy)
- **{{kbd:save:curses}}** - Used for Save File (cannot be used for Paste; {{kbd:save:curses}} is reserved by terminal for flow control)

**Workaround:** Use your terminal's native copy/paste functions instead (typically Shift+{{kbd:continue:curses}}/V or mouse selection).

### Find/Replace (Not yet implemented)
Find and Replace functionality is not yet available in Curses UI via keyboard shortcuts.

**Workaround:** Use text editor commands in your terminal (if available) or load/edit/save files externally.

### Smart Insert (Ctrl+I)
Insert a new line number at the midpoint between the current line and the next line.
Example: Between lines 10 and 20, inserts line 15.

### Sort Lines
Lines are automatically kept in numerical order. Manual sorting is available if needed.

### Syntax Checking
Real-time syntax validation as you type. Syntax errors are marked with a '?' symbol in the line number margin.

## Settings & Configuration (1 feature)

### Settings Widget (Ctrl+,)
Interactive settings dialog for configuring MBASIC behavior. Adjust auto-numbering, keyword case style, variable handling, themes, and more.

See [Curses Settings Widget](settings.md) for complete documentation.

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
| {{kbd:new:curses}} | New Program |
| {{kbd:open:curses}} | Open File |
| {{kbd:save:curses}} | Save File |
| {{kbd:run:curses}} | Run Program |
| {{kbd:stop:curses}} | Stop Program |
| {{kbd:toggle_breakpoint:curses}} | Toggle Breakpoint |
| {{kbd:step:curses}} | Step Statement |
| {{kbd:step_line:curses}} | Step Line |
| {{kbd:goto_line:curses}} | Continue |
| Ctrl+W | Variables Window |
| Menu only | Execution Stack |
| ? | Help |

### Status Bar Indicators
- **●** - Breakpoint set on line
- **?** - Syntax error on line
- **Cyan highlight** - Currently executing line

---

*See also: [Keyboard Shortcuts](../../../user/keyboard-shortcuts.md), [Getting Started](getting-started.md)*
