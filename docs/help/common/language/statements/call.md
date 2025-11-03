---
category: hardware
description: To call an assembly language subroutine
keywords: ['array', 'call', 'command', 'execute', 'for', 'function', 'program', 'statement', 'subroutine', 'variable']
syntax: CALL <variable name>[«argument list»]
title: CALL
type: statement
---

# CALL

## Implementation Note

⚠️ **Not Implemented**: This feature calls machine language (assembly) subroutines and is not implemented in this Python-based interpreter.

**Behavior**: Statement is parsed but no operation is performed

**Why**: Cannot execute machine code from a Python interpreter. CALL was used to invoke hand-written assembly language routines for performance-critical operations or hardware access.

**See Also**: [USR](../functions/usr.md) function (also not implemented)

**Historical Reference**: The documentation below is preserved from the original MBASIC 5.21 manual for historical reference.

---

## Syntax

```basic
CALL <variable name>[«argument list»]
```

## Purpose

To call an assembly language subroutine.

## Remarks

The CALL statement is one way to transfer program flow to an assembly language subroutine. (See also the USR function, Section 3.40) <variable name> contains an address that is the starting point in memory of the subroutine. <variable name> may not be an array variable name. <argument list> contains the arguments that are passed to the assembly language subroutine. <argument list> may not contain literals. The CALL statement generates the same calling sequence used by Microsoft's FORTRAN, COBOL and BASIC compilers.

## Example

```basic
110 MYROOT=&HD000
120 CALL MYROOT(I,J,K)
```

## See Also
- [OUT](out.md) - To send a byte to a machine output port
- [POKE](poke.md) - To write a byte into a memory location
- [WAIT](wait.md) - To suspend program execution while      monitoring the status of a machine input port
