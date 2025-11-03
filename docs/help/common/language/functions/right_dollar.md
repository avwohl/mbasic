---
category: string
description: Return the rightmost N characters from a string
keywords: ['right', 'substring', 'extract', 'string', 'rightmost', 'suffix', 'last']
syntax: RIGHT$(string, length)
related: ['left_dollar', 'mid_dollar', 'len']
title: RIGHT$
type: function
---

# RIGHT$

## Syntax

```basic
RIGHT$(X$,I)
```

## Description

Returns the rightmost I characters of string X$. If I=LEN(X$), returns X$. If I=0, the null string (length zero) is returned.

## Example

```basic
10 A$="DISK BASIC-80"
 20 PRINT RIGHT$(A$,8)
 RUN
 BASIC-80
 Ok
```

Also see the MID$ and LEFT$ functions.

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
- [SPACE$](space_dollar.md) - Returns a string of I spaces
- [SPC](spc.md) - Prints I blanks on the terminal
- [STR$](str_dollar.md) - Convert a number to its string representation
- [STRING$](string_dollar.md) - Returns a string of length I whose characters all have ASCII code J or the first character of X$
- [VAL](val.md) - Returns the numerical value of string X$
