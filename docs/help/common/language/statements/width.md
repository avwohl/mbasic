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

⚠️ **Emulated as No-Op**: This statement is parsed for compatibility but performs no operation.

**Behavior**: Statement executes successfully without errors, but does not affect output width.

**Why**: Terminal and UI width is controlled by the operating system or UI framework, not the BASIC program. The WIDTH statement cannot actually change these settings.

**Note**: Programs using WIDTH will run without errors, but width settings are silently ignored.

**Limitations**: The "WIDTH LPRINT" syntax is not supported (parse error). Only the simple "WIDTH <number>" form is accepted.

**Historical Reference**: The documentation below is preserved from the original MBASIC 5.21 manual for historical reference.

---

## Syntax

```basic
WIDTH <integer expression>
```

Original MBASIC 5.21 also supported:
```basic
WIDTH LPRINT <integer expression>  ' NOT SUPPORTED in this implementation
```

## Purpose

To set the printed line width in number of characters for the terminal or line printer.

## Remarks

If the LPRINT option is omitted, the line width is set at the terminal. If LPRINT is included, the line width is set at the line printer.

`<integer expression>` must have a value in the range 15 to 255. The default width is 72 characters.

If `<integer expression>` is 255, the line width is "infinite," that is, BASIC never inserts a carriage return. However, the position of the cursor or the print head, as given by the POS or LPOS function, returns to zero after position 255.

## Example

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

## See Also
- [LPRINT](lprint-lprint-using.md) - Print to line printer
- [POS](../functions/pos.md) - Returns current cursor position
- [LPOS](../functions/lpos.md) - Returns current line printer position
- [PRINT](print.md) - Output to the screen