---
category: string
description: Returns the number of characters in X$
keywords:
- function
- len
- number
- print
- return
syntax: LEN (X$)
title: LEN
type: function
---

# LEN

## Syntax

```basic
LEN (X$)
```

**Versions:** 8R, Extended, Disk

## Description

Returns the number of characters in X$. Non-printing characters and blanks are counted.

## Example

```basic
10 X$ = "PORTLAND, OREGON"
 20 PRINT LEN (X$)
 16
 Ok
```

## See Also

*Related functions will be linked here*