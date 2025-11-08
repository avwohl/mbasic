---
category: system
description: To reseed the random number generator
keywords: ['command', 'for', 'function', 'if', 'next', 'number', 'print', 'program', 'randomize', 'return']
syntax: RANDOMIZE [<expression>]
title: RANDOMIZE
type: statement
---

# RANDOMIZE

## Syntax

```basic
RANDOMIZE [<expression>]
```

## Purpose

To reseed the random number generator.

## Remarks

If <expression> is    omitted, BASIC-80 suspends program execution     and asks for a value by printing Random Number Seed (-32768 to 32767)? before executing RANDOMIZE. If the random number generator is not reseeded, the RND function returns the same sequence of random numbers each time the program is RUN. To change the sequence of random numbers every time the program is RUN, place a RANDOMIZE statement at the beginning of the program and change the argument with each RUN.

## Example

```basic
10 RANDOMIZE
20 FOR I=1 TO 5
30 PRINT RND;
40 NEXT I

RUN
Random Number Seed (-32768 to 32767)? 3
.88598 .484668 .586328 .119426 .709225
Ok

RUN
Random Number Seed (-32768 to 32767)? 4
.803506 .162462 .929364 .292443 .322921
Ok

RUN
Random Number Seed (-32768 to 32767)? 3
.88598 .484668 .586328 .119426 .709225
Ok
```

Note: Using the same seed (3) produces the same sequence of random numbers.

## See Also
- [RND](../functions/rnd.md) - Generate random numbers
- [INT](../functions/int.md) - Convert to integer for random ranges
