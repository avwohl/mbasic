---
category: file-io
description: To input an entire line (up to 254 characters) to   a string variable, without the use of delimiters
keywords: ['command', 'for', 'if', 'input', 'line', 'print', 'put', 'return', 'statement', 'string']
syntax: LINE INPUT[i] [<"prompt string">i]<string variable>
title: LINE INPUT
type: statement
---

# LINE INPUT

## Syntax

```basic
LINE INPUT[i] [<"prompt string">i]<string variable>
```

## Purpose

To input an entire line (up to 254 characters) to   a string variable, without the use of delimiters.

## Remarks

The prompt string is a string literal that is printed   at    the  terminal before input is accepted. A question mark is not printed unless it is part of the prompt string. All input from the end of the prompt to the carriage return is assigned to <string variable>. If LINE INPUT is immediately followed by a semicolon, then the carriage return typed by the user to end the input line does not echo a carriage   return/line    feed sequence at the terminal. A LINE INPUT may be escaped by typing Control-C. BASIC-SO will return to command level and type Ok. Typing CONT resumes execution at the LINE INPUT.

## Example

```basic
See Example, Section 2.32, LINE INPUT#.
```

## See Also
- [CLOAD THIS COMMAND IS NOT INCLUDED IN THE DEC VT180 VERSION](cload.md) - To load a program or an array from cassette tape into memory
- [CSAVE THIS COMMAND IS NOT INCLUDED IN THE DEC VT180 VERSION](csave.md) - To save the program or an       array   currently     in memory on cassette tape
- [CVI, CVS, CVD](../functions/cvi-cvs-cvd.md) - Convert string values to numeric values
- [DEFINT/SNG/DBL/STR](defint-sng-dbl-str.md) - To declare variable types as integer,        single precision, double precision, or string
- [ERR AND ERL VARIABLES](err-erl-variables.md) - Error code and error line number variables used in error handling
- [INPUT#](input_hash.md) - To read data items from a sequential disk    file and assign them to program variables
- [LPRINT AND LPRINT USING](lprint-lprint-using.md) - To print data at the line printer
- [MKI$, MKS$, MKD$](../functions/mki_dollar-mks_dollar-mkd_dollar.md) - Convert numeric values to string values
- [SPACE$](../functions/space_dollar.md) - Returns a string of spaces of length X
- [TAB](../functions/tab.md) - Spaces to position I on the terminal
