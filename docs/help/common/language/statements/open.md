---
category: file-io
description: To allow I/O to a disk file
keywords: ['command', 'file', 'for', 'if', 'input', 'number', 'open', 'put', 'statement', 'string']
syntax: OPEN <mode>, [#]<file number>,<filename>, [<reclen>]
title: OPEN
type: statement
---

# OPEN

## Syntax

```basic
OPEN <mode>, [#]<file number>,<filename>, [<reclen>]
```

**Versions:** Disk

## Purpose

To allow I/O to a disk file.

## Remarks

A disk file must be OPENed before any disk I/O operation can be performed on that file. OPEN allocates a buffer for I/O to the file and determines the mode of access that will be used with the buffer. <mode> is a string expression whose          first character is one of the following: o        specifies sequential output mode I       specifies sequential input mode R        specifies random input/output mode <file number> is an integer expression whose value is between one and fifteen. The number is then associated with the file for as long as it is OPEN and is used to refer other disk I/O statements to the file. <filename> is a string expression containing a name that conforms to your operating system~s rules for disk filenames. <reclen> is an integer expression which, if included, sets the record length for random files. The default record length is 128 bytes. See also page A-3. NOTE:          A file can be OPENed for sequential input or random access on more than one file number at a time. A file may be OPENed for output, however, on only one file number at a time.

## Example

```basic
10 OPEN "I",2,"INVEN"
               See also Appendix B.
```

## See Also
- [CLOSE](close.md) - Close an open file
- [INPUT#](input_hash.md) - Read from sequential file
- [PRINT#](printi-printi-using.md) - Write to sequential file
- [GET](get.md) - Read from random file
- [PUT](put.md) - Write to random file
- [FIELD](field.md) - Define random file fields
- [EOF](../functions/eof.md) - Test for end of file
- [LOC](../functions/loc.md) - Get current file position
- [LOF](../functions/lof.md) - Get file length
