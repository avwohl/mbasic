---
category: mathematical
description: Returns the cosine of X in radians
keywords:
- cos
- cosine
- trigonometry
- function
- radians
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

*Related functions will be linked here*