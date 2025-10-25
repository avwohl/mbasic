# TAB

## Syntax

```basic
TAB (I)
```

## Description

Spaces to position I on the terminal.   If the current print position is already beyond space I, TAB goes to that position on the next line. Space 1 is the leftmost position, and the rightmost position is the width minus one.   I must be in the range 1 to 255. TAB may only be used in PRINT and LPRINT statements.

## Example

```basic
10 PRINT "NAME" TAB (25) "AMOUNT" : PRINT
             20 READ A$ ,B$
             30 PRINT A$ TAB (25) B$
             40 DATA "G. T. JONES","$25.00"
             RUN
             NAME                     AMOUNT
             G. T. JONES             $25.00
             Ok
```

## See Also

*Related functions will be linked here*
