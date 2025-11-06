# Implementation Status

This document provides a comprehensive overview of what is and is not yet implemented in the MBASIC 5.21 Interpreter.

## Summary

**Parser Coverage:** 100% - All MBASIC 5.21 syntax is parsed correctly
**Runtime Implementation:** ~99% - All major features complete; only obsolete/incompatible features remain unimplemented

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
- ✓ SWAP (exchange values of two variables)
- ✓ DATA/READ/RESTORE
- ✓ INPUT (console input)
- ✓ PRINT (console output with zones and separators)
- ✓ PRINT USING (formatted output with format strings)
- ✓ PRINT# USING (formatted file output)

### Built-in Functions (47+)
- ✓ Math: ABS, ATN, COS, EXP, INT, LOG, RND, SGN, SIN, SQR, TAN
- ✓ String: ASC, CHR$, INSTR, LEFT$, LEN, MID$, RIGHT$, SPACE$, STR$, STRING$, VAL
- ✓ Conversion: CDBL, CINT, CSNG
- ✓ Binary I/O: CVI, CVS, CVD (convert string to int/single/double), MKI$, MKS$, MKD$ (convert int/single/double to string)
- ✓ Input: INKEY$ (non-blocking keyboard input)
- ✓ File I/O: EOF() (end of file test), LOC() (record position), LOF() (file length)
- ✓ Output: TAB(n) (tab to column), SPC(n) (print n spaces)
- ✓ Other: FIX, HEX$, OCT$, POS

### String Manipulation
- ✓ MID$(var$, start, len) = value$ - Replace substring in-place

### Debugging
- ✓ TRON/TROFF - Trace program execution (shows line numbers as they execute)

### User-Defined Features
- ✓ DEF FN (user-defined functions) - single-line functions with parameters
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

## ✗ Not Yet Implemented

Currently, all major MBASIC 5.21 features are implemented. See "❌ Will Not Be Implemented" below for features that are intentionally not supported due to obsolescence or incompatibility with modern systems.

## ✓ Implemented for Compatibility

These features are implemented and accepted by the parser/interpreter for compatibility with existing BASIC programs, but they perform no action or have limited functionality in a modern environment. Programs using these features will run without errors, but the features may not have visible effects.

### Screen Control

- **CLS** - Clear screen
  - Status: ✓ Implemented as no-op
  - Why: Terminal control sequences vary widely across platforms. Modern terminals provide their own clear commands. Programs can use CLS for compatibility, but it won't actually clear the screen.
  - Note: If screen clearing is needed, use your terminal's native clear command (e.g., `clear` on Unix/Linux, `cls` on Windows) before running the program.

