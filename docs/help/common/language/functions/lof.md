---
category: file-io
description: Returns the length of a file in bytes
keywords:
- lof
- file
- length
- size
- bytes
- function
- disk
syntax: "LOF(file number)"
related: [eof, loc, open]
title: LOF
type: function
---

# LOF

## Syntax

```basic
LOF(file number)
```

**Versions:** Disk

## Description

Returns the length of the file associated with the specified file number, in bytes. The file must be currently open.

LOF is useful for:
- Determining file size before reading
- Allocating space for file contents
- Validating file sizes
- Computing file positions and offsets

## Example

```basic
10 OPEN "DATA.TXT" FOR INPUT AS #1
20 PRINT "File size:"; LOF(1); "bytes"
30 CLOSE #1
Ok

10 OPEN "R", #1, "RANDOM.DAT", 128
20 RECORDS = LOF(1) / 128
30 PRINT "File contains"; RECORDS; "records"
40 CLOSE #1
```

## Notes

- The file number must refer to an open file
- Returns the total file size, not the current position
- For random access files, divide by record length to get record count

## See Also

- [EOF](eof.md) - Test for end of file
- LOC - Get current position in file (not yet documented)
- OPEN - Open a file for reading or writing (not yet documented)
