# SPACES

## Syntax

```basic
SPACE$(X)
```

**Versions:** Extended, Disk

## Description

Returns a string of spaces of length X.    The expression X is rounded to an integer and must be in the range 0 to 255.

## Example

```basic
10 FOR I = 1 TO 5
                20 X$ = SPACE$(I)
                30 PRINT X$;I
                40 NEXT I
                RUN
                     1
                         2
                             3
                                 4
                                     5
                Ok
                Also see the SPC function.
BASIC-80 FUNCTIONS                                   Page 3-20
```

## See Also

*Related functions will be linked here*
