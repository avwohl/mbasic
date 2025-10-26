---
category: string
description: Searches for the first occurrence of string Y$ in X$ and returns the
  position at which the match is found
keywords:
- error
- for
- function
- if
- instr
- line
- number
- print
- return
- string
syntax: INSTR ( [I, ] X$, Y$)
title: INSTR
type: function
---

# INSTR

## Syntax

```basic
INSTR ( [I, ] X$, Y$)
```

**Versions:** Extended, Disk

## Description

Searches for the first occurrence of string Y$ in X$ and returns the position at which the match is found. Optional offset I sets the position for starting the search. I must be in the range 1 to 255. If I>LEN(X$) or if X$ is null or if Y$ cannot be found, INSTR returns O. If Y$ is null, INSTR returns I or 1. X$ and Y$ may be string variables, string expressions or string literals.

## Example

```basic
10 X$ = "ABCDEB"
 20 Y$ = "B"
 30 PRINT INSTR(X$,Y$) ;INSTR(4,X$,Y$)
 RUN
 2 6
 Ok
NOTE: If I=O is specified, error message "ILLEGAL
 ARGUMENT IN <line number>" will be returned.
```

## See Also

*Related functions will be linked here*