# MBASIC 5.21 Interpreter

An interpreter for MBASIC 5.21 (Microsoft BASIC-80 for CP/M) written in Python.

**Status:** Core language features complete (~65%). File I/O and error handling not yet implemented.
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

✓ **MBASIC 5.21 core features**
- 100% parser coverage for valid MBASIC programs
- Core language features implemented (math, strings, arrays, control flow)
- Interactive command mode (REPL)
- File execution mode
- **Note:** File I/O and error handling not yet implemented

✓ **Complete language support**
- Variables with type suffixes ($, %, !, #)
- Arrays with DIM
- Control flow (IF/THEN/ELSE, FOR/NEXT, GOSUB/RETURN, GOTO)
- All arithmetic, relational, and logical operators
- 35+ built-in functions (SIN, COS, CHR$, LEFT$, etc.)
- User-defined functions (DEF FN)
- DATA/READ/RESTORE
- INPUT and PRINT with formatting

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

### Start interactive mode

```bash
python3 mbasic.py
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

- **[Parser Implementation](doc/PARSER_REFACTORING_2025-10-22.md)** - How the parser works
- **[Interpreter Architecture](doc/INTERPRETER_COMPILER_ARCHITECTURE_2025-10-22.md)** - Design overview
- **[Interpreter Implementation](doc/INTERPRETER_IMPLEMENTATION_2025-10-22.md)** - Implementation details
- **[Interactive Mode](doc/INTERACTIVE_MODE_2025-10-22.md)** - REPL documentation
- **[Token Analysis](doc/TOKEN_USAGE_SUMMARY_2025-10-22.md)** - Token usage statistics
- **[Parse Tree Structure](doc/PARSE_TREE_STRUCTURE_2025-10-22.md)** - AST documentation

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
- ✓ DATA/READ/RESTORE
- ✓ Expression evaluation
- ✓ All operators
- ✓ 35+ built-in functions
- ✓ User-defined functions (DEF FN)

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

### Not Yet Implemented

**Critical features missing:**
- ✗ Sequential file I/O (OPEN, CLOSE, PRINT#, INPUT#, LINE INPUT#, WRITE#, EOF)
- ✗ Random file I/O (FIELD, GET, PUT, LSET, RSET, LOC, LOF)
- ✗ Error handling (ON ERROR GOTO, RESUME)
- ✗ WHILE/WEND loops (parsed but not executed)
- ✗ Computed jumps (ON GOTO, ON GOSUB)

**See [STATUS.md](STATUS.md) for complete implementation status.**

**What this means:**
- Programs using file I/O will not work
- Programs cannot trap and handle errors
- Use FOR/NEXT instead of WHILE/WEND
- Graphics/sound commands are not part of MBASIC 5.21 core spec

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
