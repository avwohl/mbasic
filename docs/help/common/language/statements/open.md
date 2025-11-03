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
- [POS](../functions/pos.md) - Returns the current cursor position
- [PRINTi AND PRINTi USING](printi-printi-using.md) - To write data to a sequential disk file
- [PUT](put.md) - To write a record from a random buffer to a random file
- [RESET](reset.md) - Closes all open files
- [RSET](rset.md) - Right-justifies a string in a field for random file output
- [WRITE #](writei.md) - Write data to a sequential file with delimiters
- [~ INPUTi](inputi.md) - To read an entire line (up to 254 characters), without delimiters, from a sequential disk data file to a string variable
