---
category: hardware
description: NEEDS_DESCRIPTION
keywords:
- NEEDS_KEYWORDS
title: OUT
type: statement
---

# OUT

## Implementation Note

⚠️ **Not Implemented**: This feature requires direct hardware I/O port access and is not implemented in this Python-based interpreter.

**Behavior**: Statement is parsed but no operation is performed

**Why**: Cannot access hardware I/O ports from a Python interpreter. OUT was used to control hardware devices through port-based I/O.

**Historical Reference**: The documentation below is preserved from the original MBASIC 5.21 manual for historical reference.

---

## Syntax

```basic
OUT I,J
where I and J are    integer   expressions     in   the
range 0 to 255.
```

## Purpose

To send a byte to a machine output port.

## Remarks

The integer expression I is the port number, and the integer expression J is the data to be transmitted.

## Example

```basic
100 OUT 32,100
BASIC-80 COMMANDS AND STATEMENTS                        Page 2-59
```

## See Also

*Related statements will be linked here*