---
category: file-management
description: To change the name of a disk file
keywords: ['command', 'error', 'file', 'for', 'name', 'statement']
syntax: NAME <old filename> AS <new filename>
title: NAME
type: statement
---

# NAME

## Syntax

```basic
NAME <old filename> AS <new filename>
```

**Versions:** Disk

## Purpose

To change the name of a disk file.

## Remarks

<old filename> must exist and <new filename> must not exist; otherwise an error will result. After a NAME command, the file exists on the same disk, in the same area of disk space, with the new name.

## Example

```basic
NAME "ACCTS" AS "LEDGER"
```

In this example, the file that was formerly named ACCTS will now be named LEDGER.

## See Also
- [KILL](kill.md) - To delete a file from disk
- [LOAD](load.md) - To load a file from disk into memory
- [MERGE](merge.md) - To merge a specified disk file into the program currently in memory
- [SAVE](save.md) - To save a program file on disk
