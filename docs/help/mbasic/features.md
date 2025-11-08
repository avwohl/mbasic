---
title: MBASIC Features
type: reference
category: mbasic
keywords:
- features
- capabilities
- what works
- language support
- file io
- error handling
description: Complete list of MBASIC interpreter features and capabilities
---

# MBASIC Features

This document lists all features implemented in MBASIC-2025 (this implementation of MBASIC 5.21).

## Language Features

### Complete MBASIC 5.21 Syntax

✓ **100% parser coverage** for valid MBASIC 5.21 programs
✓ **All data types:** Integer (%), Single (!), Double (#), String ($)
✓ **Implicit typing** via type suffixes
✓ **Type declarations:** DEFINT, DEFSNG, DEFDBL, DEFSTR

### Variables and Arrays

- **Simple variables:** A, B$, COUNT%, TOTAL!, VALUE#
- **Arrays:** Single and multi-dimensional with DIM
- **Dynamic allocation:** Arrays allocated as needed
- **OPTION BASE:** Support for 0 or 1-based arrays
- **Array bounds:** Automatic checking for subscript errors

### Operators

**Arithmetic:** `+`, `-`, `*`, `/`, `\`, `^`, `MOD`
**Relational:** `=`, `<>`, `<`, `>`, `<=`, `>=`
**Logical:** `AND`, `OR`, `NOT`, `XOR`, `EQV`, `IMP`
**String:** `+` (concatenation)

### Control Flow

- **IF...THEN...ELSE** - Conditional execution with nesting
- **FOR...NEXT** - Counted loops with STEP
- **WHILE...WEND** - Conditional loops
- **GOTO** - Unconditional branch
- **GOSUB...RETURN** - Subroutine calls
- **ON GOTO/GOSUB** - Computed branches
- **ON ERROR GOTO/GOSUB** - Error handling

### Input/Output

**Console I/O:**
- **PRINT** - Output with formatting (`;`, `,`, TAB, SPC)
- **PRINT USING** - Formatted output with format strings
- **INPUT** - Interactive input with prompts
- **LINE INPUT** - Full line input
- **LPRINT** - Line printer output (Note: LPRINT statement is supported, but WIDTH LPRINT syntax is not)

**File I/O:**
- **Sequential files:** OPEN, CLOSE, PRINT#, INPUT#, LINE INPUT#, WRITE#
- **Random files:** FIELD, GET, PUT, LSET, RSET
- **Binary I/O:** MKI$/MKS$/MKD$, CVI/CVS/CVD
- **File management:** KILL, NAME AS, RESET
- **File queries:** EOF, LOC, LOF

### Functions (50+)

**Mathematical:**
- Trigonometric: SIN, COS, TAN, ATN
- Logarithmic: LOG, EXP
- Other: ABS, INT, FIX, SGN, SQR, RND

**String:**
- Extraction: LEFT$, RIGHT$, MID$, CHR$, STRING$
- Analysis: LEN, ASC, INSTR, VAL
- Formatting: SPACE$, STR$

**Type Conversion:**
- CINT, CSNG, CDBL - Numeric conversions
- STR$, VAL - String/number conversions

**System:**
- INKEY$ - Non-blocking keyboard input
- FRE - Free memory query
- POS - Cursor position
- PEEK, POKE - Memory access (emulated)

**User-Defined:**
- DEF FN - Single-line functions
- Multi-line DEF FN support

### Data Handling

- **DATA** - Define data values
- **READ** - Read data into variables
- **RESTORE** - Reset data pointer

### Program Control

**Direct Commands:**
- **RUN** - Execute program
- **LIST** - Display program lines
- **NEW** - Clear program
- **SAVE** - Save program to disk
- **LOAD** - Load program from disk
- **DELETE** - Delete line ranges
- **RENUM** - Renumber program lines
- **AUTO** - Auto-line numbering mode

**Execution Control:**
- **STOP** - Halt execution (resumable)
- **END** - Terminate program
- **CONT** - Continue after STOP
- **SYSTEM** - Exit MBASIC

### Error Handling

- **ON ERROR GOTO** - Error trap setup
- **ON ERROR GOSUB** - Error subroutine
- **RESUME** - Continue after error (RESUME, RESUME NEXT, RESUME line)
- **ERR** - Error code variable
- **ERL** - Error line number
- **ERROR** - Generate error

### Debugging

- **TRON/TROFF** - Line tracing
- **Breakpoints** - Set/clear breakpoints (UI-dependent)
- **Step execution** - Execute one line at a time (UI-dependent)
- **Variable watch** - Monitor variables (UI-dependent)
- **Stack viewer** - View call stack (UI-dependent)

## User Interface Features

### Curses UI (Default)

- **Full-screen editor** with line numbers
- **Split screen** - Editor above, output below
- **Syntax checking** - Real-time error marking
- **Breakpoint indicators** - Visual markers
- **Auto-numbering** - Smart line numbering
- **Line sorting** - Automatic or on-demand
- **Variables window** - Watch variable values (Ctrl+W)
- **Stack window** - View execution stack (Ctrl+K)
- **Help system** - Built-in documentation (Ctrl+H)
- **Fast paste** - Optimized for large programs

### CLI Mode

- **Classic MBASIC interface** - Authentic experience
- **REPL** - Read-Eval-Print Loop
- **Direct commands** - All MBASIC commands
- **Immediate mode** - Expression evaluation
- **Command history** (platform-dependent)

### Tkinter GUI

- **Graphical interface** - Windows, menus, toolbars
- **Syntax highlighting** - Color-coded keywords, strings, numbers
- **Find and Replace** - Search and replace text (Ctrl+F/Ctrl+H)
- **Menu bar** - File, Edit, Run operations
- **Toolbar** - Quick access buttons
- **Status bar** - Program state display

### Web UI

- **Browser-based IDE** - Run MBASIC in any modern browser
- **Syntax highlighting** - Color-coded editor
- **Session-based storage** - Files persist during browser session only (lost on page refresh)
- **Three-panel layout** - Editor, output, and command areas
- **In-memory filesystem** - Virtual filesystem with limitations:
  - 50 file limit maximum
  - 1MB per file maximum
  - No path support (simple filenames only)
  - No persistent storage across sessions
- **Basic debugging** - Simple breakpoint support via menu

See [Compatibility Guide](compatibility.md) for complete Web UI file storage details.

## Compiler Features

### Semantic Analyzer

The interpreter includes an advanced semantic analyzer with 18 optimizations:

1. **Constant folding** - Evaluate constant expressions at parse time
2. **Runtime constant propagation** - Track constant values during execution
3. **Common subexpression elimination (CSE)** - Eliminate redundant calculations
4. **Subroutine side-effect analysis** - Detect pure functions
5. **Loop analysis** - Identify loop invariants
6. **Loop-invariant code motion** - Move constant calculations out of loops
7. **Multi-dimensional array flattening** - Optimize array access
8. **Dead code detection** - Identify unreachable code
9. **Strength reduction** - Replace expensive operations with cheaper ones
10. **Copy propagation** - Eliminate redundant variable copies
11. **Algebraic simplification** - Simplify mathematical expressions
12. **Induction variable optimization** - Optimize loop counters
13. **OPTION BASE support** - Compile-time array base handling
14. **Expression reassociation** - Reorder for better optimization
15. **Boolean simplification** - Optimize logical expressions
16. **Forward substitution** - Eliminate temporary variables
17. **Branch optimization** - Optimize conditional branches
18. **Uninitialized variable detection** - Catch potential bugs

These optimizations improve execution speed while maintaining 100% MBASIC compatibility.

See [Architecture](architecture.md) for details on interpreter vs. compiler modes.

## File Format Support

### BASIC Program Files

- **ASCII text** (.BAS, .bas) - Human-readable source
- **Tokenized** (.BAS) - CP/M MBASIC format (partial support)
- **Line endings:** CR, LF, or CRLF (auto-detected)

### Data Files

- **Sequential text files** - Line-oriented text
- **Random access files** - Fixed-record binary
- **Binary files** - Raw binary with MKI$/CVI functions

## Compatibility

### What Works

✓ All valid MBASIC 5.21 programs
✓ CP/M MBASIC program listings
✓ MBASIC file I/O conventions
✓ MBASIC error codes and messages
✓ Line number range: 0-65529

### Intentional Differences

- **PEEK/POKE** - Emulated (no direct memory access)
- **INP/OUT** - Not implemented (hardware-specific)
- **USR** - Not implemented (machine code calls)
- **Memory model** - Python memory management vs. CP/M
- **File paths** - Modern OS paths vs. CP/M 8.3 format

See [Compatibility Guide](compatibility.md) for complete details.

## Platform Support

### Tested Platforms

- ✓ Linux (Ubuntu, Debian, Fedora, Arch)
- ✓ macOS (10.14+)
- ✓ Windows (10, 11)
- ✓ WSL (Windows Subsystem for Linux)

### Python Versions

- **Required:** Python 3.8+
- **Tested:** Python 3.8, 3.9, 3.10, 3.11, 3.12
- **Recommended:** Python 3.10 or later

## Dependencies

### Required

- **Python 3.8+** - Interpreter only

### Optional

- **urwid 2.0+** - For Curses UI
- **python-frontmatter 1.0+** - For help system

### Development

- **pexpect 4.8+** - For automated testing

## See Also

- [Getting Started](getting-started.md) - Installation and first steps
- [Compatibility Guide](compatibility.md) - What works, what doesn't
- [Architecture](architecture.md) - How MBASIC works internally
- [Language Reference](../common/language/statements/index.md) - BASIC-80 language
