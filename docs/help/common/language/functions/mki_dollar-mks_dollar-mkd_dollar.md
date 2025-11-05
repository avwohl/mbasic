---
category: type-conversion
description: Convert numeric values to string values
keywords: ['complementary', 'field', 'file', 'for', 'function', 'mkd', 'mki', 'mks', 'number', 'poke']
syntax: MKI$(integer_expression) MKS$(single_precision_expression) MKD$(double_precision_expression)
title: MKI$, MKS$, MKD$
type: function
---

# MKI$, MKS$, MKD$

## Syntax

```basic
MKI$(integer_expression)
MKS$(single_precision_expression)
MKD$(double_precision_expression)
```

**Versions:** Disk

## Description

Convert numeric values to string values. Any numeric value that is placed in a random file buffer with an LSET or RSET statement must be converted to a string. MKI$ converts an integer to a 2-byte string. MKS$ converts a single precision number to a 4-byte string. MKD$ converts a double precision number to an 8-byte string.

## Example

```basic
90 AMT = (K + T)
100 FIELD #1, 8 AS D$, 20 AS N$
110 LSET D$ = MKS$(AMT)
120 LSET N$ = A$
130 PUT #1
```

## See Also
- [CLOAD THIS COMMAND IS NOT INCLUDED IN THE DEC VT180 VERSION](../statements/cload.md) - To load a program or an array from cassette tape into memory
- [CDBL](cdbl.md) - Converts X to a double-precision floating-point number
- [CHR$](chr_dollar.md) - Returns a one-character string whose ASCII code is the specified value
- [CSAVE THIS COMMAND IS NOT INCLUDED IN THE DEC VT180 VERSION](../statements/csave.md) - To save the program or an array currently in memory on cassette tape
- [CVI, CVS, CVD](cvi-cvs-cvd.md) - Convert string values to numeric values
- [DEFINT/SNG/DBL/STR](../statements/defint-sng-dbl-str.md) - To declare variable types as integer, single precision, double precision, or string
- [ERR AND ERL VARIABLES](../statements/err-erl-variables.md) - Error code and error line number variables used in error handling
- [INPUT#](../statements/input_hash.md) - To read data items from a sequential disk    file and assign them to program variables
- [LINE INPUT](../statements/line-input.md) - To input an entire line (up to 254 characters) to   a string variable, without the use of delimiters
- [LPRINT AND LPRINT USING](../statements/lprint-lprint-using.md) - To print data at the line printer
- [SPACE$](space_dollar.md) - Returns a string of spaces of length X
- [TAB](tab.md) - Spaces to position I on the terminal
