---
category: system
description: Returns the memory address of a variable
keywords:
- varptr
- variable
- pointer
- address
- memory
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

- [CALL](../statements/call.md) - Call machine language subroutine (not implemented)
- [USR](usr.md) - Call user machine code routine (not implemented)
- [PEEK](peek.md) - Read byte from memory (compatibility implementation)
- [POKE](../statements/poke.md) - Write byte to memory (not implemented)
