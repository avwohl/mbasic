---
category: file-io
description: To read data items from a sequential disk file and assign them to program variables
keywords: ['command', 'data', 'file', 'for', 'if', 'input', 'line', 'number', 'open', 'print']
syntax: INPUT#<file number>,<variable list>
title: "INPUT# (File)"
type: statement
---

# INPUT#

## Syntax

```basic
INPUT#<file number>,<variable list>
```

**Versions:** Disk

## Purpose

To read data items from a sequential disk file and assign them to program variables.

## Remarks

<file number> is the number used when the file was OPENed for input. <variable list> contains the variable names that will be assigned to the items in the file. (The variable type must match the type specified by the variable name.) With INPUT#, no question mark is printed, as with INPUT. The data items in the file should appear just as they would if data were being typed in response to an INPUT statement. With numeric values, leading spaces, carriage returns and line feeds are ignored. The first character encountered that is not a space, carriage return or line feed is assumed to be the start of a number. The number terminates on a space, carriage return, line feed or comma. If BASIC-80 is scanning the sequential data file for a string item, leading spaces, carriage returns and line feeds are also ignored. The first character encountered that is not a space, carriage return, or line feed is assumed to be the start of a string item. If this first character is a quotation mark ("), the string item will consist of all characters read between the first quotation mark and the second. Thus, a quoted string may not contain a quotation mark as a character. If the first character of the string is not a quotation mark, the string is an unquoted string, and will terminate on a comma, carriage or line feed (or after 255 characters have been read). If end of file is reached when a numeric or string item is being INPUT, the item is terminated.

## Example

```basic
10 OPEN "I", 1, "DATA.TXT"
20 IF EOF(1) THEN 60
30 INPUT #1, NAME$, AGE, SALARY
40 PRINT NAME$; " is "; AGE; " years old, earning $"; SALARY
50 GOTO 20
60 CLOSE #1
```

## See Also
- [OPEN](open.md) - Open a file for input/output
- [CLOSE](close.md) - Close an open file
- [PRINT#](printi-printi-using.md) - Write data to a sequential file
- [LINE INPUT#](line-input.md) - Read an entire line from a file
- [INPUT](input.md) - Read input from keyboard
- [EOF](../functions/eof.md) - Test for end of file
- [LOC](../functions/loc.md) - Get current file position
- [LOF](../functions/lof.md) - Get length of file
