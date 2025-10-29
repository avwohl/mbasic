---
category: type-conversion
description: Converts X to a single-precision floating-point number
keywords:
- csng
- convert
- single
- precision
- float
- function
- number
syntax: CSNG(X)
related: [cint, cdbl, fix, int]
title: CSNG
type: function
---

# CSNG

## Syntax

```basic
CSNG(X)
```

**Versions:** Extended, Disk

## Description

Converts X to a single-precision floating-point number. Single-precision numbers have approximately 7 digits of precision and range from 2.938736 x 10^-39 to 1.701412 x 10^38.

If X is a double-precision number, CSNG rounds it to single precision. If X is an integer or string representation of a number, it is converted to single-precision format.

## Example

```basic
10 A# = 123.456789012345#
20 B! = CSNG(A#)
30 PRINT A#, B!
RUN
123.456789012345  123.4568
Ok
```

## Notes

- Single-precision numbers use ! as a type suffix
- Double-precision numbers use # as a type suffix
- Conversion may result in loss of precision if converting from double precision

## See Also

- [CINT](cint.md) - Convert to integer
- CDBL - Convert to double precision (not yet documented)
- [FIX](fix.md) - Truncate to integer
- [INT](int.md) - Round down to integer
