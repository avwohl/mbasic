---
category: control-flow
description: NEEDS_DESCRIPTION
keywords:
- NEEDS_KEYWORDS
title: GOSUB •.. RETURN
type: statement
---

# GOSUB •.. RETURN

## Syntax

```basic
GOSUB <line number>
RETURN
```

## Purpose

To branch to and return from a subroutine.

## Remarks

<line number>   is    the   first   line   of    the subroutine. A subroutine may be called any number of times in a program, and a subroutine may be called from within another subroutine. Such nesting of subroutines is limited only by available memory. The RETURN statement(s) in a subroutine cause BASIC-80    to   branch back to the statement following the most recent GOSUB statement.    A subroutine may contain more than one RETURN statement, should logic dictate a return at different points in the subroutine. Subroutines may appear anywhere in the program, but it is recommended    that the subroutine be readily distinguishable from the main program.       To prevent inadvertant entry into the subroutine, it may be preceded by a STOP, END, or GOTO statement that directs program control around the subroutine.

## Example

```basic
10 GOSUB 40
             20 PRINT "BACK FROM SUBROUTINE"
             30 END
             40 PRINT "SUBROUTINE" ;
             50 PRINT " IN";
             60 PRINT n PROGRESS"
             70 RETURN
             RUN
             SUBROUTINE IN PROGRESS
             BACK FROM SUBROUTINE
             Ok
BASIC-SO COMMANDS AND STATEMENTS                     Page 2-33
```

## See Also

*Related statements will be linked here*