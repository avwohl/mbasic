---
title: Web Interface Guide
type: guide
ui: web
description: Detailed guide to the MBASIC Web IDE interface components
keywords: [web, interface, editor, menu, components]
---

# Web Interface Guide

The MBASIC Web IDE provides a full-featured BASIC programming environment accessible from any modern web browser.

## Main Components

The Web UI has a vertical layout with these components:

### Menu Bar

Located at the top with File, Edit, Run, View, and Help menus. See [Menu Functions](#menu-functions) below for details.

### Toolbar

Quick-access buttons below the menu bar for common operations:
- **Run** (▶️ green) - Start program execution
- **Stop** (⏹️ red) - Stop running program
- **Step** (⏭️) - Execute all statements on current line
- **Stmt** (↻) - Execute one statement
- **Cont** (▶️⏸️) - Continue execution after pause

Additional file operations are available through the File menu.

### Program Editor (Top)

Write your BASIC program here.

- **Automatic line numbering** when you press Enter (configurable via Settings)
- Example: Type `PRINT "HELLO"` and press Enter → becomes `10 PRINT "HELLO"`
- Successive lines auto-increment: next line becomes 20, 30, 40, etc. (increment is configurable)
- **Manual numbering**: You can still type your own line numbers if desired

**Example workflow:**
```
Type: PRINT "Hello"
Press Enter → becomes: 10 PRINT "Hello"

Type: FOR I=1 TO 5
Press Enter → becomes: 20 FOR I=1 TO 5

Type: NEXT I
Press Enter → becomes: 30 NEXT I
```

### Output (Middle)

See program output and error messages.

- Shows results when you run your program
- Displays error messages and diagnostics
- Shows immediate command results

### Command (Bottom)

Type immediate commands that execute without adding to your program.

- **No automatic line numbering** - commands run immediately
- Example: Type `PRINT 2+2` → shows `4` without adding to program
- Useful for testing expressions and quick calculations

**Try these examples:**
```
Type: PRINT 2+2
Press Enter → Output shows: 4

Type: X=10: PRINT X*X
Press Enter → Output shows: 100

Type: FOR I=1 TO 3: PRINT I: NEXT I
Press Enter → Output shows: 1 2 3
```

**When to use Command vs Editor:**
- **Command** - Quick calculations, testing expressions, checking variables
- **Editor** - Writing programs you want to save and run multiple times

## Menu Functions

### File Menu

- **New** - Clear the editor and start a new program
- **Open** - Open a .bas file from your computer (via browser file picker)
- **Save** - Download current program to your computer as a .bas file
- **Save As** - Download with a new filename
- **Clear Output** - Clear the output area

**Note:** An "Open Example" feature to choose from sample BASIC programs is planned for a future release.

### Edit Menu

- **Copy** - Copy selected text to clipboard
- **Paste** - Paste from clipboard ({{kbd:paste:web}})
- **Select All** - Select all editor text
- **Sort Lines** - Sort selected lines numerically by line number
- **Smart Insert** - Insert lines intelligently between existing line numbers
- **Settings** - Configure auto-numbering, case handling, and other interpreter options

### Run Menu

- **Run Program** - Parse and execute the current program
- **Stop** - Stop a running program
- **Toggle Breakpoint** - Set or remove a breakpoint at a specific line number
- **Clear All Breakpoints** - Remove all breakpoints
- **Continue** - Resume execution after a breakpoint or step
- **Step Line** - Execute all statements on the current line, then pause
- **Step Statement** - Execute one statement, then pause

### View Menu

- **Show Variables** - Open the Variables Window to view and monitor program variables in real-time

### Help Menu

- **Help** - Open this help browser

## Writing Programs

1. Type your BASIC program in the **Program Editor** (top area)
2. Press Enter after each statement - line numbers are added automatically
3. Click **Run** → **Run Program** to execute
4. View output in the **Output** area (middle)

### Auto-Numbering

The **Program Editor** automatically adds line numbers when you press Enter:

- **First line**: Starts at 10 (configurable in Settings)
- **Subsequent lines**: Increment by 10 (20, 30, 40...) - configurable in Settings
- **Manual numbering**: You can still type your own line numbers if desired
- **Only in Editor**: The Command area does NOT auto-number (it runs commands immediately)
- **Configurable**: Use the Settings dialog (⚙️ icon) to change the increment or disable auto-numbering entirely

### Example Program

```basic
10 PRINT "Hello from MBASIC!"
20 FOR I = 1 TO 5
30   PRINT "Count: "; I
40 NEXT I
50 END
```

## File I/O

File operations in the web UI work with an **in-memory filesystem**:

- Files are stored in browser memory only
- Each user has their own isolated filesystem
- Files persist during your session (but are cleared when session ends)
- No access to the server's real filesystem (security)

**Important:** Programs and data created via BASIC file I/O commands (OPEN, PRINT #, etc.) exist only in memory during your browser session. To save your BASIC program source code permanently, use File → Save to download it to your computer.

### File Limits

- Maximum 20 files per user
- Maximum 512KB per file

### Example File I/O

```basic
10 REM Write to a file
20 OPEN "O", #1, "DATA.TXT"
30 PRINT #1, "Hello, file!"
40 CLOSE #1
50 REM Read from the file
60 OPEN "I", #1, "DATA.TXT"
70 INPUT #1, A$
80 PRINT "Read: "; A$
90 CLOSE #1
```

## Language Features

The Web UI supports all MBASIC 5.21 language features, including:

### Settings Commands

You can configure interpreter behavior using BASIC commands in your program or the Command area:

```basic
REM Configure case handling for variables
SET "variables.case_conflict" "error"

REM Configure keyword capitalization
SET "keywords.case_style" "force_capitalize"

REM View all current settings
SHOW SETTINGS
```

For complete details on case handling and other language settings, see the [Case Handling Guide](../../../user/CASE_HANDLING_GUIDE.md).

## Security & Privacy

The web UI is designed for safe multi-user access:

- ✅ **Sandboxed** - No access to server files
- ✅ **Isolated** - Your files are private to your session
- ✅ **Limited** - Resource limits prevent abuse
- ✅ **Session-based** - Data cleared when session ends

## Keyboard Shortcuts

- **{{kbd:paste:web}}** - Paste into editor
- **{{kbd:select_all:web}}** - Select all
- **{{kbd:copy:web}}** - Copy selection

## Browser Compatibility

Works best with modern browsers:
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## Limitations

Compared to desktop UIs, the web UI:
- Cannot directly access local filesystem (but can load files via browser file picker)
- Limited debugger support (basic breakpoints only via Run menu)
- Files don't persist after session ends (stored in browser memory only)

## Troubleshooting

### Program Won't Run

- Check for syntax errors in output
- Ensure all lines have line numbers
- Look for missing END statement

### File I/O Errors

- Check you haven't exceeded 20 file limit
- Ensure files aren't too large (>512KB)
- Remember to CLOSE files after use

### Can't Paste Code

- Use {{kbd:paste:web}} (not right-click menu in some browsers)
- Try Edit → Paste from menu

## About MBASIC 5.21

This is an implementation of MBASIC-80 version 5.21, originally released for CP/M systems in 1981. It provides compatibility with classic BASIC programs from that era.

For language documentation, see:
- [📕 Language Help](../../common/index.md) - BASIC language syntax and commands
- [📗 MBASIC Help](../../mbasic/index.md) - MBASIC 5.21 specific features
