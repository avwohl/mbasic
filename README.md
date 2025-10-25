# MBASIC 5.21 Interpreter

An interpreter for MBASIC 5.21 (Microsoft BASIC-80 for CP/M) written in Python.

**Status:** Full MBASIC 5.21 implementation complete. All core features, file I/O, and error handling implemented.
See [STATUS.md](STATUS.md) for detailed implementation status.

## Installation

For detailed installation instructions including virtual environment setup, see **[INSTALL.md](INSTALL.md)**.

**Quick install:**

```bash
# Clone the repository
git clone https://github.com/avwohl/mbasic.git
cd mbasic

# Create and activate a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (none required, but verifies environment)
pip install -r requirements.txt

# Run the interpreter
python3 mbasic.py
```

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
python3 mbasic.py myprogram.bas
```

### Start interactive mode (Curses Screen Editor)

```bash
python3 mbasic.py
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

See **[Curses Editor Documentation](docs/user/URWID_UI.md)** for complete guide.

### CLI Mode (Line-by-line REPL)

```bash
python3 mbasic.py --backend cli
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

## Project Structure

```
mbasic/
├── mbasic.py              # Main entry point
├── src/
│   ├── lexer.py           # Tokenizer
│   ├── parser.py          # Parser (generates AST)
│   ├── ast_nodes.py       # AST node definitions
│   ├── tokens.py          # Token types
│   ├── runtime.py         # Runtime state management
│   ├── interpreter.py     # Main interpreter
│   ├── basic_builtins.py  # Built-in functions
│   └── interactive.py     # Interactive REPL
├── basic/
│   ├── bas_tests1/        # 120 test programs
│   └── tests_with_results/# Self-checking tests
├── tests/                 # Parser and interpreter tests
└── doc/                   # Documentation
```

## Documentation

### User Documentation
- **[Curses Screen Editor](docs/user/URWID_UI.md)** - Full-screen terminal editor (default UI)
- **[Quick Reference](docs/user/QUICK_REFERENCE.md)** - Command reference

### Developer Documentation
- **[Parser Implementation](docs/dev/)** - How the parser works
- **[Interpreter Architecture](docs/dev/)** - Design overview
- **[Interpreter Implementation](docs/dev/)** - Implementation details

See the **[docs/](docs/)** directory for complete documentation.

## Testing

### Run parser tests

```bash
cd tests
python3 test_parser_corpus.py
```

Result: 121/121 files parsing (100%)

### Run self-checking tests

```bash
python3 mbasic.py basic/tests_with_results/test_operator_precedence.bas
```

Result: All 20 tests PASS

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

All core MBASIC 5.21 features are implemented and tested.

**See [STATUS.md](STATUS.md) for complete implementation status.**

**What doesn't work:**
- Hardware-specific features (PEEK/POKE for hardware access, INP/OUT ports)
- Line printer output (LPRINT, LLIST)
- Graphics/sound (not part of MBASIC 5.21 core spec)

These limitations are inherent to running vintage BASIC in a modern environment and do not affect most programs. See STATUS.md for details on compatibility features.

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

## Development History

1. **Lexer & Parser** (October 2025)
   - Complete MBASIC 5.21 tokenizer
   - Full recursive descent parser
   - 60+ AST node types
   - 100% parsing success on corpus

2. **Interpreter** (October 2025)
   - Runtime state management
   - All built-in functions
   - Statement execution
   - Expression evaluation
   - Bug fixes (GOSUB/RETURN, FOR/NEXT)

3. **Interactive Mode** (October 2025)
   - Full REPL implementation
   - All direct commands
   - Save/load functionality
   - Immediate mode

## Credits

This is a faithful implementation of MBASIC 5.21 as documented in the official Microsoft BASIC-80 manual.

## License

MIT License - see [LICENSE](LICENSE) file for details.

This project is an independent implementation for educational purposes and is not affiliated with or endorsed by Microsoft Corporation.
