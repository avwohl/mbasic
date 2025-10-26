---
category: NEEDS_CATEGORIZATION
description: Returns a string whose one element has ASCII code I
keywords:
- crr
- error
- for
- function
- print
- return
- string
syntax: CHR$(I)
title: CRR$
type: function
---

# CRR$

## Syntax

```basic
CHR$(I)
```

## Description

Returns a string whose one element has ASCII code I. (ASCII codes are listed in Appendix M.) CHR$ is commonly used to send a special character to the terminal. For instance, the BEL character could be sent (CHR$(7» as a preface to an error message, or a form feed could be sent (CRR$(12» to clear a CRT screen and return the cursor to the home position.

## Example

```basic
PRINT CHR$ (66)
 B
 Ok
 See the ASC function for ASCII-to-numeric
 conversion.
```

## See Also

*Related functions will be linked here*