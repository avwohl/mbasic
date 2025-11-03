---
category: mathematical
description: Returns e to the power of X
keywords: ['error', 'exp', 'if', 'print', 'return']
syntax: EXP(X)
title: EXP
type: function
---

# EXP

## Syntax

```basic
EXP(X)
```

## Description

Returns e to the power of X. X must be <=87.3365. If EXP overflows, the "Overflow" error message is displayed, machine infinity with the appropriate sign is supplied as the result, and execution continues.

## Example

```basic
10 X = 5
20 PRINT EXP(X-1)
RUN
54.5982
Ok
```

## See Also
- [ABS](abs.md) - Return the absolute value of a number (removes negative sign)
- [ATN](atn.md) - Returns the arctangent of X in radians
- [COS](cos.md) - Returns the cosine of X in radians
- [FIX](fix.md) - Returns the truncated integer part of X
- [INT](int.md) - Return the largest integer less than or equal to a number (floor function)
- [LOG](log.md) - Returns the natural logarithm of X
- [RND](rnd.md) - Returns a random number between 0 and 1
- [SGN](sgn.md) - Returns the sign of X (-1, 0, or 1)
- [SIN](sin.md) - Returns the sine of X in radians
- [SQR](sqr.md) - Returns the square root of X
- [TAN](tan.md) - Returns the tangent of X in radians
