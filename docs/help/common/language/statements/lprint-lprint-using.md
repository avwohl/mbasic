---
category: file-io
description: To print data at the line printer
keywords: ['command', 'data', 'field', 'file', 'for', 'function', 'if', 'line', 'lprint', 'print']
syntax: LPRINT [<list of expressions>]
title: LPRINT AND LPRINT USING
type: statement
---

# LPRINT AND LPRINT USING

## Implementation Note

⚠️ **Not Implemented**: This feature requires line printer hardware and is not implemented in this Python-based interpreter.

**Behavior**: Statement is parsed but no output is sent to a printer

**Why**: Line printers are obsolete hardware. Modern systems use different printing paradigms (print spooling, PDF generation, etc.).

**Alternative**: Use [PRINT](print.md) to output to console or [PRINT#](printi-printi-using.md) to output to a file, then print the file using your operating system's print facilities.

**Historical Reference**: The documentation below is preserved from the original MBASIC 5.21 manual for historical reference.

---

## Syntax

```basic
LPRINT [<list of expressions>]
LPRINT USING <string exp>;<list of expressions>
```

**Versions:** Extended, Disk

## Purpose

To print data at the line printer.

## Remarks

LPRINT works exactly like the PRINT statement except that output goes to the line printer instead of the screen. LPRINT USING works exactly like PRINT USING except output goes to the line printer.

## Example

```basic
10 LPRINT "Sales Report for "; DATE$
20 LPRINT
30 LPRINT "Item", "Quantity", "Price"
40 LPRINT USING "##: $$###.##"; ITEM, PRICE
```

## See Also
- [PRINT](print.md) - To output data to the screen
- [PRINT USING](print.md) - Formatted output to the screen
- [PRINT#](printi-printi-using.md) - To write data to a sequential disk file
- [WIDTH](width.md) - To set the output line width
- [LPOS](../functions/lpos.md) - Returns the current position of the line printer print head
- [POS](../functions/pos.md) - Returns the current cursor position
