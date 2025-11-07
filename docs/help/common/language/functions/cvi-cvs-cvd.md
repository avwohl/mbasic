---
category: type-conversion
description: Convert string values to numeric values
keywords: ['cvd', 'cvi', 'cvs', 'field', 'file', 'function', 'get', 'number', 'read', 'string']
syntax: CVI(2-byte string) CVS(4-byte string) CVD(8-byte string)
title: CVI, CVS, CVD
type: function
---

# CVI, CVS, CVD

## Syntax

```basic
CVI(2-byte string) CVS(4-byte string) CVD(8-byte string)
```

**Versions:** Disk

## Description

Convert string values to numeric values. Numeric values that are read in from a random disk file must be converted from strings back into numbers. CVI converts a 2-byte string to an integer. CVS converts a 4-byte string to a single precision number. CVD converts an 8-byte string to a double precision number.

**Error:** Raises "Illegal function call" (error code FC/5) if the string length is incorrect (not exactly 2, 4, or 8 bytes respectively). See [Error Codes](../appendices/error-codes.md) for details.

## Example

```basic
70 FIELD #1, 4 AS N$, 12 AS B$
80 GET #1
90 Y = CVS(N$)
```

## See Also
- [MKI$, MKS$, MKD$](mki_dollar-mks_dollar-mkd_dollar.md) - Convert numeric values to string values (inverse of CVI/CVS/CVD)
- [FIELD](../statements/field.md) - Define fields for random file access
- [GET](../statements/get.md) - Read record from random file
- [PUT](../statements/put.md) - Write record to random file
