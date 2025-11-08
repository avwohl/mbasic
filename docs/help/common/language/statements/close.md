---
category: file-io
description: To conclude I/O to a disk file
keywords: ['close', 'command', 'file', 'for', 'if', 'number', 'open', 'put', 'statement', 'then']
syntax: CLOSE[[#]<file number>[,[#]<file number>...]]
title: CLOSE
type: statement
---

# CLOSE

## Syntax

```basic
CLOSE[[#]<file number>[,[#]<file number>...]]
```

## Purpose

To conclude I/O to a disk file.

## Remarks

<file number> is the number under which the file was OPENed. A CLOSE with no arguments closes all open files. The association between a particular file and file number terminates upon execution of a CLOSE. The file may then be reOPENed using the same or a different file number; likewise, that file number may now be reused to OPEN any file. A CLOSE for a sequential output file writes the final buffer of output. The END statement and the NEW command always CLOSE all disk files automatically. (STOP does not close disk files.)

## Example

**Close a single file:**
```basic
10 OPEN "O", 1, "OUTPUT.TXT"
20 PRINT #1, "Hello, World!"
30 CLOSE 1
```

**Close multiple files:**
```basic
10 OPEN "O", 1, "FILE1.TXT"
20 OPEN "O", 2, "FILE2.TXT"
30 OPEN "O", 3, "FILE3.TXT"
40 REM ... write data ...
50 CLOSE 1, 2, 3
```

**Close all files:**
```basic
10 CLOSE
```

## See Also
- [OPEN](open.md) - Open a file for I/O
- [RESET](reset.md) - Close all open files
- [END](end.md) - End program and close all files
- [STOP](stop.md) - Stop program (doesn't close files)
- [EOF](../functions/eof.md) - Test for end of file
