---
category: input-output
description: To output data at the terminal
keywords: ['command', 'data', 'for', 'if', 'line', 'print', 'put', 'return', 'statement', 'string']
syntax: WRITE [<list of expressions>]
title: "WRITE (Screen)"
type: statement
---

# WRITE

## Syntax

```basic
WRITE [<list of expressions>]
```

**Versions:** Disk

## Purpose

To output data at the terminal.

## Remarks

If <list of expressions> is omitted, a blank line is output. If <list of expressions> is included, the values of the expressions are output at the terminal. The expressions in the list may be numeric and/or string expressions, and they must be separated by commas.

When the printed items are output, each item will be separated from the last by a comma. Printed strings will be delimited by quotation marks. After the last item in the list is printed, BASIC inserts a carriage return/line feed.

WRITE outputs numeric values using the same format as the PRINT statement.

## Example

```basic
10 A=50:B=90:C$="THAT'S ALL"
20 WRITE A,B,C$
RUN
50, 90,"THAT'S ALL"
Ok
```

## See Also
- [WRITE#](writei.md) - Write data to a sequential file (file output)
- [INPUT](input.md) - Read user input from the terminal during program execution
- [PRINT](print.md) - Output text and values to the terminal
