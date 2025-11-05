---
category: file-management
description: To load a file from disk into memory
keywords: ['close', 'command', 'data', 'file', 'for', 'if', 'line', 'load', 'open', 'program']
syntax: LOAD <filename>[,R]
title: LOAD
type: statement
---

# LOAD

## Syntax

```basic
LOAD <filename>[,R]
```

**Versions:** Disk

## Purpose

To load a file from disk into memory.

## Remarks

<filename> is the name that was used when the file was SAVEd. (With CP/M, the default extension .BAS is supplied.) LOAD closes all open files and deletes all variables and program lines currently residing in memory before it loads the designated program. However, if the ,R option is used with LOAD, the program is RUN after it is LOADed, and all open data files are kept open. Thus, LOAD with the ,R option may be used to chain several programs (or segments of the same program). Information may be passed between the programs using their disk data files.

## Example

```basic
LOAD "STRTRK"
LOAD "STRTRK",R    'Load and run immediately
```

## See Also
- [KILL](kill.md) - To delete a file from disk
- [MERGE](merge.md) - To merge a specified disk file into the program currently in memory
- [NAME](name.md) - To change the name of a disk file
- [SAVE](save.md) - To save a program file on disk
