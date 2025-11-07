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

<filename> is the name that was used when the file was SAVEd. (With CP/M, the default extension .BAS is supplied.)

**File handling:**
- **LOAD** (without ,R): Closes all open files and deletes all variables and program lines currently in memory before loading
- **LOAD** with **,R** option: Program is RUN after loading, and all open data files are **kept open** for program chaining
- Compare with **MERGE**: Never closes files (see [MERGE](merge.md))

The ,R option allows chaining several programs (or segments of the same program) while passing information between them using disk data files.

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
