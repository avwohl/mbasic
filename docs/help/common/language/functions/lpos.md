---
category: file-io
description: Returns the current position of the line printer print head within the line printer buffer
keywords: ['function', 'if', 'line', 'lpos', 'print', 'return', 'then']
syntax: LPOS(X)
title: LPOS
type: function
---

# LPOS

## Implementation Note

⚠️ **Not Implemented**: This feature requires line printer hardware and is not implemented in this Python-based interpreter.

**Behavior**: Function always returns 0

**Why**: Line printers are obsolete hardware. There is no printer print head to track in modern systems.

**Alternative**: Use [POS](pos.md) to get the current console print position, or track position manually when writing to files with [PRINT#](../statements/printi-printi-using.md).

**Historical Reference**: The documentation below is preserved from the original MBASIC 5.21 manual for historical reference.

---

## Syntax

```basic
LPOS(X)
```

**Versions:** Extended, Disk

## Description

Returns the current position of the line printer print head within the line printer buffer. Does not necessarily give the physical position of the print head. X is a dummy argument.

## Example

```basic
100 IF LPOS(X) >60 THEN LPRINT CHR$(13)
```

## See Also
- [CLOSE](../statements/close.md) - To conclude I/O to a disk file
- [EOF](eof.md) - Returns -1 (true) if the end of a sequential file has been reached
- [FIELD](../statements/field.md) - To allocate space for variables in a random file buffer
- [FILES](../statements/files.md) - Displays the directory of files on disk
- [GET](../statements/get.md) - To read a record from a random disk file into    a random buffer
- [INPUT$](input_dollar.md) - Returns a string of X characters, read from the terminal or from file number Y
- [LOC](loc.md) - With random disk files, LOC returns the next record number to be used if a GET or PUT (without a record number) is executed
- [LOF](lof.md) - Returns the length of a file in bytes
- [LSET](../statements/lset.md) - Left-justifies a string in a field for random file output
- [OPEN](../statements/open.md) - To allow I/O to a disk file
- [POS](pos.md) - Returns the current cursor position
- [PRINTi AND PRINTi USING](../statements/printi-printi-using.md) - To write data to a sequential disk file
- [PUT](../statements/put.md) - To write a record from a random buffer to a random file
- [RESET](../statements/reset.md) - Closes all open files
- [RSET](../statements/rset.md) - Right-justifies a string in a field for random file output
- [WRITE #](../statements/writei.md) - Write data to a sequential file with delimiters
- [~ INPUTi](../statements/inputi.md) - To read an entire line (up to 254 characters), without delimiters, from a sequential disk data file to a string variable
