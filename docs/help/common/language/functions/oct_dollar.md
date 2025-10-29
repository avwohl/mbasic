---
category: string
description: Returns a string which represents the octal value of the decimal argument
keywords:
- oct
- oct$
- octal
- convert
- function
- string
- number
syntax: "OCT$(X)"
related: [hex_dollar, str_dollar]
title: OCT$
type: function
---

# OCT$

## Syntax

```basic
OCT$(X)
```

**Versions:** Extended, Disk

## Description

Returns a string which represents the octal value of the decimal argument. X is rounded to an integer before OCT$(X) is evaluated.

The returned string contains only the digits 0-7, representing the octal (base-8) value of X.

## Example

```basic
10 INPUT X
20 A$ = OCT$(X)
30 PRINT X "DECIMAL IS " A$ " OCTAL"
RUN
? 64
64 DECIMAL IS 100 OCTAL
Ok

10 PRINT OCT$(255)
RUN
377
Ok
```

## See Also

- [HEX$](hex_dollar.md) - Convert to hexadecimal string
- [STR$](str_dollar.md) - Convert number to string
