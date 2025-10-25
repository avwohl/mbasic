# ERASE

## Syntax

```basic
.       ERASE <list of array variables>
```

## Purpose

To eliminate arrays from a program.

## Remarks

Arrays may be redimensioned after they are ERASEd, or the previously allocated array space in memory may be used for other purposes. If an attempt is made to redimension an array without first ERASEing it, a "Redimensioned array" error occurs. NOTE:           The Microsoft BASIC compiler   does   not    support ERASE.

## Example

```basic
450 ERASE A,B
                460 DIM B(99)
                 •
                 •
BASIC-80 COMMANDS AND STATEMENTS                    Page 2-25
```

## See Also

*Related statements will be linked here*
