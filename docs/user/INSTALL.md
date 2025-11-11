# Installation Guide

This guide will help you install and run the MBASIC-2025 Interpreter on your computer.

## Prerequisites

You need Python 3.8 or later installed on your system.

### Check if Python is installed

Open a terminal (Command Prompt on Windows, Terminal on Mac/Linux) and run:

```bash
python3 --version
```

If you see a version number like `Python 3.9.x` or higher, you're good to go! If not, download Python from [python.org](https://www.python.org/downloads/).

> **Note:** This guide uses `python3` in all examples. On some systems (especially Windows), Python 3 is available as `python` instead. If you get "python3: command not found", try using `python` instead. See the Troubleshooting section for details.

## System Package Requirements (Root Installation)

**On Debian/Ubuntu/Linux Mint systems**, you need to install these packages via `apt` with `sudo`:

### REQUIRED for Virtual Environments
```bash
sudo apt install python3-venv
# OR for specific Python version:
sudo apt install python3.12-venv
```
This is **required** to use virtual environments (recommended). Without this, the `python3 -m venv` command will fail.

### OPTIONAL for Tkinter GUI Backend
```bash
sudo apt install python3-tk
```
Only needed if you want to use the Tkinter GUI backend. Skip this if you only need CLI/Curses/Web UIs.

**On other systems** (Fedora, macOS, Windows), virtual environment support and tkinter are usually included with Python.

## Quick Install from PyPI (Beta)

**If you just want to install and use MBASIC**, the easiest method is via PyPI:

```bash
# Install the beta version (requires --pre flag)
pip install --pre mbasic

# Or with full-screen terminal UI support
pip install --pre mbasic[curses]

# Or with all UI backends
pip install --pre mbasic[all]
```

> **Beta Note**: We're currently in BETA (version 1.0.0b1) and gathering feedback. The `--pre` flag is required to install beta releases. Once we release stable 1.0.0, the `--pre` flag will no longer be necessary.

After installation, run:
```bash
mbasic
```

**If you prefer to install from source**, continue reading the sections below.

## Python Package Dependencies

MBASIC's Python dependencies depend on which UI mode you plan to use:

| UI Mode | External Dependencies |
|---------|----------------------|
| **CLI** | None (Python standard library only) |
| **Curses** | `urwid` (install via pip) |
| **Tk** | `tkinter` (system package, see above) |
| **Web** | `nicegui` (install via pip) |

**If you only want CLI mode**, you can skip all pip dependency installation steps. Just run `python3 mbasic` and you're ready to go!

**For other UIs**, use `pip install -r requirements.txt` to install the necessary dependencies.

## Installation Methods

### Method 1: Using Virtual Environment (Recommended)

A virtual environment keeps this project's dependencies separate from your system Python. This is the recommended approach for Python projects.

#### Step 1: Download the project

```bash
# Clone the repository (if using git)
git clone https://github.com/avwohl/mbasic.git
cd mbasic

# OR download and extract the ZIP file, then:
cd mbasic
```

#### Step 2: Create a virtual environment

**On Linux/Mac:**
```bash
python3 -m venv venv
```

**On Windows:**
```cmd
python -m venv venv
```

This creates a new directory called `venv` containing an isolated Python environment.

#### Step 3: Activate the virtual environment

**On Linux/Mac:**
```bash
source venv/bin/activate
```

**On Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**On Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

You should see `(venv)` appear at the beginning of your command prompt, indicating the virtual environment is active.

#### Step 4: Install dependencies

```bash
pip install -r requirements.txt
```

This installs optional dependencies for specific UIs:
- **CLI mode**: No dependencies needed (Python standard library only)
- **Curses mode**: Requires `urwid` for terminal UI
- **Tk mode**: Requires `tkinter` (usually pre-installed with Python)
- **Web mode**: Requires `nicegui` for browser-based UI

If you only plan to use CLI mode, you can skip this step.

#### Step 5: Run the interpreter

```bash
python3 mbasic
```

Or run a BASIC program:

```bash
python3 mbasic basic/bas_tests1/hello.bas
```

#### Deactivating the virtual environment

When you're done, you can deactivate the virtual environment:

```bash
deactivate
```

### Method 2: Direct Installation (Simple)

If you don't want to use a virtual environment, you can run the interpreter directly:

```bash
# Navigate to the project directory
cd mbasic

# Run the interpreter (CLI mode - no dependencies required)
python3 mbasic
```

