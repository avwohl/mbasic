---
category: variables
description: To exchange the values of two variables
keywords: ['command', 'error', 'for', 'print', 'statement', 'string', 'swap', 'variable']
syntax: SWAP <variable>,<variable>
title: SWAP
type: statement
---

# SWAP

## Syntax

```basic
SWAP <variable>,<variable>
```

**Versions:** Extended, Disk

## Purpose

To exchange the values of two variables.

## Remarks

Any type variable may be SWAPped (integer, single precision, double precision, string), but the two variables must be of the same type or a "Type mismatch" error results.

## Example

```basic
LIST
10 A$="ONE" : B$="ALL" : C$="FOR"
20 PRINT A$; " "; C$; " "; B$
30 SWAP A$, B$
40 PRINT A$; " "; C$; " "; B$

RUN
ONE FOR ALL
ALL FOR ONE
Ok
```

## See Also
- [LET](let.md) - To assign the value of an expression to a variable
