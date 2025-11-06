---
category: arrays
description: To declare the minimum value for array subscripts
keywords: ['array', 'base', 'command', 'execute', 'for', 'if', 'option', 'statement', 'the']
syntax: OPTION BASE n
title: OPTION BASE
type: statement
---

# OPTION BASE

## Syntax

```basic
OPTION BASE n
```

## Purpose

To declare the minimum value for array subscripts.

## Remarks

Where n is 1 or 0. OPTION BASE sets the default lower bound for array subscripts. If OPTION BASE is not used, the default lower bound is 0.

- **OPTION BASE 0**: Arrays start at index 0 (default)
- **OPTION BASE 1**: Arrays start at index 1

The OPTION BASE statement must appear before any DIM statements or array references in the program. Only one OPTION BASE statement is allowed per program.

## Example

```basic
10 OPTION BASE 1
20 DIM A(10)
30 ' Array A has elements A(1) through A(10)
40 FOR I = 1 TO 10
50   A(I) = I * 2
60 NEXT I
```

Without OPTION BASE 1 (using the default OPTION BASE 0), the array DIM A(10) would have elements A(0) through A(10).

## See Also
- [DIM](dim.md) - Declare array dimensions and allocate memory for array variables
- [ERASE](erase.md) - To eliminate arrays from a program
