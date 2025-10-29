---
category: display
description: Clears the screen and moves the cursor to the home position
keywords:
- cls
- clear
- screen
- display
- terminal
- home
syntax: CLS
title: CLS
type: statement
---

# CLS

## Syntax

```basic
CLS
```

**Versions:** Extended, Disk

## Purpose

To clear the screen and move the cursor to the home position (upper left corner).

## Remarks

The CLS statement clears all text from the screen and positions the cursor at row 1, column 1. This is useful for:
- Starting with a clean display
- Clearing previous output before showing new information
- Formatting screen-based programs and menus

After CLS executes, the screen will be blank and ready for new output.

## Example

```basic
10 CLS
20 PRINT "This appears on a clean screen"
RUN
This appears on a clean screen
Ok

100 CLS: PRINT "MENU": PRINT "----"
110 PRINT "1. Start"
120 PRINT "2. Exit"
```

## See Also

- PRINT - Display text on screen
- LOCATE - Position cursor (not yet documented)
