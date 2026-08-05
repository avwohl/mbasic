# MBASIC Compilers

**Status: 100% Complete!** - MBASIC-2025 now includes TWO production-ready compilers, both 100% complete!

## Overview

MBASIC-2025 includes TWO complete compiler backends:

1. **Z80/8080 Compiler** - Generates native CP/M executables for vintage hardware
2. **JavaScript Compiler** - Generates modern JavaScript for browsers and Node.js

Unlike the interpreter, compilers generate standalone code that runs without the MBASIC runtime.

## What Makes It Special

**THREE Complete Implementations in One Project:**
- **Interpreter** - Run BASIC programs interactively with modern UIs
- **Z80/8080 Compiler** - Generate native .COM executables for CP/M systems
- **JavaScript Compiler** - Generate portable JS for modern platforms

**Features Implemented (100% Microsoft BASCOM Compatible):**
- All data types (INTEGER %, SINGLE !, DOUBLE #, STRING $)
- All control structures (IF/THEN/ELSE, FOR/NEXT, WHILE/WEND, GOTO, GOSUB/RETURN)
- All 50+ built-in functions
- Complete file I/O (sequential, random access, binary)
- Error handling (ON ERROR GOTO, RESUME, ERR, ERL)
- Hardware access (PEEK/POKE/INP/OUT/WAIT) - **Works in compiled code!**
- Machine language integration (CALL/USR/VARPTR) - **Works in compiled code!**
- **CHAIN** - Program chaining using CP/M warm boot - **Just implemented!**

## Choosing a Compiler

### Z80/8080 Compiler (CP/M Targets)
**Use when:**
- Targeting vintage hardware (CP/M systems)
- Need hardware access (PEEK/POKE/INP/OUT)
- Building for embedded 8080/Z80 systems

**Output:** Native .COM executables for CP/M

### JavaScript Compiler (Modern Platforms)
**Use when:**
- Deploying to web browsers
- Running on modern operating systems
- Need cross-platform compatibility
- Want standalone HTML applications

**Output:** JavaScript files (.js) or HTML+JavaScript bundles

---

## Getting Started with Z80/8080 Compiler

### Requirements

The compiler emits C, so you need a C compiler that targets CP/M, plus a CP/M
emulator if you want to run the result on your own machine.

**Preferred toolchain**

1. **uc80** - C compiler for Z80/CP/M, optimized for small code size
   - Uses the `um80` assembler and `ul80` linker from the same family
   - Installation: `pip install uc80 um80` (`ul80` ships inside `um80`)
   - https://github.com/avwohl/uc80
   - See [Compiler Setup Guide](https://github.com/avwohl/mbasic/blob/main/docs/dev/COMPILER_SETUP.md)

2. **cpmemu** - CP/M 2.2 emulator with Z80 and 8080 CPU cores
   - Translates CP/M's BDOS/BIOS calls to the host file system, so no disk image
     is needed and your programs can live anywhere in your directory tree
   - Installation: `.deb`/`.rpm` from the releases page, or build from source
   - https://github.com/avwohl/cpmemu

**Supported alternates**

3. **z88dk** (alternate) - 8080/Z80 C cross-compiler
   - Installation: `sudo snap install z88dk --beta`

4. **tnylpo** (alternate) - CP/M emulator
   - See [CP/M Emulator Setup](https://github.com/avwohl/mbasic/blob/main/docs/dev/TNYLPO_SETUP.md)

z88dk and tnylpo are fully supported, and three things still go through z88dk
because uc80 cannot do them: Microsoft Binary Format floats (matching MBASIC's
exact bit patterns), true Intel 8080 output (uc80 is Z80-only), and the
`INP`/`OUT`/`WAIT` port statements. cpmemu runs `.COM` files from either
compiler, so the emulator choice is independent of the compiler choice.

See the [Toolchain Policy](https://github.com/avwohl/mbasic/blob/main/docs/dev/TOOLCHAIN_POLICY.md)
for which tool covers what.

### Quick Example (Z80/8080)

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

# Run it right here - no disk image needed
cpmemu HELLO.COM
```

`mbasic --compile-c` does the same job and defaults to the preferred pair. Add
`--toolchain z88dk` to build with the alternate compiler, and `--emulator tnylpo`
to pick the alternate emulator for `--run`:

```bash
# Preferred: uc80 to build, cpmemu to run
mbasic --compile-c hello --run hello.bas

# Alternate toolchain
mbasic --compile-c hello --toolchain z88dk --run --emulator tnylpo hello.bas
```

### Hardware Access Example (Z80/8080 Only)

These features only work in Z80/8080 compiled code:

```basic
10 REM Hardware access - works in Z80/8080 compiled code!
20 A = PEEK(100)         ' Read memory
30 POKE 100, 42          ' Write memory
40 B = INP(255)          ' Read I/O port
50 OUT 255, 1            ' Write I/O port
60 CALL 16384            ' Execute machine code
70 ADDR = VARPTR(A)      ' Get variable address
80 END
```

**Note:** `PEEK`, `POKE`, `CALL`, `USR`, and `VARPTR` compile under either
toolchain. `INP`, `OUT`, and `WAIT` need the port I/O routines that only z88dk
provides, so a program using them is built with the alternate compiler. The
resulting `.COM` still runs under cpmemu.

---

## Getting Started with JavaScript Compiler

### Requirements

**None!** The JavaScript compiler is built into MBASIC-2025 with zero dependencies.

- No external compiler needed
- Works on any platform with Python 3.8+
- Generates standalone JavaScript files

### Quick Example (JavaScript)

```bash
# Write a BASIC program
cat > hello.bas << 'EOF'
10 PRINT "Hello from compiled JavaScript!"
20 END
EOF

# Compile to JavaScript for Node.js
mbasic --compile-js hello.js hello.bas

# Run with Node.js
node hello.js

# Or compile to standalone HTML
mbasic --compile-js hello.js --html hello.bas

# Open hello.html in any browser!
```

### Cross-Platform Output

The JavaScript compiler generates code that works in **both** environments:

**Node.js (Command Line):**
- Real file I/O using fs module
- Console input/output
- Full file management (KILL, NAME, FILES)
- Random file access with binary operations

**Browser (Web Applications):**
- Virtual file system using localStorage
- Prompt-based INPUT
- Retro terminal styling in HTML wrapper
- Standalone HTML files (no server required)

### What Works in JavaScript

All core MBASIC 5.21 features compile successfully:

```basic
10 REM All MBASIC features work in JavaScript!
20 DIM A(100), B$(50)
30 INPUT "Name"; N$
40 FOR I = 1 TO 10
50   PRINT I; SQR(I)
60 NEXT I
70 GOSUB 1000
80 ON ERROR GOTO 9000
90 OPEN "DATA.TXT" FOR OUTPUT AS #1
100 PRINT #1, "Hello, file!"
110 CLOSE #1
120 END
1000 PRINT "Subroutine!"
1010 RETURN
9000 PRINT "Error:"; ERR(); "at line"; ERL()
9010 RESUME NEXT
```

**Supported Features:**
- ✅ All data types and operators
- ✅ All control structures (FOR/NEXT, WHILE/WEND, IF/THEN/ELSE, GOTO, GOSUB)
- ✅ All 50+ built-in functions
- ✅ Sequential file I/O (OPEN, CLOSE, PRINT#, INPUT#, LINE INPUT#)
- ✅ Random file access (FIELD, LSET, RSET, GET, PUT)
- ✅ File management (KILL, NAME, FILES)
- ✅ Error handling (ON ERROR GOTO, RESUME, ERR, ERL)
- ✅ User-defined functions (DEF FN)
- ✅ String manipulation (MID$ assignment)
- ✅ Program chaining (CHAIN)
- ✅ Formatted output (PRINT USING)

**Not Supported (JavaScript Limitations):**
- ❌ Hardware access (PEEK/POKE/INP/OUT) - no direct memory access in JavaScript
- ❌ Machine code (CALL/USR/VARPTR) - not applicable to JavaScript

## Topics

### [Optimizations](optimizations.md)
Learn about the optimization techniques used by the compiler to improve performance and reduce code size.

### Complete Documentation

- **[Feature Status](https://github.com/avwohl/mbasic/blob/main/docs/history/COMPILER_STATUS_SUMMARY.md)** - Complete feature list (100%!)
- **[Setup Guide](https://github.com/avwohl/mbasic/blob/main/docs/dev/COMPILER_SETUP.md)** - Installing uc80/um80/ul80, and z88dk as the alternate
- **[Toolchain Policy](https://github.com/avwohl/mbasic/blob/main/docs/dev/TOOLCHAIN_POLICY.md)** - Why uc80 and cpmemu are preferred, and what each alternate still covers
- **[CP/M Emulator](https://github.com/avwohl/mbasic/blob/main/docs/dev/TNYLPO_SETUP.md)** - Building tnylpo, the alternate emulator
- **[Memory Configuration](https://github.com/avwohl/mbasic/blob/main/docs/dev/COMPILER_MEMORY_CONFIG.md)** - Runtime library details

## Runtime Library

The compiler includes a sophisticated runtime library:

- **Custom string system** with O(n log n) garbage collection
- **Zero malloc** design (pool uses direct memory from BSS to stack)
- **In-place GC** with shell sort (no temporary buffers, no stdlib)
- **Optimized for CP/M** - fits comfortably in 64K TPA (~56KB string space)

## What Works

**Nearly Everything!** The compiler implements all core computational features of MBASIC 5.21:

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

## What's Not Supported (Matching Microsoft BASCOM)

MBASIC-2025 compiler now matches Microsoft BASCOM 100%! The following features are correctly NOT supported (because Microsoft BASCOM didn't support them either):

**Interpreter-Only Features (Not in Microsoft BASCOM):**
- **COMMON** - Variable passing between chained programs (MBASIC 5.21 interpreter-only)
- **CHAIN MERGE** - Merging programs during chain (MBASIC 5.21 interpreter-only)
- **CHAIN line number** - Starting at specific line (MBASIC 5.21 interpreter-only)
- **CHAIN ALL** - Passing all variables (MBASIC 5.21 interpreter-only)
- **CHAIN DELETE** - Deleting line ranges (MBASIC 5.21 interpreter-only)
- **ERASE** - Deallocating arrays (not supported by Microsoft BASCOM)
- **Interactive commands** - LIST, RUN, SAVE, LOAD (not applicable to compiled programs)
- **CLOAD/CSAVE** - Cassette tape operations (obsolete)

**What IS Supported:**
- ✅ **CHAIN "filename"** - Basic program chaining (just implemented!)

## See Also

- [BASIC-80 Language Reference](../language/index.md) - Language syntax and semantics
- [Functions](../language/functions/index.md) - All built-in functions
- [Statements](../language/statements/index.md) - All language statements
- [Developer Setup](https://github.com/avwohl/mbasic/blob/main/docs/dev/LINUX_MINT_DEVELOPER_SETUP.md) - Complete development environment
