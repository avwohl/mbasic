---
category: file-io
description: NEEDS_DESCRIPTION
keywords:
- NEEDS_KEYWORDS
title: PUT
type: statement
---

# PUT

## Syntax

```basic
PUT (#]<file number>(,<record number>]
```

**Versions:** Disk

## Purpose

To write a record from   a   random   buffer   to   a random. disk file.

## Remarks

<file number> is the number under which the file was OPENed. If <record number> is omitted, the record will have the next available record number   (after the last PUT).      The largest possible record number is 32767.   The smallest record number is 1.

## Example

```basic
See Appendix B.
NOTE:         PRINT#, PRINT# USING, and WRITE# may be used to
              put characters in the random file buffer before
              a PUT statement.
              In the case of WRITE#, BASIC-80 pads the buffer
              with spaces up to the carriage return. Any
              attempt to read or write past the end of the
              buffer causes a "Field overflow" error.
BASIC-80 COMMANDS AND STATEMENTS                          Page 2-69
```

## See Also

*Related statements will be linked here*