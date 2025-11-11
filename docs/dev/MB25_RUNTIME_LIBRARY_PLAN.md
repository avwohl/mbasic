# MB25 Runtime Library Plan

## Overview

Create a modular runtime library for MBASIC compiled programs instead of compiling the same code into every executable. This reduces executable size and simplifies maintenance.

## Library Components

### mb25_string (.o/.lib)
- String allocation and garbage collection
- String operations (concat, substring, etc.)
- String/number conversion
- Already implemented in runtime/strings/mb25_string.c

### mb25_hw (.o/.lib)
- **PEEK/POKE** - Memory access
- **INP/OUT** - I/O port access
- **WAIT** - Wait for port condition
- Status: **IMPLEMENTED** in test_compile/mb25_hw.c

### mb25_math (.o/.lib)
- Math function wrappers (for consistent naming)
- Random number generation (RND, RANDOMIZE)
- Integer functions (INT, FIX, SGN, ABS)

### mb25_io (.o/.lib)
- File operations (OPEN, CLOSE, etc.)
- Sequential I/O (PRINT#, INPUT#)
- Random access (GET, PUT, FIELD)
- Binary packing (MKI$, CVI, etc.)

### mb25_screen (.o/.lib)
- CLS - Clear screen
- POS - Cursor position
- TAB, SPC - Formatting
- INKEY$ - Non-blocking input

### mb25_system (.o/.lib)
- Error handling support
- TIMER functions
- DATE$/TIME$ (if supported)
- FRE - Free memory

## Build Process

### 1. Compile to Object Files
```bash
z88dk.zcc +cpm -c mb25_string.c -o mb25_string.o
z88dk.zcc +cpm -c mb25_hw.c -o mb25_hw.o
z88dk.zcc +cpm -c mb25_math.c -o mb25_math.o
# etc...
```

### 2. Create Library Archive
```bash
# Create library from object files
z88dk.z88dk-z80asm -xmb25 mb25_string.o mb25_hw.o mb25_math.o ...

# This creates mb25.lib
```

### 3. Link Programs
```bash
# Compile and link against library
z88dk.zcc +cpm program.c -lmb25 -L/path/to/lib -o program
```

## Linker Considerations

### Single-Pass vs Multi-Pass
Based on testing, z88dk's z80asm appears to handle library dependencies correctly. However, for safety:

1. **Order object files by dependency**:
   - Base functions first (hw, math)
   - String functions (may use memory)
   - I/O functions (may use strings)
   - High-level functions last

2. **Avoid circular dependencies**:
   - Each module should be self-contained
   - Use forward declarations where needed

## Implementation Status

### ✓ Completed
- **mb25_hw** - Hardware access (PEEK, POKE, INP, OUT, WAIT)
- Library creation process tested and working

### 🔧 In Progress
- **mb25_string** - Needs minor fixes for z88dk compilation

### 📋 TODO
- **mb25_math** - Math function wrappers
- **mb25_io** - File I/O functions
- **mb25_screen** - Screen/console functions
- **mb25_system** - System functions

## Directory Structure

```
runtime/
├── mb25/
│   ├── mb25_hw.c      # Hardware access
│   ├── mb25_hw.h
│   ├── mb25_string.c  # String system (from runtime/strings/)
│   ├── mb25_string.h
│   ├── mb25_math.c    # Math functions
│   ├── mb25_math.h
│   ├── mb25_io.c      # File I/O
│   ├── mb25_io.h
│   ├── mb25_screen.c  # Screen functions
│   ├── mb25_screen.h
│   ├── mb25_system.c  # System functions
│   ├── mb25_system.h
│   ├── mb25.h         # Master include
│   ├── Makefile       # Build all modules
│   └── mb25.lib       # Combined library
```

## Compiler Integration

### Code Generation Changes

1. **Include master header**:
```c
#include "mb25.h"  // Instead of individual includes
```

2. **Link with library**:
```python
def get_compiler_command(self, source_file: str, output_file: str) -> List[str]:
    return ['/usr/bin/env', 'z88dk.zcc', '+cpm', source_file,
            '-lmb25', '-L/path/to/runtime/mb25',  # Link with mb25 library
            '-create-app', '-o', output_file]
```

3. **Generate hardware access calls**:
```python
# PEEK(addr)
return f'mb25_peek({addr})'

# POKE addr, value
return f'mb25_poke({addr}, {value});'

# INP(port)
return f'mb25_inp({port})'

# OUT port, value
return f'mb25_outp({port}, {value});'

# WAIT port, mask, expected
return f'mb25_wait({port}, {mask}, {expected});'
```

## Benefits

1. **Smaller executables** - Runtime not duplicated
2. **Faster compilation** - Library pre-compiled
3. **Easier maintenance** - Fix bugs in one place
4. **Modular design** - Use only what's needed
5. **Professional structure** - Like real C runtime libraries

## Testing

### Hardware Access Test
```basic
10 REM Test hardware functions
20 POKE &H8000, 42
30 A = PEEK(&H8000)
40 PRINT "PEEK(8000H) ="; A
50 OUT 0, &H55
60 B = INP(0)
70 PRINT "INP(0) ="; B
80 END
```

Should compile to:
```c
mb25_poke(0x8000, 42);
a = mb25_peek(0x8000);
printf("PEEK(8000H) = %d\n", a);
mb25_outp(0, 0x55);
b = mb25_inp(0);
printf("INP(0) = %d\n", b);
```

## Next Steps

1. **Move mb25_hw to runtime/mb25/** - Organize properly
2. **Fix mb25_string for z88dk** - Address compilation issues
3. **Create Makefile** - Automate library building
4. **Update compiler** - Use library instead of inline code
5. **Implement IF/THEN/ELSE** - Most critical missing statement