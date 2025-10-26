---
category: error-handling
description: NEEDS_DESCRIPTION
keywords:
- NEEDS_KEYWORDS
title: RESUME
type: statement
---

# RESUME

**Versions:** Extended, Disk SK, Extended, Disk Disk

## Purpose

To continue program execution after an          error recovery procedure has been performed. To execute the program currently in memory. To load a file from disk into memory and run it.

## Remarks

Anyone of the four formats shown above may         be used, depending upon where execution is            to resume: RESUME                 Execution resumes at the or                   statement which caused the RESUME a               error. RESUME NEXT            Execution resumes at the statement immediately fol- lowing the one which caused the error. RESUME <line number> Execution resumes at <line number>. A RESUME statement that is not in an error trap routine causes a "RESUME without error" message to be pr inted.                       . If <line number> is specified, execution begins on that line.     Otherwise, execution begins at the lowest line number. BASIC-SO always returns to command level after a RUN is executed. <filename> is the name used when the file was SAVEd.    (With CP/M and ISIS-II, the default extension .BAS is supplied.) RUN closes all open files and deletes the current contents of memory before loading the designated program.    However, with the  nR n option, all data files remain OPEN.

## Example

```basic
10 ON ERROR GOTO 900
                  •
                900 IF (ERR=230) AND (ERL=90) THEN PRINT "TRY
                AGAIN":RESUME 80
BASIC-SO COMMANDS AND STATEMENTS                     Page 2-76
2.59
       -RUN
Format 1:     RUN [<line number>]
RUN
Format 2:     RUN <filename>[,R]
RUN nNEWFILn, R
              See also Appendix B.
BASIC-SO COMMANDS AND STATEMENTS                     Page 2-77
```

## See Also

*Related statements will be linked here*