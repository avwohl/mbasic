---
category: system
description: NEEDS_DESCRIPTION
keywords:
- NEEDS_KEYWORDS
title: WIDTH
type: statement
---

# WIDTH

## Syntax

```basic
WIDTH [LPRINT] <integer expression>
```

## Purpose

To set the printed line width in number        of characters for the terminal or line printer.

## Remarks

If the LPRINT option is omitted, the line width is set at the terminal. If LPRINT is included, the line width is set at the line printer. <integer expression> must have a value in the range 15 to 255.      The default width is 72 characters. If <integer expression> is 255, the line width is "infinite," that is, BASIC never inserts a carriage return. However, the position of the cursor or the print head, as given by the POS or LPOS function, returns to zero after position 255.

## Example

```basic
10 PRINT "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
               RUN
               ABCDEFGHIJKLMNOPQRSTUVWXYZ
               Ok
               WIDTH 18
               Ok
               RUN
               ABCDEFGHIJKLMNOPQR
               STUVWXYZ
               Ok
BASIC-SO COMMANDS AND STATEMENTS                      Page 2-S4
```

## See Also

*Related statements will be linked here*