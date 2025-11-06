# MBASIC Help System Migration Plan

## Overview

Migrate content from `docs/external/basic_ref.txt` (MBASIC Reference Manual) into the help system, separating UI-specific content from shared language reference content.

**Source:** MBASIC VT180, VS.21 BASIC-80 Reference Manual (7834 lines)

## Guiding Principles

1. **Separate UI from Language** - UI-specific content goes to `docs/help/ui/{backend}/`, language reference is shared in `docs/help/common/language/`
2. **Command-line editing is CLI-only** - The curses UI has its own editor, so command-line editing (EDIT command, line editing) is specific to CLI UI
3. **Statements are shared** - BASIC language statements (IF, FOR, PRINT, etc.) work the same across all UIs
4. **Functions are shared** - Intrinsic functions (ABS, SIN, MID$, etc.) work the same across all UIs
5. **Keep it maintainable** - Break into logical, digestible markdown files

## Source Document Structure

From `basic_ref.txt` Table of Contents:

### CHAPTER 1: General Information about BASIC-80
- 1.1 INITIALIZATION (UI-specific - varies by OS/UI)
- 1.2 MODES OF OPERATION (Language - Direct vs Program mode)
- 1.3 LINE FORMAT (Language - line structure)
  - 1.3.1 Line Numbers
- 1.4 CHARACTER SET (Language)
  - 1.4.1 Control Characters (Mixed - some UI-specific)
- 1.5 CONSTANTS (Language)
  - 1.5.1 Single And Double Precision
- 1.6 VARIABLES (Language)
  - 1.6.1 Variable Names And Declaration Characters
  - 1.6.2 Array Variables
- 1.7 TYPE CONVERSION (Language)
- 1.8 OPERATORS (Language)
  - 1.8.1 Arithmetic Operators
    - 1.8.1.1 Integer Division And Modulus Arithmetic
    - 1.8.1.2 Overflow And Division By Zero
  - 1.8.2 Relational Operators
  - 1.8.3 Logical Operators
- 1.9 INPUT EDITING (UI-specific for CLI, not applicable to curses UI)
- 1.10 ERROR MESSAGES (Language - shared error codes)

### CHAPTER 2: BASIC-80 Commands and Statements
All alphabetically ordered. Need to categorize:

**Commands (UI-specific or varies):**
- AUTO - CLI only (curses has different line numbering)
- CLOAD - Cassette tape (legacy, may not implement)
- DELETE - CLI only (delete line range)
- EDIT - CLI only (line editor)
- LIST - Shared (but UI may vary)
- LLIST - Printer output
- LOAD - Shared (file operations)
- LPRINT - Printer output
- MERGE - Shared (file operations)
- NEW - Shared
- RENUM - Shared (but UI may vary)
- RUN - Shared
- SAVE - Shared (file operations)

**Statements (Language - Shared):**
- CALL - Assembly language interface
- CHAIN - Program chaining
- CLEAR - Memory management
- CLOSE - File I/O
- COMMON - Variable passing
- CONT - Continue execution
- DATA - Data storage
- DEF FN - Function definition
- DEFINT/SNG/DBL/STR - Type declarations
- DEF USR - User functions
- DIM - Array dimensions
- END - Program termination
- ERASE - Array cleanup
- ERR AND ERL - Error handling
- ERROR - Raise errors
- FIELD - Random file I/O
- FOR...NEXT - Loops
- GET - File I/O
- GOSUB...RETURN - Subroutines
- GOTO - Flow control
- IF...THEN...ELSE - Conditionals
- INPUT - User input
- INPUT# - File input
- KILL - Delete files
- LET - Assignment
- LINE INPUT - String input
- LINE INPUT# - File input
- MID$ - String manipulation
- NAME - Rename files
- NULL - Terminal settings
- ON ERROR GOTO - Error handling
- ON...GOSUB/GOTO - Computed branches
- OPEN - File I/O
- OPTION BASE - Array base
- OUT - Port output
- POKE - Memory manipulation
- PRINT - Output
- PRINT# - File output
- PRINT USING - Formatted output
- PUT - File I/O
- RANDOMIZE - Random numbers
- READ - Data reading
- REM - Comments
- RESTORE - Reset DATA pointer
- RESUME - Error recovery
- STOP - Break execution
- SWAP - Exchange variables
- TRON/TROFF - Trace mode
- WAIT - Port waiting
- WEND - Loop end
- WHILE...WEND - While loops
- WIDTH - Output width
- WRITE - File output

