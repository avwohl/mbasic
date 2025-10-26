---
category: arrays
description: NEEDS_DESCRIPTION
keywords:
- NEEDS_KEYWORDS
title: DIM
type: statement
---

# DIM

## Syntax

```basic
DIM <list of subscripted variables>
```

## Purpose

To specify the maximum values for array variable subscripts and allocate storage accordingly.

## Remarks

If an array variable name is used without a DIM statement, the maximum value of its subscript(s) is assumed to be 10. If a subscript is used that is greater than the maximum specified, ,a "Subscript out of range" error occurs.       The minimum value for a subscript is always 0, unless otherwise specified with the OPTION BASE statement (see Section 2.46). The DIM statement sets all the elements of the specified arrays to an initial value of zero.

## Example

```basic
10 DIM A(20)
             20 FOR 1=0 TO 20
             30 READ A(I)
             40 NEXT I
                 •
BASIC-SO COMMANDS AND STATEMENTS                      Page 2-19
```

## See Also

*Related statements will be linked here*