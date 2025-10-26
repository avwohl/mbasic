---
category: string
description: Return the leftmost N characters from a string
keywords:
- left
- substring
- extract
- string
- leftmost
- prefix
- first
syntax: "LEFT$(string, length)"
related: [right_dollar, mid_dollar, len]
title: LEFT$
type: function
---

# LEFT$

## Syntax

```basic
LEFT$ (X$, I)
```

## Description

Returns a string comprised of the leftmost I characters of X$. I must be in the range 0 to 255. If I is greater than LEN (X$), the. entire string (X$) will be returned. If I=O, the null string (length zero) is returned.

## Example

```basic
10 A$ = "BASIC-80"
 20 B$ = LEFT$(A$,5}
 30 PRINT B$
 BASIC
 Ok
 Also see the MID$ and RIGHT$ functions.
```

## See Also

*Related functions will be linked here*