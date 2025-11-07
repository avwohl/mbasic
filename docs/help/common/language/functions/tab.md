---
category: output-formatting
description: Spaces to position I on the terminal
keywords: ['data', 'function', 'if', 'line', 'next', 'print', 'read', 'statement', 'tab']
syntax: TAB (I)
title: TAB
type: function
---

# TAB

## Syntax

```basic
TAB (I)
```

## Description

Spaces to position I on the terminal. If the current print position is already beyond space I, TAB goes to that position on the next line. Space 1 is the leftmost position, and the rightmost position is the width minus one. I must be in the range 1 to 255. TAB may only be used in PRINT and LPRINT statements.

## Example

```basic
10 PRINT "NAME" TAB(25) "AMOUNT": PRINT
20 READ A$, B$
30 PRINT A$ TAB(25) B$
40 DATA "G. T. JONES", "$25.00"
```

Output:
```
NAME                    AMOUNT

G. T. JONES             $25.00
```

## See Also
- [SPC](spc.md) - Print spaces (similar function)
- [SPACE$](space_dollar.md) - Returns a string of spaces
- [PRINT](../statements/print.md) - Print to console
- [LPRINT](../statements/lprint-lprint-using.md) - Print to line printer
- [POS](pos.md) - Current cursor position
- [WIDTH](../statements/width.md) - Set output line width
- [READ](../statements/read.md) - Read data from DATA statements (used in example above)
- [DATA](../statements/data.md) - Store data for READ statements (used in example above)
