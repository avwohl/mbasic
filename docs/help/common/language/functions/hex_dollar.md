# HEX$

## Syntax

```basic
HEX$ (X) Versionsr     Extended, Disk
```

## Description

Returns    a  string   which   represents   the hexadecimal value of the decimal argument. X is rounded to an integer      before   HEX$(X)  is evaluated.

## Example

```basic
10 INPUT X
              20 A$ = HEX$ (X)
              30 PRINT X "DECIMAL IS II A$ " HEXADECIMAL II
              RUN
              ? 32
               32 DECIMAL IS 20 HEXADECIMAL
              Ok
              See the OCT$ function for octal conversion.
BASIC-80 FUNCTIONS                                      Page 3-9
```

## See Also

*Related functions will be linked here*
