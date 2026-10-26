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

**Implemented for the screen.** `WIDTH n` sets the line width of the screen. PRINT wraps at that width and measures `TAB`, `SPC` and the comma zones against it. `POS(0)` returns the cursor column. The default width is 80.

**Range**: 1 to 255. Another value gives "Illegal function call". Real MBASIC 5.21 also accepts 0.

**Limitations**: The "WIDTH LPRINT" syntax is NOT supported and will cause a parse error. The form `WIDTH n, device` sets the width and then gives "Syntax error", as MBASIC 5.21 does. A disk file always has a width of 255.

**Historical Reference**: The documentation below is preserved from the original MBASIC 5.21 manual for historical reference. The default width of real MBASIC 5.21 is 80 on the console.

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

**Note:** The example below shows MBASIC 5.21 behavior. This implementation does the same for the screen.

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