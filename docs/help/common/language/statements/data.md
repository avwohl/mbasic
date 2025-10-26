---
category: data
description: NEEDS_DESCRIPTION
keywords:
- NEEDS_KEYWORDS
title: DATA
type: statement
---

# DATA

## Syntax

```basic
DATA <list of constants>
```

## Purpose

To store the numeric and string constants that are accessed by the program~s READ statement(s). (See READ, Section 2.54)

## Remarks

DATA statements are nonexecutable and may be placed    anywhere  in   the program.    A DATA statement may contain as many constants as will fit on a line (separated by commas), and any number of DATA statements may be used in a program.    The READ statements access the DATA statements in order (by line number)    and the data contained therein may be thought of as one continuous list of items, regardless of how many items are on a line or where the "lines are placed in the program. <list of    constants>    may    contain   numeric constants in any format, i.e., fixed point, floating point    or    integer.     (No   numeric expressions are allowed in the list.) String constants in DATA statements must be surrounded by double quotation marks only if they contain commas, colons or      significant    leading  or trailing spaces. Otherwise, quotation marks are not needed. The variable type (numeric or string) given in the   READ   statement   must   agree with the corresponding constant in the DATA statement. DATA statements may be reread from the beginning by use of the RESTORE statement (Section 2.57).

## Example

```basic
See examples in Section 2.54, READ.
BASIC-80 COMMANDS AND STATEMENTS                        Page 2-13
```

## See Also

*Related statements will be linked here*