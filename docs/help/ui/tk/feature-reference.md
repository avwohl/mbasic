# Tk UI - Complete Feature Reference

This document covers all features available in the Tkinter (Tk) UI, organized by category.

## File Operations (8 features)

### New Program ({{kbd:file_new:tk}})
Create a new program. Prompts to save current program if there are unsaved changes.
- Menu: File → New
- Shortcut: {{kbd:file_new:tk}}

### Open/Load File ({{kbd:file_open:tk}})
Open a BASIC program from disk using a native file dialog.
- Menu: File → Open
- Shortcut: {{kbd:file_open:tk}}
- Supports .bas and .txt files

### Save File ({{kbd:file_save:tk}})
Save the current program. If no filename is set, prompts for one (same as Save As).
- Menu: File → Save
- Shortcut: {{kbd:file_save:tk}}

### Save As ({{kbd:file_save_as:tk}})
Save the program with a new filename.
- Menu: File → Save As
- Shortcut: {{kbd:file_save_as:tk}}

### Recent Files
Access recently opened files from the File menu.
- Menu: File → Recent Files
- Shows last 10 files opened

### Auto-Save
Tk UI supports auto-save functionality. Programs are periodically saved to prevent data loss.
- Configurable interval
- Creates backup files

### Delete Lines
Delete selected lines or the current line.
- Select lines and use Edit → Delete Lines menu
- Or select and press Delete/Backspace key

### Merge Files
Merge another BASIC program into the current one.
- Menu: File → Merge
- Combines line numbers from both programs

## Execution & Control (6 features)

### Run Program ({{kbd:run_program:tk}} or F5)
Execute the current program from the beginning.
- Menu: Run → Run Program
- Shortcuts: {{kbd:run_program:tk}} or F5
- Output appears in the output pane

### Stop/Interrupt
Stop a running program immediately.
- Menu: Run → Stop
- No keyboard shortcut (menu only)

### Continue
Resume execution after pausing at a breakpoint.
- Menu: Run → Continue
- Toolbar: "Cont" button
- No keyboard shortcut

### List Program
View the program listing in the editor window.
- Menu: Edit → List Program
- Refreshes the editor view

### Renumber ({{kbd:renumber:tk}})
Renumber program lines with specified start and increment.
- Menu: Edit → Renumber
- Shortcut: {{kbd:renumber:tk}}
- Opens dialog for configuration

### Auto Line Numbers
Automatically insert line numbers when pressing Enter.
- Toggle in settings
- Configurable start and increment

## Debugging (6 features)

### Breakpoints ({{kbd:toggle_breakpoint:tk}})
Set or remove breakpoints by clicking the line number margin or using {{kbd:toggle_breakpoint:tk}}.
- Visual indicator: ● symbol
- Menu: Run → Toggle Breakpoint
- Shortcut: {{kbd:toggle_breakpoint:tk}}
- Click line number margin

### Step Statement
Execute one BASIC statement at a time.
- Menu: Run → Step Statement
- Toolbar: "Stmt" button
- No keyboard shortcut
- Pauses after each statement

### Step Line (F10)
Execute one line at a time.
- Menu: Run → Step Line
- Shortcut: F10
- Pauses after each line number

### Clear All Breakpoints
Remove all breakpoints from the program.
- Menu: Edit → Clear All Breakpoints
- No keyboard shortcut (menu only)

### Multi-Statement Debug
When stepping by statement, individual statements on multi-statement lines are highlighted separately.

### Current Line Highlight
The currently executing line is highlighted during program execution.
- Background color changes to indicate active line
- Auto-scrolls to keep current line visible

## Variable Inspection (6 features)

### Variables Window ({{kbd:toggle_variables:tk}})
Open a window showing all program variables and their current values.
- Menu: Debug → Variables Window
- Shortcut: {{kbd:toggle_variables:tk}}
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

### Execution Stack ({{kbd:toggle_stack:tk}})
View the call stack showing:
- Active GOSUB calls with return lines
- FOR loops with current iteration
- WHILE loops
- Menu: Debug → Execution Stack
- Shortcut: {{kbd:toggle_stack:tk}}

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

### Cut/Copy/Paste ({{kbd:cut:tk}}/{{kbd:copy:tk}}/{{kbd:paste:tk}})
Standard clipboard operations with native OS clipboard integration.
- Cut: {{kbd:cut:tk}}
- Copy: {{kbd:copy:tk}}
- Paste: {{kbd:paste:tk}}
- Also available via Edit menu and right-click context menu

### Find/Replace ({{kbd:find:tk}} / {{kbd:replace:tk}})
Powerful search and replace functionality:
- Find: {{kbd:find:tk}} - Opens Find dialog with search options (case-sensitive, whole word, regex)
- Replace: {{kbd:replace:tk}} - Opens combined Find/Replace dialog with find and replace options
- Find Next: F3 to find next occurrence
- Features: Visual highlighting of matches, replacement count, search wraps around
- Capabilities: Replace single occurrence or all occurrences

**Note:** Both dialogs support full search functionality. The Replace dialog includes all Find features plus replacement options.

### Smart Insert ({{kbd:smart_insert:tk}})
Insert a line number at the midpoint between current and next line.
- Menu: Edit → Smart Insert
- Shortcut: {{kbd:smart_insert:tk}}
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

### Search Help
Search across all help documentation:
- Full-text search
- Keyword search
- Results with context
- Jump to relevant section

**Note:** Search function is available via the help browser's search box (no dedicated keyboard shortcut).

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
- **Variables Window**: Detachable variable inspector ({{kbd:toggle_variables:tk}})
- **Stack Window**: Detachable call stack viewer ({{kbd:toggle_stack:tk}})
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
| {{kbd:file_new:tk}} | New Program |
| {{kbd:file_open:tk}} | Open File |
| {{kbd:file_save:tk}} | Save File |
| {{kbd:run_program:tk}} / F5 | Run Program |
| (menu only) | Stop Program |
| {{kbd:toggle_breakpoint:tk}} | Toggle Breakpoint |
| F10 | Step Line |
| (toolbar) | Step Statement |
| (toolbar) | Continue |
| {{kbd:toggle_variables:tk}} | Variables Window |
| {{kbd:toggle_stack:tk}} | Execution Stack |
| {{kbd:find:tk}} | Find |
| {{kbd:replace:tk}} | Find & Replace |
| F1 | Help |
| Shift+F1 | Context Help |

### Visual Indicators
- **●** - Breakpoint on line
- **Red underline** - Syntax error
- **Yellow highlight** - Currently executing line
- **Cyan highlight** - Current statement (when stepping)

---

*See also: [Keyboard Shortcuts](../../../user/keyboard-shortcuts.md), [Getting Started](getting-started.md), [Workflows](workflows.md)*
