# Tk UI - Complete Feature Reference

This document covers all 37 features available in the Tkinter (Tk) UI.

## File Operations (8 features)

### New Program (Ctrl+N)
Create a new program. Prompts to save current program if there are unsaved changes.
- Menu: File → New
- Shortcut: Ctrl+N

### Open/Load File (Ctrl+O)
Open a BASIC program from disk using a native file dialog.
- Menu: File → Open
- Shortcut: Ctrl+O
- Supports .bas and .txt files

### Save File (Ctrl+S)
Save the current program. If no filename is set, prompts for one (same as Save As).
- Menu: File → Save
- Shortcut: Ctrl+S

### Save As (Ctrl+Shift+S)
Save the program with a new filename.
- Menu: File → Save As
- Shortcut: Ctrl+Shift+S

### Recent Files
Access recently opened files from the File menu.
- Menu: File → Recent Files
- Shows last 10 files opened

### Auto-Save
Tk UI supports auto-save functionality. Programs are periodically saved to prevent data loss.
- Configurable interval
- Creates backup files

### Delete Lines (Ctrl+D)
Delete selected lines or the current line.
- Select lines and press Ctrl+D
- Or use Edit menu

### Merge Files
Merge another BASIC program into the current one.
- Menu: File → Merge
- Combines line numbers from both programs

## Execution & Control (6 features)

### Run Program (Ctrl+R or F5)
Execute the current program from the beginning.
- Menu: Run → Run Program
- Shortcuts: Ctrl+R or F5
- Output appears in the output pane

### Stop/Interrupt (Ctrl+X)
Stop a running program immediately.
- Menu: Run → Stop
- Shortcut: Ctrl+X

### Continue (Ctrl+G)
Resume execution after pausing at a breakpoint.
- Menu: Run → Continue
- Shortcut: Ctrl+G

### List Program
View the program listing in the editor window.
- Menu: Edit → List Program
- Refreshes the editor view

### Renumber (Ctrl+E)
Renumber program lines with specified start and increment.
- Menu: Edit → Renumber
- Shortcut: Ctrl+E
- Opens dialog for configuration

### Auto Line Numbers
Automatically insert line numbers when pressing Enter.
- Toggle in settings
- Configurable start and increment

## Debugging (6 features)

### Breakpoints (Ctrl+B)
Set or remove breakpoints by clicking the line number margin or using Ctrl+B.
- Visual indicator: ● symbol
- Menu: Run → Toggle Breakpoint
- Shortcut: Ctrl+B
- Click line number margin

### Step Statement (Ctrl+T)
Execute one BASIC statement at a time.
- Menu: Run → Step Statement
- Shortcut: Ctrl+T
- Pauses after each statement

### Step Line (F10)
Execute one line at a time.
- Menu: Run → Step Line
- Shortcut: F10
- Pauses after each line number

### Clear All Breakpoints (Ctrl+Shift+B)
Remove all breakpoints from the program.
- Menu: Run → Clear All Breakpoints
- Shortcut: Ctrl+Shift+B

### Multi-Statement Debug
When stepping by statement, individual statements on multi-statement lines are highlighted separately.

### Current Line Highlight
The currently executing line is highlighted during program execution.
- Background color changes to indicate active line
- Auto-scrolls to keep current line visible

## Variable Inspection (6 features)

### Variables Window (Ctrl+W)
Open a window showing all program variables and their current values.
- Menu: Debug → Variables Window
- Shortcut: Ctrl+W
- Shows name, type, and value
- Updates in real-time during execution

### Edit Variable Value
Double-click a variable in the Variables window to edit its value during debugging.
- Supports all data types
- Type validation
- Changes take effect immediately

### Variable Filtering
Filter the variables display to show only variables matching a search term.
- Search box in Variables window
- Real-time filtering
- Case-insensitive

### Variable Sorting
Click column headers to sort variables:
- By name (alphabetical)
- By type
- By value
- Click again to reverse order

