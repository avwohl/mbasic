---
category: program-control
description: To terminate program      execution   and    return   to command level
keywords: ['close', 'command', 'execute', 'file', 'input', 'line', 'print', 'program', 'put', 'return']
syntax: STOP
title: STOP
type: statement
---

# STOP

## Syntax

```basic
STOP
```

## Purpose

To terminate program      execution   and    return   to command level.

## Remarks

STOP statements may be used anywhere in a program to terminate execution. When a STOP is encountered, the following message is printed: Break in line nnnnn Unlike the END statement,       the   STOP   statement does not close files. BASIC-80 always returns to command level after a STOP is executed.     Execution is resumed by issuing a CONT command (see Section 2.8).

## Example

```basic
10 INPUT A,B,C
              20 K=AA2*5.3:L=B A3/.26
              30 STOP
              40 M=C*K+100:PRINT M
              RON
              ? 1,2,3
              BREAK IN 30
              Ok
              PRINT L
               30.7692
              Ok
              CONT
               115.9
              Ok
```

## See Also
- [CHAIN](chain.md) - To call a program and pass variables to it            from the current program
- [CLEAR](clear.md) - To set all numeric variables to zero and all string variables to null; and, optionally, 'to set the end of memory and the amount of stack space
- [COMMON](common.md) - To pass variables to a CHAINed program
- [CONT](cont.md) - To continue program execution after a Control-C has been typed, or a STOP or END statement has been executed
- [END](end.md) - To terminate program execution, close all files and return to command level
- [NEW](new.md) - To delete the program currently   in   memory   and clear all variables
- [RUN](run.md) - Executes the current program or loads and runs a program from disk
- [SYSTEM](system.md) - Exits MBASIC and returns to the operating system
