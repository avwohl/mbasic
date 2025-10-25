# Urwid-based Curses UI

## Overview

The new urwid-based curses UI provides a modern, full-screen terminal interface for MBASIC. It replaces the legacy npyscreen implementation with a cleaner, more maintainable codebase.

## Installation

```bash
# Install urwid
pip install urwid

# Or install all optional dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Start with new urwid UI (default)
python3 mbasic.py

# Or explicitly specify curses backend
python3 mbasic.py --backend curses

# Load a program file
python3 mbasic.py program.bas
python3 mbasic.py --backend curses program.bas
```

## Features

### Current Implementation

- **Full-screen editor** - Multi-line text editor for BASIC programs with column-based layout
- **Status indicators** - Visual breakpoint (●) and error (?) markers
- **Line number editing** - Calculator-style digit entry with auto right-justification
- **Auto-numbering** - Smart line numbering with configurable increment
- **Automatic sorting** - Lines sort by number when navigating
- **Protected columns** - Status and separator columns prevent accidental edits
- **Navigation keys** - Up/down/left/right, Page Up/Down, Home/End
- **Output window** - Displays program execution results (scrollable with Tab key)
- **Status bar** - Shows current state and keyboard shortcuts
- **Program execution** - Run BASIC programs and see output
- **Help system** - Built-in help dialog (press Ctrl+H)
- **File operations** - Save and load programs (Ctrl+S, Ctrl+O)
- **Configuration** - Configurable settings via .mbasic.conf
- **Optimized paste** - High-performance paste with automatic line number parsing
- **Edge-to-edge display** - No left borders for clean copy/paste

### Keyboard Shortcuts

#### Global Commands

| Key | Action |
|-----|--------|
| `Ctrl+Q` / `Ctrl+C` | Quit the program |
| `Ctrl+H` | Show help dialog |
| `Ctrl+R` | Run the current program |
| `Ctrl+L` | List program lines |
| `Ctrl+N` | New program (clear editor) |
| `Ctrl+S` | Save program to file |
| `Ctrl+O` | Open/Load program from file |
| `Tab` | Switch between editor and output window |

#### Navigation Keys

| Key | Behavior | Auto-Sort? |
|-----|----------|------------|
| `Up` / `Down` | Move between lines | Yes (if in line number area) |
| `Left` / `Right` | Move within current line | No |
| `Page Up` / `Page Down` | Scroll by page | Yes |
| `Home` / `End` | Jump to start/end | Yes |
| `Tab` | Move to next field | Yes |
| `Enter` | New line with auto-number | Yes |

**Auto-Sort Behavior:**
- When editing in the line number area (columns 1-5):
  - **Up/Down arrows**: Sort line into position before moving
  - **Left/Right arrows**: Move freely without sorting (for editing)
  - **Page Up/Down, Home, End**: Sort before navigating
  - **Control keys**: Sort before executing command

### UI Layout

```
┌─────────────────────────────────────────────────────┐
│ MBASIC 5.21 Screen Editor                          │
├─────────────────────────────────────────────────────┤
│●   10 PRINT "Hello, World!"                         │
│    20 FOR I = 1 TO 10                               │
│?   30 PRINT I                                       │
│    40 NEXT I                                        │
│    50 END                                           │
│                                                     │
├─────────────────────────────────────────────────────┤
│ Output Window                                       │
│ Hello, World!                                       │
│ 1                                                   │
│ 2                                                   │
├─────────────────────────────────────────────────────┤
│ Status: Ready - Press Ctrl+H for help              │
└─────────────────────────────────────────────────────┘
```

#### Column Layout

Each line has a fixed column structure:

| Columns | Purpose | Description |
|---------|---------|-------------|
| [0] | Status | `●` = breakpoint, `?` = error, ` ` = normal |
| [1-5] | Line Number | 5 digits, right-aligned (e.g., "   10") |
| [6] | Separator | Always a space character |
| [7+] | Code | BASIC program code |

**Example line format:**
```
●   10 PRINT "Hello"
^   ^^ ^
│   │  │
│   │  └─ Separator (column 6)
│   └──── Line number (columns 1-5)
└──────── Status (column 0)
```

## How to Use

### 1. Enter a Program

Type BASIC code with line numbers in the editor:

```basic
10 PRINT "Hello, World!"
20 FOR I = 1 TO 5
30 PRINT "Count: "; I
40 NEXT I
50 END
```

### 2. Run the Program

Press `Ctrl+R` to execute. The output will appear in the output window below the editor.

### 3. List the Program

Press `Ctrl+L` to see a formatted listing of your program.

### 4. Clear and Start Over

Press `Ctrl+N` to clear the editor and start a new program.

### 5. Get Help

Press `Ctrl+H` anytime to see the help dialog with all keyboard shortcuts.

## Line Number Editing

### Calculator-Style Digit Entry

Line numbers work like a 5-digit calculator display:

```
Initial:     10
Type '5':   105
Type '0':  1050
Type '0': 10500  (next digit would drop leftmost '1')
```

