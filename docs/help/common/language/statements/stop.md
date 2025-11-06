---
category: program-control
description: To terminate program execution and return to the BASIC prompt
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

To terminate program execution and return to the BASIC prompt.

## Remarks

STOP statements may be used anywhere in a program to terminate execution. When a STOP is encountered, the following message is printed: "Break in line nnnnn".

Unlike the END statement, the STOP statement does not close files. BASIC-80 always returns to the BASIC prompt after a STOP is executed. Execution is resumed by issuing a CONT command.

## Example

```basic
10 INPUT A,B,C
20 K = A^2 * 5.3: L = B^3 / .26
30 STOP
40 M = C * K + 100: PRINT M
```

Output:
```
RUN
? 1,2,3
Break in 30
Ok
PRINT L
 30.7692
Ok
CONT
 115.9
Ok
```

This example shows how STOP interrupts execution, allows inspection of variables, and resumes with CONT.

## See Also
- [CONT](cont.md) - Continue program execution after STOP
- [END](end.md) - Terminate program execution and close all files, returning to the BASIC prompt
- [CHAIN](chain.md) - Call another program and pass variables
- [CLEAR](clear.md) - Reset variables and optionally set memory limits
- [RUN](run.md) - Execute the current program
- [SYSTEM](system.md) - Exit MBASIC and return to the operating system
