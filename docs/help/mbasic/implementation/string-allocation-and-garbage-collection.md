---
description: Comprehensive analysis of string memory management in CP/M era Microsoft BASIC-80 (MBASIC), including allocation, garbage collection algorithm, and performance characteristics
keywords:
- string
- memory
- garbage collection
- allocation
- heap
- MBASIC
- CP/M
- Intel 8080
- performance
title: 'String Allocation and Garbage Collection'
type: guide
---

# CP/M Era MBASIC String Allocation and Garbage Collection

## Overview

This document provides a comprehensive analysis of how string memory management worked in CP/M era Microsoft BASIC-80 (MBASIC), based on examination of original source code and historical documentation. This implementation was widely used across 8-bit computing platforms including CP/M systems, Commodore 64, Apple II (Applesoft), and TRS-80.

## String Memory Architecture

### Memory Layout

In CP/M MBASIC, memory was organized with distinct regions:

```
High Memory (MEMSIZ)
    ↓
String Heap (grows downward)
    ↓
Free Space (FRETOP marks boundary)
    ↑
Arrays (ARYTAB to STREND)
    ↑
Simple Variables (VARTAB to ARYTAB)
    ↑
Program Text
    ↑
Low Memory
```

### String Descriptors

Each string was represented by a 3-byte descriptor:
- **Byte 0**: Length (0-255 characters max)
- **Bytes 1-2**: Pointer to actual string data (16-bit address)

String descriptors were stored in:
- Simple variable area (for string variables)
- Array area (for string arrays)
- Temporary string stack (for intermediate expressions)
- Parameter blocks (for function parameters)

### String Data Storage

Actual string data was stored in the **string heap**, which grew downward from high memory (MEMSIZ). The pointer FRETOP marked the current bottom of string storage.

## String Allocation Process

### The GETSPA Routine

The `getspa` (GET SPAce) routine was the primary string allocation function:

1. **Input**: Number of bytes needed in accumulator (A register)
2. **Process**:
   - Check if space available between FRETOP and top of arrays
   - If sufficient space: allocate and return pointer
   - If insufficient: trigger garbage collection
3. **Output**: Pointer to allocated space in DE registers

### Allocation Strategy

- Strings allocated from top down (high memory to low)
- No attempt at reuse of freed space until garbage collection
- Each string operation typically allocated new space
- String concatenation, MID$, LEFT$, RIGHT$ all created new strings

## Garbage Collection Algorithm

### The GARBAG Routine

The garbage collection process, implemented in the `garbag` routine, used a compacting algorithm:

#### Phase 1: Find Highest String
```
1. Scan all string descriptors:
   - Temporary string stack (TEMPST to TEMPPT)
   - Simple variables (VARTAB to ARYTAB)
   - Arrays (ARYTAB to STREND)
   - Parameter blocks (linked list via PRMPRV)

2. Find string with highest address in heap
```

#### Phase 2: Relocate String
```
1. Move found string to new top of heap (MEMSIZ)
2. Update descriptor with new address
3. Adjust FRETOP to new boundary
```

#### Phase 3: Repeat
```
1. Scan all descriptors again
2. Find next highest string below FRETOP
3. Move it adjacent to previous string
4. Update descriptor and FRETOP
5. Repeat until no more strings to move
```

### Key Implementation Details from Source Code

From `bistrs.mac`, the core garbage collection logic:

```assembly
garbag: ; Entry point when out of string space
    pop psw         ; Check if already collected
    lxi d,errso     ; Prepare "out of string space" error
    jz error        ; Error if already collected once

garba2: ; Main collection routine
    lhld memsiz     ; Start from top of memory
    shld fretop     ; Reset free space pointer

    ; Iterate through all string storage areas
    ; Finding highest addressed string each pass

grbpas: ; One complete pass done
    ; Move highest string to top
    ; Update its descriptor
    ; Repeat process
```

## Performance Characteristics

### O(n²) Time Complexity

The algorithm's major weakness was its quadratic time complexity:

- **N strings** requiring collection
- **N passes** through all descriptors
- **N × N** total descriptor examinations

### Real-World Impact

| Number of Strings | Approximate Time (2 MHz 8080) |
|------------------|-------------------------------|
| 10               | < 1 second                    |
| 100              | 5-10 seconds                  |
| 500              | 2-5 minutes                   |
| 1000             | 10-20 minutes                 |

### Triggering Conditions

