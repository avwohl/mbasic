---
category: control-flow
description: Branch unconditionally to a specified line number
keywords:
- goto
- branch
- jump
- transfer
- unconditional
syntax: "GOTO line_number"
related: [gosub-return, if-then-else-if-goto, on-goto, on-gosub]
title: GOTO
type: statement
---

# GOTO

## Syntax

```basic
GOTO <line number>
```

**Versions:** SK, Extended, Disk

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
              R = 5                AREA = 7S.5
              R = 7                AREA = l53.S6
              R = 12               AREA = 452.16
              ?Out of data in 10
              Ok
BASIC-SO COMMANDS AND STATEMENTS                           Page 2-34
```

## See Also

*Related statements will be linked here*