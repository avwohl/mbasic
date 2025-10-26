---
category: system
description: NEEDS_DESCRIPTION
keywords:
- NEEDS_KEYWORDS
title: PEEK
type: function
---

# PEEK

## Implementation Note

ℹ️ **Compatibility Implementation**: PEEK returns a random value between 0-255.

**Why**: Most BASIC programs use PEEK to seed random number generators or check memory-mapped I/O. This compatibility implementation provides suitable random values for RNG seeding.

**Note**: Cannot read actual memory addresses (not applicable in Python interpreter). For memory-mapped I/O operations, this implementation will not work correctly.

**Recommendation**: Use [RANDOMIZE](randomize.md) and [RND](rnd.md) instead of PEEK for random number generation.

---

## Syntax

```basic
PEEK(I)
```

## Description

Returns the byte (decimal integer in the range 0 to 255) read from memory location I.

With the 8K version of BASIC-80, I must be less than 32768. To PEEK at a memory location above 32768, subtract 65536 from the desired address.

With Extended and Disk BASIC-80, I must be in the range 0 to 65536.

PEEK is the complementary function to the [POKE](../statements/poke.md) statement.

## Example

```basic
A = PEEK(&H5A00)
```

## Common Uses (Historical)

### Random Number Seeding
```basic
10 REM Seed RNG with memory value
20 RANDOMIZE PEEK(0)
```

**Modern equivalent**:
```basic
10 REM Use RANDOMIZE alone (uses system time)
20 RANDOMIZE
```

### Memory-Mapped I/O
```basic
10 REM Check keyboard buffer (CP/M specific)
20 IF PEEK(&H0001) <> 0 THEN GOSUB 1000
```

**Note**: Memory-mapped I/O operations will not work in this implementation.

## See Also

- [POKE](../statements/poke.md) - Write byte to memory (not implemented)
- [RANDOMIZE](../statements/randomize.md) - Seed random number generator
- [RND](rnd.md) - Random number function
- [INP](inp.md) - Read from I/O port (not implemented)