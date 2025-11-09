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
INPUT[;] ["prompt string"[;|,]]variable[,variable...]
```

## Purpose

To allow input from the terminal during program execution.

## Remarks

When an INPUT statement is executed, the program pauses and waits for the user to enter data from the keyboard. If no prompt string is provided, a question mark (?) is displayed. If a prompt string is included, it is displayed instead of or along with the question mark.

The user enters values separated by commas (for multiple variables) and presses Enter to continue program execution. The entered values are assigned to the variables in the order specified.

Key behaviors:
- Multiple values must be separated by commas
- String values may be entered with or without quotes (quotes are required if the string contains commas)
- If too few values are entered, the prompt is repeated with ?? for the remaining values
- If too many values are entered, a "?Redo from start" message is displayed and the user must re-enter all values
- A semicolon immediately after INPUT suppresses the carriage return/line feed after the user presses Enter
- A semicolon after the prompt string causes the prompt to be displayed without a question mark


## Example

### Example 1: Basic Input

```basic
10 INPUT X
20 PRINT X "SQUARED IS" X^2
30 END
```

Output:
```
? 5
 5 SQUARED IS 25
```

### Example 2: Input with Prompt

```basic
10 PI = 3.14
20 INPUT "WHAT IS THE RADIUS"; R
30 A = PI * R^2
40 PRINT "THE AREA OF THE CIRCLE IS"; A
50 PRINT
60 GOTO 20
```

Output:
```
WHAT IS THE RADIUS? 7.4
THE AREA OF THE CIRCLE IS 171.9464

WHAT IS THE RADIUS? _
```

## See Also
- [LINE INPUT](line-input.md) - To input an entire line (up to 254 characters) to a string variable, without the use of delimiters
- [PRINT](print.md) - Output text and values to the screen
- [INPUT#](input_hash.md) - Read data from a sequential file
- [READ](read.md) - Read values from DATA statements
- [WRITE](write.md) - To output data at the terminal
