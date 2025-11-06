# Web UI Implementation Guide

**Date**: 2025-10-25

## Overview

Implemented a NiceGUI-based web interface for MBASIC that provides a modern IDE experience in the browser.

## Architecture

```
Browser ←→ HTTP/WebSocket ←→ NiceGUI (FastAPI) ←→ MBASIC Interpreter
```

**Key Components**:
- **Frontend**: NiceGUI with Vue/Quasar components
- **Backend**: FastAPI with WebSocket support (built into NiceGUI)
- **I/O Bridge**: `WebIOHandler` for PRINT/INPUT
- **Session**: Single-user for now (multi-user ready)

## Files Created

### Core Implementation

**`src/ui/web/web_ui.py`** - Main web IDE application
- `MBasicWebIDE` class with NiceGUI UI
- Split-pane layout (editor | output)
- Async program execution
- Example programs
- Error handling

**`src/iohandler/web_io.py`** - Web-specific I/O handler
- `WebIOHandler` class extending `IOHandler`
- `print()` - Outputs to NiceGUI log
- `input()` - Shows dialog for user input
- Async-safe blocking for INPUT statements

### Directory Structure

```
src/ui/web/
├── web_ui.py           # Main application
├── components/         # Future: Reusable UI components
├── static/
│   └── examples/       # Future: Example programs
└── sessions/           # Future: User session data
```

## How It Works

### 1. UI Layout

Split-pane interface:

**Left Panel** - Program Editor:
- Textarea for BASIC code (will upgrade to Monaco/CodeMirror)
- Toolbar: Run, Stop, Clear Output, New, Examples

**Right Panel** - Output:
- `ui.log()` component for program output
- Auto-scrolling
- 1000 line history

### 2. Program Execution

```python
async def run_program(self):
    # Parse BASIC code
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()

    # Create web I/O handler
    self.io_handler = WebIOHandler(self.output_log)

    # Run in background thread (non-blocking)
    await asyncio.to_thread(self.interpreter.run)
```

**Key Points**:
- Runs in background thread via `asyncio.to_thread()`
- Doesn't block UI updates
- I/O operations communicate with UI

### 3. I/O Handling

**PRINT statements**:
```python
def print(self, text="", end="\n"):
    output = str(text) + end
    if output.endswith("\n"):
        output = output[:-1]
    self.output_log.push(output)
```

**INPUT statements**:
```python
def input(self, prompt=""):
    # Show dialog with input field
    with ui.dialog() as dialog, ui.card():
        input_field = ui.input(label='Enter value')
        ui.button('OK', on_click=lambda: submit())

    # Block until user responds (safe - we're in asyncio.to_thread)
    while self._input_result is None:
        time.sleep(0.1)

    return self._input_result
```

### 4. Example Programs

Built-in examples accessible via Examples button:
- Hello World
- Loops (FOR/NEXT)
- Fibonacci sequence
- User Input (INPUT statement)

## Running the Web UI

### Start Server

```bash
cd src/ui/web
python3 web_ui.py
```

Server starts on: `http://localhost:8080`

### Access

Open browser to:
- `http://localhost:8080` (local)
- `http://<your-ip>:8080` (network access)

### Stop Server

Press Ctrl+C in terminal

## Features Implemented

### Core Features
- ✅ Code editor with line numbers
- ✅ Breakpoint support (click line numbers)
- ✅ Program execution with tick-based interpreter
- ✅ PRINT output to log
- ✅ INPUT via dialogs
- ✅ Error display with notifications
- ✅ Example programs (6 built-in examples)
- ✅ Clear output
- ✅ New program
- ✅ Syntax error handling
- ✅ Runtime error handling

### File Operations
- ✅ Upload from computer (.BAS files)
- ✅ Browse and load from server (with search)
- ✅ Download/save files

### Debugger
- ✅ Breakpoints (visual indicators in line numbers)
- ✅ Run, Step, Continue, Stop controls
- ✅ Variables watch window (real-time updates)
- ✅ Execution stack window (FOR loops, GOSUB stack)
- ✅ Status display (current line, breakpoint status)

### UI/UX
- ✅ Menu system (File, Run, Debug, Help)
- ✅ Toolbar with quick actions
- ✅ Split-pane layout
- ✅ Monospace font for code
- ✅ Breakpoint highlighting
- ✅ Help and About dialogs

## Features Not Yet Implemented

- ❌ Monaco/CodeMirror editor integration (using textarea)
- ❌ Syntax highlighting
- ❌ Multi-user sessions
- ❌ Sharing programs via URL
- ❌ Keyboard shortcuts (planned: Ctrl+R, Ctrl+T, etc.)
- ❌ Mobile responsive design
- ❌ Dark mode toggle

## Technical Details

### Dependencies

Installed via `pip install nicegui`:
- `nicegui==3.1.0` - Main framework
- `fastapi` - Web framework (bundled)
- `uvicorn` - ASGI server (bundled)
- `websockets` - Real-time communication (bundled)

