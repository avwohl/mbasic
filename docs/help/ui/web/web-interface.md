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

The Web UI has three main text areas:

### Program Editor (Top)

Write your BASIC program here.

- **Automatic line numbering** when you press Enter
- Example: Type `PRINT "HELLO"` and press Enter → becomes `10 PRINT "HELLO"`
- Successive lines auto-increment: next line becomes 20, 30, 40, etc.
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

### Menu Bar

Access File, Edit, Run, and Help functions.

## Menu Functions

### File Menu

- **New** - Clear the editor and start a new program
- **Load Example** - Choose from sample BASIC programs
- **Clear Output** - Clear the output area

### Edit Menu

- **Copy** - Copy selected text to clipboard
- **Paste** - Paste from clipboard (Ctrl+V)
- **Select All** - Select all editor text

### Run Menu

- **Run Program** - Parse and execute the current program
- **Stop** - Stop a running program

### Help Menu

- **Help** - Open this help browser

## Writing Programs

1. Type your BASIC program in the **Program Editor** (top area)
2. Press Enter after each statement - line numbers are added automatically
3. Click **Run** → **Run Program** to execute
4. View output in the **Output** area (middle)

### Auto-Numbering

The **Program Editor** automatically adds line numbers when you press Enter:

- **First line**: Starts at 10
- **Subsequent lines**: Increment by 10 (20, 30, 40...)
- **Manual numbering**: You can still type your own line numbers if desired
- **Only in Editor**: The Command area does NOT auto-number (it runs commands immediately)

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
- Files persist during your session
- No access to the server's real filesystem (security)

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

## Security & Privacy

The web UI is designed for safe multi-user access:

- ✅ **Sandboxed** - No access to server files
- ✅ **Isolated** - Your files are private to your session
- ✅ **Limited** - Resource limits prevent abuse
- ✅ **Session-based** - Data cleared when session ends

## Keyboard Shortcuts

- **Ctrl+V** - Paste into editor
- **Ctrl+A** - Select all
- **Ctrl+C** - Copy selection

## Browser Compatibility

Works best with modern browsers:
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## Limitations

Compared to desktop UIs, the web UI:
- Cannot access local filesystem
- No debugger or breakpoint support (yet)
- Files don't persist after session ends

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

- Use Ctrl+V (not right-click menu in some browsers)
- Try Edit → Paste from menu

## About MBASIC 5.21

This is an implementation of MBASIC-80 version 5.21, originally released for CP/M systems in 1981. It provides compatibility with classic BASIC programs from that era.

For language documentation, see:
- [📕 Language Help](../../common/index.md) - BASIC language syntax and commands
- [📗 MBASIC Help](../../mbasic/index.md) - MBASIC 5.21 specific features
