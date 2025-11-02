# MBASIC Web UI (NiceGUI Backend)

Modern browser-based interface for MBASIC 5.21 interpreter built with NiceGUI.

## Features

### Implemented
- ✅ **Full-screen web editor** - Split pane with editor and output console
- ✅ **Menu bar** - File operations (New, Open, Save, Exit)
- ✅ **Toolbar** - Quick access buttons (Run, Stop, Clear Output, List Program)
- ✅ **Status bar** - Shows current operation status
- ✅ **Program execution** - Tick-based non-blocking execution
- ✅ **Output console** - View program output in real-time
- ✅ **Line-by-line editing** - Add/modify BASIC program lines
- ✅ **Syntax validation** - Parse errors shown immediately

### Limitations
- ⚠️ **INPUT statement** - Currently placeholder, needs inline input implementation
- ⚠️ **File operations** - Open/Save not yet connected to file system
- ⚠️ **Recent files** - Menu item exists but not functional

## Installation

### Requirements
- Python 3.8 or later
- NiceGUI 3.2.0 or later
- All standard MBASIC dependencies

### Install Dependencies
```bash
# Install from requirements.txt
pip install -r requirements.txt

# Or install directly
pip install nicegui>=3.2.0
```

## Usage

### Launch Web UI
```bash
python3 mbasic --ui web
```

This starts a local web server on `http://localhost:8080`. Open this URL in your browser.

### Load and Run a Program
```bash
python3 mbasic --ui web program.bas
```

The program will be loaded and can be run from the web interface.

## User Interface

### Layout
```
┌─────────────────────────────────────────────┐
│ [File] [Edit] [Run] [Help]                  │ Menu Bar
├─────────────────────────────────────────────┤
│ [Run] [Stop] [Clear] [List] [Load] [Save]   │ Toolbar
├──────────────────────┬──────────────────────┤
│                      │                      │
│  Editor Pane         │  Output Console      │
│  (Enter BASIC lines) │  (Program output)    │
│                      │                      │
│                      │                      │
├──────────────────────┴──────────────────────┤
│ Status: Ready                               │ Status Bar
└─────────────────────────────────────────────┘
```

### Keyboard Shortcuts
- **Enter** - Add/modify BASIC line from editor

### Operations

**File Menu:**
- **New** - Clear program and start fresh
- **Open** - Load BASIC program from file (TODO)
- **Save** - Save current program to file (TODO)
- **Exit** - Close web interface

**Run Menu:**
- **Run Program** - Execute current program
- **Stop Program** - Halt execution

**Toolbar Buttons:**
- **Run** - Execute program
- **Stop** - Halt execution
- **Clear Output** - Clear output console
- **List Program** - Show program listing in output
- **Load Program** - Load file (TODO)
- **Save Program** - Save file (TODO)

## Architecture

### Components

**NiceGUIBackend** (`src/ui/web/nicegui_backend.py`)
- Main UI class extending `UIBackend`
- Builds web interface with NiceGUI components
- Manages program execution state
- Routes I/O between interpreter and web UI

**SimpleWebIOHandler** (`src/ui/web/nicegui_backend.py`)
- Custom IOHandler for web output
- Routes `print()` calls to output textarea
- INPUT placeholder (needs inline input implementation)

### Execution Model

Programs run using **tick-based execution**:

1. User clicks "Run"
2. Backend creates Runtime and Interpreter instances
3. Timer starts calling `_execute_tick()` every 10ms
4. Each tick executes up to 1000 BASIC statements
5. Output is routed to web console in real-time
6. Execution continues until program ends or user clicks "Stop"

This keeps the web UI responsive during program execution.

## Testing

### Run Test Suite
```bash
pytest tests/nicegui/test_mbasic_web_ui.py -v
```

### Test Coverage
- ✅ UI initialization
- ✅ Adding program lines
- ✅ New program command
- ✅ Clear output command
- ✅ List program command
- ✅ Program execution with output

All tests use NiceGUI's `user` fixture for fast automated testing without browser.

## TODO

### High Priority
1. **Inline INPUT implementation** - Replace placeholder with input field below output
   - Should NOT use modal dialog (blocks viewing game text)
   - Use inline input field below output console
   - See `docs/dev/WEB_UI_INPUT_UX_TODO.md` for details

### Medium Priority
2. **File operations** - Connect Open/Save to actual file system
3. **Recent files menu** - Track and show recently opened files
4. **Error highlighting** - Visual feedback for parse errors in editor
5. **Syntax highlighting** - Color-code BASIC keywords

### Low Priority
6. **Multi-line editor** - Full program view instead of line-by-line
7. **Variable inspector** - View current variable values during execution
8. **Breakpoints** - Pause execution at specific lines

## Known Issues

- **INPUT statement** - Programs using INPUT will hang (placeholder not functional)
- **File dialog** - Open/Save buttons don't show file picker yet
- **Line editing** - Must re-enter entire line to modify (no direct editing)

## Development

### Project Structure
```
src/ui/web/
├── __init__.py          # Package init, exports NiceGUIBackend
├── nicegui_backend.py   # Main implementation (440+ lines)
└── README.md            # This file

tests/nicegui/
├── __init__.py
├── conftest.py          # pytest fixtures
├── main.py              # Required by NiceGUI testing
└── test_mbasic_web_ui.py  # 6 comprehensive tests
```

### Adding Features

1. Add method to `NiceGUIBackend` class
2. Wire up to UI element (button, menu item, etc.)
3. Add test to `test_mbasic_web_ui.py`
4. Run tests: `pytest tests/nicegui/test_mbasic_web_ui.py -v`
5. Manual test: `python3 mbasic --ui web`

### Code Style
- Follow existing NiceGUI patterns
- Use markers for testable elements: `ui.button(...).props('marker=btn_run')`
- Keep UI code separate from business logic
- Use SimpleWebIOHandler for all I/O routing

## History

- **v1.0.161** - Initial NiceGUI backend created from scratch
- **v1.0.162** - Fixed ProgramManager imports, all tests passing
- **v1.0.164** - Added program execution with tick-based interpreter
- **v1.0.165** - Identified INPUT UX issue, created TODO
- **v1.0.169** - Added web backend to main mbasic entry point

## Related Documentation

- `docs/dev/WORK_IN_PROGRESS.md` - Current development status
- `docs/dev/WEB_UI_INPUT_UX_TODO.md` - INPUT implementation plan
- `docs/dev/CURSES_VS_TK_GAP_ANALYSIS.md` - Feature parity reference
- `tests/nicegui/test_mbasic_web_ui.py` - Test examples

## Credits

Built with [NiceGUI](https://nicegui.io/) - Modern Python web framework for beautiful UIs.
