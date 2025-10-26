---
category: input-output
description: Read user input from the terminal during program execution
keywords:
- input
- read
- prompt
- keyboard
- user
- interactive
- question mark
- readline
syntax: 'INPUT[;] ["prompt string";]variable[,variable...]'
related: [print, line-input, read-data]
title: INPUT
type: statement
---

# INPUT

## Syntax

```basic
INPUT[:] [<"prompt string">:]<list of variables>
```

## Purpose

To allow input from the terminal during      program execution.

## Remarks

When an INPUT statement is encountered, program execution pauses and a question mark is printed to indicate the program is waiting for data.  If <"prompt string"> ~s included, the string is printed before the question mark. The required data is then entered at the terminal. A comma may be used instead of a semicolon after the prompt string to suppress the question mark. For example,    the   statement   INPUT   "ENTER BIRTHDATE",B$ will print the prompt with no question mark. If INPUT is immediately followed by a semicolon, then the carriage return typed by the user to input data does not echo a carriage return/line feed sequence. The data that is entered is assigned to the variable(s)   given in <variable list>.    The number of data items supplied must be the same as the number of variables in the list. Data ttems are separated by commas. The variable names in the list may be numeric or string variable names    (including subscripted variables). The type of each data item that is input must agree with the type specified by the variable name.    (Strings input to an INPUT statement need not be surrounded by quotation marks.) Responding to INPUT with too many or too few items, or with the wrong type of value (numeric instead of string, etc.) causes the messsage "?Redo from start" to be printed. No assignment of input values is made until an acceptable response is given. In the 8K version,   INPUT   is   illegal     in   the direct mode. BASIC-80 COMMANDS AND STATEMENTS                   Page 2-37

## Example

```basic
10 INPUT x
            20 PRINT X "SQUARED IS" X"'2
            30 END
            RUN
            ? 5      (The 5 was typed in by the user
                      in response to the question mark.)
             5 SQUARED IS 25
            Ok
            LIST
            10 PI=3.14
            20 INPUT "WHAT IS THE RADIUS":R
            30 A=PI*R"'2
            40 PRINT "THE AREA OF THE CIRCLE IS":A
            50 PRINT
            60 GOTO 20
            Ok
            RUN
            WHAT IS THE RADIUS? 7.4 (User types 7.4)
            THE AREA OF THE CIRCLE IS 171.946
            WHAT IS THE RADIUS?
            etc.
BASlc-ao COMMANDS AND STATEMENTS                        Page 2-38
```

## See Also

*Related statements will be linked here*