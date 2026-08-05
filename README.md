# MBASIC-2025: Modern MBASIC 5.21 Interpreter & Compilers

A complete implementation of Microsoft BASIC-80 5.21 (CP/M era) with an interactive interpreter and TWO compiler backends (Z80/8080 + JavaScript), written in Python.

> **About MBASIC:** MBASIC was a BASIC interpreter originally developed by Microsoft in the late 1970s. This is an independent, open-source reimplementation created for educational purposes and historical software preservation. See [MBASIC History](docs/history/MBASIC_HISTORY.md) for more information.
>
> **📄 Want the full story?** See [MBASIC Project Overview](docs/MBASIC_PROJECT_OVERVIEW.md) for a comprehensive feature showcase.

**Status:** Full MBASIC 5.21 implementation complete with 100% compatibility in interpreter and both compiler backends.

## 🎉 THREE Complete Implementations

### Interactive Interpreter (100% Complete)
- ✅ **100% Compatible**: All original MBASIC 5.21 programs run unchanged
- ✅ **Modern Extensions**: Optional debugging commands (BREAK, STEP, WATCH, STACK)
- ✅ **Multiple UIs**: CLI (classic), Curses, Tk (GUI), Web (browser)
- ✅ **Full REPL**: Interactive command mode with RUN, LIST, SAVE, LOAD, etc.

### Z80/8080 Compiler (100% Complete)
- ✅ **100% Feature Complete**: ALL compilable MBASIC 5.21 features implemented
- ✅ **Generates CP/M Executables**: Produces native .COM files for 8080 or Z80 CP/M systems
- ✅ **Efficient Runtime**: Optimized string handling with O(n log n) garbage collection
- ✅ **Hardware Access**: Full support for PEEK/POKE/INP/OUT/WAIT
- ✅ **Machine Language**: CALL/USR/VARPTR for assembly integration

### JavaScript Compiler (100% Complete)
- ✅ **100% Feature Complete**: All MBASIC 5.21 features except hardware access
- ✅ **Generates JavaScript**: Produces standalone .js files for Node.js and browsers
- ✅ **Cross-Platform**: Same code runs in browsers and Node.js
- ✅ **Full File I/O**: localStorage in browser, fs module in Node.js
- ✅ **Standalone HTML**: Optional HTML wrapper for browser deployment

