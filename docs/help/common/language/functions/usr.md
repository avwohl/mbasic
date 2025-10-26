---
category: system
description: NEEDS_DESCRIPTION
keywords:
- NEEDS_KEYWORDS
title: USR
type: function
---

# USR

## Implementation Note

⚠️ **Not Implemented**: This feature calls machine language (assembly) routines and is not implemented in this Python-based interpreter.

**Behavior**: Always returns 0

**Why**: Cannot execute machine code from a Python interpreter. USR was designed to call hand-written assembly language subroutines for performance-critical operations or hardware access.

**Historical Reference**: The documentation below is preserved from the original MBASIC 5.21 manual for historical reference.

---

## Description

Calls the user's assembly language subroutine with the argument X. <digit> is allowed in the Extended and Disk versions only. <digit> is in the range 0 to 9 and corresponds to the digit supplied with the DEF USR statement for that routine.    If   <digit> is omitted, USRO is assumed. See Appendix x.

## Example

```basic
40 B = T*SIN (Y)
             50 C = USR (B/2)
             60 D = USR(B/3)
```

## See Also

*Related functions will be linked here*