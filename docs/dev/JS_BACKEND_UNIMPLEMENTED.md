# JavaScript Backend - Unimplemented Features

## Status: Phase 8 (Formatted Output) Complete ✅

Phase 1-4: Core implementation ✓
Phase 5-6: Enhanced features ✓
- INPUT statement (browser & Node.js)
- RANDOMIZE statement
- STOP statement
- SWAP statement
- DEF FN / FN calls
- TAB(), SPC(), INSTR()
- SPACE$(), STRING$(), HEX$(), OCT$(), POS()
- FIX(), SGN(), CINT(), CSNG(), CDBL()
- Fixed GOSUB return address calculation
- Fixed FOR loop skip when condition not met
- Fixed NEXT without variable
- ON GOSUB statement
- ERASE statement

Phase 7: Error handling ✓
- ON ERROR GOTO/GOSUB
- RESUME / RESUME NEXT / RESUME line
- ERROR statement
- ERL() and ERR() functions

Phase 8: Formatted output ✓
- PRINT USING (simplified implementation)
- Format specifiers: #, !, &, \\

Bug Fixes (2025-11-13):
- Fixed UnaryOpNode operator conversion (TokenType to string)
- Fixed semantic analyzer crash on string comparisons in IF conditions

New Features (2025-11-13):
- LINE INPUT statement (reads entire line without parsing, browser & Node.js support)
- WRITE statement (CSV-formatted output with automatic quoting)
- LPRINT statement (print to line printer / console.log)

This document tracks what's **not yet implemented** in the JavaScript backend.

---

## ✅ IMPLEMENTED (Core Features)

### Control Flow
- ✓ GOTO / ON GOTO
- ✓ GOSUB / ON GOSUB / RETURN
- ✓ FOR / NEXT (variable-indexed with state tracking)
- ✓ WHILE / WEND
- ✓ IF / THEN / ELSE

### I/O
- ✓ PRINT (with separators)
- ✓ PRINT USING (formatted output - simplified, basic format specifiers)
- ✓ WRITE (CSV-formatted output with automatic quoting)
- ✓ LPRINT (print to line printer / console.log)
- ✓ READ / DATA / RESTORE
- ✓ INPUT (browser: prompt, Node.js: readline - note: async in Node.js)
- ✓ LINE INPUT (reads entire line without parsing, browser & Node.js)

### Variables & Arrays
- ✓ LET (assignment)
- ✓ DIM (array declarations)
- ✓ Array access (subscripts)
- ✓ SWAP (variable swapping)
- ✓ ERASE (reset arrays to default values)

### Functions & Procedures
- ✓ DEF FN (user-defined functions)
- ✓ FN calls

### Error Handling
- ✓ ON ERROR GOTO/GOSUB (set error handler)
- ✓ RESUME / RESUME NEXT / RESUME line (continue after error)
- ✓ ERROR (trigger error)
- ✓ ERL() (line number where error occurred)
- ✓ ERR() (error code)

### Other
- ✓ REM (comments - skipped)
- ✓ END
- ✓ STOP (halts execution)
- ✓ RANDOMIZE (seed random generator)

---

## ⚠️ STUBBED (Partially Implemented)

_None currently - all previously stubbed features have been implemented_

---

## ❌ NOT IMPLEMENTED

### I/O Statements
- INPUT # - Read from file
- PRINT # - Write to file
- WRITE # - Write to file

### File Operations
- OPEN - Open file for I/O
- CLOSE - Close file
- RESET - Close all files
- KILL - Delete file
- NAME - Rename file
- FILES - List directory
- FIELD - Define random file buffer
- GET - Read random file record
- PUT - Write random file record
- LSET / RSET - Format string for random files
- LOF - Length of file (would be function)
- EOF - End of file test (would be function)
- LOC - Current file position (would be function)

### String Operations
- MID$ assignment - Modify substring in place

### Program Control
- STOP - Halt execution (like END but different)
- CONT - Continue after STOP (interactive only)
- CHAIN - Load and run another program
- RUN - Start program execution
- LOAD - Load program (interactive)
- SAVE - Save program (interactive)
- MERGE - Merge another program
- NEW - Clear program (interactive)
- DELETE - Delete line range (interactive)
- RENUM - Renumber lines (interactive)