### Execution Stack (Ctrl+K)
View the call stack showing:
- Active GOSUB calls with return lines
- FOR loops with current iteration
- WHILE loops
- Menu: Debug → Execution Stack
- Shortcut: Ctrl+K

### Resource Usage
Monitor memory usage and variable count in the status bar.
- Real-time updates
- Shows total variables
- Memory consumption

## Editor Features (7 features)

### Line Editing
Full text editing with:
- Cursor navigation (arrows, Home, End, Page Up/Down)
- Selection with mouse or Shift+arrows
- Standard text operations

### Multi-Line Edit
Edit multiple lines simultaneously:
- Select multiple lines
- Copy/paste blocks of code
- Indent/unindent selections

### Cut/Copy/Paste (Ctrl+X/C/V)
Standard clipboard operations with native OS clipboard integration.
- Cut: Ctrl+X
- Copy: Ctrl+C
- Paste: Ctrl+V
- Also available via Edit menu and right-click context menu

### Find/Replace (Ctrl+F / Ctrl+H)
Powerful search and replace functionality:
- Find: Ctrl+F
- Replace: Ctrl+H
- Find Next: F3
- Options: Case-sensitive, whole word, regex
- Replace single or all occurrences
- Search wraps around

### Smart Insert (Ctrl+I)
Insert a line number at the midpoint between current and next line.
- Menu: Edit → Smart Insert
- Shortcut: Ctrl+I
- Example: Between 10 and 20, inserts 15

### Sort Lines
Lines are automatically sorted by line number.
- Can also manually trigger sort
- Maintains program structure
- Preserves comments

### Syntax Checking
Real-time syntax validation as you type:
- Errors underlined in red
- Hover for error message
- Parse check on demand (F7)
- Error list in output pane

## Help System (4 features)

### Help Command (F1)
Open the main help system.
- Shortcut: F1
- Menu: Help → Help Topics
- Searchable help browser

### Integrated Docs
Complete MBASIC language documentation integrated into the UI:
- Statement reference
- Function reference
- Examples and tutorials
- Searchable index

### Search Help (Ctrl+Shift+F)
Search across all help documentation:
- Full-text search
- Keyword search
- Results with context
- Jump to relevant section

### Context Help (Shift+F1)
Get help for the BASIC keyword at the cursor:
- Place cursor on keyword
- Press Shift+F1
- Opens relevant help page

## Window Layout

The Tk UI uses a flexible window layout:
- **Menu Bar**: File, Edit, Run, Debug, Help menus
- **Toolbar**: Quick access to common operations
- **Editor Pane**: Main code editing area with line numbers
- **Output Pane**: Program output and error messages
- **Variables Window**: Detachable variable inspector (Ctrl+W)
- **Stack Window**: Detachable call stack viewer (Ctrl+K)
- **Status Bar**: Current file, cursor position, resource usage

All panes can be resized with splitters.

## Mouse Support

The Tk UI fully supports mouse operations:
- Click to position cursor
- Double-click to select word
- Triple-click to select line
- Drag to select text
- Click line numbers to toggle breakpoints
- Right-click for context menu
- Scroll with mouse wheel

## Quick Reference

### Essential Shortcuts
| Shortcut | Action |
|----------|--------|
| Ctrl+N | New Program |
| Ctrl+O | Open File |
| Ctrl+S | Save File |
| Ctrl+R / F5 | Run Program |
| Ctrl+X | Stop Program |
| Ctrl+B | Toggle Breakpoint |
| Ctrl+T | Step Statement |
| F10 | Step Line |
| Ctrl+G | Continue |
| Ctrl+W | Variables Window |
| Ctrl+K | Execution Stack |
| Ctrl+F | Find |
| Ctrl+H | Find & Replace |
| F1 | Help |
| Shift+F1 | Context Help |

### Visual Indicators
- **●** - Breakpoint on line
- **Red underline** - Syntax error
- **Yellow highlight** - Currently executing line
- **Cyan highlight** - Current statement (when stepping)

---

*See also: [Keyboard Shortcuts](keyboard-shortcuts.md), [Getting Started](getting-started.md), [Workflows](workflows.md)*
