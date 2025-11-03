---
category: type-declaration
description: To declare variable types as integer,        single precision, double precision, or string
keywords: ['command', 'dbl', 'defint', 'for', 'if', 'number', 'program', 'sng', 'statement', 'str']
syntax: DEF<type> <range(s) of letters>
title: DEFINT/SNG/DBL/STR
type: statement
---

# DEFINT/SNG/DBL/STR

## Syntax

```basic
DEF<type> <range(s) of letters>
where <type> is INT, SNG, DBL, or STR
```

## Purpose

To declare variable types as integer,        single precision, double precision, or string.

## Remarks

A DEFtype statement declares that the variable names beginning with the 1etter(s) specified will be that type variable.    However, a type declaration character always takes precedence over a DEFtype statement in the typing of a variable. If   no   type   declaration   statements    are encountered,   BASIC-SO assumes all variables without declaration    characters   are   single precision variables.

## Example

```basic
10 DEFDBL L-P    All variables beginning with
                              the letters L, M, N, 0, and P
                              will be double precision
                              variables.
             10 DEFSTR A      All variables beginning with
                              the letter A will be string
                              variables.
             10 DEFINT I-N,W-Z
                            All variable beginning with
                            the letters I, J, K, L, M,
                            N, W, X, Y, Z will be integer
                            variables.
```

## See Also
- [CLOAD THIS COMMAND IS NOT INCLUDED IN THE DEC VT180 VERSION](cload.md) - To load a program or an array from cassette tape into memory
- [CDBL](../functions/cdbl.md) - Converts X to a double-precision floating-point number
- [CHR$](../functions/chr_dollar.md) - Returns a one-character string whose ASCII code is the specified value
- [CSAVE THIS COMMAND IS NOT INCLUDED IN THE DEC VT180 VERSION](csave.md) - To save the program or an       array   currently     in memory on cassette tape
- [CVI, CVS, CVD](../functions/cvi-cvs-cvd.md) - Convert string values to numeric values
- [ERR AND ERL VARIABLES](err-erl-variables.md) - Error code and error line number variables used in error handling
- [INPUT#](input_hash.md) - To read data items from a sequential disk    file and assign them to program variables
- [LINE INPUT](line-input.md) - To input an entire line (up to 254 characters) to   a string variable, without the use of delimiters
- [LPRINT AND LPRINT USING](lprint-lprint-using.md) - To print data at the line printer
- [MKI$, MKS$, MKD$](../functions/mki_dollar-mks_dollar-mkd_dollar.md) - Convert numeric values to string values
- [SPACE$](../functions/space_dollar.md) - Returns a string of spaces of length X
- [TAB](../functions/tab.md) - Spaces to position I on the terminal
