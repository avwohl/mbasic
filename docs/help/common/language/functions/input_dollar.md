---
category: file-io
description: Returns a string of X characters, read from the terminal or from file number Y
keywords: ['data', 'else', 'file', 'for', 'function', 'goto', 'if', 'input', 'number', 'open']
syntax: INPUT$(X[,[#]Y])
title: INPUT$
type: function
---

# INPUT$

## Syntax

```basic
INPUT$(X[,[#]Y])
```

**Versions:** Disk

## Description

Returns a string of X characters, read from the terminal or from file number Y.

If the terminal is used for input, no characters will be echoed and all control characters are passed through.

**Note**: In original MBASIC, Control-C would interrupt the INPUT$ function. This implementation passes Control-C through to the program (it can be detected and handled).

## Example

```basic
' Example 1: List contents of a sequential file in hexadecimal
10 OPEN "I", 1, "DATA"
20 IF EOF(1) THEN 50
30 PRINT HEX$(ASC(INPUT$(1, #1)));
40 GOTO 20
50 PRINT
60 END

' Example 2: Get single character from user
100 PRINT "TYPE P TO PROCEED OR S TO STOP"
110 X$ = INPUT$(1)
120 IF X$ = "P" THEN 500
130 IF X$ = "S" THEN 700 ELSE 100
```

## See Also
- [INKEY$](inkey_dollar.md) - Read single character without waiting
- [INPUT](../statements/input.md) - Read input from keyboard
- [LINE INPUT](../statements/line-input.md) - Read entire line from keyboard
- [INPUT#](../statements/input_hash.md) - Read data from file
- [OPEN](../statements/open.md) - Open a file for input
- [EOF](eof.md) - Test for end of file