**Features:**
- **Overwrite mode** in columns 1-5
- **Right-justified** automatically when leaving the area
- **Leftmost digit drops** when typing at rightmost position (column 5)
- **Backspace** deletes rightmost digit and right-justifies

**Example editing session:**
```
Line:    10 PRINT "Hello"
         ^^

Edit to '101':
1. Move cursor to line number area (columns 1-5)
2. Type '1' → '110'
3. Backspace → '11 '
4. Left arrow (move to column 4)
5. Type '0' → '101'
6. Down arrow → line sorts into position
```

### Protected Areas

- **Status column (0)**: Read-only, cursor moves to line number area
- **Separator (6)**: Protected from deletion/editing
- **Code area (7+)**: Normal text editing

### Backspace Behavior

| Cursor Position | Backspace Action |
|-----------------|------------------|
| Column 1-5 (line number) | Delete rightmost digit, right-justify |
| Column 6 (separator) | Delete rightmost digit of line number |
| Column 7 (code start) | Move to column 6 (protect separator) |
| Column 8+ (code area) | Normal backspace |

## Auto-Numbering

### Default Behavior

When you press Enter on a line, the next line automatically gets a line number:

```
  10 PRINT "Hello"
[Press Enter]
  20 ← Auto-numbered
```

### Configuration

Auto-numbering can be configured in `.mbasic.conf`:

```ini
[editor]
# Starting line number for new programs
auto_number_start = 10

# Increment between auto-numbered lines
auto_number_increment = 10

# Enable/disable auto-numbering
auto_number_enabled = true
```

Configuration file search order:
1. `.mbasic.conf` in current directory
2. `.mbasic.conf` in home directory (`~/.mbasic.conf`)

### Smart Line Numbering

Auto-numbering intelligently avoids collisions:

```
Existing lines: 10, 20, 30, 100, 200

Current line: 20
Press Enter → Next line: 30 (would collide!)
              Actual: 21 (first available after 20)

Current line: 30
Press Enter → Next line: 40
              Actual: 40 (no collision, uses increment)

Current line: 100
Press Enter → Next line: 110
              Actual: 110 (no collision)
```

**Algorithm:**
1. Calculate: `next = current_line + increment`
2. Check if `next` would collide with existing line
3. If collision: use `current_line + 1` (or next available)
4. If above next line in sequence: use next available slot

## Paste Operations

### High-Performance Paste

The editor is optimized for pasting large amounts of code:

- **Instant display** - Pasted text appears in ~0.1 seconds
- **Deferred processing** - Line number parsing and sorting happens after paste completes
- **No lag** - Fast path for normal characters bypasses expensive text parsing
- **Automatic formatting** - Pasted code is automatically formatted on display

### Smart Line Number Parsing

When you paste BASIC code, line numbers are automatically detected and formatted:

#### Pasting Code Without Line Numbers

```basic
Paste:
for i=0 to 10
print i
next

Result (with auto-numbering):
   10 for i=0 to 10
   20 print i
   30 next
   40
```

Auto-numbering adds line numbers to plain code.

#### Pasting Code With Line Numbers

```basic
Paste:
210 for i=0 to 10
220  print i
230 next

Result:
  210 for i=0 to 10
  220 print i
  230 next
  240
```

**Key behaviors:**
- Line numbers from pasted code are **preserved**
- Extra spaces after line numbers are **removed** (e.g., "220  print" becomes "220 print")
- Numbers in code area are **moved to line number column**
- Replaces any auto-numbered values
- Next line continues auto-numbering from last pasted number

#### Mixed Paste (Into Auto-Numbered Lines)

If you paste "210 for..." into a line that already has auto-number "10":

```basic
Before:
   10

Paste: 210 for i=0 to 10

After:
  210 for i=0 to 10
```

The pasted line number (210) **replaces** the auto-number (10).

### Edge-to-Edge Display

The editor has **no left border** for clean copy/paste:

```
── Editor ────────────────────────
   10 PRINT "Hello"
   20 FOR I = 1 TO 10
   30 PRINT I
   40 NEXT I
```

When you select and copy text from the terminal, you get clean code without border characters.

### Scrollable Output

Press `Tab` to switch between editor and output window:

- **Editor mode** - Edit your program
- **Output mode** - Scroll through program output with Up/Down arrows
- Press `Tab` again to return to editor

Output window can display unlimited lines and is fully scrollable.

## Automatic Line Sorting

Lines are automatically sorted by line number when:

1. **Moving to a different line** (up/down arrows) while in line number area
2. **Navigating with Page Up/Down, Home, End**
3. **Executing any control command** (Ctrl+R, Ctrl+S, etc.)
4. **Pressing Enter** to create a new line

**Example workflow:**
```
1. Start with:    10 PRINT "A"
                  20 PRINT "B"
                  30 PRINT "C"

2. Go to line 10, edit number to '25':
                  25 PRINT "A"    ← edited, not sorted yet
                  20 PRINT "B"
                  30 PRINT "C"

3. Press Down arrow → Automatic sort:
                  20 PRINT "B"
                  25 PRINT "A"    ← sorted into position
                  30 PRINT "C"
```

