---
category: string
description: Returns a string of length I whose characters all have ASCII code J or the first character of X$
keywords: ['function', 'print', 'return', 'string']
title: STRING$
type: function
---

# STRING$

## Syntax

```basic
STRING$(I, J)
STRING$(I, X$)
```

**Versions:** Extended, Disk

## Description

Returns a string of length I whose characters all have ASCII code J or the first character of X$.

## Example

```basic
10 X$ = STRING$(10,45)
 20 PRINT X$ "MONTHLY REPORT" X$
 RUN
 ----------MONTHLY REPORT----------
 Ok
```

## See Also
- [ASC](asc.md) - Returns a numerical value that is the ASCII code of the first character of the string X$
- [CHR$](chr_dollar.md) - Returns a one-character string whose ASCII code is the specified value
- [HEX$](hex_dollar.md) - Returns a string which represents the hexadecimal value of the decimal argument
- [INSTR](instr.md) - Searches for the first occurrence of string Y$ in X$ and returns the position at which the match is found
- [LEFT$](left_dollar.md) - Return the leftmost N characters from a string
- [LEN](len.md) - Returns the number of characters in X$
- [MID$](mid_dollar.md) - Extract a substring from the middle of a string
- [MID$ Assignment](../statements/mid-assignment.md) - Replace characters within a string variable
- [OCT$](oct_dollar.md) - Returns a string which represents the octal value of the decimal argument
- [RIGHT$](right_dollar.md) - Return the rightmost N characters from a string
- [SPACE$](space_dollar.md) - Returns a string of I spaces
- [SPC](spc.md) - Prints I blanks on the terminal
- [STR$](str_dollar.md) - Convert a number to its string representation
- [VAL](val.md) - Returns the numerical value of string X$
