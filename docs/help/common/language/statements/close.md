---
category: file-io
description: To conclude I/O to a disk file
keywords: ['close', 'command', 'file', 'for', 'if', 'number', 'open', 'put', 'statement', 'then']
syntax: CLOSE[[#]<file number>[,[#]<file number ••• >]]
title: CLOSE
type: statement
---

# CLOSE

## Syntax

```basic
CLOSE[[#]<file number>[,[#]<file number ••• >]]
```

## Purpose

To conclude I/O to a disk file.

## Remarks

<file number> is the number under which the file was OPENed.     A CLOSE with no arguments closes all open files. The association between a particular file and file number terminates upon execution of a CLOSE. The file may then be reOPENed using the same or a different file number; likewise, that file number may now be reused to OPEN any file. A CLOSE for a sequential output file writes       the final buffer of output. The END statement and the NEW command always CLOSE all disk files automatically. (STOP does not close disk files.)

## Example

```basic
See PART II, Chapter 3, MBASIC       Disk
              I/O, of the MBASIC User's Guide.
```

## See Also
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
- [PUT](put.md) - To write a record from a random buffer to a random file
- [RESET](reset.md) - Closes all open files
- [RSET](rset.md) - Right-justifies a string in a field for random file output
- [WRITE #](writei.md) - Write data to a sequential file with delimiters
- [~ INPUTi](inputi.md) - To read an entire line (up to 254 characters), without delimiters, from a sequential disk data file to a string variable
