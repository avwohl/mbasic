---
category: control-flow
description: Execute statements in a loop while a condition is true
keywords: ['while', 'wend', 'loop', 'condition', 'test', 'repeat', 'nested']
syntax: WHILE expression ... WEND
related: ['for-next', 'if-then-else-if-goto', 'goto']
title: WHILE...WEND
type: statement
---

# WHILE...WEND

## Syntax

```basic
WHILE <expression>
[<loop statements>]
WEND
```

## Purpose

To execute a series of statements in a loop as long as a given condition is true.

## Remarks

If `<expression>` is not zero (i.e., true), `<loop statements>` are executed until the WEND statement is encountered. BASIC then returns to the WHILE statement and checks `<expression>`. If it is still true, the process is repeated. If it is not true, execution resumes with the statement following the WEND statement.

WHILE/WEND loops may be nested to any level. Each WEND will match the most recent WHILE. An unmatched WHILE statement causes a "WHILE without WEND" error, and an unmatched WEND statement causes a "WEND without WHILE" error.

## Example

```basic
90 REM BUBBLE SORT ARRAY A$
100 FLIPS = 1   ' Force one pass through loop
110 WHILE FLIPS
115   FLIPS = 0
120   FOR I = 1 TO J - 1
130     IF A$(I) > A$(I+1) THEN SWAP A$(I), A$(I+1): FLIPS = 1
140   NEXT I
150 WEND
```

This example shows a bubble sort algorithm using WHILE/WEND. The loop continues as long as FLIPS is non-zero, indicating that swaps were made in the last pass.

## See Also
- [FOR...NEXT](for-next.md) - Execute statements repeatedly with a loop counter
- [GOSUB...RETURN](gosub-return.md) - Branch to and return from a subroutine
- [GOTO](goto.md) - Branch unconditionally to a specified line number
- [IF...THEN...ELSE](if-then-else-if-goto.md) - Make decisions and control program flow based on conditional expressions
- [ON...GOSUB/ON...GOTO](on-gosub-on-goto.md) - Branch to one of several line numbers based on an expression value
