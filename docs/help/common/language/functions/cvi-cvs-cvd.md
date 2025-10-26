---
category: NEEDS_CATEGORIZATION
description: Convert string values to numeric values
keywords:
- cvd
- cvi
- cvs
- field
- file
- function
- get
- number
- read
- string
syntax: CVI«2-byte string» CVS«4-byte string» CVD«8-byte string»
title: CVI, CVS, CVD
type: function
---

# CVI, CVS, CVD

## Syntax

```basic
CVI«2-byte string» CVS«4-byte string» CVD«8-byte string»
```

**Versions:** Disk

## Description

Convert string values to numeric values. Numeric values that are read in from a random disk file must be converted from strings back into numbers. CVI converts a 2-byte string to an integer. CVS converts a 4-byte string to a single precision number. CVD converts an 8-byte string to a double precision number.

## Example

```basic
70 FIELD #1,4 AS N$, 12 AS B$, •••
 80 GET #1
 90 Y=CVS (N$)
 See also MKI$r MKS$, MKD$, Section 3.25 and
 Appendix B.
```

## See Also

*Related functions will be linked here*