### Import Path Setup

Since web UI is in `src/ui/web/`, need to add parent directories to path:

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from iohandler.web_io import WebIOHandler
from lexer import Lexer
from parser import Parser
```

### NiceGUI Event Loop

NiceGUI runs its own asyncio event loop. To run blocking code (like MBASIC interpreter):

```python
# DON'T do this - blocks UI:
self.interpreter.run()

# DO this - runs in thread pool:
await asyncio.to_thread(self.interpreter.run)
```

### INPUT Dialog Blocking

The interpreter expects `input()` to block until user responds. Since we're in `asyncio.to_thread()`, this is safe:

```python
# Blocking is OK here - we're in a thread
while self._input_result is None:
    time.sleep(0.1)
```

## Comparison to Other UIs

| Feature | CLI | Curses | Tk | Web |
|---------|-----|--------|----|----|
| Visual Editor | ❌ | ✅ | ✅ | ✅ |
| Syntax Highlighting | ❌ | ✅ | ✅ | ⏳ |
| Debugger | ❌ | ✅ | ✅ | ⏳ |
| Remote Access | ❌ | ⚠️ (SSH) | ❌ | ✅ |
| Multi-user | ❌ | ❌ | ❌ | ⏳ |
| Mobile-friendly | ❌ | ❌ | ❌ | ✅ |
| Install Required | ✅ | ✅ | ✅ | ❌ |
| Shareability | ❌ | ❌ | ❌ | ⏳ |

## Next Steps

### Phase 1: Core Features (1-2 days)
1. Implement Stop button (interrupt execution)
2. Add file save/load (download/upload .BAS files)
3. Upgrade editor to Monaco or nicegui-codemirror
4. Add syntax highlighting

### Phase 2: Enhanced Features (2-3 days)
5. Add line numbers to editor
6. File browser for examples
7. Session persistence (save program in browser localStorage)
8. Keyboard shortcuts (Ctrl+S for save, F5 for run)

### Phase 3: Advanced Features (3-5 days)
9. Multi-user sessions (unique URLs per user)
10. Share programs via URL
11. Debugger UI (integrate with existing debugger)
12. Variable watch window
13. Execution stack display

## Troubleshooting

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'iohandler'`

**Solution**: Make sure to run from `src/ui/web/` directory or set PYTHONPATH:

```bash
cd src/ui/web
python3 web_ui.py
```

### Port Already in Use

**Problem**: `OSError: [Errno 98] Address already in use`

**Solution**: Kill existing process or use different port:

```python
ui.run(port=8081)  # Use different port
```

Or kill the process:

```bash
lsof -ti:8080 | xargs kill -9
```

### INPUT Doesn't Work

**Problem**: INPUT dialog doesn't appear or hangs

**Solution**: Ensure using `asyncio.to_thread()` for interpreter execution:

```python
await asyncio.to_thread(self.interpreter.run)  # Correct
# NOT: self.interpreter.run()  # Wrong - blocks
```

## Code Examples

### Adding a New Example Program

Edit `web_ui.py`, add to `show_examples()`:

```python
examples = {
    'My Program': '''10 REM My program
20 PRINT "Hello!"
30 END
''',
    # ... other examples
}
```

### Customizing the UI

**Change colors**:

```python
ui.colors(
    primary='#1976D2',    # Blue
    secondary='#26A69A',  # Teal
    accent='#9C27B0'      # Purple
)
```

**Change port**:

```python
ui.run(
    title='MBASIC Web IDE',
    port=8080,  # Change this
)
```

**Auto-open browser**:

```python
ui.run(
    show=True,  # Opens browser automatically
)
```

## Security Considerations

**Current Status**: Development only - NOT production-ready

**Issues**:
- No authentication
- No sandboxing
- Unrestricted file access (via BASIC OPEN statements)
- No resource limits

**For Production**:
1. Add authentication (user accounts)
2. Sandbox MBASIC execution (Docker container)
3. Restrict file system access
4. Add resource limits (CPU, memory, time)
5. Rate limiting
6. HTTPS required

## Estimated Timeline

**Total: 3 days to working IDE** ✅ **COMPLETED**

- Day 1: Basic UI + I/O (✅ Done)
- Day 2: Testing + polish (⏳ In progress)
- Day 3: Documentation + deployment (⏳ Pending)

**Current Status**: Day 1 complete, basic web UI functional

## Success Metrics

- ✅ Web UI starts without errors
- ✅ Can edit BASIC code
- ✅ PRINT output displays correctly
- ✅ INPUT prompts work
- ✅ Errors display properly
- ✅ Examples load correctly

## Conclusion

Successfully implemented a basic but functional web UI for MBASIC using NiceGUI. The UI provides a modern browser-based IDE experience while reusing the existing MBASIC interpreter infrastructure. Ready for testing and incremental feature additions.