### CHAPTER 3: BASIC-80 Functions
All intrinsic functions (Language - Shared):
- ABS - Absolute value
- ASC - Character code
- ATN - Arctangent
- CDBL - Convert to double
- CHR$ - Character from code
- CINT - Convert to integer
- COS - Cosine
- CSNG - Convert to single
- CVD, CVI, CVS - Convert from string
- EOF - End of file
- EXP - Exponential
- FIX - Truncate
- FRE - Free memory
- HEX$ - Hexadecimal string
- INP - Port input
- INSTR - String search
- INT - Integer part
- LEFT$ - Left substring
- LEN - String length
- LOC - File position
- LOF - File length
- LOG - Natural logarithm
- LPOS - Printer position
- MID$ - Middle substring
- MKD$, MKI$, MKS$ - Convert to string
- OCT$ - Octal string
- PEEK - Memory read
- POS - Cursor position
- RIGHT$ - Right substring
- RND - Random number
- SGN - Sign
- SIN - Sine
- SPACE$ - Spaces
- SPC - Skip spaces
- SQR - Square root
- STR$ - Number to string
- STRING$ - Repeated character
- TAB - Tab position
- TAN - Tangent
- USR - User function call
- VAL - String to number
- VARPTR - Variable pointer

### APPENDICES
- A: New Features in BASIC-80 Release 5.0 (Historical reference)
- B: BASIC-80 Disk I/O (Shared - file operations)
- C: Assembly Language Subroutines (Advanced - shared)
- D: BASIC-80 with CP/M (OS-specific, historical)
- E: Converting Programs (Migration guide)
- F: Error Codes and Messages (Shared)
- G: Mathematical Functions (Shared)
- H: ASCII Character Codes (Shared)

## Proposed Help Structure

```
docs/help/
├── common/
│   ├── language/
│   │   ├── index.md (Language overview)
│   │   ├── basics.md (modes, line format, character set)
│   │   ├── data-types.md (constants, variables, type conversion)
│   │   ├── operators.md (arithmetic, relational, logical)
│   │   ├── error-handling.md (error messages, ON ERROR GOTO, etc.)
│   │   ├── statements/
│   │   │   ├── index.md (Alphabetical list of all statements)
│   │   │   ├── assignment.md (LET, assignment)
│   │   │   ├── flow-control.md (IF, GOTO, GOSUB, FOR, WHILE, ON...GOTO)
│   │   │   ├── input-output.md (PRINT, INPUT, LINE INPUT)
│   │   │   ├── file-io.md (OPEN, CLOSE, INPUT#, PRINT#, GET, PUT, FIELD)
│   │   │   ├── arrays.md (DIM, ERASE, OPTION BASE)
│   │   │   ├── functions.md (DEF FN, DEF USR)
│   │   │   ├── data.md (DATA, READ, RESTORE)
│   │   │   ├── error-handling.md (ON ERROR GOTO, RESUME, ERROR, ERR, ERL)
│   │   │   ├── program-control.md (CHAIN, COMMON, CLEAR, END, STOP, CONT)
│   │   │   ├── memory.md (POKE, OUT, CALL)
│   │   │   ├── type-declaration.md (DEFINT, DEFSNG, DEFDBL, DEFSTR)
│   │   │   ├── miscellaneous.md (REM, SWAP, RANDOMIZE, TRON, TROFF, etc.)
│   │   │   └── [individual statement files as needed]
│   │   ├── functions/
│   │   │   ├── index.md (Alphabetical list of all functions)
│   │   │   ├── math.md (ABS, SIN, COS, TAN, ATN, EXP, LOG, SQR, SGN, INT, FIX)
│   │   │   ├── string.md (LEFT$, RIGHT$, MID$, LEN, INSTR, ASC, CHR$, STR$, VAL, SPACE$, STRING$)
│   │   │   ├── conversion.md (CINT, CSNG, CDBL, CVD, CVI, CVS, MKD$, MKI$, MKS$, HEX$, OCT$)
│   │   │   ├── file.md (EOF, LOC, LOF)
│   │   │   ├── system.md (FRE, PEEK, INP, POS, LPOS, VARPTR, USR)
│   │   │   ├── random.md (RND, RANDOMIZE)
│   │   │   └── [individual function files as needed]
│   │   └── appendices/
│   │       ├── error-codes.md (Appendix F)
│   │       ├── math-functions.md (Appendix G)
│   │       ├── ascii-codes.md (Appendix H)
│   │       ├── disk-io.md (Appendix B)
│   │       └── assembly-language.md (Appendix C)
│   └── examples.md (Example programs)
│
├── ui/cli/
│   ├── index.md
│   ├── commands.md (AUTO, DELETE, EDIT, LIST, RENUM, etc.)
│   ├── line-editing.md (Section 1.9 INPUT EDITING)
│   ├── getting-started.md
│   └── file-operations.md (LOAD, SAVE, MERGE)
│
└── ui/curses/
    ├── index.md (Already exists - table of contents)
    ├── quick-reference.md (Already exists - keyboard shortcuts)
    ├── keyboard-commands.md
    ├── editing.md
    ├── running.md
    ├── debugging.md
    ├── files.md (LOAD, SAVE, MERGE - curses UI specific)
    ├── getting-started.md
    └── help-navigation.md
```

