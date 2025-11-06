---
category: system
description: Calls the user's assembly language subroutine with the argument X
keywords: ['execute', 'for', 'function', 'if', 'return', 'statement', 'subroutine', 'usr']
title: USR
type: function
---

# USR

## Implementation Note

⚠️ **Not Implemented**: This feature calls machine language (assembly) routines and is not implemented in this Python-based interpreter.

**Behavior**: Always returns 0

**Why**: Cannot execute machine code from a Python interpreter. USR was designed to call hand-written assembly language subroutines for performance-critical operations or hardware access.

**Historical Reference**: The documentation below is preserved from the original MBASIC 5.21 manual for historical reference.

---

## Description

Calls the user's assembly language subroutine with the argument X. <digit> is allowed in the Extended and Disk versions only. <digit> is in the range 0 to 9 and corresponds to the digit supplied with the DEF USR statement for that routine. If <digit> is omitted, USR0 is assumed.

## Example

```basic
40 B = T*SIN (Y)
 50 C = USR (B/2)
 60 D = USR(B/3)
```

## See Also
- [FRE](fre.md) - Arguments to FRE are dummy arguments
- [HELP SET](../statements/helpsetting.md) - Display help for a specific setting
- [INKEY$](inkey_dollar.md) - Returns either a one-character string containing a character read from the terminal or a null string if no character is pending at the terminal
- [INP](inp.md) - Returns the byte read from port I
- [LIMITS](../statements/limits.md) - Display resource usage and interpreter limits
- [NULL](../statements/null.md) - To set the number of nulls to be printed at the end of each line
- [PEEK](peek.md) - Returns the byte (decimal integer in the range 0 to 255) read from memory location I
- [RANDOMIZE](../statements/randomize.md) - To reseed the random number generator
- [REM](../statements/rem.md) - To allow explanatory remarks to be inserted in a program
- [SET (setting)](../statements/setsetting.md) - Configure interpreter settings at runtime
- [SHOW SETTINGS](../statements/showsettings.md) - Display current interpreter settings
- [TRON/TROFF](../statements/tron-troff.md) - To trace the execution of program statements
- [VARPTR](varptr.md) - Returns the memory address of a variable
- [WIDTH](../statements/width.md) - To set the printed line width in number of characters for the terminal or line printer
