# Microsoft BASIC Compiler vs Interpreter Differences

This document outlines the key differences between the Microsoft BASIC-80 5.x Interpreter and the Microsoft BASIC Compiler (BASCOM), based on the Microsoft BASIC Compiler 1980 documentation.

## 1. OPERATIONAL DIFFERENCES

### 1.1 No Direct Mode
- **Compiler**: No direct mode or interactive command level. The compiler only reads compiler commands to specify files to compile.
- **Interpreter**: Has both direct mode (for immediate execution) and indirect mode (for program entry).

### 1.2 Commands Not Implemented in Compiler
The following commands are NOT available in the compiled environment:
- `AUTO` - Auto line numbering
- `CLEAR` - Clear memory
- `CLOAD` - Load from cassette
- `COMMON` - Common variables (generates fatal error)
- `CONT` - Continue execution
- `CSAVE` - Save to cassette
- `DELETE` - Delete program lines
- `EDIT` - Edit program lines
- `LIST` - List program
- `LLIST` - List program to printer
- `LOAD` - Load program
- `MERGE` - Merge programs
- `NEW` - Clear program from memory
- `RENUM` - Renumber program lines
- `SAVE` - Save program

### 1.3 Program Creation and Editing
- **Compiler**: Must use Microsoft's EDIT-80 Text Editor or the BASIC-80 interpreter to create and edit programs. Files must be saved in ASCII format (using the `A` option with SAVE).
- **Interpreter**: Built-in editing capabilities with EDIT command.

### 1.4 Physical Line Length
- **Compiler**: Maximum physical line length is 127 characters (logical statements can span multiple physical lines using line feed).
- **Interpreter**: Different line length limitations.

### 1.5 Line Numbers in Object Code
- **Compiler**: Line numbers are NOT included in object code by default (to reduce size). Line numbers only included if `/D`, `/X`, or `/E` compilation switches are used.
- **Interpreter**: Line numbers always available for debugging.

### 1.6 Error Reporting
- **Compiler**: Runtime errors report memory addresses instead of line numbers (unless debug switches used). Requires compiler listing and LINK-80 map to identify error location.
- **Interpreter**: Errors always report line numbers.

## 2. LANGUAGE DIFFERENCES

### 2.1 CALL Statement
- **Compiler**: `<variable name>` must contain an External symbol recognized by LINK-80 as a global symbol. Must be supplied as assembly language subroutine or FORTRAN-80 library routine.
- **Interpreter**: Different calling mechanism.

### 2.2 COMMON Statement
- **Compiler**: NOT implemented - generates fatal error. Future versions will implement it similar to FORTRAN's COMMON statement.
- **Interpreter**: Fully implemented.

### 2.3 CHAIN and RUN
- **Compiler**: Only simplest form implemented (`CHAIN filename$`). For CP/M, default extension is `.COM`. Programs can chain to any COM file, but command line information is not automatically passed (must use POKE).
- **Interpreter**: Full implementation with parameter passing.

### 2.4 DEFINT/SNG/DBL/STR
- **Compiler**: DEFxxx statements are NOT executed - compiler reacts to static occurrence regardless of execution order. Takes effect when line is encountered during compilation. Type remains in effect until end of program or different DEFxxx statement.
- **Interpreter**: DEFxxx statements are executed dynamically during runtime.

### 2.5 USRn Functions
- **Compiler**: Significantly different - argument is ignored, integer result returned in HL registers. Recommended to replace with CALL statement.
- **Interpreter**: Full implementation with argument passing.

### 2.6 DIM and ERASE
- **Compiler**:
  - DIM is scanned rather than executed (like DEFxxx)
  - Takes effect when line is encountered during compilation
  - Subscript values must be integer constants (no variables, expressions, or floating point)
  - Cannot redimension arrays - generates "Redimensioned array" error
  - ERASE statement NOT implemented - generates fatal error
- **Interpreter**:
  - DIM executed dynamically
  - ERASE allows arrays to be erased and redimensioned
  - Subscripts can be variables or expressions

### 2.7 END Statement
- **Compiler**: Closes files and returns control to operating system. Compiler assumes END at end of program, so "running off the end" produces proper termination.
- **Interpreter**: Different behavior.

### 2.8 ON ERROR GOTO/RESUME
- **Compiler**:
  - Requires `/E` switch if program contains ON ERROR GOTO and RESUME <line number>
  - Requires `/X` switch if program uses RESUME NEXT, RESUME, or RESUME 0
  - `/E` generates extra code for GOSUB/RETURN
  - `/X` relinquishes certain optimizations
