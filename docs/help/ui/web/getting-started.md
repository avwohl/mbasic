# Getting Started with Web UI

Welcome to the MBASIC Web UI! This modern browser-based interface provides a full-featured BASIC development environment.

## Launching the Web UI

### Quick Start

1. **Start the web server:**
   ```bash
   python3 mbasic.py --backend web
   ```

2. **Open your browser:**
   - Navigate to `http://localhost:8080`
   - The interface loads automatically

3. **Alternative launch:**
   ```bash
   python3 mbasic.py --backend web --open
   ```
   This automatically opens your default browser.

## Interface Overview

### Main Components

The Web UI has four main areas:

1. **Editor Panel** (Left)
   - Line-numbered code editor
   - Syntax highlighting
   - Auto-indentation
   - Real-time syntax checking

2. **Output Panel** (Right Top)
   - Program output display
   - Error messages
   - INPUT prompt handling

3. **Debug Panel** (Right Middle)
   - Variables inspector
   - Breakpoint indicators
   - Execution state

4. **Control Bar** (Top)
   - Run/Stop buttons
   - File operations
   - Debug controls
   - Settings menu

## Your First Program

### Hello World

1. **Type in the editor:**
   ```basic
   10 PRINT "Hello, World!"
   20 PRINT "Welcome to MBASIC Web UI"
   30 END
   ```

2. **Run the program:**
   - Click the **Run** button or press `Ctrl+R`
   - Output appears in the right panel

### Interactive Input

```basic
10 INPUT "What's your name"; N$
20 PRINT "Hello, "; N$
30 INPUT "Enter your age"; A
40 PRINT "You are"; A; "years old"
50 END
```

When you run this:
- Input prompts appear in the output panel
- Type your response and press Enter
- Program continues with your input

## File Operations

### Loading Programs

**Method 1: File Menu**
1. Click **File → Open** or press `Ctrl+O`
2. Browse and select a .bas file
3. Program loads in editor

**Method 2: Drag and Drop**
- Drag a .bas file onto the editor
- File loads automatically

### Saving Programs

- **Save:** `Ctrl+S` - Saves to browser storage
- **Save As:** `Ctrl+Shift+S` - Download as file
- **Export:** File → Export - Download with custom name

### Browser Storage

The Web UI uses browser localStorage to:
- Save your current program
- Remember recent files
- Store preferences
- Maintain breakpoints

**Note:** Clearing browser data will remove stored programs!

## Basic Editing

### Keyboard Shortcuts

**Editing:**
- `Ctrl+Z` - Undo
- `Ctrl+Y` - Redo
- `Ctrl+A` - Select all
- `Ctrl+C` - Copy
- `Ctrl+X` - Cut
- `Ctrl+V` - Paste

**Navigation:**
- `Ctrl+G` - Go to line
- `Ctrl+Home` - Go to start
- `Ctrl+End` - Go to end
- `F3` - Find next

**Program Control:**
- `Ctrl+R` - Run program
- `Esc` - Stop program
- `Ctrl+.` - Break execution

### Line Operations

- **Add line:** Type number and code
- **Replace line:** Type same number with new code
- **Delete line:** Type just the number
- **Insert between:** Use intermediate numbers (15, 25, etc.)

## Running Programs

### Execution Modes

**Normal Run:**
- Click Run or press `Ctrl+R`
- Program executes from beginning
- Stops at END or error

**Debug Mode:**
- Set breakpoints first
- Click Debug or press `F5`
- Execution pauses at breakpoints

### Handling Input

When program needs input:
1. Prompt appears in output panel
2. Input field activates
3. Type your response
4. Press Enter to continue

### Stopping Programs

- Click **Stop** button
- Press `Esc` key
- Press `Ctrl+C` (break)
- Close browser tab (emergency)

## Debugging Features

### Setting Breakpoints

- Click line number to toggle breakpoint
- Red dot indicates active breakpoint
- Execution pauses before that line

### During Break

When paused at breakpoint:
- **Continue:** Resume execution
- **Step:** Execute one line
- **Stop:** End program
- **Variables:** Inspect current values

### Variable Inspector

- Shows all defined variables
- Updates in real-time
- Double-click to edit values
- Arrays show dimensions

## Web UI Features

### Auto-Save

- Program auto-saves to browser storage
- Saves every 30 seconds while editing
- Recovers on browser restart

### Syntax Checking

- Real-time syntax validation
- Red underlines for errors
- Hover for error details
- Updates as you type

### Code Completion

- Start typing BASIC keywords
- Suggestions appear
- Press Tab to complete
- Works for statements and functions

### Theme Options

- Light/Dark mode toggle
- Adjustable font size
- Customizable colors
- Saved in preferences

## Tips and Tricks

1. **Quick Run:** Press `Ctrl+R` anytime to run
2. **Clear Output:** Click output panel header
3. **Full Screen:** Press `F11` for more space
4. **Multi-Line Edit:** Select multiple lines, then type
5. **Quick Save:** `Ctrl+S` saves to browser instantly

## Browser Compatibility

**Recommended:**
- Chrome 90+
- Firefox 88+
- Edge 90+
- Safari 14+

**Features requiring modern browser:**
- localStorage (auto-save)
- Clipboard API (copy/paste)
- Drag and drop
- WebSocket (future: collaborative editing)

## Troubleshooting

### Program Won't Run
- Check for syntax errors (red underlines)
- Ensure program has line numbers
- Verify END statement exists

### Lost Program
- Check browser localStorage
- Look in Downloads folder for saves
- Use browser back button carefully

### Performance Issues
- Clear output panel if too full
- Reduce program size if very large
- Close other browser tabs
- Check browser console for errors

## Next Steps

- [Keyboard Shortcuts](keyboard-shortcuts.md) - Complete shortcut reference
- [Debugging Guide](debugging.md) - Advanced debugging
- [Features](features.md) - All Web UI capabilities
- [Settings](settings.md) - Customization options

## Getting Help

- Press `F1` for help
- Type in output: `HELP <topic>`
- Visit [MBASIC documentation](../../mbasic/index.md)
- Check [Language Reference](../../common/language/index.md)