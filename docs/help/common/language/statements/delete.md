---
category: editing
description: NEEDS_DESCRIPTION
keywords:
- NEEDS_KEYWORDS
title: DELETE
type: statement
---

# DELETE

## Syntax

```basic
DELETE[<line number>] [-<line number>]
```

## Purpose

To delete program lines.

## Remarks

BASIC-80 always returns to command level after a DELETE is executed. If <line number> does not exist, an "Illegal function call" error occurs.

## Example

```basic
DELETE 40         Deletes line 40
                DELETE 40-100     Deletes lines 40 through
                                  100, inclusive
                DELETE-40         Deletes all lines up to
                                  and including line 40
BASIC-80 COMMANDS AND STATEMENTS                    Page 2-18
```

## See Also

*Related statements will be linked here*