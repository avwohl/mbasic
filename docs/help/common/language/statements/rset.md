---
category: file-io
description: Right-justifies a string in a field for random file output
keywords: ['rset', 'file', 'random', 'field', 'justify', 'string', 'format']
syntax: RSET <string variable> = <string expression>
title: RSET
type: statement
related: ['lset', 'field', 'get', 'put', 'open']
---

# RSET

## Syntax

```basic
RSET <string variable> = <string expression>
```

**Versions:** Disk

## Purpose

To right-justify a string in a field for random file I/O operations.

## Remarks

RSET is used with random access files to prepare data for writing with PUT. It assigns the string expression to the string variable, right-justified in the field.

If the string is shorter than the field defined by the string variable, the string is padded on the left with spaces.

If the string is longer than the field, the extra characters on the right are truncated.

RSET is typically used with field variables defined by the FIELD statement to prepare numeric data or right-aligned text for writing to random access files.

## Example

```basic
10 OPEN "R", 1, "DATA.DAT", 32
20 FIELD #1, 20 AS N$, 10 AS A$
30 RSET N$ = "JOHN DOE"
40 RSET A$ = "25"
50 PUT #1, 1
60 CLOSE #1

' N$ will contain "            JOHN DOE" (padded with leading spaces)
' A$ will contain "        25" (padded with leading spaces)
```

## Notes

- RSET does not write to the file - use PUT to write the record
- The string variable should be a field variable defined with FIELD
- Leading spaces are added for padding, trailing spaces are not

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
- [PUT](put.md) - To write a record from a random buffer to a random file
- [RESET](reset.md) - Closes all open files
- [WRITE #](writei.md) - Write data to a sequential file with delimiters
- [~ INPUTi](inputi.md) - To read an entire line (up to 254 characters), without delimiters, from a sequential disk data file to a string variable
