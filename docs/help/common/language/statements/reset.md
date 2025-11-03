---
category: file-io
description: Closes all open files
keywords: ['reset', 'close', 'file', 'disk', 'buffer']
syntax: RESET
title: RESET
type: statement
related: ['close', 'open']
---

# RESET

## Syntax

```basic
RESET
```

**Versions:** Disk

## Purpose

To close all open disk files.

## Remarks

The RESET statement closes all files that have been opened with OPEN statements. It performs the same function as executing CLOSE without any file numbers, effectively closing all files at once.

When RESET executes:
- All file buffers are flushed to disk
- All file numbers become available for reuse
- File access ends for all open files

RESET is useful for:
- Ensuring all files are closed before program termination
- Recovering from errors that may have left files open
- Preparing for a clean program restart

## Example

```basic
10 OPEN "I", 1, "DATA1.TXT"
20 OPEN "O", 2, "DATA2.TXT"
30 ' ... process files ...
40 RESET
50 PRINT "All files closed"

100 ON ERROR GOTO 200
110 ' ... file operations ...
120 END
200 RESET  ' Close all files on error
210 PRINT "Error - files closed"
```

## Notes

- RESET is equivalent to CLOSE with no parameters
- All file buffers are flushed before files are closed
- Use CLOSE #n to close specific files selectively

## See Also
- [CLOSE](close.md) - To conclude I/O to a disk file
- [EOF](../functions/eof.md) - Returns -1 (true) if the end of a sequential file has been reached
- [FIELD](field.md) - To allocate space for variables in a random file buffer
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
- [RSET](rset.md) - Right-justifies a string in a field for random file output
- [WRITE #](writei.md) - Write data to a sequential file with delimiters
- [~ INPUTi](inputi.md) - To read an entire line (up to 254 characters), without delimiters, from a sequential disk data file to a string variable
