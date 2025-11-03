---
category: mathematical
description: Returns the truncated integer part of X
keywords: ['fix', 'for', 'function', 'if', 'next', 'number', 'print', 'return']
syntax: FIX(X)
title: FIX
type: function
---

# FIX

## Syntax

```basic
FIX(X)
```

**Versions:** Extended, Disk

## Description

Returns the truncated integer part of X. FIX(X) is equivalent to SGN(X)*INT(ABS(X)). The major difference between FIX and INT is that FIX does not return the next lower number for negative X.

## Example

```basic
PRINT FIX(58.75)
58
Ok
PRINT FIX(-58.75)
-58
Ok
```

## See Also
- [ABS](abs.md) - Return the absolute value of a number (removes negative sign)
- [ATN](atn.md) - Returns the arctangent of X in radians
- [COS](cos.md) - Returns the cosine of X in radians
- [EXP](exp.md) - Returns e to the power of X
- [INT](int.md) - Return the largest integer less than or equal to a number (floor function)
- [LOG](log.md) - Returns the natural logarithm of X
- [RND](rnd.md) - Returns a random number between 0 and 1
- [SGN](sgn.md) - Returns the sign of X (-1, 0, or 1)
- [SIN](sin.md) - Returns the sine of X in radians
- [SQR](sqr.md) - Returns the square root of X
- [TAN](tan.md) - Returns the tangent of X in radians
