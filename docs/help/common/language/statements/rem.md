---
category: system
description: To allow explanatory remarks to be inserted in a program
keywords: ['branch', 'command', 'execute', 'for', 'gosub', 'goto', 'line', 'next', 'program', 'put']
syntax: REM <remark>
title: REM
type: statement
---

# REM

## Syntax

```basic
REM <remark>
```

## Purpose

To allow explanatory remarks to be inserted in a program.

## Remarks

REM statements are not executed but are output exactly as entered when the program is listed. REM statements may be branched into (from a GOTO or GOSUB statement), and execution will continue with the first executable statement after the REM statement. In the Extended and Disk versions, remarks may be added to the end of a line by preceding the remark with a single quotation mark instead of : REM.

## Example

```basic
120 REM CALCULATE AVERAGE VELOCITY
130 FOR I=1 TO 20
140 SUM=SUM + V(I)
```

or, with Extended and Disk versions:
```basic
120 FOR I=1 TO 20     'CALCULATE AVERAGE VELOCITY
130 SUM=SUM+V(I)
140 NEXT I
```

## See Also
- [TRON/TROFF](tron-troff.md) - Trace execution for debugging
- [STOP](stop.md) - Stop program execution for debugging
- [PRINT](print.md) - Output text to screen
