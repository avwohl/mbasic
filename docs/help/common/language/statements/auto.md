---
category: editing
description: To generate a line number automatically after every carriage return
keywords: ['auto', 'command', 'for', 'if', 'input', 'line', 'next', 'number', 'print', 'put']
syntax: AUTO [<line number>[,<increment>]]
title: AUTO
type: statement
---

# AUTO

## Syntax

```basic
AUTO [<line number>[,<increment>]]
```

## Purpose

To generate a line number automatically after every carriage return.

## Remarks

AUTO begins numbering at <line number> and increments each subsequent line number by <increment>. The default for both values is 10. If <line number> is followed by a comma but <increment> is not specified, the last increment specified in an AUTO command is assumed. If AUTO generates a line number that is already being used, an asterisk is printed after the number to warn the user that any input will replace the existing line. However, typing a carriage return immediately after the asterisk will save the line and generate the next line number. AUTO is terminated by typing Control-C. The line in which Control-C is typed is not saved. After Control-C is typed, BASIC returns to command level.

## Example

```basic
AUTO 100,50
REM Generates line numbers 100, 150, 200, etc.

AUTO
REM Generates line numbers 10, 20, 30, 40, etc.
```

## See Also
- [DELETE](delete.md) - To delete program lines
- [EDIT](edit.md) - To enter Edit Mode at the specified line
- [LIST](list.md) - To list all or part of the program currently in memory at the terminal
- [LLIST](llist.md) - To list all or part of the program currently in memory at the line printer
- [RENUM](renum.md) - Renumber program lines and update line references
