---
category: string
description: NEEDS_DESCRIPTION
keywords:
- NEEDS_KEYWORDS
title: ASC
type: function
---

# ASC

## Syntax

```basic
ASC (X$)
```

## Description

Returns a numerical value that is the ASCII code of the first character of the string X$.    (See Appendix M for ASCII codes.) If X$ is null, an "Illegal function call" error is returned.

## Example

```basic
10 X$ = "TEST"
            20 PRINT ASC (X$)
            RUN
             84
            Ok
            See the CHR$        function   for   ASClI-to-string
            conversion.
BASIC-SO FUNCTIONS                                      Page 3-3
```

## See Also

*Related functions will be linked here*