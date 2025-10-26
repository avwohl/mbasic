---
category: NEEDS_CATEGORIZATION
description: NEEDS_DESCRIPTION
keywords:
- NEEDS_KEYWORDS
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
 BASIC-80 COMMANDS AND STATEMENTS                        Page 2-16
 2.13   ~    USR
 Format:       DEF USR[<digit>]=<integer expression>
 Versions:     Extended, Disk
 Purpose:      To specify the starting address of   an    assembly
               language subroutine.
 Remarks:     <digit> may be any digit from 0 to 9. The digit
              corresponds to the number of the USR routine
              whose address is being specified. If <digit> is
              omitted, DEF USRO is assumed.       The value of
              <integer expression> is the starting address of
              the USR routine.      See Appendix C, Assembly_
              Language Subroutines.
              Any number of DEF USR statements may appear in a
              program    to   redefine   subroutine   starting
              addresses, thus allowing access to as many
              subroutines as necessary.
_ Example:         •
                   .
              200 DEFUSRO=24000
              210 X=USRO(y A 2/2.89)
                   ."
BASIC-80 COMMANDS AND STATEMENTS                         Page 2-17
```

## See Also

*Related statements will be linked here*