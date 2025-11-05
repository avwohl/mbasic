---
category: file-io
description: Returns the current cursor position
keywords: ['function', 'if', 'pos', 'print', 'return', 'then']
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

Returns the current cursor position. The leftmost position is 1. I is a dummy argument.

## Example

```basic
10 PRINT "Hello";
20 PRINT " Position:"; POS(0)
30 IF POS(0) > 60 THEN PRINT CHR$(13)  ' New line if past column 60
RUN
Hello Position: 7
Ok
```

## See Also
- [LPOS](lpos.md) - Returns the current position within the line printer buffer
- [TAB](tab.md) - Move to specific column position in PRINT
- [SPC](spc.md) - Print spaces in PRINT statement
- [PRINT](../statements/print.md) - Output to screen
- [WIDTH](../statements/width.md) - Set output line width
