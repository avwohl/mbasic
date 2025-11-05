---
category: mathematical
description: Returns the sign of X (-1, 0, or 1)
keywords: ['branch', 'function', 'goto', 'if', 'return', 'sgn']
syntax: SGN(X)
title: SGN
type: function
---

# SGN

## Syntax

```basic
SGN(X)
```

**Versions:** 8K, Extended, Disk

## Description

Returns the sign of a number. If X>0, SGN(X) returns 1. If X=0, SGN(X) returns 0. If X<0, SGN(X) returns -1.

## Example

```basic
ON SGN(X) + 2 GOTO 100, 200, 300
```

This branches to:
- Line 100 if X is negative (SGN returns -1, so -1+2=1, first GOTO target)
- Line 200 if X is 0 (SGN returns 0, so 0+2=2, second GOTO target)
- Line 300 if X is positive (SGN returns 1, so 1+2=3, third GOTO target)

## See Also
- [ABS](abs.md) - Return the absolute value of a number (removes negative sign)
- [ATN](atn.md) - Returns the arctangent of X in radians
- [COS](cos.md) - Returns the cosine of X in radians
- [EXP](exp.md) - Returns e to the power of X
- [FIX](fix.md) - Returns the truncated integer part of X
- [INT](int.md) - Return the largest integer less than or equal to a number (floor function)
- [LOG](log.md) - Returns the natural logarithm of X
- [RND](rnd.md) - Returns a random number between 0 and 1
- [SIN](sin.md) - Returns the sine of X in radians
- [SQR](sqr.md) - Returns the square root of X
- [TAN](tan.md) - Returns the tangent of X in radians
