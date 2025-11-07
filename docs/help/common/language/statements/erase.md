---
category: arrays
description: To eliminate arrays from a program
keywords: ['array', 'command', 'dim', 'erase', 'error', 'for', 'if', 'program', 'statement', 'variable']
syntax: ERASE <array>[,<array>...]
title: ERASE
type: statement
---

# ERASE

## Syntax

```basic
ERASE <array>[,<array>...]
```

## Purpose

To eliminate arrays from a program.

## Remarks

Arrays may be redimensioned after they are ERASEd, or the previously allocated array space in memory may be used for other purposes. If an attempt is made to redimension an array without first ERASEing it, a "Redimensioned array" error occurs.

## Example

```basic
450 ERASE A,B
460 DIM B(99)
```

## See Also
- [DIM](dim.md) - Declare array dimensions and allocate memory for array variables
- [OPTION BASE](option-base.md) - To declare the minimum value for array subscripts
