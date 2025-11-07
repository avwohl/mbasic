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

### Implementation Note:
**Modern MBASIC Implementation:** This implementation provides full-screen editing capabilities through the integrated editor (Tk, Curses, or Web UI). The traditional MBASIC single-character edit mode commands (I, D, C, L, Q, etc.) are **not implemented**. Simply edit program lines directly in the full-screen editor.

**Historical Reference:** Original MBASIC 5.21 provided a line-oriented edit mode with single-character commands for inserting, deleting, and changing characters. This is not needed with modern full-screen editors.

## See Also
- [AUTO](auto.md) - To generate a line number automatically after every carriage return
- [DELETE](delete.md) - To delete program lines
- [LIST](list.md) - To list all or part of the program currently in memory at the terminal
- [LLIST](llist.md) - To list all or part of the program currently in memory at the line printer
- [RENUM](renum.md) - Renumber program lines and update line references
