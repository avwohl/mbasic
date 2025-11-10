---
category: system
description: To set the printed line width in number of characters for the terminal or line printer
keywords: ['command', 'for', 'function', 'if', 'line', 'number', 'print', 'return', 'statement', 'width']
syntax: WIDTH <integer expression>
title: WIDTH
type: statement
---

# WIDTH

## Implementation Note

⚠️ **Not Implemented**: This statement is parsed for compatibility but performs no operation.

**Behavior**: The simple "WIDTH <number>" statement parses and executes successfully without errors, but does not affect output width (settings are silently ignored).

**Why**: Terminal and UI width is controlled by the operating system or UI framework, not the BASIC program. The WIDTH statement cannot actually change these settings.

**Limitations**: The "WIDTH LPRINT" syntax is NOT supported and will cause a parse error. Only the simple "WIDTH <number>" form is accepted as a no-op.

**Alternative**: Terminal width is automatically handled by the UI. For custom formatting, use PRINT statements with TAB() and SPC() functions to control output positioning.

**Historical Reference**: The documentation below is preserved from the original MBASIC 5.21 manual for historical reference. The WIDTH statement syntax and behavior is documented for reference even though it is not implemented.

---

## Syntax

```basic
WIDTH <integer expression>
```

**⚠️ UNSUPPORTED SYNTAX** - Original MBASIC 5.21 also supported:
```basic
WIDTH LPRINT <integer expression>  ' ⚠️ NOT SUPPORTED - will cause parse error
```

## Purpose

To set the printed line width in number of characters for the terminal or line printer.

## Remarks

If the LPRINT option is omitted, the line width is set at the terminal. If LPRINT is included, the line width is set at the line printer.

`<integer expression>` must have a value in the range 15 to 255. The default width is 72 characters.

If `<integer expression>` is 255, the line width is "infinite," that is, BASIC never inserts a carriage return. However, the position of the cursor or the print head, as given by the POS or LPOS function, returns to zero after position 255.

## Example

**Note:** The example below shows historical MBASIC 5.21 behavior. In this implementation, WIDTH is a no-op, so the output would be the same before and after WIDTH is called.

**Original MBASIC 5.21 behavior:**
```basic
10 PRINT "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
```

Output (default width):
```
RUN
ABCDEFGHIJKLMNOPQRSTUVWXYZ
Ok
```

After setting width to 18:
```
WIDTH 18
Ok
RUN
ABCDEFGHIJKLMNOPQR
STUVWXYZ
Ok
```

**This implementation:** Output would be identical in both cases (WIDTH has no effect).

## See Also
- [LPRINT](lprint-lprint-using.md) - Print to line printer
- [POS](../functions/pos.md) - Returns current cursor position
- [LPOS](../functions/lpos.md) - Returns current line printer position
- [PRINT](print.md) - Output to the screen