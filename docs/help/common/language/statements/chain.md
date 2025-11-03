---
category: program-control
description: To call a program and pass variables to it            from the current program
keywords: ['chain', 'command', 'file', 'for', 'function', 'if', 'line', 'number', 'open', 'program']
syntax: CHAIN [MERGE] <filename>[,[<line number exp>]
title: CHAIN
type: statement
---

# CHAIN

## Syntax

```basic
CHAIN [MERGE] <filename>[,[<line number exp>]
[,ALL] [,DELETE<range>]]
```

**Versions:** Disk

## Purpose

To call a program and pass variables to it            from the current program.

## Remarks

The CHAIN statement loads and runs another BASIC program, optionally passing variables to it.

### Parameters:
- **MERGE** - Merges the new program with the current one instead of replacing it
- **filename** - Name of the program to chain to (with or without .BAS extension)
- **line number exp** - Optional starting line number in the chained program
- **ALL** - Pass all variables to the chained program (requires COMMON statement)
- **DELETE range** - Delete specified lines before chaining (e.g., DELETE 1000-2000)

### Variable Passing:
Variables are only passed to the chained program if they are declared in a COMMON statement. Without ALL, only COMMON variables are passed. With ALL, all variables are passed.

### Memory:
The current program is removed from memory unless MERGE is specified. Open files remain open across the chain operation.

## See Also
- [CLEAR](clear.md) - To set all numeric variables to zero and all string variables to null; and, optionally, 'to set the end of memory and the amount of stack space
- [COMMON](common.md) - To pass variables to a CHAINed program
- [CONT](cont.md) - To continue program execution after a Control-C has been typed, or a STOP or END statement has been executed
- [END](end.md) - To terminate program execution, close all   files and return to command level
- [NEW](new.md) - To delete the program currently   in   memory   and clear all variables
- [RUN](run.md) - Executes the current program or loads and runs a program from disk
- [STOP](stop.md) - To terminate program      execution   and    return   to command level
- [SYSTEM](system.md) - Exits MBASIC and returns to the operating system
