---
category: file-io
description: To allocate space for variables in a random file buffer
keywords: ['command', 'data', 'error', 'execute', 'field', 'file', 'for', 'get', 'if', 'input']
syntax: FIELD [#]<file number>,<field width> AS <string variable>[,<field width> AS <string variable>...]
title: FIELD
type: statement
---

# FIELD

## Syntax

```basic
FIELD [#]<file number>,<field width> AS <string variable>[,<field width> AS <string variable>...]
```

**Versions:** Disk

## Purpose

To allocate space for variables in a random file buffer.

## Remarks

To get data out of a random buffer after a GET or to enter data before a PUT, a FIELD statement must have been executed. `<file number>` is the number under which the file was OPENed. `<field width>` is the number of characters to be allocated to `<string variable>`.

For example, FIELD 1, 20 AS N$, 10 AS ID$, 40 AS ADD$ allocates the first 20 positions (bytes) in the random file buffer to the string variable N$, the next 10 positions to ID$, and the next 40 positions to ADD$.

FIELD does NOT place any data in the random file buffer. (See LSET/RSET and GET.)

The total number of bytes allocated in a FIELD statement must not exceed the record length that was specified when the file was OPENed. Otherwise, a "Field overflow" error occurs. (The default record length is 128.)

Any number of FIELD statements may be executed for the same file, and all FIELD statements that have been executed are in effect at the same time.

## Example

```basic
10 OPEN "R", 1, "CUSTOMER.DAT", 128
20 FIELD #1, 30 AS NAME$, 20 AS ADDR$, 15 AS CITY$, 2 AS STATE$, 5 AS ZIP$
30 ' Now the buffer is fielded:
40 ' Positions 1-30: NAME$
50 ' Positions 31-50: ADDR$
60 ' Positions 51-65: CITY$
70 ' Positions 66-67: STATE$
80 ' Positions 68-72: ZIP$
```

**Note:** Do not use a FIELDed variable name in an INPUT or LET statement. Once a variable name is FIELDed, it points to the correct place in the random file buffer. If a subsequent INPUT or LET statement with that variable name is executed, the variable's pointer is moved to string space.

## See Also
- [OPEN](open.md) - Open a random access file
- [LSET](lset.md) - Left-justify strings in a field
- [RSET](rset.md) - Right-justify strings in a field
- [GET](get.md) - Read a random file record
- [PUT](put.md) - Write a random file record
- [MKI$, MKS$, MKD$](../functions/mki_dollar-mks_dollar-mkd_dollar.md) - Convert numbers to strings for fields
- [CVI, CVS, CVD](../functions/cvi-cvs-cvd.md) - Convert field strings to numbers
- [CLOSE](close.md) - Close file when done
