---
category: system
description: Returns the memory address of a variable
keywords: ['varptr', 'variable', 'pointer', 'address', 'memory']
syntax: VARPTR(variable)
title: VARPTR
type: function
---

# VARPTR

## Implementation Note

⚠️ **Not Implemented**: This feature requires direct memory access and is not implemented in this Python-based interpreter.

**Behavior**: Function is not available

**Why**: In the original MBASIC, VARPTR returned a pointer to the variable's memory address. Python uses managed memory with garbage collection, so variables don't have fixed memory addresses.

**Historical Context**: VARPTR was used to pass variable addresses to assembly language subroutines via CALL or USR functions, which are also not implemented.

**Historical Reference**: The documentation below is preserved from the original MBASIC 5.21 manual for historical reference.

---

## Syntax

```basic
VARPTR(variable)
```

## Description

Returns the memory address of the first byte of data for the specified variable.

In original MBASIC 5.21:
- For simple variables: Returns the address where the value is stored
- For arrays: Returns the address of the first element
- For strings: Returns the address of the string descriptor

The address returned is an integer in the range -32768 to 32767. If negative, add 65536 to get the actual address.

## Historical Uses

### Passing Arrays to Machine Code
```basic
100 DIM A(100)
110 ADDR = VARPTR(A(0))
120 CALL ADDR
```

### Accessing String Data
```basic
100 A$ = "HELLO"
110 PTR = VARPTR(A$)
```

## See Also
- [FRE](fre.md) - Arguments to FRE are dummy arguments
- [HELP SET](../statements/helpsetting.md) - Display help for a specific setting
- [INKEY$](inkey_dollar.md) - Returns either a one-character string containing a character read from the terminal or a null string if no character is pending at the terminal
- [INP](inp.md) - Returns the byte read from port I
- [LIMITS](../statements/limits.md) - Display resource usage and interpreter limits
- [NULL](../statements/null.md) - To set the number of nulls to be printed at   the end of each line
- [PEEK](peek.md) - Returns the byte (decimal integer in the range 0 to 255) read from memory location I
- [RANDOMIZE](../statements/randomize.md) - To reseed the random number generator
- [REM](../statements/rem.md) - To allow explanatory remarks to be inserted in a program
- [SET (setting)](../statements/setsetting.md) - Configure interpreter settings at runtime
- [SHOW SETTINGS](../statements/showsettings.md) - Display current interpreter settings
- [TRON/TROFF](../statements/tron-troff.md) - To trace the execution of program statements
- [USR](usr.md) - Calls the user's assembly language subroutine with the argument X
- [WIDTH](../statements/width.md) - To set the printed line width in number        of characters for the terminal or line printer
