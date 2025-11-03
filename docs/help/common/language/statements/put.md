---
category: file-io
description: To write a record from a random buffer to a random file
keywords: ['command', 'error', 'field', 'file', 'for', 'if', 'next', 'number', 'open', 'print']
syntax: PUT (#]<file number>(,<record number>]
title: PUT
type: statement
---

# PUT

## Syntax

```basic
PUT (#]<file number>(,<record number>]
```

**Versions:** Disk

## Purpose

To write a record from a random buffer to a random file. disk file.

## Remarks

<file number> is the number under which the file was OPENed. If <record number> is omitted, the record will have the next available record number   (after the last PUT).      The largest possible record number is 32767.   The smallest record number is 1.

## Example

```basic
See Appendix B.
NOTE:         PRINT#, PRINT# USING, and WRITE# may be used to
              put characters in the random file buffer before
              a PUT statement.
              In the case of WRITE#, BASIC-80 pads the buffer
              with spaces up to the carriage return. Any
              attempt to read or write past the end of the
              buffer causes a "Field overflow" error.
```

## See Also
- [CLOSE](close.md) - To conclude I/O to a disk file
- [EOF](../functions/eof.md) - Returns -1 (true) if the end of a sequential file has been reached
- [FIELD](field.md) - To allocate space for variables in a random file buffer
- [FILES](files.md) - Displays the directory of files on disk
- [GET](get.md) - To read a record from a random disk file into    a random buffer
- [INPUT$](../functions/input_dollar.md) - Returns a string of X characters, read from the terminal or from file number Y
- [LOC](../functions/loc.md) - With random disk files, LOC returns the next record number to be used if a GET or PUT (without a record number) is executed
- [LOF](../functions/lof.md) - Returns the length of a file in bytes
- [LPOS](../functions/lpos.md) - Returns the current position of the line printer print head within the line printer buffer
- [LSET](lset.md) - Left-justifies a string in a field for random file output
- [OPEN](open.md) - To allow I/O to a disk file
- [POS](../functions/pos.md) - Returns the current cursor position
- [PRINTi AND PRINTi USING](printi-printi-using.md) - To write data to a sequential disk file
- [RESET](reset.md) - Closes all open files
- [RSET](rset.md) - Right-justifies a string in a field for random file output
- [WRITE #](writei.md) - Write data to a sequential file with delimiters
- [~ INPUTi](inputi.md) - To read an entire line (up to 254 characters), without delimiters, from a sequential disk data file to a string variable
