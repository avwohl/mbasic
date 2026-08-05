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

If the terminal is used for input, nothing is echoed, no Enter is required, and all control characters are passed through except Control-C, which interrupts the INPUT$.

Enter arrives as CHR$(13), as it does on a CP/M console - but a key typed *before* the INPUT$ statement is reached is still waiting in the terminal's own queue, and one typed there arrives as CHR$(10). Test for both if a program can be typed ahead of.

**Note**: Control-C breaks the program at the INPUT$ statement and CONT resumes it, as in MBASIC 5.21. This applies to a CHR$(3) arriving through redirected input as well, which is what MBASIC 5.21 does - so INPUT$ cannot read that byte from the terminal or from stdin. Read binary data from a file instead, with INPUT$(n,#f), where every byte is passed through. One difference from 5.21: it returns silently to the `Ok` prompt, while this implementation prints `Break in nn` - the same message it prints for STOP and for Control-C during INPUT. INKEY$ behaves differently; see [INKEY$](inkey_dollar.md).

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
