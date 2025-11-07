---
category: program-control
description: Executes the current program or loads and runs a program from disk
keywords: ['run', 'execute', 'start', 'load', 'program', 'file']
syntax: RUN [line number] or RUN filename
title: RUN
type: statement
related: ['load', 'chain', 'goto']
---

# RUN

## Syntax

```basic
RUN [line number]
RUN "filename"
```

**Versions:** 8K, Extended, Disk

## Purpose

To execute the current program in memory, or to load and execute a program from disk.

## Remarks

The RUN statement has several forms:

**RUN** - Executes the current program starting at the lowest line number. All variables are cleared and files are closed before execution begins.

**RUN line-number** - Executes the current program starting at the specified line number. All variables are cleared and files are closed.

**RUN "filename"** - (Disk BASIC only) Loads the specified program file from disk and executes it. The current program is replaced and all variables are cleared.

When RUN is executed:
- All variables are reset to zero or empty strings
- All open files are closed (unlike STOP, which keeps files open)
- All FOR/NEXT loops are cleared
- All GOSUB return addresses are cleared
- DATA pointers are reset to the first DATA statement

## Example

```basic
RUN
RUN 100
RUN "PROGRAM.BAS"

10 PRINT "Starting..."
20 RUN 50
30 PRINT "This line is skipped"
40 END
50 PRINT "Execution starts here"
```

## Notes

- RUN always clears all variables, even when starting at a specific line
- To resume execution without clearing variables, use GOTO instead
- File extension defaults to .BAS if not specified

## See Also
- [CHAIN](chain.md) - To call a program and pass variables to it from the current program
- [CLEAR](clear.md) - To set all numeric variables to zero and all string variables to null; and, optionally, 'to set the end of memory and the amount of stack space
- [COMMON](common.md) - To pass variables to a CHAINed program
- [CONT](cont.md) - To continue program execution after a Control-C has been typed, or a STOP or END statement has been executed
- [END](end.md) - To terminate program execution, close all files and return to the BASIC prompt
- [GOTO](goto.md) - Branch unconditionally to a specified line number
- [LOAD](load.md) - To load a file from disk into memory
- [NEW](new.md) - To delete the program currently in memory and clear all variables
- [STOP](stop.md) - To terminate program execution and return to the BASIC prompt
- [SYSTEM](system.md) - Exits MBASIC and returns to the operating system
