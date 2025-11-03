---
category: editing
description: To enter Edit Mode at the specified line
keywords: ['close', 'command', 'edit', 'error', 'execute', 'for', 'function', 'if', 'line', 'next']
syntax: EDIT <line number>
title: EDIT
type: statement
---

# EDIT

## Syntax

```basic
EDIT <line number>
```

## Purpose

To enter Edit Mode at the specified line.

## Remarks

The EDIT command enters the line editor for the specified line number, allowing you to modify an existing program line.

### Usage:
- If the specified line exists, it is displayed for editing
- If the line doesn't exist, an error is generated
- The line editor provides special commands for inserting, deleting, and modifying characters

### Edit Mode Commands:
In traditional MBASIC, EDIT mode provided special single-character commands:
- **I** - Insert mode
- **D** - Delete characters
- **C** - Change characters
- **L** - List the line
- **Q** - Quit edit mode
- **Space** - Move cursor forward
- **Enter** - Accept changes

### Note:
Modern MBASIC implementations often provide full-screen editing capabilities instead of the traditional line editor.

## See Also
- [AUTO](auto.md) - To generate a line number   automatically     after every carriage return
- [DELETE](delete.md) - To delete program lines
- [LIST](list.md) - To list all or part of the program currently            in memory at the terminal
- [LLIST](llist.md) - To list all or part of the program currently     in memory at the line printer
- [RENUM](renum.md) - Renumber program lines and update line references
