# MBASIC Web UI (NiceGUI Backend)

Modern browser-based interface for MBASIC 5.21 interpreter built with NiceGUI.

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

## More Detail

[Web UI (NiceGUI Backend) Details](../../../docs/dev/WEB_UI_NICEGUI_BACKEND.md) covers
features and limitations, the screen layout, menus, architecture, the execution model,
tests, the TODO list, known issues, development notes, history, and related documents.

## Credits

Built with [NiceGUI](https://nicegui.io/) - Modern Python web framework for beautiful UIs.
