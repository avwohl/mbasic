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
- **Automatic syntax checking** - Real-time parse error detection with '?' markers
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
| `Ctrl+B` | Toggle breakpoint on current line |
| `Ctrl+D` | Delete current line |
| `Ctrl+E` | Renumber all lines (RENUM) |
| `Ctrl+G` | Continue execution (from breakpoint) |
| `Ctrl+T` | Step - execute one line |
| `Ctrl+X` | Stop execution |
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
| [0] | Status | `?` = error (highest), `●` = breakpoint, ` ` = normal |
| [1-5] | Line Number | 5 digits, right-aligned (e.g., "   10") |
| [6] | Separator | Always a space character |
| [7+] | Code | BASIC program code |

**Status Priority:**
When a line has multiple states (error + breakpoint), the status character shows the highest priority:
1. **Error (`?`)** - Highest priority, always shown when syntax error exists
2. **Breakpoint (`●`)** - Shown when no error but breakpoint is set
3. **Normal (` `)** - Default when neither error nor breakpoint

**Example:** If line 10 has both an error and a breakpoint:
- While error exists: `?   10 foo` (shows error)
- After fixing error: `●   10 PRINT "ok"` (shows breakpoint)

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

## Automatic Syntax Checking

The editor automatically checks syntax as you type and marks errors with the '?' indicator.

### How It Works

- **Real-time checking** - Syntax is validated after 0.1s of idle time
- **Visual feedback** - Lines with parse errors show '?' in status column
- **Error messages** - Detailed error descriptions appear in output window
- **Auto-clearing** - Error markers disappear when you fix the syntax
- **Safe operation** - Uses isolated parser, won't affect running programs or breakpoints

### Status Column Indicators

| Indicator | Meaning |
|-----------|---------|
| ` ` (space) | Normal line, no errors |
| `?` | Parse error (syntax problem) |
| `●` | Breakpoint set (not yet implemented) |

### Examples

**Valid syntax:**
```basic
   10 PRINT "Hello"
   20 FOR I = 1 TO 10
   30 NEXT I
```

**With syntax errors:**
```basic
   10 PRINT "Hello"
?  20 FOR I = 1 TO       (incomplete statement)
?  30 PRINT "Missing     (missing closing quote)
   40 END
```

**Output window shows:**
```
=== Syntax Errors ===

Line 20: Expected expression after TO
Line 30: Unterminated string
```

### Error Messages

When syntax errors are detected, detailed messages appear in the output window:

**Format:**
```
=== Syntax Errors ===

Line <number>: <error description>
```

**Example error messages:**
- `Invalid statement: 'foo' is not a BASIC keyword` - Bare identifier
- `Unterminated string` - Missing closing quote
- `Expected expression after TO` - Incomplete FOR loop
- `Unexpected token: THEN` - Syntax error in IF statement

**Behavior:**
- Errors update automatically as you type
- Sorted by line number for easy reference
- Clear when you fix all errors
- Replaced by program output when you run code

### What Gets Checked

The parser validates:
- **Lexical errors** - Invalid tokens, unterminated strings
- **Syntax errors** - Incomplete statements, wrong keyword usage
- **Statement structure** - Proper BASIC statement format

### What Doesn't Get Checked

Runtime-only errors are **not** detected:
- Variable not defined (runtime error)
- Array out of bounds (runtime error)
- Division by zero (runtime error)
- Type mismatches (detected at runtime)
- Line number references (GOTO/GOSUB to non-existent line)

### Performance

Syntax checking is optimized:
- Only checks lines that changed
- Runs after typing stops (0.1s delay)
- Doesn't slow down paste operations
- Minimal impact on editing responsiveness

### Working with Breakpoints

Breakpoints can be toggled on any line using `Ctrl+B`. The status column shows:
- Line with breakpoint only: `●`
- Line with error only: `?`
- Line with both: `?` (error takes priority)

**How to use breakpoints:**
1. Position cursor on any line
2. Press `Ctrl+B` to toggle breakpoint
3. Status bar shows "Breakpoint set on line X" or "Breakpoint removed from line X"
4. Line's status column updates to show `●` (or `?` if line also has error)

**Priority system:** When a line has both an error and a breakpoint, the error (`?`) is shown. After fixing the error, the breakpoint indicator (`●`) becomes visible.

### Debugger Commands

The curses UI includes a full-featured debugger for step-by-step execution and debugging.

#### Setting Breakpoints

1. Position cursor on the line where you want to pause
2. Press `Ctrl+B` to toggle breakpoint
3. Status column shows `●` for lines with breakpoints
4. Run program with `Ctrl+R`

#### Debugger Commands

| Command | Key | Description |
|---------|-----|-------------|
| **Step** | `Ctrl+T` | Execute one line and pause |
| **Continue** | `Ctrl+G` | Continue execution until next breakpoint or end |
| **Stop** | `Ctrl+X` | Stop program execution immediately |

#### Debugging Workflow

**Basic debugging:**
```
1. Set breakpoint on line 20:
   ●   20 FOR I = 1 TO 10

2. Run program (Ctrl+R)
   → Program runs and pauses at line 20
   Output: "● Breakpoint hit at line 20"
   Status: "Paused at line 20 - Ctrl+T=Step, Ctrl+G=Continue, Ctrl+X=Stop"

3. Step through (Ctrl+T)
   → Executes line 20, pauses at line 30
   Output: "→ Paused at line 30"

4. Continue (Ctrl+G)
   → Runs until next breakpoint or program end

5. Stop (Ctrl+X)
   → Stops execution immediately
   Output: "Program stopped by user"
```

