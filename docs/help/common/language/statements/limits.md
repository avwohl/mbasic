---
category: system
description: Display resource usage and interpreter limits
keywords:
- limits
- resources
- memory
- usage
- system
- diagnostics
syntax: LIMITS
title: LIMITS
type: statement
---

# LIMITS

## Syntax

```basic
LIMITS
```

**Versions:** MBASIC Extension

## Purpose

To display current resource usage and interpreter limits.

## Remarks

LIMITS is a diagnostic statement specific to this MBASIC implementation. It displays information about:
- Memory usage
- Variable storage
- String space
- Stack depth
- Other interpreter resource limits

This command is useful for:
- Debugging programs that approach resource limits
- Understanding program resource requirements
- Optimizing programs for better resource usage

## Example

```basic
LIMITS

100 DIM A(1000)
110 LIMITS
120 PRINT "After allocating array"
```

## Notes

- This is a modern extension not present in original MBASIC 5.21
- Output format is implementation-specific
- Useful for development and debugging

## See Also

- FRE - Return available memory (not yet documented)
