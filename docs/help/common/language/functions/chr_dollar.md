---
category: string
description: Returns a one-character string whose ASCII code is the specified value
keywords:
- chr
- chr$
- ascii
- character
- string
- convert
- function
syntax: "CHR$(I)"
related: [asc, str_dollar]
title: CHR$
type: function
---

# CHR$

## Syntax

```basic
CHR$(I)
```

## Description

Returns a one-character string whose character has the ASCII code I. This function is commonly used to send special characters or control codes to the screen or printer.

The argument I must be in the range 0-255. Values outside this range will produce an "Illegal function call" error.

## Example

```basic
10 PRINT CHR$(65)
RUN
A
Ok

10 PRINT CHR$(7)    ' Ring the bell
20 PRINT CHR$(13)   ' Carriage return
30 PRINT CHR$(10)   ' Line feed
```

## See Also

- ASC - Convert character to ASCII code (inverse function)
- STR$ - Convert number to string