**Stepping through code:**
```
Program:
●   10 X = 0
    20 FOR I = 1 TO 3
    30   X = X + I
    40   PRINT X
    50 NEXT I

Workflow:
1. Ctrl+R → Runs and hits breakpoint at line 10
2. Ctrl+T → Executes line 10, pauses at line 20
3. Ctrl+T → Executes line 20, pauses at line 30
4. Ctrl+T → Executes line 30, pauses at line 40
5. Ctrl+T → Executes line 40 (prints "1"), pauses at line 50
6. Ctrl+G → Continues to end of program
```

**Multiple breakpoints:**
```
●   10 PRINT "Start"
    20 FOR I = 1 TO 5
●   30   PRINT I
    40 NEXT I
●   50 PRINT "Done"

Workflow:
1. Ctrl+R → Pauses at line 10
2. Ctrl+G → Runs lines 10-20, pauses at line 30
3. Ctrl+G → Prints "1", continues loop, pauses at line 30 again
4. Ctrl+G → Prints "2", continues loop, pauses at line 30 again
   (Repeats for each loop iteration)
5. Ctrl+G → After loop ends, pauses at line 50
6. Ctrl+G → Prints "Done", program ends
```

#### Debugger Messages

**Breakpoint hit:**
```
● Breakpoint hit at line 20
```

**Stepping:**
```
→ Paused at line 30
```

**Program status:**
- Status bar shows: "Paused at line X - Ctrl+T=Step, Ctrl+G=Continue, Ctrl+X=Stop"
- Clear indication of available commands
- Current line number displayed

**Stopping:**
```
Program stopped by user
```

#### Tips

- **Set multiple breakpoints** - Pause at different points in your code
- **Step through loops** - Use Ctrl+T to see each iteration
- **Continue past breakpoints** - Use Ctrl+G to skip to next interesting point
- **Stop anytime** - Press Ctrl+X if program is stuck or running too long
- **Combine with output** - Watch output window to see results of each step

### Line Editing Commands

#### Delete Line (Ctrl+D)

Quickly delete the current line where the cursor is positioned.

**Usage:**
1. Position cursor on any line
2. Press `Ctrl+D`
3. Line is immediately removed
4. Status bar shows "Deleted line X"
5. Cursor moves to next line (or previous if at end)

**What gets deleted:**
- The line from the display
- The line from the program
- Any breakpoint on that line
- Any syntax error for that line

**Example:**
```
Before:                After Ctrl+D:
●   10 PRINT "A"      ●   10 PRINT "A"
    20 PRINT "B"  ←       30 PRINT "C"
    30 PRINT "C"
```

#### Renumber Lines (Ctrl+E)

Renumber all program lines with custom start and increment values.

**Usage:**
1. Press `Ctrl+E`
2. Enter start line number (default: 10)
3. Enter increment (default: 10)
4. All lines are renumbered
5. Status bar shows "Renumbered N lines from X by Y"

**What gets updated:**
- All line numbers in sequence
- Breakpoints move to new line numbers
- Syntax errors move to new line numbers
- Status indicators preserved

**Example:**
```
Before:                After RENUM 100, 5:
    15 PRINT "A"           100 PRINT "A"
●   27 PRINT "B"       ●   105 PRINT "B"
?   38 PRINT "C"       ?   110 PRINT "C"
    49 END                 115 END
```

**Dialog prompts:**
- "RENUM - Start line number (default 10):" - Press Enter for default or type number
- "RENUM - Increment (default 10):" - Press Enter for default or type number

**Notes:**
- Empty input uses default values (10, 10)
- Only renumbers lines with valid line numbers
- Preserves all breakpoints and error markers
- Does NOT update GOTO/GOSUB references (use CLI RENUM for that)

### Error Messages

The curses UI provides enhanced error messages with context and helpful formatting.

#### Error Types

**1. Syntax Errors (shown while editing):**
```
┌─ Syntax Errors ──────────────────────────────────┐
│
│ Line 10:
│   foo
│   ^^^^
│ Error: Invalid statement: 'foo' is not a BASIC keyword
│
└──────────────────────────────────────────────────┘
```

**2. Parse Errors (when running program):**
```
┌─ Parse Error ────────────────────────────────────┐
│ Line 20:
│   FOR I = 1 TO
│   ^^^^
│ Error: Expected expression after TO
│
│ Fix the syntax error and try running again.
└──────────────────────────────────────────────────┘
```

**3. Runtime Errors (during execution):**
```
┌─ Runtime Error ──────────────────────────────────┐
│ Line 30:
│   PRINT 1/0
│   ^^^^
│ Error: Division by zero
└──────────────────────────────────────────────────┘
```

**4. Execution Errors (unexpected errors):**
```
┌─ Execution Error ────────────────────────────────┐
│ TypeError: unsupported operand type(s)
│
│ An error occurred during program execution.
└──────────────────────────────────────────────────┘
```

#### Error Message Features

- **Boxed formatting** - Clear visual separation from output
- **Code context** - Shows the actual line of code that failed
- **Line numbers** - Easy to locate the problem
- **Error indicators** - `^^^^` points to the problematic code
- **Helpful hints** - Suggestions for fixing common errors
- **Status bar updates** - Quick error type indication

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

- [x] Add INPUT statement support (dialog prompts work)
- [x] Implement Save/Load from UI (Ctrl+S, Ctrl+O)
- [x] Add line editing commands (Ctrl+D delete, Ctrl+E renumber)
- [x] Improve error messages (context, boxes, helpful hints)

### Medium Term (v1.5)

- [x] Add breakpoint support (toggle with Ctrl+B)
- [x] Implement Step/Continue/Stop debugger (Ctrl+T/Ctrl+G/Ctrl+X)
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
