---
category: string
description: Returns the numerical value of string X$
keywords:
- for
- function
- if
- line
- print
- read
- return
- string
- then
- val
syntax: VAL (X$)
title: VAL
type: function
---

# VAL

## Syntax

```basic
VAL (X$)
```

## Description

Returns the numerical value of string X$. The VAL function also strips leading blanks, tabs, and linefeeds from the argument string. For example, VAL (" -3) returns -3.

## Example

```basic
10 READ NAME$,CITY$,STATE$,ZIP$
 20 IF VAL(ZIP$) <90000 OR VAL(ZIP$) >96699 THEN
 PRINT NAME$ TAB(25) "OUT OF STATE"
 30 IF VAL(ZIP$) >=90801 AND VAL(ZIP$) <=90815 THEN
 PRINT NAME$ TAB(25) "LONG BEACH"
 See the STR$ function for numeric to string
 conversion.
```

## See Also

*Related functions will be linked here*