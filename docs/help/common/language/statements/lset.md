---
category: file-io
description: Left-justifies a string in a field for random file output
keywords: ['lset', 'file', 'random', 'field', 'justify', 'string', 'format']
syntax: LSET <string variable> = <string expression>
title: LSET
type: statement
related: ['rset', 'field', 'get', 'put', 'open']
---

# LSET

## Syntax

```basic
LSET <string variable> = <string expression>
```

**Versions:** Disk

## Purpose

To left-justify a string in a field for random file I/O operations.

## Remarks

LSET is used with random access files to prepare data for writing with PUT. It assigns the string expression to the string variable, left-justified in the field.

If the string is shorter than the field defined by the string variable, the string is padded on the right with spaces.

If the string is longer than the field, the extra characters on the right are truncated.

LSET is typically used with field variables defined by the FIELD statement to prepare data for writing to random access files.

## Example

```basic
10 OPEN "R", 1, "DATA.DAT", 32
20 FIELD #1, 20 AS N$, 10 AS A$
30 LSET N$ = "JOHN DOE"
40 LSET A$ = "25"
50 PUT #1, 1
60 CLOSE #1

' N$ will contain "JOHN DOE            " (padded with spaces)
' A$ will contain "25        " (padded with spaces)
```

## Notes

- LSET does not write to the file - use PUT to write the record
- The string variable should be a field variable defined with FIELD
- Trailing spaces are added for padding, leading spaces are not

## See Also
- [RSET](rset.md) - Right-justify a string in a field
- [FIELD](field.md) - Define field variables for random file
- [GET](get.md) - Read a random file record
- [PUT](put.md) - Write a random file record
- [OPEN](open.md) - Open a file for I/O
- [MKI$, MKS$, MKD$](../functions/mki_dollar-mks_dollar-mkd_dollar.md) - Convert numbers to strings for random files
- [CVI, CVS, CVD](../functions/cvi-cvs-cvd.md) - Convert strings to numbers from random files
- [CLOSE](close.md) - Close file when done
