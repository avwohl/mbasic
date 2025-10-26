---
category: program-control
description: NEEDS_DESCRIPTION
keywords:
- NEEDS_KEYWORDS
title: CLEAR
type: statement
---

# CLEAR

## Syntax

```basic
CLEAR [,[<expressionl>] [,<expression2>]]
```

**Versions:** SK, -Extended, Disk

## Purpose

To set all numeric variables to zero and all string variables to null; and, optionally, 'to set the end of memory and the amount of stack space.

## Remarks

<expr'essionl> is a memory location which, if specified, sets the highest location available for use by BASIC-SO. <expression2> sets aside stack space for BASIC. The default is 256 bytes or one-eighth of the available memory, whichever is smaller. NOTE:           In previous versions of BASIC-SO, <expressionl> set    the    amount  of   string    space,' and <expression2> set the end of memory.   BASIC-80, release 5.0 and later, allocates string space dynamically. An ROut of string space error R occurs only if there is no free memory left for BASIC to use.

## Example

```basic
CLEAR
                CLEAR ,32768
                CLEAR ,,2000
                CLEAR ,32768,2000
MICROSOFT BASIC COMMANDS AND STATEMENTS                         Page 2-7
```

## See Also

*Related statements will be linked here*