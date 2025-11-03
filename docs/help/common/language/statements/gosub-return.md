---
category: control-flow
description: Branch to and return from a subroutine
keywords: ['gosub', 'return', 'subroutine', 'call', 'branch', 'nested', 'stack']
aliases: ['gosub-return']
syntax: GOSUB line_number ... RETURN
related: ['goto', 'on-gosub', 'for-next']
title: GOSUB...RETURN
type: statement
---

# GOSUB...RETURN

## Syntax

```basic
GOSUB <line number>
RETURN
```

## Purpose

To branch to and return from a subroutine.

## Remarks

`<line number>` is the first line of the subroutine. A subroutine may be called any number of times in a program, and a subroutine may be called from within another subroutine. Such nesting of subroutines is limited only by available memory.

The RETURN statement(s) in a subroutine cause BASIC-80 to branch back to the statement following the most recent GOSUB statement. A subroutine may contain more than one RETURN statement, should logic dictate a return at different points in the subroutine.

Subroutines may appear anywhere in the program, but it is recommended that the subroutine be readily distinguishable from the main program. To prevent inadvertent entry into the subroutine, it may be preceded by a STOP, END, or GOTO statement that directs program control around the subroutine.

## Example

```basic
10 GOSUB 40
20 PRINT "BACK FROM SUBROUTINE"
30 END
40 PRINT "SUBROUTINE ";
50 PRINT " IN";
60 PRINT " PROGRESS"
70 RETURN
```

Output:
```
SUBROUTINE IN PROGRESS
BACK FROM SUBROUTINE
```

## See Also
- [FOR...NEXT](for-next.md) - Execute statements repeatedly with a loop counter
- [GOTO](goto.md) - Branch unconditionally to a specified line number
- [IF...THEN...ELSE](if-then-else-if-goto.md) - Make decisions and control program flow based on conditional expressions
- [ON...GOSUB/ON...GOTO](on-gosub-on-goto.md) - Branch to one of several line numbers based on an expression value
- [WHILE...WEND](while-wend.md) - Execute statements in a loop while a condition is true
