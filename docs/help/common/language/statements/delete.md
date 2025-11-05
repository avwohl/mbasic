---
category: editing
description: To delete program lines
keywords: ['command', 'delete', 'error', 'execute', 'function', 'if', 'line', 'number', 'program', 'return']
syntax: DELETE[<line number>] [-<line number>]
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
DELETE 40-100     Deletes lines 40 through 100, inclusive
DELETE-40         Deletes all lines up to and including line 40
```

## See Also
- [AUTO](auto.md) - To generate a line number automatically after every carriage return
- [EDIT](edit.md) - To enter Edit Mode at the specified line
- [LIST](list.md) - To list all or part of the program currently in memory at the terminal
- [LLIST](llist.md) - To list all or part of the program currently in memory at the line printer
- [RENUM](renum.md) - Renumber program lines and update line references
