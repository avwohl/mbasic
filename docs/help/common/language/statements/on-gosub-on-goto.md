---
category: control-flow
description: NEEDS_DESCRIPTION
keywords:
- NEEDS_KEYWORDS
title: ON ••• GOSUB AND ON ••• GOTO
type: statement
---

# ON ••• GOSUB AND ON ••• GOTO

## Syntax

```basic
ON <expression> GOTO <list of line numbers>
ON <expression> GOSUB <list of line numbers>
```

**Versions:** SK, Extended, Disk

## Purpose

To branch to one of several specified line numbers, depending on the value returned when an expression is evaluated.

## Remarks

The value of <expression> determines which line number in the list will be used for branching. For example, if the value is three, the third line number in the list will be the destination of the branch.  (If the value is a non-integer, the fractional portion is rounded.) In the ON ••• GOSUB statement, each line number in the list must be the first line number of a subroutine. If the value of <expression> is zero or greater than the number of items in the list (but less than or equal to 255), BASIC continues with the next executable statement.     If the value of <expression> is negative or greater than 255, an "Illegal function call" error occurs.

## Example

```basic
100 ON L-1 GOTO 150,300,320,390
BASIC-80 COMMANDS AND STATEMENTS                        Page 2-56
```

## See Also

*Related statements will be linked here*