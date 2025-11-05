---
category: variables
description: To assign the value of an expression to a variable
keywords: ['command', 'let', 'statement', 'variable']
syntax: [LET] <variable>=<expression>
title: LET
type: statement
---

# LET

## Syntax

```basic
[LET] <variable>=<expression>
```

## Purpose

To assign the value of an expression to a variable.

## Remarks

Notice the word LET is optional, i.e., the equal sign is sufficient when assigning an expression to a variable name.

## Example

```basic
110 LET D=12
120 LET E=12^2
130 LET F=12^4
140 LET SUM=D+E+F
```

Or without LET:
```basic
110 D=12
120 E=12^2
130 F=12^4
140 SUM=D+E+F
```

## See Also
- [SWAP](swap.md) - To exchange the values of two variables
