---
category: file-io
description: To read data items from a sequential disk    file and assign them to program variables
keywords: ['command', 'data', 'file', 'for', 'if', 'input', 'line', 'number', 'open', 'print']
syntax: INPUT#<file number>,<variable list>
title: INPUT#
type: statement
---

# INPUT#

## Syntax

```basic
INPUT#<file number>,<variable list>
```

**Versions:** Disk

## Purpose

To read data items from a sequential disk    file and assign them to program variables.

## Remarks

<file number> is the number used when the file was OPENed for input. <variable list> contains the vari?lble names that will be assigned to the items in the file.       (The variable type must match the type specified by the variable name.) With INPUT#, no question mark is printed, as with INPUT. The data items in the file should appear just as they would if data were being typed in response to an INPUT statement.    with numeric values, leading spaces, carriage returns and line feeds are ignored. The first character encountered that is not a space, carriage return or line feed is assumed to be the start of a number. The number terminates on a space, carriage return, line feed or comma. If BASIC-aO is scanning the sequential data file for a string item, leading spaces, carriage returns and line feeds are also ignored.      The first character encountered that is not a space, carriage return, or line feed is assumed to be the start of a string item.         If this first character is a quotation mark   ("), the string item will consist of all characters read between the first quotation mark and the second.    Thus, a quoted string may not contain a quotation mark as a character. If the first character of the string is not a quotation mark, the string is an unquoted string, and will terminate on a comma, carriage or line feed (or after 255 characters have been read). If end of file is reached when a numeric or string item is being INPUT, the item is terminated.

## Example

```basic
See Appendix B.
```

## See Also
- [CLOAD THIS COMMAND IS NOT INCLUDED IN THE DEC VT180 VERSION](cload.md) - To load a program or an array from cassette tape into memory
- [CSAVE THIS COMMAND IS NOT INCLUDED IN THE DEC VT180 VERSION](csave.md) - To save the program or an       array   currently     in memory on cassette tape
- [CVI, CVS, CVD](../functions/cvi-cvs-cvd.md) - Convert string values to numeric values
- [DEFINT/SNG/DBL/STR](defint-sng-dbl-str.md) - To declare variable types as integer,        single precision, double precision, or string
- [ERR AND ERL VARIABLES](err-erl-variables.md) - Error code and error line number variables used in error handling
- [LINE INPUT](line-input.md) - To input an entire line (up to 254 characters) to   a string variable, without the use of delimiters
- [LPRINT AND LPRINT USING](lprint-lprint-using.md) - To print data at the line printer
- [MKI$, MKS$, MKD$](../functions/mki_dollar-mks_dollar-mkd_dollar.md) - Convert numeric values to string values
- [SPACE$](../functions/space_dollar.md) - Returns a string of spaces of length X
- [TAB](../functions/tab.md) - Spaces to position I on the terminal
