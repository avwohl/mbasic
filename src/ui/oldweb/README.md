# MBASIC Web UI

Full-featured web-based IDE for MBASIC using NiceGUI with complete debugger support.

## Quick Start

```bash
cd src/ui/web
python3 web_ui.py
```

Open browser to: `http://localhost:8080`

## Features

### Editor
- ✅ Code editor with line numbers
- ✅ Click line numbers to toggle breakpoints
- ✅ Breakpoint visual indicators
- ✅ Monospace font for code

### Execution
- ✅ Run, Step, Continue, Stop controls
- ✅ Real-time output display
- ✅ Interactive INPUT support via dialogs
- ✅ Tick-based interpreter for debugging
- ✅ Error handling and notifications

### Debugger
- ✅ Breakpoints with visual feedback
- ✅ Variables watch window (live updates)
- ✅ Execution stack window (FOR/GOSUB)
- ✅ Status bar showing current line

### File Management
- ✅ Upload files from computer
- ✅ Browse and load from server (with search)
- ✅ Download/save files
- ✅ 6 built-in example programs
- ✅ New/Open/Save menu

### UI
- ✅ Menu system (File, Run, Debug, Help)
- ✅ Toolbar with quick actions
- ✅ Split-pane layout (editor | output)
- ✅ Help and About dialogs

## Requirements

```bash
pip install nicegui
```

## Documentation

See `/docs/dev/WEB_UI_IMPLEMENTATION.md` for full details.

## Architecture

- **Framework**: NiceGUI (FastAPI + Vue/Quasar)
- **I/O Handler**: `src/iohandler/web_io.py`
- **Execution**: Tick-based with breakpoint support
- **Port**: 8080 (configurable)

## Usage

1. Click line numbers to set/remove breakpoints
2. Use Run to execute entire program
3. Use Step to execute line-by-line
4. Open Variables/Stack windows to watch state
5. Continue resumes from breakpoint
6. Upload files or browse server examples

## Keyboard Shortcuts (Planned)

- Ctrl+R: Run program
- Ctrl+T: Step
- Ctrl+G: Continue
- Ctrl+Q: Stop
