---
category: type-declaration
description: To declare variable types as integer, single precision, double precision, or string
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

To declare variable types as integer, single precision, double precision, or string.

## Remarks

A DEFtype statement declares that the variable names beginning with the letter(s) specified will be that type variable. However, a type declaration character always takes precedence over a DEFtype statement in the typing of a variable.

If no type declaration statements are encountered, BASIC-80 assumes all variables without declaration characters are single precision variables.

## Example

```basic
10 DEFDBL D-E
' All variables beginning with the letters D and E
' will be double precision variables.

20 DEFSTR A
' All variables beginning with the letter A will be string variables.

30 DEFINT I-N, W-Z
' All variables beginning with the letters I, J, K, L, M, N, W, X, Y, Z
' will be integer variables.

40 DATA# = 12.5     ' Double precision (starts with D)
50 AMOUNT$ = "100"  ' String (has $ suffix, overrides DEFSTR)
60 INDEX = 42       ' Integer (starts with I)
70 A1 = "TEST"      ' String (starts with A, DEFSTR applies)
```

**Note:** When ranges overlap, the last declaration takes precedence. For example, if you declare both `DEFDBL L-P` and `DEFINT I-N`, variables starting with L, M, and N would be affected by both declarations, with the later declaration taking effect.

## See Also
- [Data Types](../data-types.md) - Overview of BASIC data types
- [Variables](../variables.md) - Variable naming and usage
- [CINT](../functions/cint.md) - Convert to integer
- [CSNG](../functions/csng.md) - Convert to single precision
- [CDBL](../functions/cdbl.md) - Convert to double precision
- [STR$](../functions/str_dollar.md) - Convert number to string
- [VAL](../functions/val.md) - Convert string to number
