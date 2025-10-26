# Web UI Help

Welcome to the MBASIC 5.21 Web IDE!

## Getting Started

The web interface provides a full-featured BASIC programming environment accessible from any modern web browser.

### Main Components

- **Editor** (top) - Write your BASIC code here
- **Output** (bottom) - See program output and error messages
- **Menu Bar** - Access File, Edit, Run, and Help functions

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

1. Type your BASIC program in the editor
2. Use line numbers (e.g., `10 PRINT "HELLO"`)
3. Click **Run** → **Run Program** to execute
4. View output in the bottom panel

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

## Getting More Help

Use the tabs in this help browser to explore:

- **📕 Language** - BASIC language syntax and commands
- **📗 MBASIC** - MBASIC 5.21 specific features
- **📘 Web UI** - This web interface (you are here)

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

This is an implementation of Microsoft BASIC-80 version 5.21, originally released for CP/M systems in 1981. It provides compatibility with classic BASIC programs from that era.

For language documentation, see the **📕 Language** and **📗 MBASIC** help tabs.
