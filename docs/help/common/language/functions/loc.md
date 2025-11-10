---
category: file-io
description: With random disk files, LOC returns the next record number to be used if a GET or PUT (without a record number) is executed
keywords: ['execute', 'file', 'function', 'get', 'if', 'loc', 'next', 'number', 'open', 'put']
syntax: LOC(file number)
title: LOC
type: function
---

# LOC

## Syntax

```basic
LOC(file number)
```

**Versions:** Disk

## Description

With random disk files, LOC returns the next record number to be used if a GET or PUT (without a record number) is executed. With sequential files, LOC returns the number of sectors (128 byte blocks) read from or written to the file since it was OPENed.

## Example

```basic
200 IF LOC(1) > 50 THEN STOP
```

## See Also
- [CLOSE](../statements/close.md) - To conclude I/O to a disk file
- [EOF](eof.md) - Returns -1 (true) if the end of a sequential file has been reached
- [FIELD](../statements/field.md) - To allocate space for variables in a random file buffer
- [FILES](../statements/files.md) - Displays the directory of files on disk
- [GET](../statements/get.md) - To read a record from a random disk file into    a random buffer
- [INPUT$](input_dollar.md) - Returns a string of X characters, read from the terminal or from file number Y
- [LOF](lof.md) - Returns the total file size in bytes (LOC returns current position/record number)
- [LPOS](lpos.md) - Returns the current position of the line printer print head within the line printer buffer
- [LSET](../statements/lset.md) - Left-justifies a string in a field for random file output
- [OPEN](../statements/open.md) - To allow I/O to a disk file
- [POS](pos.md) - Returns the current cursor position
- [PRINTi AND PRINTi USING](../statements/printi-printi-using.md) - To write data to a sequential disk file
- [PUT](../statements/put.md) - To write a record from a random buffer to a random file
- [RESET](../statements/reset.md) - Closes all open files
- [RSET](../statements/rset.md) - Right-justifies a string in a field for random file output
- [WRITE #](../statements/writei.md) - Write data to a sequential file with delimiters
- [LINE INPUT#](../statements/inputi.md) - To read an entire line (up to 254 characters), without delimiters, from a sequential disk data file to a string variable
