---
category: type-conversion
description: Converts X to a double-precision floating-point number
keywords:
- cdbl
- convert
- double
- precision
- float
- function
- number
syntax: CDBL(X)
related: [cint, csng, fix, int]
title: CDBL
type: function
---

# CDBL

## Syntax

```basic
CDBL(X)
```

**Versions:** Extended, Disk

## Description

Converts X to a double-precision floating-point number. Double-precision numbers have approximately 16 digits of precision and range from 2.938735877055719 x 10^-39 to 1.701411834604692 x 10^38.

If X is a single-precision number or integer, it is converted to double-precision format. If X is a string representation of a number, it is converted to double-precision format.

## Example

```basic
10 A! = 123.456!
20 B# = CDBL(A!)
30 PRINT A!, B#
RUN
123.456  123.456
Ok

10 PRINT CDBL(5)
RUN
5
Ok
```

## Notes

- Single-precision numbers use ! as a type suffix
- Double-precision numbers use # as a type suffix
- Converting from single to double precision preserves all available precision

## See Also

- [CINT](cint.md) - Convert to integer
- [CSNG](csng.md) - Convert to single precision
- [FIX](fix.md) - Truncate to integer
- [INT](int.md) - Round down to integer
