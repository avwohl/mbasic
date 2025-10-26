---
category: string
description: Returns a string of length I whose characters all have ASCII code J or
  the first character of X$
keywords:
- function
- print
- return
- string
title: STRING$
type: function
---

# STRING$

**Versions:** Extended, Disk-

## Description

Returns a string of length I whose characters all have ASCII code J or the first character of X$.

## Example

```basic
10 X$ = STRING$(10,45)
 20 PRINT X$ "MONTHLY REPORT" X$
 RUN
 ----------MONTHLY REPORT----------
 Ok
```

## See Also

*Related functions will be linked here*