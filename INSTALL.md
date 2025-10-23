# Installation Guide

This guide will help you install and run the MBASIC 5.21 Interpreter on your computer.

## Prerequisites

You need Python 3.8 or later installed on your system.

### Check if Python is installed

Open a terminal (Command Prompt on Windows, Terminal on Mac/Linux) and run:

```bash
python3 --version
```

If you see a version number like `Python 3.9.x` or higher, you're good to go! If not, download Python from [python.org](https://www.python.org/downloads/).

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

Note: Since this project has no external dependencies, this step mainly verifies your Python environment is working correctly.

#### Step 5: Run the interpreter

```bash
python3 mbasic.py
```

Or run a BASIC program:

```bash
python3 mbasic.py basic/bas_tests1/hello.bas
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

# Run the interpreter
python3 mbasic.py
```

This method works fine since the project has no external dependencies.

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
python3 mbasic.py
```

You should see:

```
MBASIC 5.21 Interpreter
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
python3 mbasic.py basic/tests_with_results/test_operator_precedence.bas
```

You should see:

```
All 20 tests PASS
```

## Troubleshooting

### "python3: command not found"

Try using `python` instead of `python3`:

```bash
python --version
python mbasic.py
```

### Permission Denied on Linux/Mac

Make sure the script is executable:

```bash
chmod +x mbasic.py
./mbasic.py
```

### Virtual Environment Not Activating on Windows

If you get an error about execution policies in PowerShell, you may need to allow scripts:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try activating again.

### "Module not found" errors

Make sure you're in the correct directory (the `mbasic` folder containing `mbasic.py`).

## Important Limitations

This interpreter is a work in progress. Before using it, be aware of these limitations:

### What Works
- ✓ Mathematical calculations and expressions
- ✓ String processing and manipulation
- ✓ Arrays and data structures
- ✓ Control flow (IF/THEN/ELSE, FOR/NEXT, GOTO, GOSUB)
- ✓ Console input/output (INPUT, PRINT)
- ✓ DATA/READ/RESTORE statements
- ✓ User-defined functions (DEF FN)
- ✓ Interactive mode commands (RUN, LIST, SAVE, LOAD, etc.)

### What Does NOT Work Yet
- ✗ **File I/O** - Cannot read or write data files (OPEN, CLOSE, PRINT#, INPUT#)
- ✗ **Error handling** - Cannot trap errors (ON ERROR GOTO, RESUME)
- ✗ **WHILE/WEND loops** - Parser recognizes them but runtime raises error (use FOR/NEXT instead)
- ✗ **Computed jumps** - ON GOTO and ON GOSUB not implemented (use IF/THEN chains)

### What Programs Will Work

Programs that:
- Do math calculations
- Process strings
- Use arrays and variables
- Accept user input and display results
- Use FOR/NEXT loops and IF/THEN logic

### What Programs Will NOT Work

Programs that:
- Read or write data files
- Use WHILE/WEND loops
- Need error trapping
- Use ON GOTO or ON GOSUB

**For complete implementation status, see [STATUS.md](STATUS.md)**

## Next Steps

Once installed, check out:

- [README.md](README.md) - Project overview and quick start guide
- [STATUS.md](STATUS.md) - Complete implementation status
- [doc/](doc/) - Detailed documentation
- [basic/bas_tests1/](basic/bas_tests1/) - Example BASIC programs to try

## Getting Help

If you encounter issues:

1. Check that you're using Python 3.8 or later
2. Make sure you're in the project directory
3. Try running with `DEBUG=1` for more detailed error messages:
   ```bash
   DEBUG=1 python3 mbasic.py yourprogram.bas
   ```

Happy BASIC programming!