## Implementation Details

### Architecture

The urwid UI follows the standard `UIBackend` interface defined in `src/ui/base.py`:

```python
class CursesBackend(UIBackend):
    """Urwid-based curses UI backend."""

    def __init__(self, io_handler, program_manager):
        # Initialize widgets
        self.editor = EditorWidget()
        self.output = urwid.Text("")
        self.status_bar = urwid.Text("...")

    def start(self):
        # Create UI layout
        self._create_ui()
        # Run main loop
        self.loop.run()
```

### Program Execution

When you press `Ctrl+R`, the UI:

1. **Parses editor content** - Extracts line-numbered statements
2. **Loads into program manager** - Converts text to program lines
3. **Creates capturing IO handler** - Intercepts PRINT output
4. **Runs interpreter** - Executes the program
5. **Displays results** - Shows output in the output window

### Output Capture

Program output is captured using a custom IO handler:

```python
class CapturingIOHandler:
    def __init__(self, output_list):
        self.output_list = output_list

    def output(self, text, end='\n'):
        """Capture PRINT statements to list."""
        self.output_list.append(str(text))
```

This allows PRINT statements to display in the output window instead of the terminal.

### Widget Structure

The UI uses urwid's pile layout:

```python
pile = urwid.Pile([
    ('weight', 7, editor_frame),    # 70% - Editor
    ('weight', 3, output_frame),    # 30% - Output
    ('pack', self.status_bar)       # Fixed - Status
])
```

## Features

The urwid-based curses UI provides a modern, full-featured terminal interface:

- **Active Maintenance**: urwid is actively maintained with regular updates
- **Comprehensive Documentation**: Extensive documentation and examples available
- **Clean API**: Pythonic and intuitive widget library
- **Better Performance**: Optimized rendering and event handling
- **No Cursor Bugs**: Stable cursor positioning and display
- **Extensive Widgets**: Rich widget library for complex UIs

## Current Limitations

### Implemented Features

- ✅ **Program execution** - Run BASIC programs
- ✅ **INPUT statements** - Interactive user input via dialog
- ✅ **File operations** - Save and Load programs (Ctrl+S, Ctrl+O)
- ✅ **Program listing** - View program lines (Ctrl+L)
- ✅ **Help system** - Built-in help dialog (Ctrl+H)

### Not Yet Implemented

- **Breakpoints** - Visual breakpoint indicators
- **Debugging** - Step, Continue, End commands
- **Menus** - File, Edit, Run menus
- **Syntax highlighting** - Colorized BASIC keywords
- **Mouse support** - Click to position cursor, toggle breakpoints
- **Line editing** - Auto-renum, delete ranges

### Future Development

Advanced features planned for future releases:
- Breakpoints and debugging (Step, Continue, End)
- Full menu system
- Mouse support for all operations

## Development

### Adding New Features

1. Edit `src/ui/curses_ui.py`
2. Add keyboard shortcut in `_handle_input()`
3. Implement handler method (e.g., `_save_program()`)
4. Update help text in `_show_help()`
5. Test with real programs

### Testing

Manual testing:

```bash
# Create test program
cat > test.bas << 'EOF'
10 PRINT "Test"
20 END
EOF

# Run with urwid UI
python3 mbasic.py --backend curses test.bas
```

### Debug Mode

To see error details:

```bash
python3 mbasic.py --backend curses --debug
```

Errors will appear in the output window with full tracebacks.

## Roadmap

### Short Term (v1.0)

- [ ] Add INPUT statement support
- [ ] Implement Save/Load from UI
- [ ] Add line editing commands
- [ ] Improve error messages

### Medium Term (v1.5)

- [ ] Add breakpoint support
- [ ] Implement Step/Continue/End
- [ ] Add syntax highlighting
- [ ] Create menu system

### Long Term (v2.0)

- [ ] Mouse support for all operations
- [ ] Split-pane view (code + output side-by-side)
- [ ] Watch window for variables
- [ ] Call stack viewer
- [ ] Deprecate npyscreen backend

## Resources

- **Urwid Tutorial**: http://urwid.org/tutorial/
- **Urwid Reference**: http://urwid.org/reference/
- **MBASIC Docs**: `docs/` directory
- **UI Architecture**: `src/ui/base.py`
- **Migration Guide**: `docs/dev/URWID_MIGRATION.md`

## Troubleshooting

### "No module named 'urwid'"

Install urwid:

```bash
pip install urwid
```

### "Terminal too small"

urwid requires a minimum terminal size. Resize your terminal window.

### Display issues

If you see garbled text or incorrect layouts:

1. Make sure your terminal supports UTF-8
2. Try resizing the terminal
3. Use a different terminal emulator

## Contributing

To contribute to the urwid UI:

1. Read `docs/dev/URWID_MIGRATION.md`
2. Follow the coding style in `src/ui/curses_ui.py`
3. Test your changes thoroughly
4. Update documentation

## License

Same as MBASIC interpreter - see `LICENSE` file.
