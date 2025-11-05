---
category: mathematical
description: Returns the tangent of X in radians
keywords: ['error', 'function', 'if', 'return', 'tan']
syntax: TAN (X)
title: TAN
type: function
---

# TAN

## Syntax

```basic
TAN (X)
```

## Description

Returns the tangent of X in radians. TAN (X) is calculated in single precision. If TAN overflows, the "Overflow" error message is displayed, machine infinity with the appropriate sign is supplied as the result, and execution continues.

## Example

```basic
10 Y = Q*TAN(X)/2
```

## See Also
- [ABS](abs.md) - Return the absolute value of a number (removes negative sign)
- [ATN](atn.md) - Returns the arctangent of X in radians
- [COS](cos.md) - Returns the cosine of X in radians
- [EXP](exp.md) - Returns e to the power of X
- [FIX](fix.md) - Returns the truncated integer part of X
- [INT](int.md) - Return the largest integer less than or equal to a number (floor function)
- [LOG](log.md) - Returns the natural logarithm of X
- [RND](rnd.md) - Returns a random number between 0 and 1
- [SGN](sgn.md) - Returns the sign of X (-1, 0, or 1)
- [SIN](sin.md) - Returns the sine of X in radians
- [SQR](sqr.md) - Returns the square root of X
