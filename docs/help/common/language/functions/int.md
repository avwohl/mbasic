---
category: mathematical
description: Return the largest integer less than or equal to a number (floor function)
keywords: ['int', 'integer', 'floor', 'truncate', 'round', 'convert']
syntax: INT(number)
related: ['fix', 'cint', 'csng', 'cdbl']
title: INT
type: function
---

# INT

## Syntax

```basic
INT(X)
```

**Versions:** 8K, Extended, Disk

## Description

Returns the largest integer less than or equal to X.

## Examples

```basic
PRINT INT(99.89)
 99
Ok

PRINT INT(-12.11)
 -13
Ok
```

## See Also
- [ABS](abs.md) - Return the absolute value of a number (removes negative sign)
- [ATN](atn.md) - Returns the arctangent of X in radians
- [CDBL](cdbl.md) - Converts X to a double-precision floating-point number
- [CINT](cint.md) - Converts X to an integer by rounding the fractional portion
- [COS](cos.md) - Returns the cosine of X in radians
- [CSNG](csng.md) - Converts X to a single-precision floating-point number
- [EXP](exp.md) - Returns e to the power of X
- [FIX](fix.md) - Returns the truncated integer part of X
- [LOG](log.md) - Returns the natural logarithm of X
- [RND](rnd.md) - Returns a random number between 0 and 1
- [SGN](sgn.md) - Returns the sign of X (-1, 0, or 1)
- [SIN](sin.md) - Returns the sine of X in radians
- [SQR](sqr.md) - Returns the square root of X
- [TAN](tan.md) - Returns the tangent of X in radians
