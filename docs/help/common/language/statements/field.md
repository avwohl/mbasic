---
category: file-io
description: NEEDS_DESCRIPTION
keywords:
- NEEDS_KEYWORDS
title: FIELD
type: statement
---

# FIELD

## Syntax

```basic
FIELD[i]<file number>,<field width> AS <string variable> •••
```

**Versions:** Disk

## Purpose

To allocate space for variables in a random file buffer.

## Remarks

To get data out of a random buffer after a GET or to enter data before a PUT, a FIELD statement must have been executed. <file number> is the number und~r which the file was OPENed.    <field width> is the number of characters to be allocated to <string variable>. For example, FIELD 1, 20 AS N$, 10 AS ID$, 40 AS ADD$ allocates the first 20 positions. (bytes) in the· random file buffer to the string variable N$, the next 10 positions to ID$, and the next 40 positions to ADD$.     FIELD does NOT place any data in the random file buffer.   (See LSET/RSET and GET.) The total number of bytes allocated in a FIELD statement must not exceed the record length that was specified when the      file    was  OPENed. Otherwise, a "Field overflow" error occurs. (The default record length is l28.) Any number of FIELD statements may be executed for the same file, and all FIELD statements that have been executed are in effect at the same time.

## Example

```basic
See Appendix B.
NOTE:            ~  !!2! ~ a FIELDed var iable name in an I.NPUT
                 or LET statement.     Once a -viriable--name is
                 FIELDed, it points to the correct place in the
                 random file buffer.     If a subsequent INPUT or
                 LET statement with that variable       name   is
                 executed, the variable~s pointer is moved to
                 string space.
BASIC-SO COMMANDS AND STATEMENTS                           Page 2-29
```

## See Also

*Related statements will be linked here*