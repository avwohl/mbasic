---
category: file-management
description: NEEDS_DESCRIPTION
keywords:
- NEEDS_KEYWORDS
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

<filename> is the name that was used when the file   was   SAVEd.   (With CP/M, the default extension .BAS is supplied.) LOAD closes all open files and deletes all variables and program lines currently residing in memory before it loads       the   designated program.   However, if the nRn option is used with LOAD, the program is RUN after it is LOADed, and all open data files are kept open. Thus, LOAD with the nRn option may be used to chain several programs (or segments of the same program). Information may be passed between the programs using their disk data files.

## Example

```basic
LOAD nSTRTRKn,R
BASIC-80 COMMANDS AND STATEMENTS                          Page 2-47
```

## See Also

*Related statements will be linked here*