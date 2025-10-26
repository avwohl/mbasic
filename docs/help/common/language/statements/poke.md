---
category: hardware
description: To write a byte into a memory location
keywords:
- command
- data
- for
- function
- if
- number
- poke
- put
- read
- statement
syntax: POKE I,J
title: POKE
type: statement
---

# POKE

## Implementation Note

⚠️ **Emulated as No-Op**: This feature requires direct memory access and cannot be implemented in a Python-based interpreter.

**Behavior**: Statement is parsed and executes successfully, but performs no operation

**Why**: Cannot write to arbitrary memory addresses from a Python interpreter. POKE was used to modify memory directly, load machine code, or control memory-mapped hardware.

**Note**: Programs using POKE will run without errors, but the memory writes are silently ignored. This allows legacy programs to execute without modification.

**Historical Reference**: The documentation below is preserved from the original MBASIC 5.21 manual for historical reference.

---

## Syntax

```basic
POKE I,J
where I and J are integer expressions
```

## Purpose

To write a byte into a memory location.

## Remarks

The integer expression I is the address of the memory   location to be POKEd.      The integer expression J is the data to be POKEd. J must be in the range 0 to 255. In the 8K version, I must be less than 32768.  In the Extended and Disk versions, I must be in the range 0 to 65536. With the 8K version, data may be POKEd into memory locations above 32768 by supplying a negative number for I.     The value of I is computed by subtracting 65536 from the desired address.   For example, to POKE      data   into location 45000, I = 45000-65536, or -20536. The complementary function to POKE is PEEK. The argument to PEEK is an address from which a byte is to be read. See Section 3.27. POKE and PEEK are useful for efficient data storage, loading assembly language subroutines, and passing arguments and results to and from assembly language subroutines.

## Example

```basic
10 POKE &H5AOO,&HFF
BASIC-SO COMMANDS AND STATEMENTS                      Page 2-60
```

## See Also

*Related statements will be linked here*