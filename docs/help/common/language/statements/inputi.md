---
category: file-io
description: To read an entire line from a sequential file to a string variable
keywords: ['close', 'command', 'data', 'field', 'file', 'for', 'if', 'input', 'line']
syntax: LINE INPUT#<file number>,<string variable>
title: "LINE INPUT# (File)"
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

<file number> is the number under which the file was OPENed. <string variable> is the variable name to which the line will be assigned. LINE INPUT# reads all characters in the sequential file up to a carriage return. It then skips over the carriage return/line feed sequence, and the next LINE INPUT# reads all characters up to the next carriage return. (If a line feed/carriage return sequence is encountered, it is preserved.) LINE INPUT# is especially useful if each line of a data file has been broken into fields, or if a BASIC-80 program saved in ASCII mode is being read as data by another program.

## Example

```basic
10 OPEN "O", 1, "LIST"
20 LINE INPUT "CUSTOMER INFORMATION? "; C$
30 PRINT #1, C$
40 CLOSE 1
50 OPEN "I", 1, "LIST"
60 LINE INPUT #1, C$
70 PRINT C$
80 CLOSE 1
```

Output:
```
CUSTOMER INFORMATION? LINDA JONES  234,4  MEMPHIS
LINDA JONES  234,4  MEMPHIS
Ok
```

## See Also
- [OPEN](open.md) - Open a file for input
- [CLOSE](close.md) - Close the file when done
- [INPUT#](input_hash.md) - Read data from sequential file
- [LINE INPUT](line-input.md) - Read entire line from keyboard
- [PRINT#](printi-printi-using.md) - Write data to sequential file
- [EOF](../functions/eof.md) - Test for end of file
- [LOF](../functions/lof.md) - Get file length
