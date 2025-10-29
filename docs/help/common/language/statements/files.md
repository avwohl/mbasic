---
category: file-io
description: Displays the directory of files on disk
keywords:
- files
- directory
- list
- disk
- catalog
syntax: FILES [filespec]
title: FILES
type: statement
related: [kill, name, open]
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

- [OPEN](open.md) - Open file for I/O
- KILL - Delete a file (not yet documented)
- NAME - Rename a file (not yet documented)
