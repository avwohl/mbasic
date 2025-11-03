---
category: file-io
description: To read a record from a random disk file into    a random buffer
keywords: ['command', 'file', 'get', 'if', 'input', 'line', 'next', 'number', 'open', 'put']
syntax: GET [#]<file number>[,<record number>]
title: GET
type: statement
---

# GET

## Syntax

```basic
GET [#]<file number>[,<record number>]
```

**Versions:** Disk

## Purpose

To read a record from a random disk file into    a random buffer.

## Remarks

<file number> is the number under which the file was OPENed. If <record number> is omitted, the next record (after the last GET)  is read into the buffer. The largest possible record number is 32767.

## Example

```basic
10 OPEN "R", 1, "INVENTORY.DAT", 128
20 FIELD #1, 20 AS ITEM$, 4 AS PRICE$, 2 AS QTY$
30 GET #1, 5  ' Read record 5 into buffer
40 PRINT "Item: "; ITEM$
50 PRINT "Price: "; CVS(PRICE$)
60 PRINT "Quantity: "; CVI(QTY$)
```

**Note:** After a GET statement, INPUT# and LINE INPUT# may be used to read characters from the random file buffer.

## See Also
- [PUT](put.md) - Write a random file record
- [FIELD](field.md) - Define field variables for random file
- [OPEN](open.md) - Open a random access file
- [LSET](lset.md) - Left-justify strings in a field
- [RSET](rset.md) - Right-justify strings in a field
- [CVI, CVS, CVD](../functions/cvi-cvs-cvd.md) - Convert field strings to numbers
- [LOC](../functions/loc.md) - Get next record number for random files
- [LOF](../functions/lof.md) - Get file length
- [EOF](../functions/eof.md) - Test for end of file
- [CLOSE](close.md) - Close file when done
