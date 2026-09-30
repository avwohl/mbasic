# Compilers (100% Complete)

MBASIC includes **TWO fully-featured compilers**:

1. **Z80/8080 Compiler** - Generates C code and compiles to native CP/M executables for 8080 or Z80 processors
2. **JavaScript Compiler** - Generates portable JavaScript for browsers and Node.js

Both compilers are **100% feature-complete** - every MBASIC 5.21 feature that can be compiled is now implemented!

## Z80/8080 Compiler Requirements

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

## JavaScript Compiler Requirements

**None!** The JavaScript compiler is built into MBASIC with zero external dependencies. Just use `mbasic --compile-js`.

## Quick Compiler Check

```bash
# Check if Z80/8080 compiler tools are installed
python3 utils/check_compiler_tools.py
```

## Compiling BASIC to CP/M (Z80/8080)

```bash
# Compile BASIC to C, then to CP/M .COM file
cd test_compile
python3 test_compile.py program.bas

# This generates:
#   program.c    - C source code
#   PROGRAM.COM  - CP/M executable (runs on 8080 or Z80 CP/M systems)
```

## Compiling BASIC to JavaScript

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

## Compiler Features (100% Complete!)

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
- `docs/history/JS_BACKEND_REMAINING.md` - JavaScript compiler feature list
- `docs/dev/TNYLPO_SETUP.md` - CP/M emulator installation (for Z80/8080 testing)
