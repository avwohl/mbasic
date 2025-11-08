---
description: Reference guide for BASIC-80 operators including arithmetic, comparison, and logical operations
keywords:
- condition
- data
- else
- error
- expressions
- for
- function
- goto
- if
- number
title: Operators and Expressions
type: guide
---

# Operators and Expressions

BASIC-80 operators for arithmetic, comparison, and logical operations.

## Arithmetic Operators

| Operator | Operation | Example | Result |
|----------|-----------|---------|--------|
| `+` | Addition | `5 + 3` | 8 |
| `-` | Subtraction | `5 - 3` | 2 |
| `*` | Multiplication | `5 * 3` | 15 |
| `/` | Division (floating point) | `5 / 2` | 2.5 |
| `\` | Integer Division | `5 \ 2` | 2 |
| `MOD` | Modulus (remainder) | `5 MOD 2` | 1 |
| `^` | Exponentiation | `5 ^ 2` | 25 |
| `-` | Negation (unary) | `-5` | -5 |

### Integer Division and Modulus

```basic
10 PRINT 17 \ 5      ' Integer division: 3
20 PRINT 17 MOD 5    ' Remainder: 2
30 PRINT 17 / 5      ' Float division: 3.4
```

### Overflow and Division by Zero

- **Overflow**: Result too large → "Overflow" error
- **Underflow**: Result too small → becomes 0 (no error)
- **Division by zero**: Returns machine infinity, execution continues

```basic
10 X = 5 / 0         ' X becomes infinity, no error
20 PRINT X           ' Displays large number
```

## Relational Operators

Compare two values, return -1 (true) or 0 (false).

| Operator | Meaning | Example | Result |
|----------|---------|---------|--------|
| `=` | Equal to | `5 = 5` | -1 (true) |
| `<>` | Not equal to | `5 <> 3` | -1 (true) |
| `<` | Less than | `3 < 5` | -1 (true) |
| `>` | Greater than | `5 > 3` | -1 (true) |
| `<=` | Less than or equal | `3 <= 3` | -1 (true) |
| `>=` | Greater than or equal | `5 >= 3` | -1 (true) |

### Examples

```basic
10 IF 5 > 3 THEN PRINT "5 is greater than 3"
20 X = (A = B)       ' X is -1 if A equals B, 0 otherwise
30 IF N$ <> "" THEN PRINT "String is not empty"
```

## Logical Operators

Perform boolean operations on numeric values.

| Operator | Operation | Example | Description |
|----------|-----------|---------|-------------|
| `NOT` | Logical NOT | `NOT X` | Inverts all bits |
| `AND` | Logical AND | `X AND Y` | 1 where both bits are 1 |
| `OR` | Logical OR | `X OR Y` | 1 where either bit is 1 |
| `XOR` | Exclusive OR | `X XOR Y` | 1 where bits differ |
| `EQV` | Equivalence | `X EQV Y` | 1 where bits are same |
| `IMP` | Implication | `X IMP Y` | 0 only if X is true and Y is false |

### Truth Table for Logical Operators

| X | Y | X AND Y | X OR Y | X XOR Y | X EQV Y | X IMP Y |
|---|---|---------|--------|---------|---------|---------|
| 0 | 0 | 0 | 0 | 0 | -1 | -1 |
| 0 | -1 | 0 | -1 | -1 | 0 | -1 |
| -1 | 0 | 0 | -1 | -1 | 0 | 0 |
| -1 | -1 | -1 | -1 | 0 | -1 | -1 |

### Logical Operators as Boolean Logic

```basic
10 IF AGE >= 18 AND CITIZEN THEN PRINT "Can vote"
20 IF X < 0 OR X > 100 THEN PRINT "Out of range"
30 FLAG = NOT FLAG   ' Toggle flag
```

### Logical Operators as Bitwise Operations

```basic
10 REM Set bit 3 (value 4)
20 X = X OR 4

30 REM Clear bit 3
40 X = X AND NOT 4

50 REM Toggle bit 3
60 X = X XOR 4

70 REM Test if bit 3 is set
80 IF (X AND 4) <> 0 THEN PRINT "Bit 3 is set"
```

## Operator Precedence

Operators are evaluated in this order (highest to lowest):

1. **Parentheses** `( )`
2. **Exponentiation** `^`
3. **Negation** `-` (unary)
4. **Multiplication, Division** `*`, `/`, `\`, `MOD`
5. **Addition, Subtraction** `+`, `-`
6. **Relational** `=`, `<>`, `<`, `>`, `<=`, `>=`
7. **NOT**
8. **AND**
9. **OR**
10. **XOR**
11. **EQV**
12. **IMP**

### Examples

```basic
10 PRINT 2 + 3 * 4        ' Result: 14 (not 20)
20 PRINT (2 + 3) * 4      ' Result: 20
30 PRINT 2 ^ 3 * 4        ' Result: 32 (2^3 = 8, then 8*4)
40 PRINT 10 > 5 AND 3 < 7 ' Result: -1 (true)
```

## String Concatenation

Use `+` to join strings:

```basic
10 A$ = "Hello"
20 B$ = "World"
30 C$ = A$ + " " + B$     ' Result: "Hello World"
40 PRINT C$
```

## Type Conversion in Expressions

BASIC-80 automatically converts between numeric types:

```basic
10 I% = 5             ' Integer
20 S! = 3.14          ' Single precision
30 D# = I% * S!       ' Result is single precision
40 PRINT D#           ' Displays: 15.7
```

**Conversion rules:**
- Integer + Single → Single
- Single + Double → Double
- Integer + Double → Double

## See Also

- [Type Conversion Functions](functions/index.md#type-conversion-functions)
- [LET Statement](statements/let.md) - Variable assignment
- [IF Statement](statements/if-then-else-if-goto.md) - Conditional execution
- [DEFINT/SNG/DBL/STR](statements/defint-sng-dbl-str.md) - Variable type declarations