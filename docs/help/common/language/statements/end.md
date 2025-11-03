---
category: program-control
description: To terminate program execution, close all files and return to command level
keywords: ['close', 'command', 'else', 'end', 'execute', 'file', 'goto', 'if', 'print', 'program']
syntax: END
title: END
type: statement
---

# END

## Syntax

```basic
END
```

**Versions:** 8K, Extended, Disk

## Purpose

To terminate program execution, close all files and return to command level.

## Remarks

END statements may be placed anywhere in the program to terminate execution. Unlike the STOP statement, END does not cause a BREAK message to be printed. An END statement at the end of a program is optional. BASIC-80 always returns to command level after an END is executed.

## Example

```basic
520 IF K>lOOO THEN END ELSE GOTO 20
```

## See Also
- [CHAIN](chain.md) - To call a program and pass variables to it            from the current program
- [CLEAR](clear.md) - To set all numeric variables to zero and all string variables to null; and, optionally, 'to set the end of memory and the amount of stack space
- [COMMON](common.md) - To pass variables to a CHAINed program
- [CONT](cont.md) - To continue program execution after a Control-C has been typed, or a STOP or END statement has been executed
- [NEW](new.md) - To delete the program currently   in   memory   and clear all variables
- [RUN](run.md) - Executes the current program or loads and runs a program from disk
- [STOP](stop.md) - To terminate program      execution   and    return   to command level
- [SYSTEM](system.md) - Exits MBASIC and returns to the operating system
