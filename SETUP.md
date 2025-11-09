# MBASIC Virtual Environment Setup

## System Package Requirements (Root Installation)

**REQUIRED** - Must be installed via apt/sudo:
```bash
sudo apt install python3.12-venv
```
This package is **required** to create virtual environments on Debian/Ubuntu/Mint systems.

**OPTIONAL** - Only needed for Tkinter GUI backend:
```bash
sudo apt install python3-tk
```
This package enables the Tkinter GUI backend. Skip if you only need CLI/Curses/Web UIs.

## Initial Setup (already completed)
```bash
# 1. Install system packages (see above - required: python3.12-venv, optional: python3-tk)
sudo apt install python3.12-venv python3-tk

# 2. Create virtual environment
python3 -m venv venv

# 3. Install Python dependencies (all installed in venv, no root needed)
venv/bin/pip install --upgrade pip
venv/bin/pip install urwid python-frontmatter nicegui
```

## Daily Usage

### Activate the virtual environment
```bash
source venv/bin/activate
```

### Or run directly without activating
```bash
venv/bin/python3 mbasic [options]
```

### Examples
```bash
# List available backends
venv/bin/python3 mbasic --list-backends

# Run with CLI backend
venv/bin/python3 mbasic --ui cli program.bas

# Run with Curses backend (default)
venv/bin/python3 mbasic --ui curses program.bas

# Run with Tkinter GUI
venv/bin/python3 mbasic --ui tk program.bas

# Run with Web UI (opens in browser)
venv/bin/python3 mbasic --ui web
venv/bin/python3 mbasic --ui web --port 3000  # Custom port

# Interactive mode (default: curses)
venv/bin/python3 mbasic
```

## Installed Components
- **Python**: 3.12.3
- **Virtual environment**: ./venv/
- **Python packages**: urwid 3.0.3, python-frontmatter 1.1.0, nicegui 3.2.0, and dependencies

## Available Backends (ALL ✓)
- ✓ **CLI** - Line-based interface (no extra deps)
- ✓ **Visual** - Generic stub (no extra deps)
- ✓ **Curses** - Full-screen terminal UI (urwid 3.0.3)
- ✓ **Tkinter** - Graphical UI (python3-tk)
- ✓ **Web** - Browser-based UI (nicegui 3.2.0)

## System Packages Installed (via apt/sudo)
- **python3.12-venv** - REQUIRED for creating virtual environments on Debian/Ubuntu/Mint
- **python3-tk** - OPTIONAL for Tkinter GUI backend only

All other dependencies are installed locally in the venv (no root access needed).
