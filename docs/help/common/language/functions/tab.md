---
category: output-formatting
description: Spaces to position I on the terminal
keywords: ['data', 'function', 'if', 'line', 'next', 'print', 'read', 'statement', 'tab']
syntax: TAB (I)
title: TAB
type: function
---

# TAB

## Syntax

```basic
TAB (I)
```

## Description

Spaces to position I on the terminal. If the current print position is already beyond space I, TAB goes to that position on the next line. Space 1 is the leftmost position, and the rightmost position is the width minus one. I must be in the range 1 to 255. TAB may only be used in PRINT and LPRINT statements.

## Example

```basic
10 PRINT "NAME" TAB (25) "AMOUNT" : PRINT
 20 READ A$ ,B$
 30 PRINT A$ TAB (25) B$
 40 DATA "G. T. JONES","$25.00"
 RUN
 NAME AMOUNT
 G. T. JONES $25.00
 Ok
```

## See Also
- [CLOAD THIS COMMAND IS NOT INCLUDED IN THE DEC VT180 VERSION](../statements/cload.md) - To load a program or an array from cassette tape into memory
- [CDBL](cdbl.md) - Converts X to a double-precision floating-point number
- [CHR$](chr_dollar.md) - Returns a one-character string whose ASCII code is the specified value
- [CSAVE THIS COMMAND IS NOT INCLUDED IN THE DEC VT180 VERSION](../statements/csave.md) - To save the program or an       array   currently     in memory on cassette tape
- [CVI, CVS, CVD](cvi-cvs-cvd.md) - Convert string values to numeric values
- [DEFINT/SNG/DBL/STR](../statements/defint-sng-dbl-str.md) - To declare variable types as integer,        single precision, double precision, or string
- [ERR AND ERL VARIABLES](../statements/err-erl-variables.md) - Error code and error line number variables used in error handling
- [INPUT#](../statements/input_hash.md) - To read data items from a sequential disk    file and assign them to program variables
- [LINE INPUT](../statements/line-input.md) - To input an entire line (up to 254 characters) to   a string variable, without the use of delimiters
- [LPRINT AND LPRINT USING](../statements/lprint-lprint-using.md) - To print data at the line printer
- [MKI$, MKS$, MKD$](mki_dollar-mks_dollar-mkd_dollar.md) - Convert numeric values to string values
- [SPACE$](space_dollar.md) - Returns a string of spaces of length X
