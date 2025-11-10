---
category: file-io
description: Returns the current position of the line printer print head within the line printer buffer
keywords: ['function', 'if', 'line', 'lpos', 'print', 'return', 'then']
syntax: LPOS(X)
title: LPOS
type: function
---

# LPOS

## Implementation Note

⚠️ **Not Implemented**: This feature requires line printer hardware and is not implemented in this Python-based interpreter.

**Behavior**: Function always returns 0

**Why**: Line printers are obsolete hardware. There is no printer print head to track in modern systems. The function exists for compatibility with old BASIC programs but cannot provide meaningful position data.

**Alternative**: Use [POS](pos.md) to get the current console print position, or track position manually when writing to files with [PRINT#](../statements/printi-printi-using.md).

**Historical Reference**: The documentation below is preserved from the original MBASIC 5.21 manual for historical reference.

---

## Syntax

```basic
LPOS(X)
```

**Versions:** Extended, Disk

## Description

Returns the current position of the line printer print head within the line printer buffer. Does not necessarily give the physical position of the print head. X is a dummy argument.

## Example

```basic
100 IF LPOS(X) >60 THEN LPRINT CHR$(13)
```

## See Also
- [POS](pos.md) - Get current cursor position
- [LPRINT](../statements/lprint-lprint-using.md) - Print to line printer
- [LPRINT USING](../statements/lprint-lprint-using.md) - Formatted print to line printer
- [WIDTH LPRINT](../statements/width.md) - Set line printer width
- [PRINT](../statements/print.md) - Print to console
- [PRINT#](../statements/printi-printi-using.md) - Write to file
