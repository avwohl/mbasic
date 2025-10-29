---
category: file-io
description: Right-justifies a string in a field for random file output
keywords:
- rset
- file
- random
- field
- justify
- string
- format
syntax: "RSET <string variable> = <string expression>"
title: RSET
type: statement
related: [lset, field, get, put, open]
---

# RSET

## Syntax

```basic
RSET <string variable> = <string expression>
```

**Versions:** Disk

## Purpose

To right-justify a string in a field for random file I/O operations.

## Remarks

RSET is used with random access files to prepare data for writing with PUT. It assigns the string expression to the string variable, right-justified in the field.

If the string is shorter than the field defined by the string variable, the string is padded on the left with spaces.

If the string is longer than the field, the extra characters on the right are truncated.

RSET is typically used with field variables defined by the FIELD statement to prepare numeric data or right-aligned text for writing to random access files.

## Example

```basic
10 OPEN "R", 1, "DATA.DAT", 32
20 FIELD #1, 20 AS N$, 10 AS A$
30 RSET N$ = "JOHN DOE"
40 RSET A$ = "25"
50 PUT #1, 1
60 CLOSE #1

' N$ will contain "            JOHN DOE" (padded with leading spaces)
' A$ will contain "        25" (padded with leading spaces)
```

## Notes

- RSET does not write to the file - use PUT to write the record
- The string variable should be a field variable defined with FIELD
- Leading spaces are added for padding, trailing spaces are not

## See Also

- [LSET](lset.md) - Left-justify string in field
- FIELD - Define fields for random file access (not yet documented)
- [PUT](put.md) - Write record to random file
- [GET](get.md) - Read record from random file
- [OPEN](open.md) - Open file for I/O
