---
category: string
description: Searches for the first occurrence of string Y$ in X$ and returns the position at which the match is found
keywords: ['error', 'for', 'function', 'if', 'instr', 'line', 'number', 'print', 'return', 'string']
syntax: INSTR ( [I, ] X$, Y$)
title: INSTR
type: function
---

# INSTR

## Syntax

```basic
INSTR ( [I, ] X$, Y$)
```

**Versions:** Extended, Disk

## Description

Searches for the first occurrence of string Y$ in X$ and returns the position at which the match is found. Optional offset I sets the position for starting the search. I must be in the range 1 to 255. If I>LEN(X$) or if X$ is null or if Y$ cannot be found, INSTR returns O. If Y$ is null, INSTR returns I or 1. X$ and Y$ may be string variables, string expressions or string literals.

## Example

```basic
10 X$ = "ABCDEB"
20 Y$ = "B"
30 PRINT INSTR(X$, Y$); INSTR(4, X$, Y$)
RUN
2 6
Ok
```

**Note**: If I=0 is specified, an "Illegal function call" error will occur.

## See Also
- [ASC](asc.md) - Returns a numerical value that is the ASCII code of the first character of the string X$
- [CHR$](chr_dollar.md) - Returns a one-character string whose ASCII code is the specified value
- [HEX$](hex_dollar.md) - Returns a string which represents the hexadecimal value of the decimal argument
- [LEFT$](left_dollar.md) - Return the leftmost N characters from a string
- [LEN](len.md) - Returns the number of characters in X$
- [MID$](mid_dollar.md) - Extract a substring from the middle of a string
- [MID$ Assignment](../statements/mid-assignment.md) - Replace characters within a string variable
- [OCT$](oct_dollar.md) - Returns a string which represents the octal value of the decimal argument
- [RIGHT$](right_dollar.md) - Return the rightmost N characters from a string
- [SPACE$](space_dollar.md) - Returns a string of I spaces
- [SPC](spc.md) - Prints I blanks on the terminal
- [STR$](str_dollar.md) - Convert a number to its string representation
- [STRING$](string_dollar.md) - Returns a string of length I whose characters all have ASCII code J or the first character of X$
- [VAL](val.md) - Returns the numerical value of string X$
