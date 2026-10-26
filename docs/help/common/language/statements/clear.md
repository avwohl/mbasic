---
category: program-control
description: To set all numeric variables to zero and all string variables to null; and, optionally, to set the end of memory and the amount of stack space
keywords: ['clear', 'command', 'error', 'for', 'if', 'statement', 'string', 'variable']
syntax: CLEAR [,[<expression1>] [,<expression2>]]
title: CLEAR
type: statement
---

# CLEAR

## Syntax

```basic
CLEAR [,[<expression1>] [,<expression2>]]
```

**Versions:** 8K, Extended, Disk

## Purpose

To set all numeric variables to zero and all string variables to null; and, optionally, 'to set the end of memory and the amount of stack space.

## Remarks

CLEAR resets all variables to their initial values (0 for numbers, empty for strings) and optionally configures memory usage.

A CLEAR that succeeds also does these things, as MBASIC 5.21 does:

- It removes `ON ERROR GOTO`, so the next error stops the program. A handler
  that is running ends, and its `RESUME` gives "RESUME without error". `ERR`
  and `ERL` keep their values.
- It empties the FOR and GOSUB stacks, sends the DATA pointer back to the first
  item, forgets the `DEF FN` functions defined so far, and allows `OPTION BASE`
  again.
- It closes all files.

**Difference:** `DEFINT`, `DEFSTR` and the other type statements are set when
the program is read, so `CLEAR` does not reset them here.

### Parameters

**In MBASIC 5.21 (BASIC-80 release 5.0 and later):**

- **expression1**: If specified, sets the highest memory location available for BASIC to use
- **expression2**: Sets the stack space reserved for BASIC (default: 256 bytes or 1/8 of available memory, whichever is smaller)

### Memory Management

**Note about string space:** In BASIC-80 release 5.0 and later (including MBASIC 5.21), string space is allocated dynamically from available memory. You'll only get an "Out of string space" error if there's no free memory left. The expression1 parameter does NOT control string space in MBASIC 5.21.

**Historical note:** In earlier versions of BASIC-80 (before release 5.0), the parameters had different meanings:
- expression1 set the amount of string space
- expression2 set the end of memory

This behavior changed in release 5.0 to support dynamic string allocation.

## Example

```basic
CLEAR
CLEAR ,32768
CLEAR ,,2000
CLEAR ,32768,2000
```

## See Also
- [CHAIN](chain.md) - To call a program and pass variables to it from the current program
- [COMMON](common.md) - To pass variables to a CHAINed program
- [CONT](cont.md) - To continue program execution after a Control-C has been typed, or a STOP or END statement has been executed
- [END](end.md) - To terminate program execution, close all files and return to command level
- [NEW](new.md) - To delete the program currently in memory and clear all variables
- [RUN](run.md) - Executes the current program or loads and runs a program from disk
- [STOP](stop.md) - To terminate program execution and return to command level
- [SYSTEM](system.md) - Exits MBASIC and returns to the operating system
