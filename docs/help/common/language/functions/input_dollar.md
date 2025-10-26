---
category: file-io
description: Returns a string of X characters, read from the terminal or from file
  number Y
keywords:
- data
- else
- file
- for
- function
- goto
- if
- input
- number
- open
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

Returns a string of X characters, read from the terminal or from file number Y. If the terminal is used for input, no characters will be echoed and all control characters are passed through except Control-C, which is used to interrupt the execution of the INPUT$ function. Example 1: 5 ~LIST THE CONTENTS OF A SEQUENTIAL FILE IN HEXADECIMAL 10 OPEN"I",l,"DATA" 20 IF EOF(l) THEN 50 30 PRINT HEX$(ASC(INPUT$(l,#l»); 40 GOTO 20 50 PRINT 60 END Example 2: • 100 PRINT "TYPE P TO PROCEED OR S TO STOP" 110 X$=INPUT$(l) 120 IF X$="P" THEN 500 130 IF X$="S" THEN 700 ELSE 100 BASIC-80 FUNCTIONS Page 3-11

## See Also

*Related functions will be linked here*