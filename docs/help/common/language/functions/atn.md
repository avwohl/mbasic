---
category: mathematical
description: NEEDS_DESCRIPTION
keywords:
- NEEDS_KEYWORDS
title: ATN
type: function
---

# ATN

## Syntax

```basic
ATN(X)
```

**Versions:** SK, Extended, Disk

## Description

Returns the arctangent of X in radians.   Result is in the range -pi/2 to pi/2. The expression X may be any numeric type, but the evaluation of ATN is always performed in single precision.

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

*Related functions will be linked here*