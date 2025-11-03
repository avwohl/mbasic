---
category: control-flow
description: Make decisions and control program flow based on conditional expressions
keywords: ['if', 'then', 'else', 'goto', 'condition', 'test', 'decision', 'branch', 'nested']
aliases: ['if-then', 'if-goto', 'if-then-else']
syntax: IF expression THEN statement|line_number [ELSE statement|line_number]
related: ['while-wend', 'for-next', 'goto', 'on-goto']
title: IF ••• THEN[ ••• ELSE] AND IF ••• GOTO
type: statement
---

# IF ••• THEN[ ••• ELSE] AND IF ••• GOTO

## Syntax

```basic
IF <expression> THEN <statement(s»          <line number>
,
[ELSE <statement(s)>     I <line number>]
IF <expression> GOTO <line number>
[ELSE <statement(s)>     I <line number>]
```

**Versions:** SK, Extended, Disk NOTE:          The ELSE clause is allowed only in Extended        and Disk versions.

## Purpose

To make a decision regarding program flow       based on the result returned by an expression.

## Remarks

The IF...THEN...ELSE statement executes statements conditionally based on the evaluation of an expression.

### Expression Evaluation:
- If expression is **true** (non-zero), THEN clause executes
- If expression is **false** (zero), ELSE clause executes (if present)
- Expression can be numeric or use relational/logical operators

### Forms:
1. **IF...THEN statement** - Execute statement if true
2. **IF...THEN line_number** - Jump to line if true
3. **IF...GOTO line_number** - Same as THEN line_number
4. **IF...THEN...ELSE** - Execute different code for true/false

### Multiple Statements:
Use colon to separate multiple statements in THEN or ELSE clause:
```basic
IF X > 0 THEN A = 1 : B = 2 : PRINT "Positive"
```

### Nested IF:
```basic
IF X > 0 THEN IF Y > 0 THEN PRINT "Both positive"
```

### Examples:
```basic
10 INPUT "Enter a number: "; N
20 IF N > 0 THEN PRINT "Positive" ELSE PRINT "Non-positive"
30 IF N = 0 GOTO 100
40 PRINT "Not zero"
```

### Notes:
- ELSE must be on the same line as IF...THEN
- Cannot use GOTO between THEN and ELSE
- Expression is evaluated left to right

## See Also
- [FOR ••• NEXT](for-next.md) - Execute statements repeatedly with a loop counter
- [GOSUB •.. RETURN](gosub-return.md) - Branch to and return from a subroutine
- [GOTO](goto.md) - Branch unconditionally to a specified line number
- [ON ••• GOSUB AND ON ••• GOTO](on-gosub-on-goto.md) - To branch to one of several specified line numbers, depending on the value returned when an expression is evaluated
- [WHILE ••• WEND](while-wend.md) - Execute statements in a loop while a condition is true
