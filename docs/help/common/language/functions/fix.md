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

## Examples

**Basic truncation:**
```basic
PRINT FIX(58.75)
58
Ok
PRINT FIX(-58.75)
-58
Ok
```

**Using FIX for array indexing with floating-point calculations:**
```basic
10 DIM VALUES(10)
20 FOR I = 1 TO 10: VALUES(I) = I * 10: NEXT I
30 X = 3.7
40 INDEX = FIX(X)    ' Truncate to 3, not 4
50 PRINT "VALUE AT INDEX"; INDEX; "IS"; VALUES(INDEX)
VALUE AT INDEX 3 IS 30
Ok
```

Note: FIX is useful for converting floating-point results to array indices, ensuring truncation toward zero rather than rounding down (which INT does for negative numbers).

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
