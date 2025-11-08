---
category: system
description: To trace the execution of program statements
keywords: ['close', 'command', 'execute', 'for', 'line', 'next', 'number', 'print', 'program', 'statement']
syntax: TRON
title: TRON-TROFF
type: statement
---

# TRON-TROFF

## Syntax

```basic
TRON
TROFF
```

## Purpose

To trace the execution of program statements.

## Remarks

As an aid in debugging, the TRON statement (executed in either the direct or indirect mode) enables a trace flag that prints each line number of the program as it is executed. The numbers appear enclosed in square brackets. The trace flag is disabled with the TROFF statement (or when a NEW command is executed).

## Example

```basic
TRON
Ok

LIST
10 K=10
20 FOR J=1 TO 2
30 L=K + 10
40 PRINT J, K, L
50 K=K+10
60 NEXT
70 END
Ok

RUN
[10] [20] [30] [40] 1   10   20
[50] [60] [30] [40] 2   20   30
[50] [60] [70]
Ok

TROFF
Ok
```

## See Also
- [STOP](stop.md) - Stop program execution for debugging
- [CONT](cont.md) - Continue execution after STOP
- [ON ERROR GOTO](on-error-goto.md) - Error handling for debugging
- [REM](rem.md) - Add comments for debugging notes
