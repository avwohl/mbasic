---
category: file-management
description: To merge a specified disk file into the program currently in memory
keywords: ['command', 'error', 'file', 'for', 'if', 'line', 'merge', 'number', 'program', 'return']
syntax: MERGE <filename>
title: MERGE
type: statement
---

# MERGE

## Syntax

```basic
MERGE <filename>
```

**Versions:** Disk

## Purpose

To merge a specified disk file into the program currently in memory.

## Remarks

<filename> is the name used when the file was SAVEd. (With CP/M, the default extension .BAS is supplied if none is specified.) The file must have been SAVEd in ASCII format. (If not, a "Bad file mode" error occurs.)

If any lines in the disk file have the same line numbers as lines in the program in memory, the lines from the file on disk will replace the corresponding lines in memory. (MERGEing may be thought of as "inserting" the program lines on disk into the program in memory.)

**File handling:** Unlike LOAD (without ,R), MERGE does **NOT close open files**. Files that are open before MERGE remain open after MERGE completes. (Compare with [LOAD](load.md) which closes files except when using the ,R option.)

BASIC-80 always returns to command level after executing a MERGE command.

## Example

```basic
MERGE "NUMBRS"
```

## See Also
- [KILL](kill.md) - To delete a file from disk
- [LOAD](load.md) - To load a file from disk into memory
- [NAME](name.md) - To change the name of a disk file
- [SAVE](save.md) - To save a program file on disk
