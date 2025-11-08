---
category: mathematical
description: Returns the arctangent of X in radians
keywords: ['atn', 'for', 'function', 'input', 'print', 'put', 'return']
syntax: ATN(X)
title: ATN
type: function
---

# ATN

## Syntax

```basic
ATN(X)
```

**Versions:** 8K, Extended, Disk

## Description

Returns the arctangent of X in radians. Result is in the range -pi/2 to pi/2. The expression X may be any numeric type, but the evaluation of ATN is always performed in single precision (~7 significant digits).

**Note:** When computing PI with `ATN(1) * 4`, the result is limited to single precision (~7 digits). For higher precision, use `ATN(CDBL(1)) * 4` to get double precision.

## Example

```basic
10 INPUT X
 20 PRINT ATN (X)
 RUN
 ? 3
 1.24905
 Ok
```

## See Also
- [ABS](abs.md) - Return the absolute value of a number (removes negative sign)
- [COS](cos.md) - Returns the cosine of X in radians
- [EXP](exp.md) - Returns e to the power of X
- [FIX](fix.md) - Returns the truncated integer part of X
- [INT](int.md) - Return the largest integer less than or equal to a number (floor function)
- [LOG](log.md) - Returns the natural logarithm of X
- [RND](rnd.md) - Returns a random number between 0 and 1
- [SGN](sgn.md) - Returns the sign of X (-1, 0, or 1)
- [SIN](sin.md) - Returns the sine of X in radians
- [SQR](sqr.md) - Returns the square root of X
- [TAN](tan.md) - Returns the tangent of X in radians