## Migration Tasks

### Phase 1: Language Reference - Core Concepts
1. Extract Chapter 1 sections → `docs/help/common/language/basics.md`
   - Modes of operation
   - Line format and line numbers
   - Character set
2. Extract data types → `docs/help/common/language/data-types.md`
   - Constants (1.5)
   - Variables (1.6)
   - Type conversion (1.7)
3. Extract operators → `docs/help/common/language/operators.md`
   - Arithmetic (1.8.1)
   - Relational (1.8.2)
   - Logical (1.8.3)
4. Extract error handling → `docs/help/common/language/error-handling.md`
   - Error messages (1.10)

### Phase 2: Statements Reference
Create individual markdown files for each statement category from Chapter 2:
1. Flow control (IF, GOTO, GOSUB, FOR...NEXT, WHILE...WEND, ON...GOSUB/GOTO)
2. Input/Output (PRINT, INPUT, LINE INPUT, PRINT USING)
3. File I/O (OPEN, CLOSE, INPUT#, PRINT#, GET, PUT, FIELD, etc.)
4. Arrays (DIM, ERASE, OPTION BASE)
5. Program control (CHAIN, COMMON, CLEAR, END, STOP, CONT, RUN)
6. Error handling (ON ERROR GOTO, RESUME, ERROR, ERR, ERL)
7. Data handling (DATA, READ, RESTORE)
8. Functions (DEF FN, DEF USR)
9. Type declarations (DEFINT, DEFSNG, DEFDBL, DEFSTR)
10. Memory/Hardware (POKE, OUT, CALL, INP, PEEK)
11. Miscellaneous (REM, SWAP, RANDOMIZE, TRON, TROFF, etc.)

Create index with full alphabetical reference.

### Phase 3: Functions Reference
Create individual markdown files for each function category from Chapter 3:
1. Mathematical functions
2. String functions
3. Type conversion functions
4. File functions
5. System functions
6. Random numbers

Create index with full alphabetical reference.

### Phase 4: Appendices
1. Error codes (Appendix F)
2. Math functions table (Appendix G)
3. ASCII codes (Appendix H)
4. Disk I/O guide (Appendix B)
5. Assembly language interface (Appendix C)

### Phase 5: CLI UI Documentation
Extract and adapt:
1. Command-line editing (Section 1.9)
2. AUTO command
3. DELETE command
4. EDIT command
5. LIST variations
6. RENUM command

### Phase 6: Integration & Testing
1. Add navigation links between related topics
2. Add "See Also" sections
3. Test all help navigation from curses UI
4. Verify CLI UI help (if implemented)
5. Cross-reference statements and functions

## Notes

- The original manual is ~7800 lines - expect ~50-100 markdown files when properly split
- Prioritize most commonly used statements/functions first
- Keep original examples where helpful
- Modernize or clarify where the 1979 manual is outdated
- Mark unimplemented features clearly (e.g., CLOAD for cassette tape)

## Progress Tracking

Will track in separate checklist document as work progresses.
