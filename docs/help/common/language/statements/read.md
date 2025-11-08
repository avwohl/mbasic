---
category: data
description: To read values from a DATA statement and assign them to variables
keywords: ['array', 'command', 'data', 'error', 'for', 'if', 'line', 'next', 'number', 'print']
syntax: READ <list of variables>
title: READ
type: statement
---

# READ

## Syntax

```basic
READ <list of variables>
```

## Purpose

To read values from a DATA statement and assign them to variables.

## Remarks

A READ statement must always be used with a DATA statement. READ statements assign variables to DATA statement values on a one-to-one basis. READ statement variables may be numeric or string, and the values read must agree with the variable types specified.

If the number of variables in the list exceeds the number of elements in the DATA statement(s), an "Out of DATA" error occurs.

Variables in the list may be subscripted. Array elements must be dimensioned before being referenced in a READ statement.

## Example

```basic
10 DATA 100, "John", 85.5
20 DATA 200, "Mary", 92.3
30 READ ID, NAME$, SCORE
40 PRINT "Student"; ID; NAME$; "scored"; SCORE
50 READ ID, NAME$, SCORE
60 PRINT "Student"; ID; NAME$; "scored"; SCORE
```

Output:
```
Student 100 John scored 85.5
Student 200 Mary scored 92.3
```

## See Also
- [DATA](data.md) - To store the numeric and string constants that are accessed by the program's READ statements
- [RESTORE](restore.md) - Resets the DATA pointer to the beginning or a specified line
