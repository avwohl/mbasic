---
category: program-control
description: To set all numeric variables to zero and all string variables to null; and, optionally, 'to set the end of memory and the amount of stack space
keywords: ['clear', 'command', 'error', 'for', 'if', 'statement', 'string', 'variable']
syntax: CLEAR [,[<expressionl>] [,<expression2>]]
title: CLEAR
type: statement
---

# CLEAR

## Syntax

```basic
CLEAR [,[<expressionl>] [,<expression2>]]
```

**Versions:** 8K, -Extended, Disk

## Purpose

To set all numeric variables to zero and all string variables to null; and, optionally, 'to set the end of memory and the amount of stack space.

## Remarks

<expr'essionl> is a memory location which, if specified, sets the highest location available for use by BASIC-SO. <expression2> sets aside stack space for BASIC. The default is 256 bytes or one-eighth of the available memory, whichever is smaller. NOTE:           In previous versions of BASIC-SO, <expressionl> set    the    amount  of   string    space,' and <expression2> set the end of memory.   BASIC-80, release 5.0 and later, allocates string space dynamically. An ROut of string space error R occurs only if there is no free memory left for BASIC to use.

## Example

```basic
CLEAR
                CLEAR ,32768
                CLEAR ,,2000
                CLEAR ,32768,2000
```

## See Also
- [CHAIN](chain.md) - To call a program and pass variables to it            from the current program
- [COMMON](common.md) - To pass variables to a CHAINed program
- [CONT](cont.md) - To continue program execution after a Control-C has been typed, or a STOP or END statement has been executed
- [END](end.md) - To terminate program execution, close all files and return to command level
- [NEW](new.md) - To delete the program currently   in   memory   and clear all variables
- [RUN](run.md) - Executes the current program or loads and runs a program from disk
- [STOP](stop.md) - To terminate program      execution   and    return   to command level
- [SYSTEM](system.md) - Exits MBASIC and returns to the operating system
