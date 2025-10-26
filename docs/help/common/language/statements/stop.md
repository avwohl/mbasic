---
category: program-control
description: NEEDS_DESCRIPTION
keywords:
- NEEDS_KEYWORDS
title: STOP
type: statement
---

# STOP

## Syntax

```basic
STOP
```

## Purpose

To terminate program      execution   and    return   to command level.

## Remarks

STOP statements may be used anywhere in a program to terminate execution. When a STOP is encountered, the following message is printed: Break in line nnnnn Unlike the END statement,       the   STOP   statement does not close files. BASIC-80 always returns to command level after a STOP is executed.     Execution is resumed by issuing a CONT command (see Section 2.8).

## Example

```basic
10 INPUT A,B,C
              20 K=AA2*5.3:L=B A3/.26
              30 STOP
              40 M=C*K+100:PRINT M
              RON
              ? 1,2,3
              BREAK IN 30
              Ok
              PRINT L
               30.7692
              Ok
              CONT
               115.9
              Ok
BASIC-SO COMMANDS AND STATEMENTS                      Page 2-79
```

## See Also

*Related statements will be linked here*