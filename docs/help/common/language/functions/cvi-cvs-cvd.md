---
category: type-conversion
description: Convert string values to numeric values
keywords: ['cvd', 'cvi', 'cvs', 'field', 'file', 'function', 'get', 'number', 'read', 'string']
syntax: CVI(2-byte string) CVS(4-byte string) CVD(8-byte string)
title: CVI, CVS, CVD
type: function
---

# CVI, CVS, CVD

## Syntax

```basic
CVI(2-byte string) CVS(4-byte string) CVD(8-byte string)
```

**Versions:** Disk

## Description

Convert string values to numeric values. Numeric values that are read in from a random disk file must be converted from strings back into numbers. CVI converts a 2-byte string to an integer. CVS converts a 4-byte string to a single precision number. CVD converts an 8-byte string to a double precision number.

## Example

```basic
70 FIELD #1,4 AS N$, 12 AS B$, •••
 80 GET #1
 90 Y=CVS (N$)
 See also MKI$r MKS$, MKD$, Section 3.25 and
 Appendix B.
```

## See Also
- [CLOAD THIS COMMAND IS NOT INCLUDED IN THE DEC VT180 VERSION](../statements/cload.md) - To load a program or an array from cassette tape into memory
- [CDBL](cdbl.md) - Converts X to a double-precision floating-point number
- [CHR$](chr_dollar.md) - Returns a one-character string whose ASCII code is the specified value
- [CSAVE THIS COMMAND IS NOT INCLUDED IN THE DEC VT180 VERSION](../statements/csave.md) - To save the program or an array currently in memory on cassette tape
- [DEFINT/SNG/DBL/STR](../statements/defint-sng-dbl-str.md) - To declare variable types as integer, single precision, double precision, or string
- [ERR AND ERL VARIABLES](../statements/err-erl-variables.md) - Error code and error line number variables used in error handling
- [INPUT#](../statements/input_hash.md) - To read data items from a sequential disk    file and assign them to program variables
- [LINE INPUT](../statements/line-input.md) - To input an entire line (up to 254 characters) to   a string variable, without the use of delimiters
- [LPRINT AND LPRINT USING](../statements/lprint-lprint-using.md) - To print data at the line printer
- [MKI$, MKS$, MKD$](mki_dollar-mks_dollar-mkd_dollar.md) - Convert numeric values to string values
- [SPACE$](space_dollar.md) - Returns a string of spaces of length X
- [TAB](tab.md) - Spaces to position I on the terminal
