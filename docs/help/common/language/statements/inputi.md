---
category: file-io
description: To read an entire line (up to 254 characters), without delimiters, from a sequential disk data file to a string variable
keywords: ['close', 'command', 'data', 'field', 'file', 'for', 'if', 'input', 'inputi', 'line']
syntax: LINE INPUT#<file number>,<string variable>
title: LINE INPUT#
type: statement
---

# LINE INPUT#

## Syntax

```basic
LINE INPUT#<file number>,<string variable>
```

**Versions:** Disk

## Purpose

To read an entire line (up to 254 characters), without delimiters, from a sequential disk data file to a string variable.

## Remarks

<file number> is the number under which the file was OPENed.    <string variable> is the variable name to which the 'line will be assigned.   LINE INPUT# reads all characters in the sequential file up to a carriage return.    It then skips over the carriage return/line feed sequence, and the next LINE INPUT# reads all characters up to the   next   carriage    return.    (If   a line feed/carriage return sequence is encountered, it is preserved.) LINE INPUT# is especially useful if each line of a data file has been broken into fields, or if a BASIC-SO program saved in ASCII mode is being read as data by another program.

## Example

```basic
10 OPEN "O",l,"LIST"
           20 LINE INPUT "CUSTOMER INFORMATION? " :C$
           30 PRINT iI, C$
           40 CLOSE 1
           50 OPEN "I",l,"LIST"
           60 LINE INPUT iI, C$
           70 PRINT C$
           SO 'CLOSE 1
           RUN
           CUSTOMER INFORMATION? LINDA JONES    234,4    MEMPHIS
           LINDA JONES     234,4   MEMPHIS
           Ok
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
- [PUT](put.md) - To write a record from   a   random   buffer   to   a random
- [RESET](reset.md) - Closes all open files
- [RSET](rset.md) - Right-justifies a string in a field for random file output
- [WRITE #](writei.md) - Write data to a sequential file with delimiters
