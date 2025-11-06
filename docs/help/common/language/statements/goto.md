---
category: control-flow
description: Branch unconditionally to a specified line number
keywords: ['goto', 'branch', 'jump', 'transfer', 'unconditional']
syntax: GOTO line_number
related: ['gosub-return', 'if-then-else-if-goto', 'on-goto', 'on-gosub']
title: GOTO
type: statement
---

# GOTO

## Syntax

```basic
GOTO <line number>
```

**Versions:** 8K, Extended, Disk

## Purpose

To branch unconditionally out of the normal program sequence to a specified line number.

## Remarks

If <line number> is an executable statement, that statement and those following are executed. If it is a nonexecutable statement, execution proceeds   at the first executable statement encountered after <line number>.

## Example

```basic
LIST
              10 READ R
              20 PRINT "R =" :R,
              30 A = 3.l4*R .... 2
              40 PRINT "AREA =" :A
              50 GOTO 10
              60 DATA 5,7,12
              Ok
              RUN
              R = 5                AREA = 78.5
              R = 7                AREA = 153.86
              R = 12               AREA = 452.16
              ?Out of data in 10
              Ok
```

## See Also
- [FOR ••• NEXT](for-next.md) - Execute statements repeatedly with a loop counter
- [GOSUB •.. RETURN](gosub-return.md) - Branch to and return from a subroutine
- [IF ••• THEN[ ••• ELSE] AND IF ••• GOTO](if-then-else-if-goto.md) - Make decisions and control program flow based on conditional expressions
- [ON ••• GOSUB AND ON ••• GOTO](on-gosub-on-goto.md) - To branch to one of several specified line numbers, depending on the value returned when an expression is evaluated
- [WHILE ••• WEND](while-wend.md) - Execute statements in a loop while a condition is true
