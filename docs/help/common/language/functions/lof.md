---
category: file-io
description: Returns the length of a file in bytes
keywords: ['lof', 'file', 'length', 'size', 'bytes', 'function', 'disk']
syntax: LOF(file number)
related: ['eof', 'loc', 'open']
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
- [CLOSE](../statements/close.md) - To conclude I/O to a disk file
- [EOF](eof.md) - Returns -1 (true) if the end of a sequential file has been reached
- [FIELD](../statements/field.md) - To allocate space for variables in a random file buffer
- [FILES](../statements/files.md) - Displays the directory of files on disk
- [GET](../statements/get.md) - To read a record from a random disk file into    a random buffer
- [INPUT$](input_dollar.md) - Returns a string of X characters, read from the terminal or from file number Y
- [LOC](loc.md) - Returns current file position/record number (LOF returns total size in bytes)
- [LPOS](lpos.md) - Returns the current position of the line printer print head within the line printer buffer
- [LSET](../statements/lset.md) - Left-justifies a string in a field for random file output
- [OPEN](../statements/open.md) - To allow I/O to a disk file
- [POS](pos.md) - Returns the current cursor position
- [PRINTi AND PRINTi USING](../statements/printi-printi-using.md) - To write data to a sequential disk file
- [PUT](../statements/put.md) - To write a record from a random buffer to a random file
- [RESET](../statements/reset.md) - Closes all open files
- [RSET](../statements/rset.md) - Right-justifies a string in a field for random file output
- [WRITE #](../statements/writei.md) - Write data to a sequential file with delimiters
- [LINE INPUT#](../statements/inputi.md) - To read an entire line (up to 254 characters), without delimiters, from a sequential disk data file to a string variable
