---
category: functions
description: NEEDS_DESCRIPTION
keywords:
- NEEDS_KEYWORDS
title: DEF FN
type: statement
---

# DEF FN

## Syntax

```basic
DEF FN<name>[«parameter list>}]=<function definition>
```

## Purpose

To define and name a function that is written by the user.

## Remarks

<name> must be a legal variable name.        This name, preceded by FN, becomes the name of the function.   <parameter list> is comprised of those variable names in the function definition that are to be replaced when the function is called.   The items in the list are separated by commas. <function definition> is an expression that performs the operation of the function.   It is limited to one line.    Variable names that appear in this expression serve only to define the function;    they do not affect      program variables that have the same name. A variable name used in a function definition mayor may not appear in the parameter list. If it does, the value of the parameter is supplied when the function is called.     Otherwise, the current value of the variable is used. The variables in the parameter list represent, on a one-to-one basis, the argument variables or values that will be given in the function call. (Remember, in the 8K version only one argument is allowed in a function call, therefore the DEF FN statement will contain only one variable.) In Extended and Disk BASIC-80, user-defined functions may be numeric or string; in 8K, user-defined string functions are not allowed. If a type is specified in the function name, the value of the expression is forced to that type before it is returned to the calling statement. If a type is specified in the function name and the argument type does not match, a "Type mismatch" error occurs. A DEF FN statement must be executed before the function   it defines may be called.      If a function is called before it has been defined, an "Undefined user function" error occurs. DEF FN is illegal in the direct mode. BASIC-SO COMMANDS AND STATEMENTS                 Page 2-14

## Example

```basic
410 DEF FNAB(X,Y)=X A 3/y A 2
            420 T=FNAB (I, J)
            Line 410 defines the function     FNAB.    The
            function is called in line 420.
BASIC-SO COMMANDS AND STATEMENTS                      Page 2-15
```

## See Also

*Related statements will be linked here*