See [Implementation Status](#implementation-status) section below for details, [Extensions](docs/help/mbasic/extensions.md) for modern features, [Compiler Features](#compiler-100-complete) for compiler information, and [PROJECT_STATUS.md](docs/PROJECT_STATUS.md) for current project health and metrics.

## Installation

### From PyPI

```bash
# Minimal install - CLI backend only (zero dependencies)
pip install mbasic

# With full-screen terminal UI (curses backend)
pip install "mbasic[curses]"

# With graphical UI (tkinter - included with Python)
pip install "mbasic[tk]"

# With browser-based UI (web backend)
pip install "mbasic[web]"

# With all UI backends
pip install "mbasic[all]"

# For development
pip install "mbasic[dev]"
```

Running `mbasic` with no `--ui` starts the full-screen curses UI when it is
installed, and otherwise falls back to the CLI UI. `mbasic --list-backends`
shows what is installed and how to add the rest.

**Building from source**: See [Linux Mint Developer Setup](docs/dev/LINUX_MINT_DEVELOPER_SETUP.md) for complete system setup including all required packages, compiler tools, and development dependencies.

**Note:** Tkinter is included with most Python installations. If missing:
- **Debian/Ubuntu:** `sudo apt-get install python3-tk`
- **RHEL/Fedora:** `sudo dnf install python3-tkinter`
- **macOS/Windows:** Reinstall Python from [python.org](https://python.org)

### From Source

**For end users** (interpreter only): See **[INSTALL.md](docs/user/INSTALL.md)** for detailed installation instructions.

**For developers** (full development environment including compiler): See **[Linux Mint Developer Setup](docs/dev/LINUX_MINT_DEVELOPER_SETUP.md)** for comprehensive system setup with all packages and tools.

**System Requirements (Debian/Ubuntu/Mint only):**
```bash
# REQUIRED for virtual environments:
sudo apt install python3-venv

# OPTIONAL for Tkinter GUI backend:
sudo apt install python3-tk
```

**Quick install:**

```bash
# Clone the repository
git clone https://github.com/avwohl/mbasic.git
cd mbasic

# Create and activate a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (optional - only needed for non-CLI UIs)
pip install -r requirements.txt

# Run the interpreter
python3 mbasic
```

### Check Available Backends

```bash
python3 mbasic --list-backends
```

This shows which UI backends are available on your system.

## Features

✓ **Complete MBASIC 5.21 implementation**
- 100% parser coverage for valid MBASIC programs
- All core language features (math, strings, arrays, control flow)
- Sequential and random file I/O (OPEN, CLOSE, FIELD, GET, PUT, etc.)
- Error handling (ON ERROR GOTO/GOSUB, RESUME)
- Interactive command mode (REPL)
- File execution mode

✓ **Complete language support**
- Variables with type suffixes ($, %, !, #)
- Arrays with DIM
- Control flow (IF/THEN/ELSE, FOR/NEXT, WHILE/WEND, GOSUB/RETURN, GOTO, ON GOTO/GOSUB)
- All arithmetic, relational, and logical operators
- 50+ built-in functions (SIN, COS, CHR$, LEFT$, MKI$/CVI, etc.)
- User-defined functions (DEF FN)
- DATA/READ/RESTORE
- INPUT and PRINT with formatting (including PRINT USING)
- Sequential file I/O (OPEN, CLOSE, PRINT#, INPUT#, LINE INPUT#, WRITE#, EOF)
- Random file I/O (FIELD, GET, PUT, LSET, RSET, LOC, LOF)
- Binary file I/O (MKI$/MKS$/MKD$, CVI/CVS/CVD)
- Error handling (ON ERROR GOTO/GOSUB, RESUME, ERL, ERR)
- File system operations (KILL, NAME AS, RESET)
- Non-blocking keyboard input (INKEY$)
- Execution tracing (TRON/TROFF)

✓ **Interactive mode**
- Line-by-line program entry
- Direct commands (RUN, LIST, SAVE, LOAD, NEW, DELETE, RENUM)
- Immediate mode expression evaluation
- Compatible with classic MBASIC workflow

## Quick Start

### Run a BASIC program

```bash
python3 mbasic myprogram.bas
```

### Start interactive mode (Curses Screen Editor)

```bash
python3 mbasic
```

The **curses screen editor** (default) provides a full-screen terminal interface:
- Visual line editor with auto-numbering
- Status indicators for breakpoints and errors
- **Automatic syntax checking** (marks parse errors with '?')
- Calculator-style line number editing
- Automatic line sorting
- Split-screen output window
- Optimized paste performance (instant display)
- Smart line number parsing (preserves pasted line numbers)
- Edge-to-edge display (clean copy/paste without borders)

**Features:**
- `Ctrl+R` - Run program
- `Ctrl+S` - Save program
- `Ctrl+O` - Open program
- `Ctrl+B` - Toggle breakpoint on current line
- `Ctrl+D` - Delete current line
- `Ctrl+E` - Renumber all lines (RENUM)
- `Ctrl+H` - Help
- `Tab` - Switch between editor and output
- Arrow keys, Page Up/Down for navigation
- Auto-numbering with smart collision avoidance
- Fast paste operations with automatic formatting

**Debugger:**
- `Ctrl+G` - Continue execution (from breakpoint)
- `Ctrl+T` - Step (execute one line)
- `Ctrl+X` - Stop execution

See **[Curses Editor Documentation](docs/help/ui/curses/index.md)** for complete guide.

### CLI Mode (Line-by-line REPL)

```bash
python3 mbasic --ui cli
```

Then enter your program:

```basic
MBASIC 5.21 Interpreter
Ready

10 PRINT "Hello, World!"
20 FOR I = 1 TO 10
30 PRINT I
40 NEXT I
50 END
RUN
LIST
SAVE "hello.bas"
```

## Compilers (100% Complete)

MBASIC includes **TWO fully-featured compilers**:

1. **Z80/8080 Compiler** - Generates C code and compiles to native CP/M executables for 8080 or Z80 processors
2. **JavaScript Compiler** - Generates portable JavaScript for browsers and Node.js

Both compilers are **100% feature-complete** - every MBASIC 5.21 feature that can be compiled is now implemented!

### Z80/8080 Compiler Requirements

The Z80/8080 compiler emits C, so you need a C compiler that targets CP/M, and
optionally a CP/M emulator to run the result.

**Preferred toolchain**

1. **uc80** (preferred) - C compiler for Z80/CP/M, optimized for small code size
   - Needs the `um80` assembler and `ul80` linker from the same family
   - Installation: `pip install uc80 um80`
   - https://github.com/avwohl/uc80

2. **cpmemu** (preferred) - CP/M 2.2 emulator with Z80 and 8080 CPU cores
   - Translates BDOS/BIOS calls to the host file system, so no disk image is
     needed and test programs can live anywhere in your tree
   - Installation: `.deb`/`.rpm` from the releases page, or build from source
   - https://github.com/avwohl/cpmemu

**Supported alternates**

z88dk and tnylpo also work, and are still used for the cases uc80 does not cover:
Microsoft Binary Format floats (`--math-mbf32`, matching MBASIC's exact bit
patterns), true Intel 8080 output, and the `INP`/`OUT`/`WAIT` port statements.
Building and testing with both toolchains is supported and encouraged.

3. **z88dk** (alternate) - 8080/Z80 C compiler
   - Must have `z88dk.zcc` in your PATH
   - Installation: snap, source build, or docker

4. **tnylpo** (alternate) - CP/M emulator
   - Must have `tnylpo` in your PATH
   - Installation: build from source

See `docs/dev/TOOLCHAIN_POLICY.md` for the full policy, the exact uc80 build
pipeline, and the toolchain gotchas worth knowing before you touch this code.

### JavaScript Compiler Requirements

**None!** The JavaScript compiler is built into MBASIC with zero external dependencies. Just use `mbasic --compile-js`.

### Quick Compiler Check

```bash
# Check if Z80/8080 compiler tools are installed
python3 utils/check_compiler_tools.py
```

### Compiling BASIC to CP/M (Z80/8080)

```bash
# Compile BASIC to C, then to CP/M .COM file
cd test_compile
python3 test_compile.py program.bas

# This generates:
#   program.c    - C source code
#   PROGRAM.COM  - CP/M executable (runs on 8080 or Z80 CP/M systems)
```

### Compiling BASIC to JavaScript

```bash
# Compile to JavaScript for Node.js
mbasic --compile-js program.js program.bas
node program.js

# Or compile to standalone HTML for browsers
mbasic --compile-js program.js --html program.bas
# Open program.html in any browser!

# This generates:
#   program.js   - JavaScript code
#   program.html - Standalone HTML wrapper (if --html used)
```

### Compiler Features (100% Complete!)

**Core Language (100%)**
- All data types: INTEGER (%), SINGLE (!), DOUBLE (#), STRING ($)
- Variables, arrays with DIM, multi-dimensional arrays
- All operators: arithmetic, relational, logical (AND/OR/NOT/XOR)
- Control flow: IF/THEN/ELSE, FOR/NEXT, WHILE/WEND, GOTO, GOSUB/RETURN, ON...GOTO/GOSUB
- DATA/READ/RESTORE, SWAP, RANDOMIZE

**Functions (100%)**
- Math: ABS, SGN, INT, FIX, SIN, COS, TAN, ATN, EXP, LOG, SQR, RND
- String: LEFT$, RIGHT$, MID$, CHR$, STR$, SPACE$, STRING$, HEX$, OCT$, LEN, ASC, VAL, INSTR
- Conversion: CINT, CSNG, CDBL
- Binary data: MKI$/CVI, MKS$/CVS, MKD$/CVD (for file formats)
- User-defined: DEF FN
- Memory: FRE(), VARPTR()
- Hardware: PEEK(), INP()
- Machine language: USR()

**I/O Operations (100%)**
- Console: PRINT, INPUT, PRINT USING (formatted output), TAB(), SPC()
- Sequential files: OPEN, CLOSE, PRINT#, INPUT#, LINE INPUT#, WRITE#, KILL, EOF(), LOC(), LOF()
- Random files: FIELD, GET, PUT, LSET, RSET (database-style records)
- File system: RESET (close all), NAME AS (rename), LPRINT (printer output)

**Advanced Features (100%)**
- Error handling: ON ERROR GOTO, RESUME, RESUME NEXT, RESUME line, ERR, ERL, ERROR
- Hardware access: PEEK/POKE (memory), INP/OUT (I/O ports), WAIT (port polling)
- Machine language: CALL (execute ML routine), USR (call ML function), VARPTR (get address)
- String manipulation: MID$ assignment (substring replacement)

**Optimized Runtime (Z80/8080)**
- Custom string library with O(n log n) garbage collection
- Only 1 malloc (string pool initialization) - everything else uses the pool
- In-place GC (no temp buffers)
- Efficient memory usage optimized for CP/M's limited RAM

**JavaScript Runtime**
- Leverages JavaScript's built-in garbage collection
- Clean, readable output code
- Dual runtime for Node.js and browser environments
- Virtual filesystem (localStorage) and real filesystem (fs module)

**What Works in Z80/8080 Compiler But Not Interpreter**
- PEEK/POKE - Direct memory access (hardware-specific)
- INP/OUT/WAIT - I/O port operations (hardware-specific)
- CALL/USR/VARPTR - Machine language integration
- These generate proper 8080/Z80 assembly calls in Z80/8080 compiled code!

**What Works in Both Compilers**
- All core MBASIC 5.21 language features
- Sequential and random file I/O
- Error handling
- String manipulation
- Program chaining (CHAIN)

For detailed setup instructions and compiler documentation, see:
- `docs/help/common/compiler/index.md` - Compiler guide for both backends
- `docs/dev/COMPILER_SETUP.md` - Z80/8080 compiler setup guide
- `docs/history/COMPILER_STATUS_SUMMARY.md` - Z80/8080 full feature list and status
- `docs/dev/JS_BACKEND_REMAINING.md` - JavaScript compiler feature list
- `docs/dev/TNYLPO_SETUP.md` - CP/M emulator installation (for Z80/8080 testing)

## Project Structure

```
mbasic/
├── mbasic                 # Main entry point (interpreter)
├── src/
│   ├── lexer.py              # Tokenizer (shared by interpreter & compilers)
│   ├── parser.py             # Parser - generates AST (shared)
│   ├── ast_nodes.py          # AST node definitions (shared)
│   ├── tokens.py             # Token types (shared)
│   ├── semantic_analyzer.py  # Type checking and analysis (compilers)
│   ├── codegen_backend.py    # Code generation to C (Z80/8080 compiler)
│   ├── codegen_js_backend.py # Code generation to JavaScript (JS compiler)
│   ├── runtime.py            # Runtime state management (interpreter)
│   ├── interpreter.py        # Main interpreter
│   ├── basic_builtins.py     # Built-in functions (interpreter)
│   ├── interactive.py        # Interactive REPL
│   └── ui/                   # UI backends (cli, curses, tk, web)
├── test_compile/
│   ├── test_compile.py       # Compiler test script
│   ├── mb25_string.h/.c      # String runtime library for compiled code
│   └── test_*.bas            # Compiler test programs
├── basic/
│   ├── dev/                  # Development and test programs
│   │   ├── bas_tests/            # BASIC test programs
│   │   ├── tests_with_results/   # Self-checking BASIC tests
│   │   └── bad_syntax/           # Programs with parse errors
│   ├── games/                # Game programs
│   ├── utilities/            # Utility programs
│   └── ...                   # Other categorized programs
├── tests/
│   ├── regression/           # Automated regression tests
│   ├── manual/               # Manual verification tests
│   └── run_regression.py     # Test runner
├── docs/
│   ├── user/                 # User documentation
│   ├── dev/                  # Developer documentation (includes compiler docs)
│   └── help/                 # In-UI help system content
└── utils/                    # Development utilities
```

## Documentation

### User Documentation
- **[Curses Screen Editor](docs/help/ui/curses/index.md)** - Full-screen terminal editor (default UI)
- **[Quick Reference](docs/user/QUICK_REFERENCE.md)** - Command reference
- **[Installation Guide](docs/user/INSTALL.md)** - Detailed installation instructions

### Compiler Documentation
- **[Compiler Status Summary](docs/history/COMPILER_STATUS_SUMMARY.md)** - Complete feature list (100% complete!)
- **[Compiler Setup](docs/dev/COMPILER_SETUP.md)** - z88dk installation and configuration
- **[CP/M Emulator Setup](docs/dev/TNYLPO_SETUP.md)** - tnylpo installation for testing

### Developer Documentation
- **[Linux Mint Developer Setup](docs/dev/LINUX_MINT_DEVELOPER_SETUP.md)** - Complete system setup guide (all packages & tools)
- **[Parser Implementation](docs/dev/)** - How the parser works (shared by interpreter & compiler)
- **[Interpreter Architecture](docs/dev/)** - Interpreter design overview
- **[Interpreter Implementation](docs/dev/)** - Interpreter implementation details
- **[Compiler Architecture](docs/dev/)** - Code generation and optimization

See the **[docs/](docs/)** directory for complete documentation.

## Testing

MBASIC has a comprehensive test suite with automated regression tests and BASIC program tests.

### Quick Start

Run all regression tests:
```bash
python3 tests/run_regression.py
```

Run tests in a specific category:
```bash
python3 tests/run_regression.py --category lexer
python3 tests/run_regression.py --category interpreter
```

### Test Organization

```
tests/
├── regression/          # Automated regression tests
│   ├── commands/       # REPL commands (RENUM, LIST, etc.)
│   ├── debugger/       # Debugger functionality
│   ├── editor/         # Editor behavior
│   ├── integration/    # End-to-end tests
│   ├── interpreter/    # Core interpreter features
│   ├── lexer/          # Tokenization and case handling
│   ├── parser/         # Parsing and AST generation
│   ├── serializer/     # Code formatting
│   └── ui/            # UI-specific tests
├── manual/             # Manual verification tests
└── run_regression.py   # Test runner script
```

### Test Categories

- **regression/** - Automated tests (deterministic, repeatable)
- **manual/** - Tests requiring human verification
- **debug/** - Temporary debugging tests (not tracked in git)

### BASIC Test Programs

Test BASIC programs live in `basic/dev/bas_tests/`:

```bash
# Run any BASIC test program
python3 mbasic basic/dev/bas_tests/test_operator_precedence.bas
```

Self-checking tests verify correctness and report results:
```bash
python3 mbasic basic/dev/tests_with_results/test_operator_precedence.bas
# Result: All 20 tests PASS
```

### Writing Tests

Test files must:
- Start with `test_` prefix
- Use `src.` prefix for imports (`from src.lexer import Lexer`)
- Exit with code 0 on success, 1 on failure
- Include clear assertion messages

Example test structure:
```python
#!/usr/bin/env python3
import sys
import os

# Add project root to path (3 levels up from tests/regression/category/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.lexer import Lexer

def test_feature():
    lexer = Lexer("10 PRINT \"Hello\"")
    tokens = lexer.tokenize()
    assert len(tokens) > 0, "Should tokenize code"
    print("✓ Feature works")

if __name__ == "__main__":
    try:
        test_feature()
        print("\n✅ All tests passed")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
```

**See [tests/README.md](tests/README.md) for complete testing guide.**

### Test Coverage

✓ All statement types (FOR, WHILE, IF, GOSUB, etc.)
✓ All built-in functions (ABS, INT, LEFT$, etc.)
✓ All commands (RENUM, LIST, LOAD, SAVE, etc.)
✓ Edge cases and error handling
✓ Settings system
✓ Help system
✓ Editor features (case/spacing preservation)

## Implementation Status

### Core Interpreter (✓ Complete)

- ✓ Runtime state management
- ✓ Variable storage (all type suffixes)
- ✓ Array support with DIM
- ✓ Line number resolution
- ✓ GOSUB/RETURN stack
- ✓ FOR/NEXT loops
- ✓ WHILE/WEND loops
- ✓ ON GOTO/ON GOSUB (computed jumps)
- ✓ DATA/READ/RESTORE
- ✓ Expression evaluation
- ✓ All operators
- ✓ 50+ built-in functions
- ✓ User-defined functions (DEF FN)
- ✓ Sequential file I/O (OPEN, CLOSE, PRINT#, INPUT#, LINE INPUT#, WRITE#, EOF)
- ✓ Random file I/O (FIELD, GET, PUT, LSET, RSET, LOC, LOF)
- ✓ Binary file I/O (MKI$/MKS$/MKD$, CVI/CVS/CVD)
- ✓ Error handling (ON ERROR GOTO/GOSUB, RESUME, ERL, ERR)
- ✓ File system operations (KILL, NAME AS, RESET)
- ✓ Non-blocking input (INKEY$)
- ✓ Execution tracing (TRON/TROFF)
- ✓ PRINT USING with all format types
- ✓ SWAP statement
- ✓ MID$ assignment

### Interactive Mode (✓ Complete)

- ✓ Line entry and editing
- ✓ RUN command
- ✓ LIST command (with ranges)
- ✓ SAVE/LOAD commands
- ✓ NEW command
- ✓ DELETE command
- ✓ RENUM command
- ✓ Immediate mode
- ✓ Error recovery
- ✓ CONT (continue after STOP or Ctrl+C)
- ✓ EDIT command (line editor)

### Implementation Complete

**Both interpreter and compiler are 100% feature-complete!**

**Interpreter Mode:**
- All core MBASIC 5.21 features work perfectly
- Hardware features (PEEK/POKE/INP/OUT) generate warnings (not applicable in modern environment)
- LPRINT works (outputs to console)

**Compiler Mode:**
- **EVERYTHING works** - including hardware features!
- PEEK/POKE - Direct memory access (generates real 8080/Z80 memory operations)
- INP/OUT/WAIT - I/O port operations (generates real 8080/Z80 port operations)
- CALL/USR/VARPTR - Machine language integration
- Generates native CP/M .COM executables for 8080 or Z80 processors

**What's Not Applicable:**
- Graphics/sound (not part of MBASIC 5.21 core spec)
- Interpreter commands in compiler (LIST, LOAD, SAVE - these are for interactive mode only)
- CHAIN/COMMON (program chaining - requires interpreter/loader infrastructure)

See [PROJECT_STATUS.md](docs/PROJECT_STATUS.md) for complete project metrics and health information, and [docs/history/COMPILER_STATUS_SUMMARY.md](docs/history/COMPILER_STATUS_SUMMARY.md) for detailed compiler feature list.

## Example Programs

### Factorial Calculator

```basic
10 REM Factorial calculator
20 INPUT "Enter a number"; N
30 F = 1
40 FOR I = 1 TO N
50 F = F * I
60 NEXT I
70 PRINT "Factorial of"; N; "is"; F
80 END
```

### Prime Number Checker

```basic
10 INPUT "Enter a number"; N
20 IF N < 2 THEN PRINT "Not prime" : END
30 FOR I = 2 TO SQR(N)
40 IF N MOD I = 0 THEN PRINT "Not prime" : END
50 NEXT I
60 PRINT "Prime!"
70 END
```

### Fibonacci Sequence

```basic
10 INPUT "How many numbers"; N
20 A = 0
30 B = 1
40 FOR I = 1 TO N
50 PRINT A;
60 C = A + B
70 A = B
80 B = C
90 NEXT I
100 END
```

### Hardware Access (Compiler Only)

These features work in the compiler and generate real 8080/Z80 machine code:

```basic
10 REM Hardware access example - works in compiled code!
20 REM Memory operations
30 A = PEEK(100)          ' Read byte from memory address 100
40 POKE 100, 42           ' Write byte 42 to address 100
50 REM Port I/O
60 B = INP(255)           ' Read from I/O port 255
70 OUT 255, 1             ' Write 1 to I/O port 255
80 WAIT 255, 1            ' Wait until port 255 bit 0 is set
90 REM Machine language interface
100 ADDR = VARPTR(A)      ' Get address of variable A
110 RESULT = USR(16384)   ' Call machine code at address 16384
120 CALL 16384            ' Execute machine code routine
130 END
```

Compile this with:
```bash
cd test_compile
python3 test_compile.py hardware.bas
# Generates hardware.com - runs on 8080 or Z80 CP/M systems!
```

## Development History

1. **Lexer & Parser** (October 2025)
   - Complete MBASIC 5.21 tokenizer
   - Full recursive descent parser
   - 60+ AST node types
   - 100% parsing success on corpus
   - Shared infrastructure for both interpreter and compiler

2. **Interpreter** (October 2025)
   - Runtime state management
   - All built-in functions
   - Statement execution
   - Expression evaluation
   - Bug fixes (GOSUB/RETURN, FOR/NEXT)
   - File I/O (sequential and random)
   - Error handling (ON ERROR GOTO, RESUME)

3. **Interactive Mode** (October 2025)
   - Full REPL implementation
   - All direct commands
   - Save/load functionality
   - Immediate mode
   - Multiple UI backends (CLI, Curses, Tk, Web)

4. **Z80/8080 Compiler** (October-November 2025)
   - Semantic analyzer with type checking
   - C code generator (Z88dk backend)
   - Custom string runtime (O(n log n) GC)
   - Memory optimization (zero malloc design)
   - Complete file I/O (sequential, random, binary)
   - Error handling implementation
   - **Final push (November 11, 2025):**
     - Hardware access (PEEK/POKE/INP/OUT/WAIT)
     - Machine language interface (CALL/USR/VARPTR)
     - File management (RESET/NAME/LPRINT/CHAIN)
     - **100% feature complete!**

5. **JavaScript Compiler** (November 2025)
   - JavaScript code generator
   - Dual runtime (Node.js + browser)
   - Virtual filesystem (localStorage)
   - Complete file I/O (sequential, random, binary)
   - Error handling implementation
   - **Final push (November 13, 2025):**
     - Random file access (FIELD/LSET/RSET/GET/PUT)
     - Program chaining (CHAIN)
     - **100% feature complete!**

## Credits and Disclaimers

**Original Language:** MBASIC 5.21 was created by Microsoft Corporation (1970s-1980s). See [MBASIC History](docs/history/MBASIC_HISTORY.md) for the historical context and Microsoft's role in creating BASIC interpreters.

**This Implementation:**
- Every line of code written by CLAUDE.ai
  Supervised by pet human  Aaron Wohl (2025)
- Independent, open-source project
- Not created, endorsed, or supported by Microsoft
- Based on published MBASIC 5.21 specifications and documentation
- Created for educational purposes and historical software preservation

**Credit Distribution:**
- Language design and historical implementation: Microsoft Corporation
- This Python reimplementation: Andrew Wohl and contributors
- Any bugs or issues in this implementation: Our responsibility, not Microsoft's
- Quality of the original language design: Credit to Microsoft's team

## License

GPLv3 License - see [LICENSE](LICENSE) file for details.

This project is an independent implementation created for educational and historical preservation purposes. It is not affiliated with, endorsed by, or supported by Microsoft Corporation. MBASIC and Microsoft BASIC are historical products of Microsoft Corporation.
## Related Projects

- [80un](https://github.com/avwohl/80un) - Unpacker for the CP/M archive and compression formats LBR, ARC, squeeze, crunch, and CrLZH.
- [cpmdroid](https://github.com/avwohl/cpmdroid) - Z80/CP/M emulator for Android phones and tablets. It emulates the RomWBW HBIOS interface and a VT100 terminal.
- [cpmemu](https://github.com/avwohl/cpmemu) - Z80/CP/M emulator for Linux and Windows, with Z80 and 8080 CPU cores. It translates the BDOS and BIOS calls of CP/M 2.2 programs to the host file system.
- [ioscpm](https://github.com/avwohl/ioscpm) - Z80/CP/M emulator for iOS and macOS. It emulates the RomWBW HBIOS interface and runs CP/M 2.2 and CP/M 3.
- [learn-ada-z80](https://github.com/avwohl/learn-ada-z80) - Collection of more than 90 Ada example programs for uada80, the Ada compiler for the Z80 processor and CP/M.
- [mbasic2025](https://github.com/avwohl/mbasic2025) - Reconstruction of the lost source code of MBASIC 5.21, the Microsoft BASIC-80 for CP/M. The MACRO-80 source code assembles to a binary that matches mbasic.com byte for byte.
- [mbasicc](https://github.com/avwohl/mbasicc) - C++17 interpreter for MBASIC 5.21, the Microsoft BASIC-80 for CP/M. It runs on Linux and macOS.
- [mbasicc_web](https://github.com/avwohl/mbasicc_web) - Web browser interpreter for MBASIC 5.21, the Microsoft BASIC-80 for CP/M. Emscripten compiles the mbasicc interpreter to WebAssembly.
- [mpm2](https://github.com/avwohl/mpm2) - Z80 emulator for MP/M II, the multi-user CP/M operating system. Users connect over SSH, and SFTP clients transfer files.
- [romwbw_emu](https://github.com/avwohl/romwbw_emu) - Hardware-level Z80/CP/M emulator for Linux and macOS. It emulates the RomWBW HBIOS interface and switches banks in 512 KB of ROM and 512 KB of RAM.
- [scelbal](https://github.com/avwohl/scelbal) - Floating-point BASIC interpreter for the 8080 processor and CP/M. A translator converts the original 8008 source code to 8080 source code.
- [uada80](https://github.com/avwohl/uada80) - Ada compiler for the Z80 processor and CP/M 2.2. It compiles a subset of Ada 2012 to CP/M .COM files.
- [uc80](https://github.com/avwohl/uc80) - C compiler for the Z80 processor and CP/M. It optimizes for small code size.
- [ucow](https://github.com/avwohl/ucow) - Cowgol compiler for the Z80 processor and CP/M. It runs on Linux in Python.
- [um80_and_friends](https://github.com/avwohl/um80_and_friends) - Linux toolchain that is compatible with Microsoft MACRO-80. It has an assembler, a linker, a librarian, and a disassembler.
- [upeepz80](https://github.com/avwohl/upeepz80) - Peephole optimizer for Z80 compilers that write lowercase Z80 assembly language. It shortens jumps to jr, builds djnz loops, and removes dead stores.
- [uplm80](https://github.com/avwohl/uplm80) - PL/M-80 compiler for the Z80 processor and CP/M. It writes Intel 8080 and Zilog Z80 assembly language.
- [z80cpmw](https://github.com/avwohl/z80cpmw) - Z80/CP/M emulator for Windows. It emulates the RomWBW HBIOS interface and boots CP/M from disk images.

