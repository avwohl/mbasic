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

**Versions:** 8K, Extended, Disk

## Purpose

To allow a series of instructions to be performed in a loop a given number of times.

## Remarks

The FOR...NEXT loop executes a block of statements a specified number of times, automatically incrementing a counter variable.

### Parameters:
- **variable** - The loop counter (any numeric variable)
- **x** - Starting value
- **y** - Ending value
- **z** - Step increment (optional, defaults to 1)

### Operation:
1. Variable is set to the starting value (x)
2. Statements in loop body execute
3. Variable increments by step value (z)
4. Loop termination test (see below)
5. If test passes, process repeats from step 2

### Loop Termination:
The loop terminates when the variable passes the ending value, considering the STEP direction:
- **Positive STEP** (or no STEP): Loop terminates when variable > ending value
- **Negative STEP**: Loop terminates when variable < ending value

For example:
- `FOR I = 1 TO 10` terminates when I > 10 (after I reaches 10 and increments to 11)
- `FOR I = 10 TO 1 STEP -1` terminates when I < 1 (after I reaches 1 and decrements to 0)

### Features:
- **STEP** can be positive, negative, or fractional (defaults to 1 if omitted)
- Loop body may not execute at all if start/end/step values would cause immediate termination (e.g., `FOR I=10 TO 1` with positive STEP)
- Multiple variables can be specified in NEXT for nested loops (e.g., `NEXT J, I`)

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
- [GOSUB...RETURN](gosub-return.md) - Branch to and return from a subroutine
- [GOTO](goto.md) - Branch unconditionally to a specified line number
- [IF...THEN...ELSE](if-then-else-if-goto.md) - Make decisions and control program flow based on conditional expressions
- [ON...GOSUB/ON...GOTO](on-gosub-on-goto.md) - Branch to one of several line numbers based on an expression value
- [WHILE...WEND](while-wend.md) - Execute statements in a loop while a condition is true