- **WIDTH [#n,] width** - Set output width
  - Status: ✓ Implemented as no-op
  - Why: Modern terminals handle line width automatically and dynamically adjust to window size. Setting a fixed width is not meaningful in modern terminal contexts.
  - Note: Programs can use WIDTH for compatibility, but it won't affect output formatting.

### Hardware Access

- **PEEK(addr)** - Read byte from memory address
  - Status: ✓ Implemented - returns random value 0-255
  - Why: Direct memory access is not possible in modern Python/OS environments. Most vintage BASIC programs use PEEK to seed random number generators (e.g., `RANDOMIZE PEEK(0)`), so returning a random value provides reasonable compatibility for this common use case.
  - Note: Programs that rely on reading specific memory addresses will not work correctly.

## ❌ Will Not Be Implemented

These features are obsolete, hardware-specific, or incompatible with modern computing environments. They are parsed for compatibility but will never have functional implementations.

### 1. Hardware Access (CP/M-Specific)
**Reason:** Requires direct hardware/memory access not available in modern operating systems

- **POKE addr, value** - Write byte to memory address
  - Status: Parsed but does nothing
  - Why: Would require hardware emulation; not relevant for modern use

- **INP(port)** - Read from I/O port
  - Status: Returns 0 (placeholder)
  - Why: I/O ports don't exist in modern operating systems

- **OUT port, value** - Write to I/O port
  - Status: Parsed but does nothing
  - Why: I/O ports are obsolete; no modern equivalent

- **CALL addr** - Call machine language subroutine
  - Status: Parsed but does nothing
  - Why: Would require Z80 emulation; not practical or useful

- **USR(n)** - Call user machine code routine
  - Status: Returns 0 (placeholder)
  - Why: Cannot execute Z80/8080 machine code from Python

- **VARPTR(var)** - Return memory address of variable
  - Status: Not implemented
  - Why: Memory addresses are not meaningful in Python's managed memory environment; variables don't have fixed addresses

- **FRE(n)** - Return free memory available
  - Status: Not implemented
  - Why: Modern systems use virtual memory and garbage collection; "free memory" is meaningless in Python
  - Note: Would return arbitrary values that don't reflect actual system memory

### 2. Printer Support (Obsolete Hardware)
**Reason:** Line printers are obsolete; modern systems use different printing paradigms

- **LPRINT [USING] ...** - Print to line printer
  - Status: Not implemented
  - Why: Line printers don't exist; would need complex OS print spooling
  - Alternative: Use PRINT to redirect output, then print from file

- **LLIST** - List program to printer
  - Status: Not implemented
  - Why: Same as LPRINT; obsolete hardware interface

- **LPOS(n)** - Get line printer head position
  - Status: Not implemented
  - Why: No printer head to query on modern systems

### 3. Cassette/Tape Operations (Obsolete Media)
**Reason:** Cassette tapes are not used for data storage in modern systems

- **CLOAD** - Load program from cassette
  - Status: Not in MBASIC 5.21 spec (only in earlier versions)
  - Why: Cassette tapes are obsolete storage media

- **CSAVE** - Save program to cassette
  - Status: Not in MBASIC 5.21 spec (only in earlier versions)
  - Why: Cassette tapes are obsolete storage media

### 4. Terminal Control (Obsolete/Unnecessary)
**Reason:** Modern terminals handle these automatically or differently

- **NULL n** - Set number of nulls after carriage return
  - Status: Not implemented
  - Why: Was needed for slow mechanical teletypes; modern terminals don't need this

**Note:** These features are documented here for completeness and to explain why they appear in MBASIC documentation but aren't implemented. Programs that rely heavily on these features cannot be run without modification.

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
- **PRINT USING:** Fully tested (string formats: !, \\ \\, &; numeric formats: #, +, -, ., ,, **, $$, **$, ^^^^, overflow)
- **SWAP:** Fully tested (simple variables, array elements, mixed types)

## Compatibility Notes

### What Works
Programs that use:
- Mathematical calculations
- String processing (including MID$ assignment for in-place modification)
- Arrays and data structures
- Variable operations (LET, SWAP)
- Control flow (IF, FOR, WHILE/WEND, GOSUB, ON GOTO/GOSUB)
- Error handling (ON ERROR GOTO/GOSUB, RESUME)
- Debugging (TRON/TROFF execution trace)
- User input/output
- Formatted output (PRINT USING, PRINT# USING with all format types)
- Non-blocking keyboard input (INKEY$)
- Sequential file I/O (OPEN, CLOSE, PRINT#, INPUT#, LINE INPUT#, WRITE#, EOF)
- Random access file I/O (FIELD, GET, PUT, LSET, RSET, LOC, LOF)
- Binary file I/O (CVI/CVS/CVD, MKI$/MKS$/MKD$ for reading/writing numeric data)
- File system operations (KILL, NAME AS, RESET)
- DATA statements
- User-defined functions

### What Doesn't Work
Programs that require:
- Hardware/memory access (POKE, INP, OUT, CALL, USR, VARPTR, FRE)
- Line printer output (LPRINT, LLIST, LPOS)
- Cassette tape storage (CLOAD, CSAVE - not in MBASIC 5.21 anyway)
- Terminal null padding (NULL)

See the **"❌ Will Not Be Implemented"** section above for detailed explanations of why these features are not supported.

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

### Phase 5 (Completed) - Formatted Output ✓
- ✓ TAB(n) and SPC(n) functions
- ✓ PRINT USING with string formats (!, \ \, &)
- ✓ PRINT USING with numeric formats (#, +, -, ., ,)
- ✓ PRINT USING with special formats (**, $$, **$, ^^^^)
- ✓ PRINT# USING for file output
- ✓ Format overflow detection (%)
- ✓ Literal character escaping (_)

### Phase 6 (Future) - Enhancements
- Documentation improvements
- Performance optimization
- Extended error messages
- Additional debugging features

## Known Limitations

### Floating Point Precision (FEATURE, NOT A BUG)

This implementation uses Python's native `float` type (IEEE 754 double precision, 64-bit) for all numeric calculations, while original MBASIC 5.21 used single precision (32-bit) floats.

**Result**: Our implementation is ~9 orders of magnitude MORE accurate than the original:
- Original MBASIC: ~6-7 significant digits, errors at 10⁻⁷
- Our MBASIC: ~15-16 significant digits, errors at 10⁻¹⁶

This means:
- **Better accuracy** in trig functions (SIN, COS, TAN, ATN)
- **Better preservation** of mathematical identities (e.g., SIN²+COS²=1)
- **Better precision** in compound calculations
- The ATN (arctangent) function, notorious for poor accuracy in original MBASIC, is highly accurate

**Note**: Programs may produce slightly different numeric results due to this improved precision. This is expected and beneficial.

**See**: `doc/MATH_PRECISION_ANALYSIS.md` for detailed comparison with real MBASIC 5.21, including side-by-side test results.

## Testing Your Program

To check if your MBASIC program will work:

1. **Parser test:**
   ```bash
   python3 mbasic yourprogram.bas
   ```
   If it parses without errors, the syntax is valid.

2. **Check for unimplemented features:**
   - Look for "NotImplementedError" when running
   - Review the "Not Yet Implemented" section above
   - Check if your program uses file I/O or computed jumps

3. **Run tests:**
   ```bash
   # Run self-checking tests
   python3 mbasic basic/tests_with_results/test_operator_precedence.bas
   ```

## Contributing

Contributions welcome! Priority areas:
1. Additional test cases
2. Performance optimization
3. Enhanced error messages and debugging features

Contributions welcome - see the project repository for details.