**Note**: CLI mode uses only Python's standard library and requires no external dependencies. For other UIs (Curses, Tk, Web), you'll need to install their dependencies via `pip install -r requirements.txt`.

### Method 3: Install as a Python Package

For system-wide installation:

```bash
cd mbasic
pip install -e .
```

After this, you can run `mbasic` from anywhere on your system.

## Verifying the Installation

### Test Interactive Mode

Run the interpreter without arguments:

```bash
python3 mbasic
```

You should see:

```
MBASIC-2025 - Modern MBASIC 5.21 Interpreter
Ready

Ok
```

Try entering:

```basic
PRINT "Hello, World!"
```

You should see the output immediately.

### Test File Execution

Run one of the included test programs:

```bash
python3 mbasic basic/tests_with_results/test_operator_precedence.bas
```

You should see:

```
All 20 tests PASS
```

## Troubleshooting

### "python3: command not found"

On some systems, Python 3 is available as `python` instead of `python3`:

```bash
python --version
```

If this shows Python 3.8 or later, you can use `python` instead of `python3`:

```bash
python mbasic
```

### Permission Denied on Linux/Mac

Make sure the script is executable:

```bash
chmod +x mbasic
./mbasic
```

### Virtual Environment Not Activating on Windows

If you get an error about execution policies in PowerShell, you may need to allow scripts:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try activating again.

### "Module not found" errors

Make sure you're in the correct directory (the `mbasic` folder containing `mbasic`).

### "ensurepip is not available" when creating venv

**On Debian/Ubuntu/Linux Mint**, if you get this error:
```
The virtual environment was not created successfully because ensurepip is not available.
```

You need to install the `python3-venv` package:
```bash
sudo apt install python3-venv
# OR for specific Python version:
sudo apt install python3.12-venv
```

This is a required system package for creating virtual environments on Debian-based systems.

## Feature Status

MBASIC-2025 is a comprehensive implementation of MBASIC 5.21. All core language features and statements are implemented and tested, with some hardware-specific features emulated or adapted for modern systems.

### What Works
- ✓ Mathematical calculations and expressions
- ✓ String processing and manipulation
- ✓ Arrays and data structures
- ✓ Control flow (IF/THEN/ELSE, FOR/NEXT, WHILE/WEND, GOTO, GOSUB, ON GOTO/GOSUB)
- ✓ Console input/output (INPUT, PRINT, PRINT USING)
- ✓ DATA/READ/RESTORE statements
- ✓ User-defined functions (DEF FN)
- ✓ Interactive mode commands (RUN, LIST, SAVE, LOAD, EDIT, DELETE, RENUM, CONT)
- ✓ Settings system (SET, SHOW SETTINGS commands with global/project configuration files)
- ✓ Sequential file I/O (OPEN, CLOSE, PRINT#, INPUT#, LINE INPUT#, WRITE#, EOF)
- ✓ Random file I/O (FIELD, GET, PUT, LSET, RSET, LOC, LOF)
- ✓ Binary file I/O (MKI$/MKS$/MKD$, CVI/CVS/CVD)
- ✓ Error handling (ON ERROR GOTO/GOSUB, RESUME, ERL, ERR)
- ✓ File system operations (KILL, NAME AS, RESET)
- ✓ Non-blocking keyboard input (INKEY$)
- ✓ Execution tracing (TRON/TROFF)
- ✓ SWAP statement and MID$ assignment

### What Doesn't Work

These are hardware-specific features that cannot work in a modern environment:
- ✗ **Hardware access** - PEEK/POKE for hardware memory access (PEEK returns random values for compatibility)
- ✗ **I/O ports** - INP/OUT for hardware ports
- ✗ **Line printer** - LPRINT, LLIST (dedicated printer output)

These limitations are inherent to running vintage BASIC in a modern environment and do not affect most programs.

**For complete implementation status and compatibility notes, see [PROJECT_STATUS.md](../PROJECT_STATUS.md)**

## Next Steps

Once installed, check out:

- Project overview and quick start guide in the main README
- [PROJECT_STATUS.md](../PROJECT_STATUS.md) - Complete implementation status
- Additional documentation in the docs/ directory
- Example BASIC programs in the basic/ directory

## Getting Help

If you encounter issues:

1. Check that you're using Python 3.8 or later
2. Make sure you're in the project directory
3. Try running with `DEBUG=1` for more detailed error messages:
   ```bash
   DEBUG=1 python3 mbasic yourprogram.bas
   ```

Happy BASIC programming!
