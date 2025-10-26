---
category: mathematical
description: NEEDS_DESCRIPTION
keywords:
- NEEDS_KEYWORDS
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

* [LOG](log.md) - Natural logarithm