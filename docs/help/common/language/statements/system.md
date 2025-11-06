---
category: program-control
description: Exits MBASIC and returns to the operating system
keywords: ['system', 'exit', 'quit', 'end', 'terminate', 'shell', 'os']
syntax: SYSTEM
title: SYSTEM
type: statement
related: ['end', 'stop']
---

# SYSTEM

## Syntax

```basic
SYSTEM
```

**Versions:** Disk

## Purpose

To exit MBASIC and return control to the operating system (CP/M).

## Remarks

The SYSTEM statement terminates the BASIC interpreter and returns to the operating system. This is different from END and STOP, which return to the BASIC prompt (the "Ok" prompt where you can enter immediate mode commands).

When SYSTEM is executed:
- All open files are closed
- Program execution terminates
- The interpreter exits
- Control returns to the operating system

SYSTEM is particularly useful when running BASIC programs as batch scripts or when you want to completely exit MBASIC rather than return to the interactive prompt.

## Example

```basic
10 PRINT "Program complete"
20 SYSTEM

100 INPUT "Exit to OS (Y/N)"; A$
110 IF A$ = "Y" THEN SYSTEM
120 GOTO 100
```

## Notes

- SYSTEM is only available in Disk BASIC
- Use END to terminate a program but remain in BASIC
- Use STOP to pause execution with a BREAK message

## See Also
- [CHAIN](chain.md) - To call a program and pass variables to it from the current program
- [CLEAR](clear.md) - To set all numeric variables to zero and all string variables to null; and, optionally, 'to set the end of memory and the amount of stack space
- [COMMON](common.md) - To pass variables to a CHAINed program
- [CONT](cont.md) - To continue program execution after a Control-C has been typed, or a STOP or END statement has been executed
- [END](end.md) - To terminate program execution, close all files and return to the BASIC prompt
- [NEW](new.md) - To delete the program currently in memory and clear all variables
- [RUN](run.md) - Executes the current program or loads and runs a program from disk
- [STOP](stop.md) - To terminate program execution and return to the BASIC prompt
