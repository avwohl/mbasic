---
category: control-flow
description: Execute statements repeatedly with a loop counter
keywords: ['for', 'next', 'loop', 'iteration', 'counter', 'step', 'nested', 'repeat']
syntax: FOR variable = start TO end [STEP increment]
related: ['while-wend', 'goto', 'gosub-return']
title: FOR ••• NEXT
type: statement
---

# FOR ••• NEXT

## Syntax

```basic
FOR <variable>=x TO y [STEP z]
NEXT [<variable>] [,<variable> ••• ]
where x, y and z are numeric expressions.
```

**Versions:** SK, Extended, Disk

## Purpose

To allow a series of instructions        to         be performed in a loop a given number of times.

## Remarks

The FOR...NEXT loop executes a block of statements a specified number of times, automatically incrementing a counter variable.

### Parameters:
- **variable** - The loop counter (any numeric variable)
- **x** - Starting value
- **y** - Ending value
- **z** - Step increment (optional, defaults to 1)

### Operation:
1. Variable is set to the starting value (x)
2. If variable exceeds ending value (y), loop terminates
3. Statements in loop body execute
4. Variable increments by step value (z)
5. Process repeats from step 2

### Features:
- **STEP** can be positive, negative, or fractional
- Negative STEP counts backward
- Loop always executes at least once if start equals end
- Multiple variables can be specified in NEXT for nested loops

### Example:
```basic
10 FOR I = 1 TO 10 STEP 2
20   PRINT I;
30 NEXT I
```
Output: 1 3 5 7 9

### Nested Loops:
```basic
10 FOR I = 1 TO 3
20   FOR J = 1 TO 2
30     PRINT I; J
40   NEXT J, I
```

## See Also
- [GOSUB •.. RETURN](gosub-return.md) - Branch to and return from a subroutine
- [GOTO](goto.md) - Branch unconditionally to a specified line number
- [IF ••• THEN[ ••• ELSE] AND IF ••• GOTO](if-then-else-if-goto.md) - Make decisions and control program flow based on conditional expressions
- [ON ••• GOSUB AND ON ••• GOTO](on-gosub-on-goto.md) - To branch to one of several specified line numbers, depending on the value returned when an expression is evaluated
- [WHILE ••• WEND](while-wend.md) - Execute statements in a loop while a condition is true
