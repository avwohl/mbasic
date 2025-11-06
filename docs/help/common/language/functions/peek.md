---
category: system
description: Returns the byte (decimal integer in the range 0 to 255) read from memory location I
keywords: ['complementary', 'for', 'function', 'gosub', 'if', 'number', 'peek', 'program', 'read', 'return']
syntax: PEEK(I)
title: PEEK
type: function
---

# PEEK

## Implementation Note

ℹ️ **Emulated with Random Values**: PEEK does NOT read actual memory. Instead, it returns a random value between 0-255 (inclusive).

**Behavior**: Each call to PEEK returns a new random integer in the range 0-255. This value is NOT related to any POKE operation.

**Why**: Most legacy BASIC programs used PEEK to seed random number generators (e.g., `RANDOMIZE PEEK(0)`). Since we cannot read actual memory addresses in a Python interpreter, returning random values provides compatibility for this common use case.

**Important Limitations**:
- **PEEK does NOT return values written by POKE** (POKE is a no-op that does nothing)
- Memory-mapped I/O operations will not work
- Each PEEK call returns a different random value
- Cannot be used for actual memory inspection or hardware control

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
- [FRE](fre.md) - Arguments to FRE are dummy arguments
- [HELP SET](../statements/helpsetting.md) - Display help for a specific setting
- [INKEY$](inkey_dollar.md) - Returns either a one-character string containing a character read from the terminal or a null string if no character is pending at the terminal
- [INP](inp.md) - Returns the byte read from port I
- [LIMITS](../statements/limits.md) - Display resource usage and interpreter limits
- [NULL](../statements/null.md) - To set the number of nulls to be printed at the end of each line
- [RANDOMIZE](../statements/randomize.md) - To reseed the random number generator
- [REM](../statements/rem.md) - To allow explanatory remarks to be inserted in a program
- [SET (setting)](../statements/setsetting.md) - Configure interpreter settings at runtime
- [SHOW SETTINGS](../statements/showsettings.md) - Display current interpreter settings
- [TRON/TROFF](../statements/tron-troff.md) - To trace the execution of program statements
- [USR](usr.md) - Calls the user's assembly language subroutine with the argument X
- [VARPTR](varptr.md) - Returns the memory address of a variable
- [WIDTH](../statements/width.md) - To set the printed line width in number of characters for the terminal or line printer
