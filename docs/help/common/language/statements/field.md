---
category: file-io
description: To allocate space for variables in a random file buffer
keywords: ['command', 'data', 'error', 'execute', 'field', 'file', 'for', 'get', 'if', 'input']
syntax: FIELD[i]<file number>,<field width> AS <string variable> •••
title: FIELD
type: statement
---

# FIELD

## Syntax

```basic
FIELD[i]<file number>,<field width> AS <string variable> •••
```

**Versions:** Disk

## Purpose

To allocate space for variables in a random file buffer.

## Remarks

To get data out of a random buffer after a GET or to enter data before a PUT, a FIELD statement must have been executed. <file number> is the number und~r which the file was OPENed.    <field width> is the number of characters to be allocated to <string variable>. For example, FIELD 1, 20 AS N$, 10 AS ID$, 40 AS ADD$ allocates the first 20 positions. (bytes) in the· random file buffer to the string variable N$, the next 10 positions to ID$, and the next 40 positions to ADD$.     FIELD does NOT place any data in the random file buffer.   (See LSET/RSET and GET.) The total number of bytes allocated in a FIELD statement must not exceed the record length that was specified when the      file    was  OPENed. Otherwise, a "Field overflow" error occurs. (The default record length is l28.) Any number of FIELD statements may be executed for the same file, and all FIELD statements that have been executed are in effect at the same time.

## Example

```basic
See Appendix B.
NOTE:            ~  !!2! ~ a FIELDed var iable name in an I.NPUT
                 or LET statement.     Once a -viriable--name is
                 FIELDed, it points to the correct place in the
                 random file buffer.     If a subsequent INPUT or
                 LET statement with that variable       name   is
                 executed, the variable~s pointer is moved to
                 string space.
```

## See Also
- [CLOSE](close.md) - To conclude I/O to a disk file
- [EOF](../functions/eof.md) - Returns -1 (true) if the end of a sequential file has been reached
- [FILES](files.md) - Displays the directory of files on disk
- [GET](get.md) - To read a record from a random disk file into    a random buffer
- [INPUT$](../functions/input_dollar.md) - Returns a string of X characters, read from the terminal or from file number Y
- [LOC](../functions/loc.md) - With random disk files, LOC returns the next record number to be used if a GET or PUT (without a record number) is executed
- [LOF](../functions/lof.md) - Returns the length of a file in bytes
- [LPOS](../functions/lpos.md) - Returns the current position of the line printer print head within the line printer buffer
- [LSET](lset.md) - Left-justifies a string in a field for random file output
- [OPEN](open.md) - To allow I/O to a disk file
- [POS](../functions/pos.md) - Returns the current cursor position
- [PRINTi AND PRINTi USING](printi-printi-using.md) - To write data to a sequential disk file
- [PUT](put.md) - To write a record from a random buffer to a random file
- [RESET](reset.md) - Closes all open files
- [RSET](rset.md) - Right-justifies a string in a field for random file output
- [WRITE #](writei.md) - Write data to a sequential file with delimiters
- [~ INPUTi](inputi.md) - To read an entire line (up to 254 characters), without delimiters, from a sequential disk data file to a string variable
