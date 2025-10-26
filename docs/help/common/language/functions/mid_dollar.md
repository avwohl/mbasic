---
category: string
description: NEEDS_DESCRIPTION
keywords:
- NEEDS_KEYWORDS
title: MID$
type: function
---

# MID$

## Syntax

```basic
MID$ (X$, I [ ,J] )
```

## Description

Returns a string of length J characters from X$ beginning with the Ith character. I and J must be in the range 1 to 255. If J is omitted or if there are fewer than J characters to the right of the Ith character, all rightmost characters beginning with the Ith character are returned. If I>LEN(X$), MID$ returns a null string.

## Example

```basic
LIST
               10 A$=nGOOD n
               20 B$=nMORNING EVENING AFTERNOON"
               30 PRINT A$;MID$(B$,9,7)
               Ok
               RUN
               GOOD EVENING
               Ok
               Also see the LEFT$ and RIGHT$ functions.
NOTE:          If I=O is specified, error message "ILLEGAL
               ARGUMENT IN <line number>" will be returned.
```

## See Also

*Related functions will be linked here*