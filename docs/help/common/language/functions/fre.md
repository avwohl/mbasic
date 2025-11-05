---
category: system
description: Arguments to FRE are dummy arguments
keywords: ['for', 'fre', 'function', 'number', 'print', 'return']
syntax: FRE(0) FRE(X$)
title: FRE
type: function
---

# FRE

## Syntax

```basic
FRE(0)
FRE(X$)
```

## Description

Arguments to FRE are dummy arguments. FRE returns the number of bytes in memory not being used by BASIC-80. FRE("") forces a garbage collection before returning the number of free bytes. BE PATIENT: garbage collection may take 1 to 1-1/2 minutes. BASIC will not initiate garbage collection until all free memory has been used up. Therefore, using FRE("") periodically will result in shorter delays for each garbage collection.

## Example

```basic
PRINT FRE(0)
 14542
 Ok
```

## See Also
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
- [USR](usr.md) - Calls the user's assembly language subroutine with the argument X
- [VARPTR](varptr.md) - Returns the memory address of a variable
- [WIDTH](../statements/width.md) - To set the printed line width in number of characters for the terminal or line printer
