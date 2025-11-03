---
category: mathematical
description: Returns the cosine of X in radians
keywords: ['cos', 'cosine', 'trigonometry', 'function', 'radians']
syntax: COS (X)
title: COS
type: function
---

# COS

## Syntax

```basic
COS (X)
```

**Versions:** SK, Extended, Disk Extended, Disk

## Description

Returns the cosine of X in radians. The angle X must be specified in radians, not degrees.

The calculation of COS(X) is performed in single precision.

## Example

```basic
10 X = 2 * COS(.4)
20 PRINT X
RUN
1.84212
Ok
```

To convert degrees to radians, multiply by π/180 (approximately 0.0174533):

```basic
10 PI = 3.141592653589793#
20 DEG = 45
30 RAD = DEG * PI / 180
40 PRINT "COS("; DEG; " degrees) ="; COS(RAD)
RUN
COS( 45  degrees) = 0.707107
Ok
```

## See Also
- [ABS](abs.md) - Return the absolute value of a number (removes negative sign)
- [ATN](atn.md) - Returns the arctangent of X in radians
- [EXP](exp.md) - Returns e to the power of X
- [FIX](fix.md) - Returns the truncated integer part of X
- [INT](int.md) - Return the largest integer less than or equal to a number (floor function)
- [LOG](log.md) - Returns the natural logarithm of X
- [RND](rnd.md) - Returns a random number between 0 and 1
- [SGN](sgn.md) - Returns the sign of X (-1, 0, or 1)
- [SIN](sin.md) - Returns the sine of X in radians
- [SQR](sqr.md) - Returns the square root of X
- [TAN](tan.md) - Returns the tangent of X in radians
