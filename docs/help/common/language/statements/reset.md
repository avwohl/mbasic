---
category: file-io
description: Closes all open files
keywords:
- reset
- close
- file
- disk
- buffer
syntax: RESET
title: RESET
type: statement
related: [close, open]
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

- [CLOSE](close.md) - Close specific files or all files
- [OPEN](open.md) - Open file for I/O
- [END](end.md) - End program (also closes files)
