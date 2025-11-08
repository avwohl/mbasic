---
category: system
description: Returns either a one-character string containing a character read from the terminal or a null string if no character is pending at the terminal
keywords: ['for', 'function', 'if', 'inkey', 'input', 'next', 'program', 'put', 'read', 'return']
syntax: INKEY$
title: INKEY$
type: function
---

# INKEY$

## Syntax

```basic
INKEY$
```

## Description

Returns either a one-character string containing a character read from the terminal or a null string if no character is pending at the terminal. No characters will be echoed and all characters are passed through to the program.

**Note**: Control-C behavior varied in original implementations. In MBASIC 5.21 interpreter mode, Control-C would terminate the program. This implementation passes Control-C through (CHR$(3)) for program detection and handling, allowing programs to detect and handle it explicitly.

## Example

```basic
1000 REM TIMED INPUT SUBROUTINE
1010 RESPONSE$=""
1020 FOR I%=1 TO TIMELIMIT%
1030 A$=INKEY$ : IF LEN(A$)=0 THEN 1060
1040 IF ASC(A$)=13 THEN TIMEOUT%=0 : RETURN
1050 RESPONSE$=RESPONSE$+A$
1060 NEXT I%
1070 TIMEOUT%=1 : RETURN
```

## See Also
- [FRE](fre.md) - Arguments to FRE are dummy arguments
- [HELP SET](../statements/helpsetting.md) - Display help for a specific setting
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
