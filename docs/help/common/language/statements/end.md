---
category: program-control
description: NEEDS_DESCRIPTION
keywords:
- NEEDS_KEYWORDS
title: END
type: statement
---

# END

## Syntax

```basic
END
```

**Versions:** SK, Extended, Disk

## Purpose

To terminate program execution, close all   files and return to command level.

## Remarks

END statements may be placed anywbere in the program to terminate execution. Unlike the STOP statement, END does not cause a BREAK message to be printed.    An END statement at the end of a program is optional. BASIC-aO·always returns to command level after an END is executed.

## Example

```basic
520 IF K>lOOO THEN END ELSE GOTO 20
BASIC-80 COMMANDS AND STATEMENTS                            Page 2-24
```

## See Also

*Related statements will be linked here*