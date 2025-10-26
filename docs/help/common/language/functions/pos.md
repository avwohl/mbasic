---
category: file-io
description: Returns the current cursor position
keywords:
- function
- if
- pos
- print
- return
- then
syntax: POS (I)
title: POS
type: function
---

# POS

## Syntax

```basic
POS (I)
```

## Description

Returns the current cursor position. The leftmost position is 1. X is a dummy argument.

## Example

```basic
IF POS(X) >60 THEN PRINT CHR$(13)
 Also see the LPOS function.
```

## See Also

*Related functions will be linked here*