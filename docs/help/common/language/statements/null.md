---
category: system
description: To set the number of nulls to be printed at the end of each line
keywords: ['command', 'for', 'goto', 'if', 'input', 'line', 'null', 'number', 'print', 'put']
syntax: NULL <integer expression>
title: NULL
type: statement
---

# NULL

## Syntax

```basic
NULL <integer expression>
```

## Purpose

To set the number of nulls to be printed at the end of each line.

## Remarks

For 10-character-per-second tape punches, <integer expression> should be >=3. When tapes are not being punched, <integer expression> should be 0 or 1 for Teletypes and Teletype-compatible CRTs. <integer expression> should be 2 or 3 for 30 cps hard copy printers. The default value is O.

## Example

```basic
NULL 2
100 INPUT X
200 IF X<50 GOTO 800
```

Two null characters will be printed after each line.

## See Also
- [WIDTH](width.md) - Set printed line width
- [PRINT](print.md) - Output to terminal
- [LPRINT](lprint-lprint-using.md) - Output to line printer
- [POS](../functions/pos.md) - Get cursor position
- [LPOS](../functions/lpos.md) - Get line printer position
