---
category: string
description: Returns a string of I spaces
keywords:
- space
- space$
- spaces
- string
- function
- formatting
syntax: "SPACE$(I)"
related: [string_dollar, spc, tab]
title: SPACE$
type: function
---

# SPACE$

## Syntax

```basic
SPACE$(I)
```

**Versions:** Extended, Disk

## Description

Returns a string consisting of I spaces. This is equivalent to STRING$(I, 32) since 32 is the ASCII code for a space character.

SPACE$ is commonly used for formatting output or creating padding in strings.

## Example

```basic
10 A$ = "HELLO"
20 B$ = "WORLD"
30 PRINT A$ + SPACE$(5) + B$
RUN
HELLO     WORLD
Ok

10 PRINT "NAME:" + SPACE$(10) + "AGE:"
RUN
NAME:          AGE:
Ok
```

## Notes

- The argument I must be in the range 0-255
- SPACE$(0) returns an empty string
- For variable spacing in PRINT statements, see SPC() and TAB()

## See Also

- [STRING$](string_dollar.md) - Create string of repeated characters
- SPC - Print spaces (for use in PRINT statements)
- TAB - Move to column position (for use in PRINT statements)
