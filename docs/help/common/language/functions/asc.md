---
category: string
description: Returns a numerical value that is the ASCII code of the first character of the string X$
keywords: ['asc', 'error', 'for', 'function', 'if', 'illegal', 'print', 'return', 'string']
syntax: ASC (X$)
title: ASC
type: function
---

# ASC

## Syntax

```basic
ASC (X$)
```

## Description

Returns a numerical value that is the ASCII code of the first character of the string X$. (See [ASCII Codes](../appendices/ascii-codes.md) for a complete reference.) If X$ is null, an "Illegal function call" error is returned.

## Example

```basic
10 X$ = "TEST"
20 PRINT ASC(X$)
RUN
84
Ok
```

## See Also
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
- [VAL](val.md) - Returns the numerical value of string X$
