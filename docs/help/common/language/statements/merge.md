---
category: file-management
description: NEEDS_DESCRIPTION
keywords:
- NEEDS_KEYWORDS
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

To merge a specified disk file into the      program currently in memory.

## Remarks

<filename> is the name used when the file was SAVEd.    (With CP/M, the default extension .BAS is supplied.) The file must have been SAVEd in ASCII format.   (If not, a "Bad file mode" error occurs. ) If any lines in the disk file have the same line numbers as lines in the program in memory, the lines from the file on disk will replace the corresponding lines in memory.   (MERGEing may be thought of as "inserting" the program lines on disk into the program in memory.) BASIC-80 always returns to command   level     after executing a MERGE command.

## Example

```basic
MERGE "NUMBRS"
BASIC-SO COMMANDS AND STATEMENTS                        Page 2-50
```

## See Also

*Related statements will be linked here*