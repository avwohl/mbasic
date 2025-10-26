---
category: type-conversion
description: NEEDS_DESCRIPTION
keywords:
- NEEDS_KEYWORDS
title: CINT
type: function
---

# CINT

## Syntax

```basic
CINT(X)
```

**Versions:** Extended, Disk

## Description

Converts X to an integer by rounding         the fractional portion.    If X is not in the range -32768 to 32767, an "Overflow" error occurs.

## Example

```basic
PRINT CINT(45.67)
              46
             Ok
             See the CDBL and CSNG functions for converting
             numbers to the double precision and single
             precision data type. See also the FIX and INT
             functions, both of which return integers.
BASIC-SO FUNCTIONS                                      Page 3-5
```

## See Also

*Related functions will be linked here*