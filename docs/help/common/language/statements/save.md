---
category: file-management
description: To save a program file on disk
keywords: ['command', 'file', 'for', 'if', 'program', 'read', 'save', 'statement', 'string']
syntax: SAVE <filename> [,A][,P]
title: SAVE
type: statement
---

# SAVE

## Syntax

```basic
SAVE <filename> [,A][,P]
```

**Versions:** Disk

## Purpose

To save a program file on disk.

## Remarks

`<filename>` is a quoted string that conforms to your operating system's requirements for filenames. (With CP/M, the default extension .BAS is supplied.) If `<filename>` already exists, the file will be written over.

### Options

- **,A** - Save the file in ASCII format. Otherwise, BASIC saves the file in a compressed binary format. ASCII format takes more space on the disk, but some disk access requires that files be in ASCII format. For instance, the MERGE command requires an ASCII format file, and some operating system commands such as LIST may require an ASCII format file.

- **,P** - Protect the file by saving it in an encoded binary format. When a protected file is later RUN (or LOADed), any attempt to list or edit it will fail.

## Example

```basic
SAVE "MYPROGRAM.BAS"
SAVE "MYPROGRAM.BAS", A  ' Save in ASCII format
SAVE "SECRET.BAS", P     ' Save as protected file

' To save current program with a user-specified name:
10 INPUT "Filename"; F$
20 SAVE F$
```

## See Also
- [KILL](kill.md) - To delete a file from disk
- [LOAD](load.md) - To load a file from disk into memory
- [MERGE](merge.md) - To merge a specified disk file into the      program currently in memory
- [NAME](name.md) - To change the name of a disk file
