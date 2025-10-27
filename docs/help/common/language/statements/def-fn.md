---
category: functions
description: Define and name a user-defined function
keywords:
- def
- function
- user function
- def fn
- define
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

## Parameters

- **name** - A legal variable name. This name, preceded by FN, becomes the name of the function.
- **parameter list** - Variable names in the function definition that are to be replaced when the function is called. Items are separated by commas.
- **function definition** - An expression that performs the operation of the function. Limited to one line.

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

## Examples

### Example 1: Simple Mathematical Function

```basic
10 DEF FNAB(X,Y) = X^3 / Y^2
20 I = 5
30 J = 2
40 T = FNAB(I, J)
50 PRINT "FNAB("; I; ","; J; ") ="; T
60 END
```

**Output:**
```
FNAB( 5 , 2 ) = 31.25
```

**Explanation:**
- Line 10 defines the function FNAB which raises X to the 3rd power and divides by Y squared
- Line 40 calls the function with arguments I=5 and J=2
- Result: 5^3 / 2^2 = 125 / 4 = 31.25

### Example 2: String Function

```basic
10 DEF FN$ = "Hello, " + N$
20 N$ = "World"
30 PRINT FN$
40 END
```

**Output:**
```
Hello, World
```

### Example 3: Single Parameter Function

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

### Example 4: Using Current Variable Values

```basic
10 A = 10
20 DEF FNX(Y) = Y + A
30 PRINT FNX(5)
40 A = 20
50 PRINT FNX(5)
60 END
```

**Output:**
```
 15
 25
```

**Explanation:**
- The function FNX uses the current value of variable A
- First call: Y=5, A=10, result = 15
- Second call: Y=5, A=20, result = 25

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

- [Functions Overview](../functions/index.md) - List of all built-in functions
- [LET](let.md) - Assign values to variables
- [GOSUB...RETURN](gosub-return.md) - Call subroutines
