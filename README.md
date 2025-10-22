# MBASIC 5.21 Compiler

A compiler for CP/M era Microsoft BASIC-80 (MBASIC) version 5.21, written in Python.

## Current Status

**Lexer: Complete** ✓

The lexer tokenizes MBASIC 5.21 source code according to the BASIC-80 Reference Manual specifications.

**Tested against 373 real CP/M BASIC programs**: **63.0% success rate (235/374 files lexed successfully)**
- Started at ~16% with basic implementation
- Improved to 47.1% with REMARK, #, & support
- Achieved 59.4% with leading-decimal-point support (.5 syntax)
- Improved to 63.0% with detokenizer fixes
- Estimated 75% success rate on pure MBASIC programs (excluding other dialects)

**Parser: Complete** ✓

The parser builds an Abstract Syntax Tree (AST) from tokenized source code using a two-pass compilation approach.

**Successfully parses real MBASIC programs** (tested with hanoi.bas and other programs from corpus)

**Fully Implemented:**
- ✓ Two-pass compilation (collect DEF types globally, then parse)
- ✓ Expression parsing with full operator precedence (12 levels)
- ✓ Control flow: IF/THEN, FOR/NEXT, WHILE/WEND, GOTO, GOSUB, RETURN, ON GOTO/GOSUB
- ✓ I/O statements: PRINT, INPUT, READ, DATA, RESTORE
- ✓ Arrays: DIM declaration with array subscript access in expressions
- ✓ Type declarations: DEFINT, DEFSNG, DEFDBL, DEFSTR (applied globally)
- ✓ Built-in functions: All numeric and string functions (SQR, INT, CHR$, LEFT$, etc.)
- ✓ All operators: arithmetic (+, -, *, /, \\, ^, MOD), relational (=, <>, <, >, <=, >=), logical (AND, OR, NOT, XOR, EQV, IMP)
- ✓ Other statements: END, STOP, SWAP, CLEAR, WIDTH, POKE, OUT
- ✓ Error handling: ON ERROR GOTO, RESUME
- ✓ Comments: REM, REMARK
- ✓ Line number management and GOTO/GOSUB resolution

**Not yet implemented (less common features):**
- File I/O: OPEN, CLOSE, FIELD, GET, PUT, LINE INPUT, WRITE
- DEF FN: User-defined functions
- COMMON: Shared variables

## Features

### Supported Token Types

- **Literals**
  - Integer numbers: `123`, `-456`
  - Fixed-point numbers: `3.14159`
  - Floating-point with scientific notation: `1.5E+10`, `2.5D-5`
  - Hexadecimal: `&HFF`, `&H10`
  - Octal: `&O77`, `&77`
  - String literals: `"Hello, World!"`

- **Identifiers**
  - Variable names with type suffixes:
    - `NAME$` - string variable
    - `COUNT%` - integer variable
    - `VALUE!` - single precision variable
    - `TOTAL#` - double precision variable

- **Keywords**
  - Control flow: `IF`, `THEN`, `ELSE`, `FOR`, `TO`, `STEP`, `NEXT`, `WHILE`, `WEND`, `GOTO`, `GOSUB`, `RETURN`
  - I/O: `PRINT`, `INPUT`, `READ`, `DATA`, `WRITE`
  - Program control: `RUN`, `LOAD`, `SAVE`, `NEW`, `LIST`, `END`, `STOP`
  - Data: `DIM`, `DEF`, `LET`, `CLEAR`, `COMMON`
  - File operations: `OPEN`, `CLOSE`, `FIELD`, `GET`, `PUT`

- **Operators**
  - Arithmetic: `+`, `-`, `*`, `/`, `^` (power), `\` (integer division), `MOD`
  - Relational: `=`, `<>`, `><`, `<`, `>`, `<=`, `>=`
  - Logical: `AND`, `OR`, `NOT`, `XOR`, `EQV`, `IMP`

- **Built-in Functions**
  - Numeric: `ABS`, `ATN`, `COS`, `SIN`, `TAN`, `EXP`, `LOG`, `SQR`, `INT`, `FIX`, `RND`, `SGN`
  - String: `LEFT$`, `RIGHT$`, `MID$`, `CHR$`, `STR$`, `LEN`, `ASC`, `VAL`, `INKEY$`, `INSTR`, `SPACE$`, `STRING$`
  - Type conversion: `CINT`, `CSNG`, `CDBL`
  - Other: `PEEK`, `POKE`, `INP`, `OUT`, `USR`

- **Special Features**
  - Line numbers: `10`, `20`, `100`, etc. (range 0-65529)
  - Comments: `REM` keyword or `'` apostrophe
  - `?` as shorthand for `PRINT`
  - Multiple statements per line with `:` separator