- **Interpreter**: No special switches required.

### 2.9 REM Statements
- **Compiler**: REM statements and remarks (starting with single quote) take NO time or space during execution. Can be used freely.
- **Interpreter**: REMs consume some runtime resources.

### 2.10 STOP Statement
- **Compiler**: Identical to END - closes files and returns to operating system.
- **Interpreter**: Halts execution but allows CONT to resume.

### 2.11 TRON/TROFF
- **Compiler**: Requires `/D` compilation switch. Without it, TRON/TROFF are ignored and warning message generated.
- **Interpreter**: Always available.

### 2.12 FOR/NEXT and WHILE/WEND
- **Compiler**: Loops must be statically nested (proper nesting determined at compile time).
- **Interpreter**: More flexible dynamic nesting.

### 2.13 Double Precision Transcendental Functions
- **Compiler**: SIN, COS, TAN, SQR, LOG, EXP return double precision results if given double precision argument. Exponentiation with double precision operands returns double precision result.
- **Interpreter (BASIC-80/86)**: Only integer and single precision results returned by functions (noted in documentation).

### 2.14 %INCLUDE Statement
- **Compiler**: `%INCLUDE <filename>` statement allows including source from alternate file. Must be last statement on line. Format: `<line number> %INCLUDE <filename>`
- **Interpreter**: Not available.

## 3. EXPRESSION EVALUATION DIFFERENCES

### 3.1 Type Conversion
Both compiler and interpreter convert operands to the most precise type during expression evaluation. However:

### 3.2 Numeric Overflow Handling
- **Compiler**: More limited in numeric overflow handling. Type conversion decisions made at compilation time, not runtime.
  - Example: `I%=20000`, `J%=20000`, `K%=-30000`, `M%=I%+J%-K%`
  - Interpreter: Converts to floating point when overflow occurs, yields 10000
  - Compiler: Performs entire operation in integer mode, produces incorrect result (unless `/D` switch used)

### 3.3 Algebraic Transformations
- **Compiler**: May perform valid algebraic transformations before generating code for optimization. Follows operator precedence and parentheses but makes no other guarantee of evaluation order.
- **Interpreter**: More predictable left-to-right evaluation.

## 4. COMPILATION SWITCHES

The compiler provides several switches to control compilation behavior:

- **/E** - Program contains ON ERROR GOTO (generates extra code, includes line numbers)
- **/X** - Program contains RESUME/RESUME NEXT/RESUME 0 (implies /E, relinquishes optimizations)
- **/N** - Prevents listing of generated symbolic code
- **/D** - Debug mode - generates checking code for:
  - Arithmetic overflow/underflow
  - Array bounds checking
  - Line numbers in binary
  - RETURN without GOSUB checking
  - Required for TRON/TROFF
- **/Z** - Use Z80 opcodes when possible
- **/S** - Write long quoted strings to binary immediately (saves memory, wastes space for duplicates, code cannot be in ROM)
- **/4** - Use Microsoft 4.51 lexical conventions (spaces insignificant, 2-char variable names)
- **/C** - Relax line numbering (allows any order or no line numbers, underscore for continuation)

## 5. PERFORMANCE CONSIDERATIONS

### 5.1 Integer Variables
- **Compiler**: Maximum use of integer variables produces fastest, most compact code. Integer loop counters can execute ~30 times faster than floating point. Integer array subscripts generate significantly faster and more compact code.
- **Interpreter**: Performance difference less dramatic.

### 5.2 Code Size
- **Compiler**: Generates compact machine code. REM statements have zero overhead.
- **Interpreter**: Tokenized format, REMs consume some space/time.

## 6. DEVELOPMENT WORKFLOW

### Recommended Approach:
1. Create programs using EDIT-80 or BASIC-80 interpreter
2. Debug thoroughly using BASIC-80 interpreter
3. Save in ASCII format (SAVE "filename",A)
4. Compile with BASCOM
5. Link with LINK-80
6. Test compiled version

### Debugging:
- Use interpreter for initial debugging (has better error reporting)
- Use compiler `/D` switch for runtime debugging of compiled code
- Compiler listing and LINK-80 map needed to locate errors in compiled code

## 7. FILE FORMATS

- **Compiler Input**: Requires ASCII format source files
- **Interpreter**: Can save/load in both compressed binary and ASCII formats
- **Protected Files**: Interpreter can save protected (encoded) files that cannot be listed or edited
