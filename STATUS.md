# Implementation Status

This document provides a comprehensive overview of what is and is not yet implemented in the MBASIC 5.21 Interpreter.

## Summary

**Parser Coverage:** 100% - All MBASIC 5.21 syntax is parsed correctly
**Runtime Implementation:** ~75% - Core features complete, file I/O pending

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
- ✓ FOR/NEXT (including STEP)
- ✓ WHILE/WEND
- ✓ END
- ✓ STOP/CONT

### Data Management
- ✓ LET (assignment)
- ✓ DATA/READ/RESTORE
- ✓ INPUT (console input)
- ✓ PRINT (console output with zones and separators)

### Built-in Functions (35+)
- ✓ Math: ABS, ATN, COS, EXP, INT, LOG, RND, SGN, SIN, SQR, TAN
- ✓ String: ASC, CHR$, INSTR, LEFT$, LEN, MID$, RIGHT$, SPACE$, STR$, STRING$, VAL
- ✓ Conversion: CDBL, CINT, CSNG
- ✓ Input: INKEY$ (non-blocking keyboard input)
- ✓ Other: FIX, HEX$, OCT$, TAB, POS

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

### Error Handling
- ✓ ON ERROR GOTO line - Set error trap (GOTO)
- ✓ ON ERROR GOSUB line - Set error trap (GOSUB)
- ✓ ON ERROR GOTO 0 - Disable error trapping
- ✓ RESUME - Resume at error statement
- ✓ RESUME NEXT - Resume at next statement
- ✓ RESUME line - Resume at specific line
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

### 1. Sequential File I/O
**Priority:** High

- ✗ **OPEN "filename" FOR INPUT/OUTPUT/APPEND AS #n** - Open file
- ✗ **CLOSE #n** - Close file
- ✗ **PRINT #n, ...** - Write to file
- ✗ **INPUT #n, var1, var2, ...** - Read from file
- ✗ **LINE INPUT #n, var$** - Read line from file
- ✗ **WRITE #n, ...** - Write comma-delimited data
- ✗ **EOF(n)** - Test for end of file

**Status:** Parsed but not executed
**Impact:** Cannot read from or write to text files
**Workaround:** Use SAVE/LOAD for program files only

### 2. Random Access File I/O
**Priority:** Medium

- ✗ **OPEN "filename" AS #n LEN=reclen** - Open random file
- ✗ **FIELD #n, width AS var$, ...** - Define record layout
- ✗ **GET #n [,record]** - Read record
- ✗ **PUT #n [,record]** - Write record
- ✗ **LSET var$ = value$** - Left-justify in field
- ✗ **RSET var$ = value$** - Right-justify in field
- ✗ **LOC(n)** - Get current record position
- ✗ **LOF(n)** - Get file length

**Status:** Parsed but not executed
**Impact:** Cannot access random-access database files

### 3. File System Operations
**Priority:** Medium

- ✗ **KILL "filename"** - Delete file
- ✗ **NAME "old" AS "new"** - Rename file
- ✗ **RESET** - Close all open files

**Status:** Parsed but not executed
**Impact:** Cannot manage files from within BASIC programs

### 4. Computed Jumps
**Priority:** Medium

- ✗ **ON expression GOTO line1, line2, ...** - Computed GOTO
- ✗ **ON expression GOSUB line1, line2, ...** - Computed GOSUB

**Status:** Parsed but not executed
**Impact:** Cannot do multi-way branching
**Workaround:** Use IF/THEN/ELSE chains

### 5. String Manipulation
**Priority:** Low

- ✗ **MID$(var$, start, len) = value$** - Replace substring in-place

**Status:** Parsed but not executed
**Impact:** Cannot modify strings in-place
**Workaround:** Use LEFT$, MID$, RIGHT$ to rebuild strings

### 6. Variable Operations
**Priority:** Low

- ✗ **SWAP var1, var2** - Exchange values of two variables

**Status:** Parsed but not executed
**Impact:** Minor convenience feature
**Workaround:** Use temp variable

### 7. Output Control
**Priority:** Low

- ✗ **WIDTH [#filenum,] width** - Set output width
- ✗ **LPRINT** - Print to printer

**Status:** Parsed but not executed
**Impact:** Cannot control display width or print to printer

### 8. Graphics and Sound
**Priority:** Very Low (Not Planned)

Graphics commands (SCREEN, LINE, CIRCLE, PSET, etc.) and sound commands (SOUND, BEEP, PLAY) are not part of MBASIC 5.21 core specification and are not planned for implementation.

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
- **File I/O:** Not tested (not implemented)

## Compatibility Notes

### What Works
Programs that use:
- Mathematical calculations
- String processing
- Arrays and data structures
- Control flow (IF, FOR, WHILE/WEND, GOSUB)
- Error handling (ON ERROR GOTO/GOSUB, RESUME)
- User input/output
- Non-blocking keyboard input (INKEY$)
- DATA statements
- User-defined functions

### What Doesn't Work
Programs that require:
- File I/O (reading/writing data files)
- Computed jumps (ON GOTO/GOSUB)
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

### Phase 3 (In Progress) - File I/O
- ⚠ Sequential file I/O (OPEN, CLOSE, PRINT#, INPUT#)
- ⚠ EOF() function
- ⚠ LINE INPUT # statement

### Phase 4 (Planned) - Extended Features
- ⚠ Computed jumps (ON GOTO/GOSUB)
- ⚠ Random file I/O (FIELD, GET, PUT, LSET, RSET)

### Phase 5 (Future) - Enhancements
- Documentation improvements
- Performance optimization
- Extended error messages
- Debugging features

### Not Planned
- Graphics commands (hardware-specific)
- Sound commands (hardware-specific)
- Printer support (LPRINT)
- Direct hardware access (PEEK, POKE, INP, OUT)

## Known Limitations

1. **No file I/O** - Cannot read or write data files
2. **No computed jumps** - Use IF/THEN chains instead
3. **No random files** - Cannot access binary data files
4. **Integer division precision** - May differ slightly from original MBASIC due to Python float handling

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
1. Sequential file I/O implementation
2. ON GOTO/GOSUB computed jumps
3. Random file I/O implementation
4. Additional test cases

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.
