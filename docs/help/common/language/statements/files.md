---
category: file-io
description: Displays the directory of files on disk
keywords: ['files', 'directory', 'list', 'disk', 'catalog']
syntax: FILES [filespec]
title: FILES
type: statement
related: ['kill', 'name', 'open']
---

# FILES

## Syntax

```basic
FILES [<filespec>]
```

**Versions:** Disk

## Purpose

To display the directory of files on the current or specified disk drive.

## Remarks

The FILES statement lists the directory of files matching the optional filespec. If no filespec is provided, all files in the current directory are displayed.

The filespec may include:
- Drive letter (A:, B:, etc.)
- Filename with or without extension
- Wildcard characters (* and ?)

The display shows:
- Filenames and extensions
- File sizes (implementation dependent)
- Number of bytes free on disk (implementation dependent)

## Example

```basic
FILES
' Lists all files in current directory

FILES "*.BAS"
' Lists all BASIC program files

FILES "B:DATA.*"
' Lists all DATA files on drive B

10 FILES "*.TXT"
20 INPUT "Enter filename"; F$
30 OPEN "I", 1, F$
```

## Notes

- The exact format of the directory listing is system-dependent
- Wildcard * matches any sequence of characters
- Wildcard ? matches any single character
- FILES does not change the current directory

## See Also
- [CLOSE](close.md) - To conclude I/O to a disk file
- [EOF](../functions/eof.md) - Returns -1 (true) if the end of a sequential file has been reached
- [FIELD](field.md) - To allocate space for variables in a random file buffer
- [GET](get.md) - To read a record from a random disk file into    a random buffer
- [INPUT$](../functions/input_dollar.md) - Returns a string of X characters, read from the terminal or from file number Y
- [KILL](kill.md) - To delete a file from disk
- [LOC](../functions/loc.md) - With random disk files, LOC returns the next record number to be used if a GET or PUT (without a record number) is executed
- [LOF](../functions/lof.md) - Returns the length of a file in bytes
- [LPOS](../functions/lpos.md) - Returns the current position of the line printer print head within the line printer buffer
- [LSET](lset.md) - Left-justifies a string in a field for random file output
- [NAME](name.md) - To change the name of a disk file
- [OPEN](open.md) - To allow I/O to a disk file
- [POS](../functions/pos.md) - Returns the current cursor position
- [PRINTi AND PRINTi USING](printi-printi-using.md) - To write data to a sequential disk file
- [PUT](put.md) - To write a record from a random buffer to a random file
- [RESET](reset.md) - Closes all open files
- [RSET](rset.md) - Right-justifies a string in a field for random file output
- [WRITE #](writei.md) - Write data to a sequential file with delimiters
- [~ INPUTi](inputi.md) - To read an entire line (up to 254 characters), without delimiters, from a sequential disk data file to a string variable
