---
category: system
description: Returns the byte (decimal integer in the range 0 to 255) read from memory
  location I
keywords:
- complementary
- for
- function
- gosub
- if
- number
- peek
- program
- read
- return
syntax: PEEK(I)
title: PEEK
type: function
---

# PEEK

## Implementation Note

ℹ️ **Emulated with Random Values**: PEEK returns a random value between 0-255 (inclusive).

**Behavior**: Each call to PEEK returns a new random integer in the range 0-255. This value is NOT related to any POKE operation.

**Why**: Most legacy BASIC programs used PEEK to seed random number generators (e.g., `RANDOMIZE PEEK(0)`). Since we cannot read actual memory addresses in a Python interpreter, returning random values provides compatibility for this common use case.

**Note**:
- PEEK does NOT return values written by POKE (POKE is a no-op)
- Memory-mapped I/O operations will not work
- Each PEEK call returns a different random value

**Recommendation**: Use [RANDOMIZE](../statements/randomize.md) and [RND](rnd.md) instead of PEEK for random number generation.

---

## Syntax

```basic
PEEK(I)
```

## Description

Returns the byte (decimal integer in the range 0 to 255) read from memory location I.

With the 8K version of BASIC-80, I must be less than 32768. To PEEK at a memory location above 32768, subtract 65536 from the desired address.

With Extended and Disk BASIC-80, I must be in the range 0 to 65536.

PEEK is traditionally the complementary function to the [POKE](../statements/poke.md) statement. However, in this implementation, PEEK returns random values and POKE is a no-op, so they are not functionally related.

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

- [POKE](../statements/poke.md) - Write byte to memory (no-op)
- [RANDOMIZE](../statements/randomize.md) - Seed random number generator
- [RND](rnd.md) - Random number function
- [INP](inp.md) - Read from I/O port (not implemented)