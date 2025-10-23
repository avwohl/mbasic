# Implementation Status

This document provides a comprehensive overview of what is and is not yet implemented in the MBASIC 5.21 Interpreter.

## Summary

**Parser Coverage:** 100% - All MBASIC 5.21 syntax is parsed correctly
**Runtime Implementation:** ~96% - Core features, file I/O, and string manipulation complete

## ✓ Fully Implemented

### Core Language Features
- ✓ Variables (all type suffixes: $, %, !, #)
- ✓ Arrays with DIM, ERASE, OPTION BASE
- ✓ All arithmetic operators (+, -, *, /, \, ^, MOD)
- ✓ All relational operators (=, <>, <, >, <=, >=)
- ✓ All logical operators (AND, OR, XOR, NOT)
- ✓ String concatenation
- ✓ Expression evaluation with correct precedence
- ✓ Type coercion and conversion

### Control Flow
- ✓ IF/THEN/ELSE (both line numbers and statements)
- ✓ GOTO
- ✓ GOSUB/RETURN
- ✓ ON expression GOTO line1, line2, ... (computed GOTO)
- ✓ ON expression GOSUB line1, line2, ... (computed GOSUB)
- ✓ FOR/NEXT (including STEP)
- ✓ WHILE/WEND
- ✓ END
- ✓ STOP/CONT

### Data Management
- ✓ LET (assignment)
- ✓ DATA/READ/RESTORE
- ✓ INPUT (console input)
- ✓ PRINT (console output with zones and separators)

### Built-in Functions (45+)
- ✓ Math: ABS, ATN, COS, EXP, INT, LOG, RND, SGN, SIN, SQR, TAN
- ✓ String: ASC, CHR$, INSTR, LEFT$, LEN, MID$, RIGHT$, SPACE$, STR$, STRING$, VAL
- ✓ Conversion: CDBL, CINT, CSNG
- ✓ Binary I/O: CVI, CVS, CVD (convert string to int/single/double), MKI$, MKS$, MKD$ (convert int/single/double to string)
- ✓ Input: INKEY$ (non-blocking keyboard input)
- ✓ File I/O: EOF() (end of file test), LOC() (record position), LOF() (file length)
- ✓ Other: FIX, HEX$, OCT$, TAB, POS

### String Manipulation
- ✓ MID$(var$, start, len) = value$ - Replace substring in-place

### Debugging
- ✓ TRON/TROFF - Trace program execution (shows line numbers as they execute)

### User-Defined Features
- ✓ DEF FN (user-defined functions)
- ✓ DEFINT/DEFSNG/DEFDBL/DEFSTR (type declarations)

### Interactive Mode
- ✓ Line entry and editing
- ✓ RUN (execute program)
- ✓ LIST (list program lines)
- ✓ SAVE/LOAD (save/load programs to disk)
- ✓ NEW (clear program)
- ✓ DELETE (delete line ranges)
- ✓ RENUM (renumber program lines)
- ✓ FILES (list directory)
- ✓ CHAIN (load and execute another program)
- ✓ MERGE (merge program from file)
- ✓ SYSTEM (exit interpreter)
- ✓ COMMON (declare variables for CHAIN)
- ✓ CLEAR (clear all variables)
- ✓ Immediate mode (evaluate expressions directly)

### File System Operations
- ✓ KILL "filename" - Delete file
- ✓ NAME "old" AS "new" - Rename file
- ✓ RESET - Close all open files

### Sequential File I/O
- ✓ OPEN "I"/"O"/"A", #n, "file" - Open file for input/output/append
- ✓ CLOSE [#n] - Close file(s)
- ✓ PRINT #n, data - Write to file
- ✓ INPUT #n, var1, var2 - Read comma-separated values
- ✓ LINE INPUT #n, var$ - Read entire line
- ✓ WRITE #n, data - Write comma-delimited data with quoted strings
- ✓ EOF(n) - Test for end of file (respects ^Z as CP/M EOF marker)

### Random Access File I/O
- ✓ OPEN "R", #n, "file", record_len - Open random file
- ✓ FIELD #n, width AS var$, ... - Define record layout
- ✓ GET #n [,record] - Read record
- ✓ PUT #n [,record] - Write record
- ✓ LSET var$ = value$ - Left-justify in field
- ✓ RSET var$ = value$ - Right-justify in field
- ✓ LOC(n) - Get current record position
- ✓ LOF(n) - Get file length

### Error Handling
- ✓ ON ERROR GOTO line - Set error trap (GOTO)
- ✓ ON ERROR GOSUB line - Set error trap (GOSUB)
- ✓ ON ERROR GOTO 0 - Disable error trapping
- ✓ RESUME - Retry the statement that caused the error
- ✓ RESUME 0 - Same as RESUME (retry error statement)
- ✓ RESUME NEXT - Continue at next statement after error
- ✓ RESUME line - Resume at specific line number
- ✓ ERR% - Error code variable
- ✓ ERL% - Error line number variable

### Program State Management
- ✓ Break handling (Ctrl+C)
- ✓ STOP/CONT (pause and resume execution)
- ✓ GOSUB stack preservation
- ✓ FOR loop stack preservation
- ✓ WHILE loop stack preservation
- ✓ Variable preservation across STOP

## ⚠ Partially Implemented

### Built-in Functions (Hardware/System)
- **PEEK, POKE, INP, OUT, CALL, USR**
  - **Status:** Parsed, but return placeholder values or do nothing
  - **Reason:** Requires hardware emulation or system-level access
  - **Not planned:** These are CP/M-specific and not relevant for modern use

## ✗ Not Yet Implemented

### 1. Formatted Output (High Priority)
**Priority:** High - Commonly used features

- ✗ **PRINT USING** - Format output with format strings (e.g., "###.##" for numbers)
- ✗ **PRINT# USING** - Format file output with format strings
- ✗ **TAB(n)** - Tab to column n in PRINT statements
- ✗ **SPC(n)** - Print n spaces in PRINT statements

**Status:** Not implemented
**Impact:** Cannot format numbers/strings for display or tabulate output
**Workaround:** Manual string formatting with SPACE$ and STR$

### 2. Debugging and System Functions (Low Priority)
**Priority:** Low - Useful but not critical

- ✗ **FRE(n)** - Return free memory available
- ✗ **VARPTR(var)** - Return memory address of variable

**Status:** Not implemented
**Impact:** Less memory introspection
**Workaround:** Not critical for most programs

### 3. Variable and Terminal Operations (Low Priority)
**Priority:** Low - Minor convenience features

- ✗ **SWAP var1, var2** - Exchange values of two variables
- ✗ **NULL n** - Set number of nulls after carriage return
- ✗ **WIDTH [#filenum,] width** - Set output width

**Status:** Parsed but not executed (SWAP, WIDTH); Not implemented (NULL)
**Impact:** Minor convenience features
**Workaround:** Use temp variable for SWAP; not needed for NULL/WIDTH on modern terminals

### 4. Printer Support (Not Planned)
**Priority:** Very Low - Obsolete hardware

- ✗ **LPRINT/LPRINT USING** - Print to printer
- ✗ **LLIST** - List program to printer
- ✗ **LPOS(n)** - Get printer head position

**Status:** Not implemented
**Impact:** Cannot print to line printer
**Note:** Not planned - obsolete hardware interface

## Testing Status

### Parser Tests
- **Coverage:** 121/121 files (100%)
- **Status:** All valid MBASIC 5.21 programs parse successfully
- **Test corpus:** 120+ real MBASIC programs from vintage sources

### Interpreter Tests
- **Core features:** Fully tested
- **Self-checking tests:** 20/20 pass
- **Manual testing:** Extensive testing with vintage programs
- **Error handling:** Fully tested (ON ERROR GOTO/GOSUB, RESUME variants)
- **WHILE/WEND:** Tested with nested loops
- **INKEY$:** Tested with cross-platform support
- **ON GOTO/GOSUB:** Tested with multiple values, out-of-range, expressions
- **File system ops:** Tested (KILL, NAME AS, RESET)
- **Sequential file I/O:** Fully tested (OPEN, CLOSE, PRINT#, INPUT#, LINE INPUT#, WRITE#, EOF with ^Z support)
- **Random file I/O:** Fully tested (FIELD, GET, PUT, LSET, RSET, LOC, LOF)
- **Binary conversions:** Fully tested (CVI/CVS/CVD, MKI$/MKS$/MKD$ for binary file I/O)
- **MID$ assignment:** Fully tested (replace substring in-place, simple vars and arrays)
- **TRON/TROFF:** Fully tested (execution trace for debugging)

## Compatibility Notes

### What Works
Programs that use:
- Mathematical calculations
- String processing (including MID$ assignment for in-place modification)
- Arrays and data structures
- Control flow (IF, FOR, WHILE/WEND, GOSUB, ON GOTO/GOSUB)
- Error handling (ON ERROR GOTO/GOSUB, RESUME)
- Debugging (TRON/TROFF execution trace)
- User input/output
- Non-blocking keyboard input (INKEY$)
- Sequential file I/O (OPEN, CLOSE, PRINT#, INPUT#, LINE INPUT#, WRITE#, EOF)
- Random access file I/O (FIELD, GET, PUT, LSET, RSET, LOC, LOF)
- Binary file I/O (CVI/CVS/CVD, MKI$/MKS$/MKD$ for reading/writing numeric data)
- File system operations (KILL, NAME AS, RESET)
- DATA statements
- User-defined functions

### What Doesn't Work
Programs that require:
- Hardware access (PEEK, POKE, ports)

## Roadmap

### Phase 1 (Current) - Core Language ✓
- ✓ Complete parser
- ✓ Basic interpreter
- ✓ Interactive mode
- ✓ Essential built-in functions

### Phase 2 (Completed) - Advanced Features ✓
- ✓ Error handling (ON ERROR GOTO/GOSUB, RESUME)
- ✓ WHILE/WEND loops
- ✓ INKEY$ non-blocking input
- ✓ Computed jumps (ON GOTO/GOSUB)
- ✓ File system operations (KILL, NAME AS, RESET)

### Phase 3 (Completed) - Sequential File I/O ✓
- ✓ OPEN for INPUT/OUTPUT/APPEND
- ✓ CLOSE statement
- ✓ PRINT#, INPUT#, LINE INPUT# statements
- ✓ WRITE# statement
- ✓ EOF() function with ^Z support

### Phase 4 (Completed) - Random File I/O ✓
- ✓ OPEN "R" for random access
- ✓ FIELD statement for record layout
- ✓ GET/PUT for record read/write
- ✓ LSET/RSET for field assignment
- ✓ LOC/LOF functions

### Phase 5 (Future) - Enhancements
- Documentation improvements
- Performance optimization
- Extended error messages
- Debugging features

### Not Planned
- Printer support (LPRINT)
- Direct hardware access (PEEK, POKE, INP, OUT)

## Known Limitations

1. **Integer division precision** - May differ slightly from original MBASIC due to Python float handling

## Testing Your Program

To check if your MBASIC program will work:

1. **Parser test:**
   ```bash
   python3 mbasic.py yourprogram.bas
   ```
   If it parses without errors, the syntax is valid.

2. **Check for unimplemented features:**
   - Look for "NotImplementedError" when running
   - Review the "Not Yet Implemented" section above
   - Check if your program uses file I/O or computed jumps

3. **Run tests:**
   ```bash
   # Run self-checking tests
   python3 mbasic.py basic/tests_with_results/test_operator_precedence.bas
   ```

## Contributing

Contributions welcome! Priority areas:
1. Additional test cases
2. Performance optimization
3. Enhanced error messages and debugging features

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.
