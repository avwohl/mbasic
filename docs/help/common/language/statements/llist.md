---
category: editing
description: To list all or part of the program currently     in memory at the line printer
keywords: ['command', 'execute', 'for', 'line', 'llist', 'number', 'print', 'program', 'return', 'statement']
syntax: LLIST [<line number>[-[<line number>]]]
title: LLIST
type: statement
---

# LLIST

## Implementation Note

⚠️ **Not Implemented**: This feature requires line printer hardware and is not implemented in this Python-based interpreter.

**Behavior**: Statement is parsed but no listing is sent to a printer

**Why**: Line printers are obsolete hardware. Modern systems use different printing paradigms.

**Alternative**: Use [LIST](list.md) to display program to console or redirect console output to a file for printing:
```bash
python3 mbasic yourprogram.bas > listing.txt
# Then print listing.txt using your OS print facilities
```

**Historical Reference**: The documentation below is preserved from the original MBASIC 5.21 manual for historical reference.

---

## Syntax

```basic
LLIST [<line number>[-[<line number>]]]
```

## Purpose

To list all or part of the program currently     in memory at the line printer.

## Remarks

LLIST assumes a l32-character wide printer. BASIC-80 always returns to command level after an LLIST is executed. The options for LLIST are the same as for LIST, Format 2. NOTE:           LLIST and LPRINT are not       included    in   all implementations of BASIC-80.

## Example

```basic
See the examples for LIST, Format 2.
```

## See Also
- [AUTO](auto.md) - To generate a line number   automatically     after every carriage return
- [DELETE](delete.md) - To delete program lines
- [EDIT](edit.md) - To enter Edit Mode at the specified line
- [LIST](list.md) - To list all or part of the program currently            in memory at the terminal
- [RENUM](renum.md) - Renumber program lines and update line references