## Files

- `tokens.py` - Token type definitions and keyword mapping
- `lexer.py` - Lexer implementation
- `test_lexer.py` - Comprehensive test suite
- `example.py` - Example usage demonstration
- `debug_test.py` - Debug utility
- `COMPILER_DESIGN.md` - Design notes for compiled vs interpreted BASIC (focus on DEFINT and core differences)
- `LANGUAGE_CHANGES.md` - Comprehensive analysis of ALL language changes: scoping, control flow, procedures, arrays, etc.
- `LEXER_ISSUES.md` - Detailed analysis of lexer issues found in real programs
- `TEST_RESULTS.md` - Results from testing against 373 real BASIC programs
- `test_bas_files.py` - Automated test script for BASIC file corpus
- `examples/interpreter_vs_compiler.bas` - Examples showing behavioral differences
- `bas/` - Directory containing 373 real CP/M BASIC programs for testing

## Usage

### Basic Usage

```python
from lexer import tokenize

# Tokenize MBASIC source code
code = '10 PRINT "Hello, World!"'
tokens = tokenize(code)

for token in tokens:
    print(token)
```

### Running Tests

```bash
python3 test_lexer.py
```

### Running Example

```bash
python3 example.py
```

## Implementation Notes

### MBASIC 5.21 Specific Features

1. **Type Suffixes**: The `$`, `%`, `!`, and `#` characters are part of identifiers, not separate tokens
2. **String Functions**: Functions like `LEFT$`, `RIGHT$`, `MID$` include the `$` in their name
3. **Number Formats**: Supports both `E` and `D` for scientific notation (MBASIC treats them the same)
4. **Octal/Hex**: `&H` prefix for hex, `&O` or `&` prefix for octal
5. **Line Numbers**: Required at the start of program lines, range 0-65529
6. **Comments**: Both `REM` statements and `'` apostrophe comments are supported

## Compiler vs Interpreter Considerations

This project targets **compiled** BASIC, not interpreted BASIC. Key differences:

### Critical Design Decisions

1. **DEF Type Statements (DEFINT/DEFSNG/DEFDBL/DEFSTR)**
   - **Interpreter**: Executes when encountered, affects only subsequent variables
   - **Compiler**: Applied globally at compile time to all variables in scope
   - **Our approach**: Collect all DEF statements in first pass, apply globally

2. **Array Dimensions (DIM)**
   - **Interpreter**: Can use variables `DIM A(N)` where N is runtime value
   - **Compiler**: Requires constant dimensions `DIM A(100)`
   - **Our approach**: Static arrays with constant dimensions (may add $DYNAMIC mode later)

3. **Variable Types**
   - **Interpreter**: Types can change during execution
   - **Compiler**: Each variable has fixed type throughout program
   - **Our approach**: Determine all types at compile time

4. **Removed Features**
   - Interactive commands: `AUTO`, `LIST`, `EDIT`, `RENUM`, `DELETE`, `LOAD`, `SAVE`, `NEW`
   - Dynamic memory: `CLEAR`, `ERASE` (in static mode)
   - These are interpreter-only features

See `COMPILER_DESIGN.md` for detailed analysis of interpreter vs compiler differences.

## Next Steps

- [ ] Parser - Build an Abstract Syntax Tree (AST) from tokens
  - [ ] First pass: Collect all DEFINT/DEFSNG/DEFDBL/DEFSTR statements
  - [ ] Build global type mapping
  - [ ] Parse expressions and statements
- [ ] Semantic Analyzer - Type checking and symbol table
  - [ ] Apply global type rules to all variables
  - [ ] Validate array dimensions are constants
  - [ ] Verify all GOTO/GOSUB targets exist
- [ ] Code Generator - Generate target code
- [ ] Optimizer - Optimize generated code

## References

- BASIC-80 (MBASIC) Reference Manual, Version 5.21, 1981
- Microsoft BASIC Compiler (BASCOM) for CP/M, 1980
- Microsoft QuickBASIC 4.5 Language Reference
- CP/M Operating System documentation

## License

This is an educational project for understanding compiler construction and retro computing.
