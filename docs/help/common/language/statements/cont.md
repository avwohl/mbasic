---
category: program-control
description: To continue program execution after interruption
keywords: ['command', 'cont', 'end', 'error', 'execute', 'for', 'goto', 'if', 'input', 'line']
syntax: CONT
title: CONT
type: statement
---

# CONT

## Syntax

```basic
CONT
```

## Purpose

To continue program execution after a Control-C has been typed, or a STOP or END statement has been executed.

## Remarks

Execution resumes at the point where the break occurred. If the break occurred after a prompt from an INPUT statement, execution continues with the reprinting of the prompt (? or prompt string). CONT is usually used in conjunction with STOP for debugging. When execution is stopped, intermediate values may be examined and changed using direct mode statements. Execution may be resumed with CONT or a direct mode GOTO, which resumes execution at a specified line number. With the Extended and Disk versions, CONT may be used to continue execution after an error. CONT is invalid if the program has been edited during the break. In 8K BASIC-80, execution cannot be CONTinued if a direct mode error has occurred during the break.

## Example

```basic
See example Section 2.61, STOP.
```

## See Also
- [CHAIN](chain.md) - To call a program and pass variables to it from the current program
- [CLEAR](clear.md) - To set all numeric variables to zero and all string variables to null; and, optionally, 'to set the end of memory and the amount of stack space
- [COMMON](common.md) - To pass variables to a CHAINed program
- [END](end.md) - To terminate program execution, close all files and return to command level
- [NEW](new.md) - To delete the program currently in memory and clear all variables
- [RUN](run.md) - Executes the current program or loads and runs a program from disk
- [STOP](stop.md) - To terminate program execution and return to command level
- [SYSTEM](system.md) - Exits MBASIC and returns to the operating system
