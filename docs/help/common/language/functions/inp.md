---
category: system
description: Returns the byte read from port I
keywords: ['complementary', 'for', 'function', 'if', 'inp', 'out', 'read', 'return', 'statement']
syntax: INP (I)
title: INP
type: function
---

# INP

## Implementation Note

⚠️ **Not Implemented**: This feature requires direct hardware I/O port access and is not implemented in this Python-based interpreter.

**Behavior**: Always returns 0

**Why**: Cannot access hardware I/O ports from a Python interpreter. This function is specific to systems with memory-mapped I/O or port-based hardware interfaces.

**Historical Reference**: The documentation below is preserved from the original MBASIC 5.21 manual for historical reference.

---

## Syntax

```basic
INP (I)
```

## Description

Returns the byte read from port I. I must be in the range 0 to 255. INP is the complementary function to the [OUT](../statements/out.md) statement.

## Example

```basic
100 A=INP(255)
```

## See Also
- [FRE](fre.md) - Arguments to FRE are dummy arguments
- [HELP SET](../statements/helpsetting.md) - Display help for a specific setting
- [INKEY$](inkey_dollar.md) - Returns either a one-character string containing a character read from the terminal or a null string if no character is pending at the terminal
- [LIMITS](../statements/limits.md) - Display resource usage and interpreter limits
- [NULL](../statements/null.md) - To set the number of nulls to be printed at the end of each line
- [PEEK](peek.md) - Returns the byte (decimal integer in the range 0 to 255) read from memory location I
- [RANDOMIZE](../statements/randomize.md) - To reseed the random number generator
- [REM](../statements/rem.md) - To allow explanatory remarks to be inserted in a program
- [SET (setting)](../statements/setsetting.md) - Configure interpreter settings at runtime
- [SHOW SETTINGS](../statements/showsettings.md) - Display current interpreter settings
- [TRON/TROFF](../statements/tron-troff.md) - To trace the execution of program statements
- [USR](usr.md) - Calls the user's assembly language subroutine with the argument X
- [VARPTR](varptr.md) - Returns the memory address of a variable
- [WIDTH](../statements/width.md) - To set the printed line width in number of characters for the terminal or line printer