Garbage collection was triggered when:
1. String allocation request couldn't be satisfied
2. No free space between FRETOP and top of arrays
3. FRE() function explicitly called by program

## Intel 8080 Specific Considerations

### Register Usage

The 8080 assembly implementation made specific use of registers:
- **HL**: Primary pointer for descriptor traversal
- **DE**: Secondary pointer/destination address
- **BC**: Counter and temporary storage
- **A**: Length values and comparisons

### Memory Access Patterns

- **Sequential scanning**: Efficient for 8080's limited addressing modes
- **Block moves**: Used BLTUC routine for string relocation
- **16-bit arithmetic**: Heavy use of HL pair for address calculations

### Optimization Constraints

The 8080's limitations influenced the design:
- No multiply/divide instructions (affected array indexing)
- Limited register set (required frequent memory access)
- 64KB address space (made compaction necessary)
- No hardware memory management (software had to handle everything)

## Comparison with Other Implementations

### Contemporary Systems

| System | Garbage Collection | Time Complexity | Notes |
|--------|-------------------|-----------------|-------|
| MBASIC 5.21 | Compacting | O(n²) | Reference implementation |
| Commodore 64 BASIC 2.0 | Compacting | O(n²) | Same algorithm |
| Applesoft BASIC | Compacting | O(n²) | Same core design |
| BBC BASIC | Reference counting | O(1) | Different approach |

### Later Improvements

**BASIC 4.0 and later** (not available on most 8-bit systems):
- Added "back pointers" in string space
- Enabled single-pass collection
- Reduced complexity to O(n)
- Required additional memory per string

**Third-party improvements**:
- Randy Wigginton's Applesoft replacement: grouped string identification
- BASIC.SYSTEM (ProDOS): windowing garbage collector
- Various patches: incremental collection attempts

## Programming Implications

### Best Practices for CP/M Era

1. **Minimize string variables**: Use arrays of characters when possible
2. **Reuse string variables**: Overwrite rather than create new
3. **Clear unused strings**: Set to "" to free descriptors
4. **Pre-allocate space**: Use CLEAR command to set string space
5. **Monitor with FRE()**: Check available space periodically

### Common Pitfalls

1. **String concatenation in loops**: Each operation allocated new space
2. **Parsing operations**: MID$, LEFT$, RIGHT$ all created copies
3. **INPUT from files**: Each line created new string
4. **Array initialization**: Setting many array elements triggered collection

## Implementation for Modern Emulation

### Requirements for 8080 Target

For implementing a compatible garbage collector for 8080 compilation:

1. **Memory Layout Compatibility**
   - Maintain same descriptor format (3 bytes)
   - Preserve heap growth direction (downward)
   - Keep same memory region organization

2. **Algorithm Fidelity**
   - Implement same compacting strategy
   - Maintain O(n²) behavior for compatibility
   - Preserve error conditions and messages

3. **Register Conventions**
   - Follow same register usage patterns
   - Maintain calling conventions
   - Preserve flag settings

4. **Critical Routines**
   - `getspa`: Allocation entry point
   - `garbag`: Collection trigger
   - `garba2`: Main collection loop
   - `grbpas`: Pass completion handler
   - `bltuc`: Block move utility

### Testing Considerations

1. **Boundary conditions**: Full heap, empty heap, single string
2. **Stress testing**: Many small strings vs few large strings
3. **Compatibility**: Test with period-appropriate BASIC programs
4. **Performance**: Verify O(n²) behavior matches original

## Conclusion

The CP/M era MBASIC string garbage collection system represented a pragmatic solution to memory management within the severe constraints of 8-bit systems. While its O(n²) performance could cause significant delays with many strings, it provided automatic memory management that was revolutionary for its time. Understanding this system is crucial for:

- Accurate emulation of period systems
- Writing efficient BASIC programs for vintage hardware
- Appreciating the evolution of memory management techniques
- Implementing compatible interpreters for modern systems

The simplicity of the algorithm, while inefficient, made it reliable and portable across the diverse 8-bit architectures of the late 1970s and early 1980s.

## References

1. Original MBASIC source code: `bistrs.mac` (String handling and garbage collection)
2. "CP/M Era MBASIC String Garbage Collection" historical documentation
3. Microsoft BASIC-80 Reference Manual
4. Various retrocomputing community discussions and analyses
5. Commodore 64 Programmer's Reference Guide
6. Applesoft BASIC Programming Reference Manual
