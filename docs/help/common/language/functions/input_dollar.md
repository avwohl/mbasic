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

Returns a string of X characters, read from the terminal or from file number Y. If the terminal is used for input, no characters will be echoed and all control characters are passed through except Control-C, which is used to interrupt the execution of the INPUT$ function. Example 1: 5 ~LIST THE CONTENTS OF A SEQUENTIAL FILE IN HEXADECIMAL 10 OPEN"I",l,"DATA" 20 IF EOF(l) THEN 50 30 PRINT HEX$(ASC(INPUT$(l,#l»); 40 GOTO 20 50 PRINT 60 END Example 2: • 100 PRINT "TYPE P TO PROCEED OR S TO STOP" 110 X$=INPUT$(l) 120 IF X$="P" THEN 500 130 IF X$="S" THEN 700 ELSE 100 BASIC-80 FUNCTIONS Page 3-11

## See Also
- [CLOSE](../statements/close.md) - To conclude I/O to a disk file
- [EOF](eof.md) - Returns -1 (true) if the end of a sequential file has been reached
- [FIELD](../statements/field.md) - To allocate space for variables in a random file buffer
- [FILES](../statements/files.md) - Displays the directory of files on disk
- [GET](../statements/get.md) - To read a record from a random disk file into    a random buffer
- [LOC](loc.md) - With random disk files, LOC returns the next record number to be used if a GET or PUT (without a record number) is executed
- [LOF](lof.md) - Returns the length of a file in bytes
- [LPOS](lpos.md) - Returns the current position of the line printer print head within the line printer buffer
- [LSET](../statements/lset.md) - Left-justifies a string in a field for random file output
- [OPEN](../statements/open.md) - To allow I/O to a disk file
- [POS](pos.md) - Returns the current cursor position
- [PRINTi AND PRINTi USING](../statements/printi-printi-using.md) - To write data to a sequential disk file
- [PUT](../statements/put.md) - To write a record from a random buffer to a random file
- [RESET](../statements/reset.md) - Closes all open files
- [RSET](../statements/rset.md) - Right-justifies a string in a field for random file output
- [WRITE #](../statements/writei.md) - Write data to a sequential file with delimiters
- [~ INPUTi](../statements/inputi.md) - To read an entire line (up to 254 characters), without delimiters, from a sequential disk data file to a string variable
