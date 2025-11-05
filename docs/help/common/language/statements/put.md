---
category: file-io
description: To write a record from a random buffer to a random file
keywords: ['command', 'error', 'field', 'file', 'for', 'if', 'next', 'number', 'open', 'print']
syntax: PUT [#]<file number>[,<record number>]
title: PUT
type: statement
---

# PUT

## Syntax

```basic
PUT [#]<file number>[,<record number>]
```

**Versions:** Disk

## Purpose

To write a record from a random buffer to a random file.

## Remarks

<file number> is the number under which the file was OPENed. If <record number> is omitted, the record will have the next available record number (after the last PUT). The largest possible record number is 32767. The smallest record number is 1.

## Example

```basic
10 OPEN "R", 1, "INVENTORY.DAT", 128
20 FIELD #1, 20 AS ITEM$, 4 AS PRICE$, 2 AS QTY$
30 LSET ITEM$ = "Widget"
40 LSET PRICE$ = MKS$(29.95)
50 LSET QTY$ = MKI%(100)
60 PUT #1, 5  ' Write to record 5
70 CLOSE #1
```

**Note:** PRINT#, PRINT# USING, and WRITE# may be used to put characters in the random file buffer before a PUT statement. In the case of WRITE#, BASIC-80 pads the buffer with spaces up to the carriage return. Any attempt to read or write past the end of the buffer causes a "Field overflow" error.

## See Also
- [GET](get.md) - Read a random file record
- [FIELD](field.md) - Define field variables for random file
- [OPEN](open.md) - Open a random access file
- [LSET](lset.md) - Left-justify strings in a field
- [RSET](rset.md) - Right-justify strings in a field
- [MKI$, MKS$, MKD$](../functions/mki_dollar-mks_dollar-mkd_dollar.md) - Convert numbers to strings for fields
- [LOC](../functions/loc.md) - Get next record number for random files
- [LOF](../functions/lof.md) - Get file length
- [CLOSE](close.md) - Close file when done
