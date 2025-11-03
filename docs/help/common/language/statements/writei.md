---
category: file-io
description: Write data to a sequential file with delimiters
keywords: ['write', 'file', 'output', 'sequential', 'data', 'disk']
syntax: WRITE #<file number>, <list of expressions>
title: WRITE #
type: statement
related: ['print', 'input', 'open', 'close']
---

# WRITE #

## Syntax

```basic
WRITE #<file number>, <list of expressions>
```

**Versions:** Disk

## Purpose

To write data to a sequential file in a format that can be easily read back with INPUT #.

## Remarks

WRITE # outputs data to a sequential file opened for output (mode "O") or append (mode "A"). Unlike PRINT #, WRITE # formats the data with:
- Strings enclosed in quotation marks
- Numeric values without leading/trailing spaces
- Commas separating each value

This format makes it easy to read the data back using INPUT # statements, as the delimiters and quotes are automatically handled.

The file must be opened for sequential output before using WRITE #.

## Example

```basic
10 OPEN "O", 1, "DATA.TXT"
20 WRITE #1, "John Doe", 25, "Engineer"
30 WRITE #1, "Jane Smith", 30, "Manager"
40 CLOSE #1

' File contents:
' "John Doe",25,"Engineer"
' "Jane Smith",30,"Manager"

100 OPEN "I", 1, "DATA.TXT"
110 INPUT #1, N$, A, J$
120 PRINT N$, A, J$
130 CLOSE #1
```

## Notes

- Strings are always quoted, making them safe for reading with INPUT #
- Numeric values have no leading/trailing spaces
- Each WRITE # adds a newline at the end
- Use PRINT # for more control over output formatting
- The file number must refer to a file opened for output ("O") or append ("A")

## See Also
- [CLOSE](close.md) - To conclude I/O to a disk file
- [EOF](../functions/eof.md) - Returns -1 (true) if the end of a sequential file has been reached
- [FIELD](field.md) - To allocate space for variables in a random file buffer
- [FILES](files.md) - Displays the directory of files on disk
- [GET](get.md) - To read a record from a random disk file into    a random buffer
- [INPUT](input.md) - Read user input from the terminal during program execution
- [INPUT$](../functions/input_dollar.md) - Returns a string of X characters, read from the terminal or from file number Y
- [LOC](../functions/loc.md) - With random disk files, LOC returns the next record number to be used if a GET or PUT (without a record number) is executed
- [LOF](../functions/lof.md) - Returns the length of a file in bytes
- [LPOS](../functions/lpos.md) - Returns the current position of the line printer print head within the line printer buffer
- [LSET](lset.md) - Left-justifies a string in a field for random file output
- [OPEN](open.md) - To allow I/O to a disk file
- [POS](../functions/pos.md) - Returns the current cursor position
- [PRINT](print.md) - Output text and values to the screen
- [PRINTi AND PRINTi USING](printi-printi-using.md) - To write data to a sequential disk file
- [PUT](put.md) - To write a record from a random buffer to a random file
- [RESET](reset.md) - Closes all open files
- [RSET](rset.md) - Right-justifies a string in a field for random file output
- [~ INPUTi](inputi.md) - To read an entire line (up to 254 characters), without delimiters, from a sequential disk data file to a string variable
