---
category: string
description: Returns a numerical value that is the ASCII code of the first character
  of the string X$
keywords:
- asc
- error
- for
- function
- if
- illegal
- print
- return
- string
syntax: ASC (X$)
title: ASC
type: function
---

# ASC

## Syntax

```basic
ASC (X$)
```

## Description

Returns a numerical value that is the ASCII code of the first character of the string X$. (See Appendix M for ASCII codes.) If X$ is null, an "Illegal function call" error is returned.

## Example

```basic
10 X$ = "TEST"
 20 PRINT ASC (X$)
 RUN
 84
 Ok
 See the CHR$ function for ASCII-to-string
 conversion.
```

## See Also

*Related functions will be linked here*