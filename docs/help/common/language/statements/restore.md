---
category: data
description: Resets the DATA pointer to the beginning or a specified line
keywords:
- restore
- data
- read
- reset
- pointer
syntax: "RESTORE [line number]"
title: RESTORE
type: statement
related: [read, data]
---

# RESTORE

## Syntax

```basic
RESTORE [line number]
```

**Versions:** SK, Extended, Disk

## Purpose

To reset the DATA pointer so that the next READ statement will access data from the beginning of the program or from a specified line number.

## Remarks

The RESTORE statement repositions the internal DATA pointer used by READ statements.

**RESTORE** - Resets the pointer to the first DATA statement in the program.

**RESTORE line-number** - Resets the pointer to the first DATA statement at or after the specified line number.

After RESTORE executes, the next READ statement will start reading from the repositioned DATA pointer. This allows:
- Re-reading the same data multiple times
- Jumping to different sets of DATA statements
- Resetting after reading all data

## Example

```basic
10 DATA 1, 2, 3, 4, 5
20 READ A, B, C
30 PRINT A; B; C
40 RESTORE
50 READ X, Y
60 PRINT X; Y
RUN
1 2 3
1 2
Ok

100 DATA "Red", "Green", "Blue"
110 DATA 10, 20, 30
120 RESTORE 110
130 READ N1, N2, N3
140 PRINT N1; N2; N3
RUN
10 20 30
Ok
```

## Notes

- If line number is specified, it need not contain a DATA statement; the pointer is set to the first DATA at or after that line
- "Out of DATA" error occurs if READ is executed when no more DATA is available

## See Also

- [READ](read.md) - Read values from DATA statements
- [DATA](data.md) - Define data values
