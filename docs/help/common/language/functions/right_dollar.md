---
category: string
description: Return the rightmost N characters from a string
keywords:
- right
- substring
- extract
- string
- rightmost
- suffix
- last
syntax: "RIGHT$(string, length)"
related: [left_dollar, mid_dollar, len]
title: RIGHT$
type: function
---

# RIGHT$

## Syntax

```basic
RIGHT$(X$,I)
```

## Description

Returns the rightmost I characters of string X$. If I=LEN{X$), returns X$.      If I=O, the null string (length zero) is returned.

## Example

```basic
10 A$="DISK BASIC-80"
                20 PRINT RIGHT$(A$,8)
                RUN
                BASIC-80
                Ok
                Also see the MID$ and LEFT$ functions.
BASIC-SO FUNCTIONS                                  Page 3-1S
```

## See Also

*Related functions will be linked here*