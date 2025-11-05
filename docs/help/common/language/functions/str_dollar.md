---
category: string
description: Convert a number to its string representation
keywords: ['str', 'string', 'convert', 'number', 'format', 'text']
syntax: STR$(number)
related: ['val', 'print-using', 'left_dollar', 'right_dollar']
title: STR$
type: function
---

# STR$

## Syntax

```basic
STR$(X)
```

## Description

Returns a string representation of the value of X.

## Example

```basic
5 REM ARITHMETIC FOR KIDS
10 INPUT "TYPE A NUMBER"; N
20 ON LEN(STR$(N)) GOSUB 30, 100, 200, 300, 400, 500
30 PRINT "Single digit"
40 RETURN
100 PRINT "Two digits"
110 RETURN
' ... (additional subroutines at 200, 300, 400, 500)
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
- [STRING$](string_dollar.md) - Returns a string of length I whose characters all have ASCII code J or the first character of X$
- [VAL](val.md) - Returns the numerical value of string X$
