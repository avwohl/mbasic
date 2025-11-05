---
category: program-control
description: To pass variables to a CHAINed program
keywords: ['array', 'command', 'common', 'if', 'program', 'statement', 'variable']
syntax: COMMON <list of variables>
title: COMMON
type: statement
---

# COMMON

## Syntax

```basic
COMMON <list of variables>
```

**Versions:** Disk

## Purpose

To pass variables to a CHAINed program.

## Remarks

The COMMON statement is used in conjunction with the CHAIN statement.     COMMON statements may appear anywhere in a program, though it is recommended that they appear at the beginning. The same variable cannot appear in more than one COMMON statement. Array variables are specified by appending "()" to the variable name.   If all variables are to be passed, use CHAIN with the ALL option and omit the COMMON statement.

## Example

```basic
100 COMMON A,B,C,D(),G$
               110 CHAIN "PROG3",10
                    •
```

## See Also
- [CHAIN](chain.md) - To call a program and pass variables to it from the current program
- [CLEAR](clear.md) - To set all numeric variables to zero and all string variables to null; and, optionally, 'to set the end of memory and the amount of stack space
- [CONT](cont.md) - To continue program execution after a Control-C has been typed, or a STOP or END statement has been executed
- [END](end.md) - To terminate program execution, close all files and return to command level
- [NEW](new.md) - To delete the program currently in memory and clear all variables
- [RUN](run.md) - Executes the current program or loads and runs a program from disk
- [STOP](stop.md) - To terminate program execution and return to command level
- [SYSTEM](system.md) - Exits MBASIC and returns to the operating system
