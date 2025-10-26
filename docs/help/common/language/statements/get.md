---
category: file-io
description: NEEDS_DESCRIPTION
keywords:
- NEEDS_KEYWORDS
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
See Appendix B.
NOTE:         After a GET statement, INPUT# and LINE INPUT#
              may be done to read characters from the random
              file buffer.
BASIC-80 COMMANDS AND STATEMENTS                        Page 2-32
```

## See Also

*Related statements will be linked here*