---
category: file-io
description: To read a record from a random disk file into    a random buffer
keywords: ['command', 'file', 'get', 'if', 'input', 'line', 'next', 'number', 'open', 'put']
syntax: GET [#]<file number>[,<record number>]
title: GET
type: statement
---

# GET

## Syntax

```basic
GET [#]<file number>[,<record number>]
```

**Versions:** Disk

## Purpose

To read a record from a random disk file into    a random buffer.

## Remarks

<file number> is the number under which the file was OPENed. If <record number> is omitted, the next record (after the last GET)  is read into the buffer. The largest possible record number is 32767.

## Example

```basic
See Appendix B.
NOTE:         After a GET statement, INPUT# and LINE INPUT#
              may be done to read characters from the random
              file buffer.
```

## See Also
- [CLOSE](close.md) - To conclude I/O to a disk file
- [EOF](../functions/eof.md) - Returns -1 (true) if the end of a sequential file has been reached
- [FIELD](field.md) - To allocate space for variables in a random file buffer
- [FILES](files.md) - Displays the directory of files on disk
- [INPUT$](../functions/input_dollar.md) - Returns a string of X characters, read from the terminal or from file number Y
- [LOC](../functions/loc.md) - With random disk files, LOC returns the next record number to be used if a GET or PUT (without a record number) is executed
- [LOF](../functions/lof.md) - Returns the length of a file in bytes
- [LPOS](../functions/lpos.md) - Returns the current position of the line printer print head within the line printer buffer
- [LSET](lset.md) - Left-justifies a string in a field for random file output
- [OPEN](open.md) - To allow I/O to a disk file
- [POS](../functions/pos.md) - Returns the current cursor position
- [PRINTi AND PRINTi USING](printi-printi-using.md) - To write data to a sequential disk file
- [PUT](put.md) - To write a record from a random buffer to a random file
- [RESET](reset.md) - Closes all open files
- [RSET](rset.md) - Right-justifies a string in a field for random file output
- [WRITE #](writei.md) - Write data to a sequential file with delimiters
- [~ INPUTi](inputi.md) - To read an entire line (up to 254 characters), without delimiters, from a sequential disk data file to a string variable
