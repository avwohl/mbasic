---
category: functions
description: Define and name a user-defined function
keywords: ['def', 'function', 'user function', 'def fn', 'define']
syntax: DEF FN<name>[(<parameter list>)]=<function definition>
title: DEF FN
type: statement
---

# DEF FN

## Purpose

To define and name a function that is written by the user.

## Syntax

```basic
DEF FN<name>[(<parameter list>)]=<function definition>
```

**Alternative forms (all valid):**
```basic
DEF FN<name> [(<parameter list>)] = <function definition>  ' With spaces
DEF FN<name>(<parameter list>)=<function definition>       ' Without spaces
```

## Parameters

- **name** - A legal variable name that becomes the function name after FN.
  - **Original MBASIC 5.21**: Single character only (e.g., `A`, `B`, `X$`)
  - **This implementation**: Can be one or more characters (e.g., `A`, `ABC`, `UCASE$`, `DISTANCE`)
- **parameter list** - Variable names in the function definition that are to be replaced when the function is called. Items are separated by commas.
- **function definition** - An expression that performs the operation of the function. Limited to one line.

## Syntax Notes

### Function Names

**Original MBASIC 5.21**: Function names were limited to a single character after FN:
- ✓ `FNA` - single character
- ✓ `FNB$` - single character with type suffix

**This implementation (extension)**: Function names can be multiple characters:
- ✓ `FNA` - single character (compatible with original)
- ✓ `FNABC` - multiple characters
- ✓ `FNUCASE$` - multi-character with type suffix
- ✓ `FNDIST` - descriptive multi-character name
- ✓ `FNAREA%` - multi-character with integer type

### Spacing

**Space after FN is optional**. Both styles are valid:
- `DEF FN A(X) = X * 2` - with space after FN (FN and A are separate)
- `DEF FNA(X) = X * 2` - without space after FN (FNA is one token)

Choose the style that matches your coding preference. Both are equally supported.

## Remarks

### Function Definition

Variable names that appear in the function definition serve only to define the function; they do not affect program variables that have the same name.

A variable name used in a function definition may or may not appear in the parameter list:
- If it does, the value of the parameter is supplied when the function is called
- Otherwise, the current value of the variable is used

The variables in the parameter list represent, on a one-to-one basis, the argument variables or values that will be given in the function call.

**Note:** In 8K BASIC, only one argument is allowed in a function call, therefore the DEF FN statement will contain only one variable.

### Function Types

- **Extended and Disk BASIC**: User-defined functions may be numeric or string
- **8K BASIC**: User-defined string functions are not allowed

### Type Specification

If a type is specified in the function name:
- The value of the expression is forced to that type before it is returned to the calling statement
- If the argument type does not match, a "Type mismatch" error occurs

### Execution Requirements

- A DEF FN statement must be executed before the function it defines may be called
- If a function is called before it has been defined, an "Undefined user function" error occurs
- DEF FN is illegal in direct mode

## Example

### Example 1: Single-Character Name (Traditional Style)

```basic
10 DEF FND(X) = X * 2
20 FOR I = 1 TO 5
30   PRINT FND(I);
40 NEXT I
50 END
```

**Output:**
```
 2  4  6  8  10
```

### Example 2: Multi-Character Name (More Descriptive)

```basic
10 DEF FNAREA(R) = 3.14159 * R^2
20 RADIUS = 5
30 PRINT "Area of circle with radius"; RADIUS; "is"; FNAREA(RADIUS)
40 END
```

**Output:**
```
Area of circle with radius 5 is 78.53975
```

### Example 3: Compact Style (No Spaces)

```basic
10 DEF FNMAX(A,B)=A*(A>=B)+B*(B>A)
20 PRINT FNMAX(10, 20)
30 PRINT FNMAX(30, 15)
40 END
```

**Output:**
```
 20
 30
```

**Explanation:**
- Uses compact syntax without spaces
- Returns the maximum of two numbers
- Uses boolean expressions: (A>=B) is -1 if true, 0 if false

### Example 4: String Function - Uppercase Conversion

```basic
10 DEF FNUCASE$(Z$,N)=CHR$(ASC(MID$(Z$,N,1)) AND &H5F)
20 A$ = "hello world"
30 FOR I = 1 TO LEN(A$)
40   PRINT FNUCASE$(A$, I);
50 NEXT I
60 PRINT
70 END
```

**Output:**
```
HELLO WORLD
```

**Explanation:**
- Multi-character function name with type suffix
- Converts a single character to uppercase using bit manipulation
- `&H5F` is hexadecimal notation (hex 5F = decimal 95 = binary 01011111)
- `AND &H5F` clears bit 5 (the lowercase bit in ASCII), converting lowercase to uppercase
- For more on hexadecimal constants, see [Constants](../data-types.md)

### Example 5: Distance Calculation (Real-World Example)

```basic
10 DEF FNDIST(X1,Y1,X2,Y2) = SQR((X2-X1)^2 + (Y2-Y1)^2)
20 ' Calculate distance between two points
30 PRINT "Distance from (0,0) to (3,4):"; FNDIST(0,0,3,4)
40 PRINT "Distance from (1,1) to (4,5):"; FNDIST(1,1,4,5)
50 END
```

**Output:**
```
Distance from (0,0) to (3,4): 5
Distance from (1,1) to (4,5): 5
```

### Example 6: Using Current Variable Values

```basic
10 A = 10
20 DEF FNX(Y) = Y + A
30 PRINT "With A=10: FNX(5) ="; FNX(5)
40 A = 20
50 PRINT "With A=20: FNX(5) ="; FNX(5)
60 END
```

**Output:**
```
With A=10: FNX(5) = 15
With A=20: FNX(5) = 25
```

**Explanation:**
- The function FNX uses the current value of variable A
- Variable A is not in the parameter list, so its current value is used
- First call: Y=5, A=10, result = 15
- Second call: Y=5, A=20, result = 25

### Example 7: Integer Function with Type Suffix

```basic
10 DEF FNHALF%(N) = N \ 2
20 PRINT FNHALF%(7)
30 PRINT FNHALF%(10)
40 PRINT FNHALF%(15)
50 END
```

**Output:**
```
 3
 5
 7
```

**Explanation:**
- Function returns integer division (truncates, doesn't round)
- Type suffix % forces integer result

### Example 8: Temperature Conversion Functions

```basic
10 DEF FNFTOC(F) = (F - 32) * 5 / 9
20 DEF FNCTOF(C) = C * 9 / 5 + 32
30 PRINT "100°F ="; FNFTOC(100); "°C"
40 PRINT "0°C ="; FNCTOF(0); "°F"
50 PRINT "32°F ="; FNFTOC(32); "°C"
60 END
```

**Output:**
```
100°F = 37.77778 °C
0°C = 32 °F
32°F = 0 °C
```

## Common Errors

### Undefined User Function

```basic
10 X = FNA(5)    ' Error: FNA not defined yet
20 DEF FNA(Y) = Y * 2
```

**Error:** "Undefined user function"

**Fix:** Define the function before calling it:

```basic
10 DEF FNA(Y) = Y * 2
20 X = FNA(5)
```

### Type Mismatch

```basic
10 DEF FNA%(X) = X * 2    ' Integer function
20 Y = FNA%(3.5)          ' Error: passing float to integer function
```

**Error:** "Type mismatch"

**Fix:** Match argument types or remove type suffix

## See Also
- [DEF USR](def-usr.md) - Define assembly subroutine address
- [USR](../functions/usr.md) - Call assembly language subroutine
- [GOSUB-RETURN](gosub-return.md) - Branch to and return from a subroutine
