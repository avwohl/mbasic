---
category: string
description: Returns the numerical value of string X$
keywords: ['for', 'function', 'if', 'line', 'print', 'read', 'return', 'string', 'then', 'val']
syntax: VAL (X$)
title: VAL
type: function
---

# VAL

## Syntax

```basic
VAL (X$)
```

## Description

Returns the numerical value of string X$. The VAL function also strips leading blanks, tabs, and linefeeds from the argument string. For example, VAL (" -3") returns -3.

## Example

```basic
10 READ NAME$, CITY$, STATE$, ZIP$
20 IF VAL(ZIP$) < 90000 OR VAL(ZIP$) > 96699 THEN PRINT NAME$; TAB(25); "OUT OF STATE"
30 IF VAL(ZIP$) >= 90801 AND VAL(ZIP$) <= 90815 THEN PRINT NAME$; TAB(25); "LONG BEACH"
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
- [STRING$](string_dollar.md) - Returns a string of length I whose characters all have ASCII code J or the first character of X$
