# MBASIC Compiler Missing Features Analysis

## Currently Implemented

### Statements
✓ PRINT (basic, no USING support)
✓ INPUT (keyboard only, no file I/O)
✓ LET (assignment)
✓ FOR/NEXT
✓ WHILE/WEND
✓ GOTO
✓ GOSUB/RETURN
✓ END
✓ REM

### Variable Types
✓ INTEGER (%)
✓ SINGLE (!)
✓ DOUBLE (#)
✓ STRING ($)

### String Functions
✓ LEFT$, RIGHT$, MID$ (functions)
✓ LEN, ASC, VAL
✓ CHR$
✓ String concatenation (+)

### Operators
✓ Arithmetic: +, -, *, /, ^ (power)
✓ Relational: =, <>, <, <=, >, >=
✗ Logical: AND, OR, NOT, XOR, IMP, EQV
✗ MOD, \ (integer division)

## Missing Features to Implement

### Critical Control Flow
- **IF/THEN/ELSE** - Essential for any non-trivial program
- **ON GOTO/ON GOSUB** - Computed branching
- **ON ERROR GOTO/RESUME** - Error handling

### Arrays
- **DIM** - Array declaration
- **Array access** - Need to generate proper C arrays
- **ERASE** - Clear arrays
- **OPTION BASE** - 0 or 1 based arrays

### Data Statements
- **DATA/READ/RESTORE** - Static data initialization

### Math Functions (via math.h)
Easy to add since z88dk includes math.h:
- **SIN, COS, TAN** - Trigonometric
- **ATN** - Arc tangent
- **SQR** - Square root (sqrt in C)
- **EXP, LOG** - Exponential/Natural log
- **ABS** - Absolute value
- **SGN** - Sign function
- **INT, FIX** - Integer conversion
- **RND** - Random numbers

### String Functions
- **STR$** - Number to string
- **STRING$** - Repeat character
- **SPACE$** - Spaces string
- **INSTR** - Find substring
- **MID$ statement** - Substring replacement
- **LCASE$, UCASE$** - Case conversion (if supported)

### File I/O
All file operations need implementation:
- **OPEN, CLOSE** - File management
- **PRINT #, INPUT #, LINE INPUT #** - Sequential I/O
- **EOF, LOC, LOF** - File status
- **GET, PUT** - Random access I/O
- **FIELD, LSET, RSET** - Record fields
- **WRITE #** - CSV output
- **KILL, NAME AS** - File operations

### Binary Data (for files)
- **MKI$, MKS$, MKD$** - Pack numbers to strings
- **CVI, CVS, CVD** - Unpack strings to numbers

### Hardware Access (Can be implemented in compiled code!)
- **INP(port)** - Read from I/O port
- **OUT port, value** - Write to I/O port
- **PEEK(address)** - Read memory
- **POKE address, value** - Write memory
- **WAIT port, mask** - Wait for port condition

### User Functions
- **DEF FN** - User-defined functions

### Other Statements
- **STOP** - Like END but shows line number
- **SWAP** - Swap variables
- **RANDOMIZE** - Seed random generator
- **CLS** - Clear screen (system("clear"))
- **WIDTH** - Set line width
- **CLEAR** - Clear variables/set stack

### System Functions
- **FRE** - Free memory
- **POS** - Cursor position
- **TAB, SPC** - Formatting
- **TIMER** - System timer
- **DATE$, TIME$** - Date/time strings
- **INKEY$** - Non-blocking keyboard input
- **ERR, ERL** - Error info

## Implementation Priority

### Phase 1: Essential Control Flow
1. **IF/THEN/ELSE** - Critical for logic
2. **DIM and arrays** - Required for most programs
3. **DATA/READ/RESTORE** - Static initialization

### Phase 2: Math & Strings
1. **Math functions** (SIN, COS, etc.) - Easy via math.h
2. **STR$** - Number formatting
3. **INSTR** - String searching
4. **Logical operators** (AND, OR, NOT)

### Phase 3: Hardware Access
1. **PEEK/POKE** - Memory access via pointers
2. **INP/OUT** - I/O ports (z88dk should support)
3. **WAIT** - Port waiting

### Phase 4: File I/O
1. **Sequential files** (OPEN, PRINT#, INPUT#)
2. **Random access** (GET, PUT, FIELD)
3. **Binary packing** (MKI$, CVI, etc.)

### Phase 5: Advanced Features
1. **ON ERROR/RESUME** - Error handling
2. **DEF FN** - User functions
3. **ON GOTO/GOSUB** - Computed jumps

## Hardware Access Implementation Notes

### PEEK/POKE
```c
// PEEK(addr)
uint8_t peek_value = *((uint8_t*)addr);

// POKE addr, value
*((uint8_t*)addr) = value;
```

### INP/OUT
z88dk likely provides:
```c
#include <z80.h>
// or
uint8_t inp(uint16_t port);
void outp(uint16_t port, uint8_t value);
```

### WAIT
```c
// WAIT port, mask, [invert_mask]
while ((inp(port) & mask) != expected) {
    // busy wait
}
```

## Library Creation Plan

### Create mb25.lib
Instead of compiling mb25_string.c into every program:

1. **Compile to object file:**
```bash
z88dk.zcc +cpm -c mb25_string.c -o mb25_string.o
```

2. **Create library:**
```bash
z88dk.z80asm -xmb25 mb25_string.o
```

3. **Link programs against library:**
```bash
z88dk.zcc +cpm program.c -lmb25 -L. -o program
```

### Library Organization
If z80asm linker is single-pass, order matters:
```
mb25.lib:
  - String functions (mb25_string.o)
  - Math helpers (mb25_math.o)
  - I/O functions (mb25_io.o)
  - Hardware access (mb25_hw.o)
```

Functions should be ordered so dependencies come first.

### Check Linker Type
```bash
# Check z88dk documentation or test with circular dependencies
z88dk.z80asm --help | grep -i pass
```

## Next Steps

1. **Create mb25 runtime library** - Avoid relinking strings every time
2. **Implement IF/THEN/ELSE** - Most critical missing feature
3. **Add array support** - Required for real programs
4. **Add math functions** - Easy wins via math.h
5. **Hardware access functions** - PEEK/POKE/INP/OUT for system programming