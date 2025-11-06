---
search:
  exclude: true
---

# BASIC-80 Language Reference

Complete language reference for MBASIC 5.21 (BASIC-80).

## Quick Access

- [Functions](functions/index.md) - 45 intrinsic functions
- [Statements](statements/index.md) - 77 commands and statements
- [Appendices](appendices/index.md) - Error codes, ASCII table, math functions
- [Compiled BASIC-80](../compiler/index.md) - Compiler optimizations and code generation

## Language Components

### [Functions](functions/index.md)
Built-in functions for mathematical operations, string manipulation, file I/O, and system operations.

**Categories:**
- Mathematical (ABS, SIN, COS, SQR, etc.)
- String (LEFT$, RIGHT$, MID$, LEN, etc.)
- Type Conversion (CINT, CDBL, STR$, VAL, etc.)
- File I/O (EOF, LOC, INPUT$, etc.)
- System (FRE, PEEK, INP, VARPTR, etc.)

### [Statements and Commands](statements/index.md)
Programming statements for control flow, I/O, file operations, and program management.

**Categories:**
- Program Control (END, STOP, CLEAR, etc.)
- Flow Control (FOR-NEXT, IF-THEN-ELSE, WHILE-WEND, etc.)
- Input/Output (INPUT, PRINT, LINE INPUT, etc.)
- File I/O (OPEN, CLOSE, GET, PUT, etc.)
- Arrays (DIM, ERASE, OPTION BASE)
- Error Handling (ON ERROR GOTO, RESUME, etc.)

### [Operators](operators.md)
Arithmetic, comparison, logical, and string operators.

### [Appendices](appendices/index.md)
Additional reference material.

**Available:**
- [Error Codes](appendices/error-codes.md) - Complete error reference
- [ASCII Codes](appendices/ascii-codes.md) - Character code table
- [Mathematical Functions](appendices/math-functions.md) - Derived functions

## Learning Resources

### Getting Started
- **Direct Mode** - Execute statements immediately
- **Program Mode** - Write multi-line programs with line numbers
- **Variables** - Integer (%), single (!), double (#), string ($)
- **Arrays** - Multi-dimensional data structures

### Common Tasks

#### Input and Output
```basic
10 INPUT "Enter your name"; N$
20 PRINT "Hello, "; N$
```

#### Loops
```basic
10 FOR I = 1 TO 10
20   PRINT I
30 NEXT I
```

#### Conditionals
```basic
10 INPUT "Enter a number"; N
20 IF N > 0 THEN PRINT "Positive" ELSE PRINT "Not positive"
```

#### File Operations
```basic
10 OPEN "DATA.TXT" FOR OUTPUT AS #1
20 PRINT #1, "Hello, file!"
30 CLOSE #1
```

### Error Handling
```basic
10 ON ERROR GOTO 1000
20 REM ... your code here ...
1000 REM Error handler
1010 PRINT "Error"; ERR; "on line"; ERL
1020 RESUME NEXT
```

## Language Features

### Data Types
- **Integer (%)** - Whole numbers (-32768 to 32767)
- **Single Precision (!)** - Floating point (~7 digits)
- **Double Precision (#)** - Floating point (~16 digits)
- **String ($)** - Text (up to 255 characters)

### Operators
- **Arithmetic**: `+`, `-`, `*`, `/`, `^`, `\` (integer div), `MOD`
- **Relational**: `=`, `<>`, `<`, `>`, `<=`, `>=`
- **Logical**: `AND`, `OR`, `NOT`, `XOR`, `EQV`, `IMP`

### Line Numbers
- Range: 0 to 65529
- Increment by 10 is standard
- Use RENUM to renumber

## Help Navigation

- **Arrow Keys** - Scroll through current page
- **Tab** - Move to next link
- **Enter** - Follow link
- **U** - Go back to previous page
- **ESC/Q** - Close help

## See Also

- [Functions Index](functions/index.md) - All functions alphabetically
- [Statements Index](statements/index.md) - All statements alphabetically
- [Error Codes](appendices/error-codes.md) - Error reference
- [Examples](../examples.md) - Sample programs
