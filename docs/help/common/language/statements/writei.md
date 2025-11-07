---
category: file-io
description: Write data to a sequential file with delimiters
keywords: ['write', 'file', 'output', 'sequential', 'data', 'disk']
syntax: WRITE #<file number>, <list of expressions>
title: "WRITE# (File)"
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
- [WRITE](write.md) - Write data to terminal (terminal output)
- [INPUT#](input_hash.md) - Read data from a sequential file
- [PRINT#](printi-printi-using.md) - Write formatted data to a file
- [OPEN](open.md) - Open a file for I/O
- [CLOSE](close.md) - Close an open file
- [EOF](../functions/eof.md) - Test for end of file
- [LOC](../functions/loc.md) - Get current file position
- [LOF](../functions/lof.md) - Get length of file
