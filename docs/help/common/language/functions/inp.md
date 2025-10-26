---
category: system
description: Returns the byte read from port I
keywords:
- complementary
- for
- function
- if
- inp
- out
- read
- return
- statement
syntax: INP (I)
title: INP
type: function
---

# INP

## Implementation Note

⚠️ **Not Implemented**: This feature requires direct hardware I/O port access and is not implemented in this Python-based interpreter.

**Behavior**: Always returns 0

**Why**: Cannot access hardware I/O ports from a Python interpreter. This function is specific to systems with memory-mapped I/O or port-based hardware interfaces.

**Historical Reference**: The documentation below is preserved from the original MBASIC 5.21 manual for historical reference.

---

## Syntax

```basic
INP (I)
```

## Description

Returns the byte read from port I. I must be in the range 0 to 255. INP is the complementary function to the OUT statement, Section 2.47.

## Example

```basic
100 A=INP(255)
```

## See Also

*Related functions will be linked here*