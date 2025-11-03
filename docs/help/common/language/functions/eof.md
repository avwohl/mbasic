---
category: file-io
description: Returns -1 (true) if the end of a sequential file has been reached
keywords: ['data', 'eof', 'error', 'file', 'for', 'function', 'goto', 'if', 'input', 'number']
syntax: EOF(file number)
title: EOF
type: function
---

# EOF

## Syntax

```basic
EOF(file number)
```

**Versions:** Disk

## Description

Returns -1 (true) if the end of a sequential file has been reached. Use EOF to test for end-of-file while INPUTting, to avoid "Input past end" errors.

## Example

```basic
10 OPEN "I",l,"DATA"
 20 C=O
 30 IF EOF(l) THEN 100
 40 INPUT #l,M(C)
 50 C=C+l:GOTO 30
```

## See Also
- [CLOSE](../statements/close.md) - To conclude I/O to a disk file
- [FIELD](../statements/field.md) - To allocate space for variables in a random file buffer
- [FILES](../statements/files.md) - Displays the directory of files on disk
- [GET](../statements/get.md) - To read a record from a random disk file into    a random buffer
- [INPUT$](input_dollar.md) - Returns a string of X characters, read from the terminal or from file number Y
- [LOC](loc.md) - With random disk files, LOC returns the next record number to be used if a GET or PUT (without a record number) is executed
- [LOF](lof.md) - Returns the length of a file in bytes
- [LPOS](lpos.md) - Returns the current position of the line printer print head within the line printer buffer
- [LSET](../statements/lset.md) - Left-justifies a string in a field for random file output
- [OPEN](../statements/open.md) - To allow I/O to a disk file
- [POS](pos.md) - Returns the current cursor position
- [PRINTi AND PRINTi USING](../statements/printi-printi-using.md) - To write data to a sequential disk file
- [PUT](../statements/put.md) - To write a record from a random buffer to a random file
- [RESET](../statements/reset.md) - Closes all open files
- [RSET](../statements/rset.md) - Right-justifies a string in a field for random file output
- [WRITE #](../statements/writei.md) - Write data to a sequential file with delimiters
- [~ INPUTi](../statements/inputi.md) - To read an entire line (up to 254 characters), without delimiters, from a sequential disk data file to a string variable
