---
category: input-output
description: Read user input from the terminal during program execution
keywords: ['input', 'read', 'prompt', 'keyboard', 'user', 'interactive', 'question mark', 'readline']
syntax: INPUT[;] ["prompt string";]variable[,variable...]
related: ['print', 'line-input', 'read-data']
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

When an INPUT statement is executed, the program pauses and waits for the user to enter data from the keyboard. If no prompt string is provided, a question mark (?) is displayed. If a prompt string is included, it is displayed instead of or along with the question mark.

The user enters values separated by commas (for multiple variables) and presses Enter to continue program execution. The entered values are assigned to the variables in the order specified.

Key behaviors:
- Multiple values must be separated by commas
- String values may be entered with or without quotes (quotes are required if the string contains commas)
- If too few values are entered, the prompt is repeated with ?? for the remaining values
- If too many values are entered, the extras are ignored with a ?Redo from start message
- The semicolon after INPUT suppresses the carriage return after the user presses Enter
- A semicolon after the prompt string causes the prompt to be displayed without a question mark


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
```

## See Also
- [LINE INPUT](line-input.md) - To input an entire line (up to 254 characters) to   a string variable, without the use of delimiters
- [PRINT](print.md) - Output text and values to the screen
- [WRITE](write.md) - To output data at the terminal
