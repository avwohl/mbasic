---
category: editing
description: To list all or part of the program currently in memory at the terminal
keywords: ['command', 'execute', 'for', 'if', 'line', 'list', 'number', 'program', 'return', 'statement']
title: LIST
type: statement
---

# LIST

**Versions:** 8K, Extended, Disk

## Syntax

```basic
Format 1: LIST [<line number>]           (8K version)
Format 2: LIST [<line number>[-[<line number>]]]  (Extended, Disk)
```

## Purpose

To list all or part of the program currently in memory at the terminal.

## Remarks


## Example

```basic
Format 1:
            LIST            Lists the program currently
                            in memory.
            LIST 500        In the 8K version, lists
                            all programs lines from
                            500 to the end.
                            In Extended and Disk,
                            lists line 500.
            Format 2:
            LIST 150-       Lists all lines from 150
                            to the end.
            LIST -1000      Lists all lines from the
                            lowest number through 1000.
            LIST 150-1000   Lists lines 150 through
                            1000, inclusive.
```

## See Also
- [AUTO](auto.md) - To generate a line number automatically after every carriage return
- [DELETE](delete.md) - To delete program lines
- [EDIT](edit.md) - To enter Edit Mode at the specified line
- [LLIST](llist.md) - To list all or part of the program currently in memory at the line printer
- [RENUM](renum.md) - Renumber program lines and update line references
