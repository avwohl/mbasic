---
title: Web UI Keyboard Shortcuts
type: guide
ui: web
description: Keyboard shortcut reference for the web browser interface
keywords: [shortcuts, keyboard, web, browser, hotkeys, commands]
---

# Web UI Keyboard Shortcuts

Keyboard shortcuts for the web browser interface.

## Program Execution

| Shortcut | Action |
|----------|--------|
| **Ctrl+R** | Run program from start |
| **Ctrl+Q** | Stop execution |
| **Ctrl+T** | Step (execute one statement, then pause) |
| **Ctrl+G** | Continue (run to next breakpoint or end) |

## File Operations

| Shortcut | Action |
|----------|--------|
| **Ctrl+N** | New program (clear editor) |
| **Ctrl+O** | Open file (upload dialog) |
| **Ctrl+S** | Save current program (download) |

## Debugging

| Shortcut | Action |
|----------|--------|
| **Ctrl+B** | Toggle breakpoint (shows info) |
| **Ctrl+V** | Show/hide Variables window |
| **Ctrl+K** | Show/hide Execution Stack window |

## Editor Commands

| Shortcut | Action |
|----------|--------|
| **Ctrl+E** | Renumber program lines (opens dialog) |

**Note:** All keyboard shortcuts are now supported! Previously, many actions required using buttons or menus.

## Statement-Level Debugging

When stepping through code with **Ctrl+T**:

- The status bar shows which statement is executing
- For multi-statement lines (using `:`), each statement executes individually
- Status shows `Paused at line 100 statement 2`
- During execution shows `Running... line 50 [stmt 3]`

Example:
```basic
100 A = 1 : B = 2 : PRINT A + B
```

Step 1: `Paused at line 100 statement 1` (A = 1)
Step 2: `Paused at line 100 statement 2` (B = 2)
Step 3: `Paused at line 100 statement 3` (PRINT A + B)
Step 4: Advances to next line

## Mouse Actions

### Line Numbers Column

- **Click line number** → Toggle breakpoint on that line
- **?** indicator → Parse error (syntax error)
- **●** indicator → Breakpoint set
- **Priority:** Error (?) > Breakpoint (●) > Normal

### Visual Indicators

| Indicator | Background | Meaning |
|-----------|------------|---------|
| **? N** | Red | Parse error on line N |
| **● N** | Light red | Breakpoint on line N |
| **N** | Normal | Regular line N |

### Variables Window

- **Click "Edit Selected"** button → Edit the selected variable
- **Double-click row** → Edit variable value
- **Click column header** → Sort by that column

### Editor Buttons

The toolbar provides buttons for common actions:

| Button | Action |
|--------|--------|
| **Run** | Run program (Ctrl+R) |
| **Step** | Step one statement (Ctrl+T) |
| **Continue** | Continue to next breakpoint (Ctrl+G) |
| **Stop** | Stop execution (Ctrl+Q) |
| **Sort** | Sort program lines by line number |
| **Renumber** | Renumber lines with configurable start/increment |
| **Breakpoint** | Info about breakpoint usage |
| **Variables** | Open variables window |
| **Stack** | Open execution stack window |

## File Operations

Use the menu buttons in the header:

### File Menu (Folder Icon)

- **New** → Clear editor, start new program
- **Open from Computer** → Upload .BAS file from your device
- **Open from Server** → Browse and load files from server
- **Save** → Download current program
- **Save As** → Download with custom filename
- **Load Example** → Choose from built-in example programs

### Run Menu (Play Icon)

- **Run (Ctrl+R)** → Start program execution
- **Step (Ctrl+T)** → Execute one statement
- **Continue (Ctrl+G)** → Run to next breakpoint
- **Stop (Ctrl+Q)** → Halt execution
- **Clear Output** → Clear the output log

### Debug Menu (Bug Icon)

- **Toggle Breakpoint** → Instructions for setting breakpoints
- **Variables Window** → Show/hide variables
- **Stack Window** → Show/hide execution stack

### Help Menu (Question Mark Icon)

- **Help Topics** → Browse help documentation
- **About** → Version and information

## Editor Features

### Sort and Renumber

**Sort Button:**
- Sorts all lines by line number
- Keeps unnumbered lines at the end
- Updates line number display

**Renumber Button:**
- Opens configuration dialog
- Choose start line number (default: 10)
- Choose increment (default: 10)
- Automatically updates GOTO/GOSUB references
- Updates ON GOTO and ON GOSUB statements

