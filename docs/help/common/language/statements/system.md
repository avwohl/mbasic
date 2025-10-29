---
category: program-control
description: Exits MBASIC and returns to the operating system
keywords:
- system
- exit
- quit
- end
- terminate
- shell
- os
syntax: SYSTEM
title: SYSTEM
type: statement
related: [end, stop]
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

The SYSTEM statement terminates the BASIC interpreter and returns to the operating system command level. This is different from END, which returns to the BASIC "Ok" prompt.

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

- [END](end.md) - Terminate program and return to BASIC prompt
- STOP - Pause execution with BREAK message (not yet documented)
