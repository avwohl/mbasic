# MBASIC Compiler

**Status: 100% Complete!** - The MBASIC compiler is fully implemented with every compilable MBASIC 5.21 feature.

## Overview

The MBASIC compiler translates BASIC-80 programs into native CP/M executables for Z80 processors. Unlike the interpreter, the compiler generates real machine code that runs directly on hardware or emulators.

## What Makes It Special

**Two Complete Implementations in One Project:**
- **Interpreter** - Run BASIC programs interactively with modern UIs
- **Compiler** - Generate native .COM executables for CP/M systems

**100% Feature Complete:**
- All data types (INTEGER %, SINGLE !, DOUBLE #, STRING $)
- All control structures (IF/THEN/ELSE, FOR/NEXT, WHILE/WEND, GOTO, GOSUB/RETURN)
- All 50+ built-in functions
- Complete file I/O (sequential, random access, binary)
- Error handling (ON ERROR GOTO, RESUME, ERR, ERL)
- Hardware access (PEEK/POKE/INP/OUT/WAIT)
- Machine language integration (CALL/USR/VARPTR)

## Getting Started

### Requirements

1. **z88dk** - Z80 C cross-compiler
   - Installation: `sudo snap install z88dk --beta`
   - See [Compiler Setup Guide](https://github.com/avwohl/mbasic/blob/main/docs/dev/COMPILER_SETUP.md)

2. **tnylpo** (optional) - CP/M emulator for testing
   - See [CP/M Emulator Setup](https://github.com/avwohl/mbasic/blob/main/docs/dev/TNYLPO_SETUP.md)

### Quick Example

```bash
# Write a BASIC program
cat > hello.bas << 'EOF'
10 PRINT "Hello from compiled BASIC!"
20 END
EOF

# Compile to CP/M executable
cd test_compile
python3 test_compile.py hello.bas

# This generates:
#   hello.c      - C source code
#   HELLO.COM    - CP/M executable
```

### Hardware Access Example

These features only work in compiled code:

```basic
10 REM Hardware access - works in compiled code!
20 A = PEEK(100)         ' Read memory
30 POKE 100, 42          ' Write memory
40 B = INP(255)          ' Read I/O port
50 OUT 255, 1            ' Write I/O port
60 CALL 16384            ' Execute machine code
70 ADDR = VARPTR(A)      ' Get variable address
80 END
```

## Topics

### [Optimizations](optimizations.md)
Learn about the optimization techniques used by the compiler to improve performance and reduce code size.

### Complete Documentation

- **[Feature Status](https://github.com/avwohl/mbasic/blob/main/docs/dev/COMPILER_STATUS_SUMMARY.md)** - Complete feature list (100%!)
- **[Setup Guide](https://github.com/avwohl/mbasic/blob/main/docs/dev/COMPILER_SETUP.md)** - z88dk installation
- **[CP/M Emulator](https://github.com/avwohl/mbasic/blob/main/docs/dev/TNYLPO_SETUP.md)** - Testing compiled programs
- **[Memory Configuration](https://github.com/avwohl/mbasic/blob/main/docs/dev/COMPILER_MEMORY_CONFIG.md)** - Runtime library details

## Runtime Library

The compiler includes a sophisticated runtime library:

- **Custom string system** with O(n log n) garbage collection
- **Single malloc** design (only pool initialization)
- **In-place GC** (no temporary buffers)
- **Optimized for CP/M** - fits comfortably in 64K TPA

## What Works

**Everything!** The compiler implements 100% of compilable MBASIC 5.21 features:

✅ All data types and operators
✅ All control flow structures
✅ All 50+ built-in functions
✅ Sequential file I/O
✅ Random access file I/O
✅ Binary file operations (MKI$/CVI, MKS$/CVS, MKD$/CVD)
✅ Error handling (ON ERROR GOTO, RESUME)
✅ Hardware access (PEEK/POKE/INP/OUT/WAIT)
✅ Machine language (CALL/USR/VARPTR)
✅ String manipulation (MID$ assignment)
✅ User-defined functions (DEF FN)

## What Doesn't Apply

These are interpreter-only features:

- Interactive commands (LIST, RUN, SAVE, LOAD) - not applicable to compiled programs
- CHAIN/COMMON - requires runtime loader infrastructure
- CLOAD/CSAVE - cassette tape operations

## See Also

- [BASIC-80 Language Reference](../language/index.md) - Language syntax and semantics
- [Functions](../language/functions/index.md) - All built-in functions
- [Statements](../language/statements/index.md) - All language statements
- [Developer Setup](https://github.com/avwohl/mbasic/blob/main/docs/dev/LINUX_MINT_DEVELOPER_SETUP.md) - Complete development environment
