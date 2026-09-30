# Features and Implementation Status

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

See [PROJECT_STATUS.md](../PROJECT_STATUS.md) for complete project metrics and health information, and [docs/history/COMPILER_STATUS_SUMMARY.md](../history/COMPILER_STATUS_SUMMARY.md) for detailed compiler feature list.