### System/Hardware
- POKE - Write to memory address
- OUT - Output to I/O port
- WAIT - Wait for I/O port condition
- SYSTEM - Exit to operating system
- CLS - Clear screen (could implement in browser)
- LOCATE - Position cursor (could implement)
- COLOR - Set colors (could implement)
- WIDTH - Set screen/printer width

### Arrays
- OPTION BASE - Set array base 0/1 (handled in semantic analysis)
- COMMON - Share variables between chained programs

### Other
- RANDOMIZE - Seed random generator (could implement)
- CALL - Call machine language subroutine
- DEF SEG - Set memory segment
- DEF type statements - Type declarations (handled in semantic analysis)
- TRON / TROFF - Trace on/off (debugging)
- CLEAR - Set memory limits
- LIMITS - Show memory limits
- STEP - Single-step execution (debugging)

### Interactive/Editor Commands (Not Relevant)
- LIST - List program
- HELP - Show help
- SET - Configure settings
- SHOW - Show settings

---

## 🔧 KNOWN ISSUES / TODOs

### Fixed Issues (Phase 2)
1. ✓ **GOSUB return address** - Now properly calculates next statement/line
2. ✓ **FOR loop skip** - When initial condition not met, jumps to line after NEXT
3. ✓ **NEXT without variable** - Now uses most recent FOR loop

### Implemented Runtime Functions (Phase 2)
- ✓ TAB() - Tab to column (simplified implementation)
- ✓ SPC() - Print N spaces
- ✓ INSTR() - Find substring position
- ✓ SPACE$() - Generate N spaces
- ✓ STRING$() - Repeat character N times
- ✓ FIX() - Truncate to integer (rounds toward zero)
- ✓ SGN() - Sign of number
- ✓ CINT() - Convert to integer (round)
- ✓ CSNG() - Convert to single precision (no-op in JavaScript)
- ✓ CDBL() - Convert to double precision (no-op in JavaScript)
- ✓ HEX$() - Number to hex string
- ✓ OCT$() - Number to octal string
- ✓ POS() - Current print position (simplified)

### Missing Runtime Functions (Hardware/System)
- PEEK() - Read memory (not applicable in JavaScript)
- POKE - Write to memory (not applicable in JavaScript)
- INP() - Read I/O port (not applicable in JavaScript)
- OUT - Output to I/O port (not applicable in JavaScript)
- USR() - Call machine code (not applicable in JavaScript)

---

## 📊 Implementation Priority

### ✅ COMPLETED (Phase 2-8)
1. ✓ INPUT - User input (browser: prompt, Node.js: readline)
2. ✓ RANDOMIZE - Proper random seeding
3. ✓ TAB() / SPC() - Print formatting
4. ✓ INSTR() - String searching
5. ✓ DEF FN - User-defined functions
6. ✓ SWAP - Variable swapping
7. ✓ Additional string functions (SPACE$, STRING$, HEX$, OCT$, POS)
8. ✓ Additional math functions (FIX, SGN, CINT, CSNG, CDBL)
9. ✓ STOP statement
10. ✓ ON GOSUB - Computed subroutine calls
11. ✓ ERASE - Reset arrays
12. ✓ Error handling (ON ERROR, RESUME, ERROR, ERL, ERR)
13. ✓ PRINT USING - Formatted output (simplified)

### MEDIUM (Nice to have)
1. MID$ assignment - String modification

### LOW (Specialized/Advanced)
1. File I/O (OPEN, CLOSE, etc.)
2. CHAIN - Program chaining
3. Graphics (not in MBASIC 5.21)
4. Sound (not in MBASIC 5.21)
5. Machine code / hardware access (POKE, PEEK, CALL, etc.)

### NOT APPLICABLE (Interactive/Editor)
- LIST, NEW, RUN, LOAD, SAVE, DELETE, RENUM
- HELP, SET, SHOW
- CONT, STEP

---

## 📝 Notes

- **File I/O**: Could implement with localStorage (browser) and fs module (Node.js)
- **Graphics**: Could use Canvas API (browser), skip in Node.js
- **Sound**: Could use Web Audio API (browser), skip in Node.js
- **Screen control**: Could implement CLS/LOCATE/COLOR for browser, map to ANSI codes in Node.js
- **Hardware access**: POKE/PEEK/OUT/INP not meaningful in JavaScript, could stub or error

---

**Last Updated**: 2025-11-13
**Version**: 1.0.898