### Error Detection

The editor validates syntax automatically:

- **On file load** → Checks all lines
- **After sort** → Validates organized code
- **After renumber** → Checks renumbered lines

Errors show with **?** marker in red in the line numbers column.

## Browser Text Editing

Standard browser text editing shortcuts work in the editor:

| Shortcut | Action |
|----------|--------|
| **Ctrl+A** | Select all |
| **Ctrl+X** | Cut |
| **Ctrl+C** | Copy |
| **Ctrl+V** | Paste |

## Debugging Workflow

### Basic Debugging

1. **Click line number** to set a breakpoint (● appears)
2. **Click Run button** or press **Ctrl+R**
3. Program pauses at breakpoint
4. **Click Step** or press **Ctrl+T** to advance one statement
5. **Click Variables** button to inspect values
6. **Click Continue** or press **Ctrl+G** to resume

### Multi-Statement Debugging

For lines like `100 A=1 : B=2 : C=3`:

1. Set breakpoint on line 100
2. Run program
3. Press **Ctrl+T** repeatedly to step through each statement
4. Status bar shows `statement 1`, `statement 2`, `statement 3`
5. Variables window updates after each statement

### Variable Inspection

1. **Click Variables button** to open window
2. **Sort by Modified** to see recent changes
3. **Double-click variable** or click "Edit Selected" to modify
4. **Enter new value** and click OK
5. Continue debugging with new value

## Tips

### Efficient Workflow

- Keep Variables window open while debugging
- Use **Ctrl+T** to step through complex lines
- Watch the status bar for statement numbers
- Set breakpoints on key lines before running

### Example Programs

The web UI includes built-in examples:
- Click **File → Load Example**
- Browse example programs
- Click to load into editor
- Perfect for learning BASIC!

### Server Files

Access files on the server:
- Click **File → Open from Server**
- Browse `basic/` directory
- Search to filter files
- Click to load

### Multi-Statement Lines

When debugging lines with multiple statements:
- Watch the status bar for statement position
- Use **Ctrl+T** to step through each statement
- Check variables after each statement
- Helps understand complex one-liners like:
  ```basic
  100 FOR I=1 TO 3 : PRINT I; : NEXT I
  ```

## Limitations

### Keyboard Shortcuts

✅ **All major keyboard shortcuts are now implemented!**

The Web UI now supports all the same keyboard shortcuts as the Tk and Curses UIs:
- ✅ File operations (Ctrl+N, Ctrl+O, Ctrl+S)
- ✅ Execution (Ctrl+R, Ctrl+T, Ctrl+G, Ctrl+Q)
- ✅ Debugging (Ctrl+B, Ctrl+V, Ctrl+K)
- ✅ Editor (Ctrl+E for renumber)

**Remaining button-only actions:**
- Sort lines - use Sort button (by design, manual operation)
- Help - use Help menu
- Browser text shortcuts (Ctrl+Z, Ctrl+C, Ctrl+V) work as normal

### Current Line Highlight

Unlike Tk UI, the Web UI doesn't highlight the current cursor line in the editor. This is a limitation of the textarea component.

## See Also

- [Debugging Features](../../common/debugging.md) - Complete debugging guide
- [Web UI Features](../../mbasic/features.md) - What's available
- [Getting Started](../../mbasic/getting-started.md) - Your first program
- [Editor Commands](../../common/editor-commands.md) - Editing features

## Quick Reference

### Essential Shortcuts

| Task | Shortcut | Alternative |
|------|----------|-------------|
| Run | **Ctrl+R** | Run button |
| Step | **Ctrl+T** | Step button |
| Stop | **Ctrl+Q** | Stop button |
| Continue | **Ctrl+G** | Continue button |
| Breakpoint | **Ctrl+B** or click line number | Breakpoint button |
| Variables | **Ctrl+V** | Variables button |
| Stack | **Ctrl+K** | Stack button |
| New | **Ctrl+N** | File menu → New |
| Open | **Ctrl+O** | File menu → Open |
| Save | **Ctrl+S** | File menu → Save |
| Renumber | **Ctrl+E** | Renumber button |

Print this table for quick reference!

---

**Pro tip:** The web UI now has full keyboard shortcut support! All the shortcuts from Tk and Curses UIs work in the browser too.
