---
category: mathematical
description: Returns a random number between 0 and 1
keywords: ['for', 'function', 'next', 'number', 'print', 'program', 'return', 'rnd']
syntax: RND [ (X) ]
title: RND
type: function
---

# RND

## Syntax

```basic
RND [ (X) ]
```

**Versions:** SK, Extended, Disk

## Description

Returns a random number between 0 and 1. The same sequence of random numbers is generated each time the program is RUN unless the random number generator is reseeded (see RANDOMIZE, Section 2.53). However, X<O always restarts the same sequence for any given X. X>O or X omitted generates the next random number in the sequence. x=o repeats the last number generated.

## Example

```basic
10 FOR I=l TO 5
 20 PRINT INT(RND*100);
 30 NEXT
 RUN
 24 30 31 51 5
 Ok
```

## See Also
- [ABS](abs.md) - Return the absolute value of a number (removes negative sign)
- [ATN](atn.md) - Returns the arctangent of X in radians
- [COS](cos.md) - Returns the cosine of X in radians
- [EXP](exp.md) - Returns e to the power of X
- [FIX](fix.md) - Returns the truncated integer part of X
- [INT](int.md) - Return the largest integer less than or equal to a number (floor function)
- [LOG](log.md) - Returns the natural logarithm of X
- [SGN](sgn.md) - Returns the sign of X (-1, 0, or 1)
- [SIN](sin.md) - Returns the sine of X in radians
- [SQR](sqr.md) - Returns the square root of X
- [TAN](tan.md) - Returns the tangent of X in radians
