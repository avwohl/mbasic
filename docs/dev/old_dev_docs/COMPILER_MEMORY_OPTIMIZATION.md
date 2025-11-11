# Compiler Backend Memory Optimization Design

**Status**: Future Work - Design complete, implementation pending

## Overview

Design for managing large objects (arrays and string space) in constrained memory systems like the 8080, following MBASIC 5.21 memory management patterns.

This is a comprehensive design document for future implementation when targeting 8080 or other memory-constrained systems.

## Problem Statement

In an 8080 system with limited memory (typically 16-64KB), we need to efficiently manage:

1. **Arrays** - Large multi-dimensional data structures
2. **String space** - Dynamic string storage
3. **String descriptors** - Metadata for each string variable

Runtime stack and loop stack have small, known limits and can be statically allocated. The challenge is managing the two large, dynamic memory areas.

## Memory Layout

### Overall Memory Organization

```
┌──────────────────────────────────┐ ← 0x0000
│ CP/M System Area                 │
├──────────────────────────────────┤
│ MBASIC Interpreter               │
├──────────────────────────────────┤
│ Loaded BASIC Program             │
├──────────────────────────────────┤
│ Static Variables                 │ (Simple variables: A%, X, NAME$, etc.)
├──────────────────────────────────┤ ← STKTOP (start of dynamic area)
│                                  │
│ ↓ Arrays (grow downward)         │ ← Arrays allocated here
│                                  │
│         Free Space               │
│                                  │
│ ↑ Strings (grow upward)          │ ← Strings allocated here
│                                  │
├──────────────────────────────────┤ ← MEMSIZ (top of available memory)
│ Runtime Stack                    │ (Small, fixed size ~256 bytes)
├──────────────────────────────────┤
│ FOR/WHILE Loop Stack            │ (Small, fixed size ~512 bytes)
├──────────────────────────────────┤
│ GOSUB Stack                      │ (Small, fixed size ~256 bytes)
└──────────────────────────────────┘ ← Top of RAM
```

### Key Pointers

- **STKTOP** - Top of static variables, start of dynamic memory pool
- **ARYEND** - End of array area (grows down from STKTOP)
- **STREND** - Start of string space (grows up toward MEMSIZ)
- **MEMSIZ** - Top of available memory for dynamic allocation

### Invariant

```
STKTOP >= ARYEND >= STREND >= MEMSIZ - (stack sizes)
```

At all times: `ARYEND - STREND` = free space

## Array Management

### Array Storage

Arrays are allocated as contiguous blocks in the array area.

**Layout per array**:
```
┌────────────────────────────────────┐
│ Name (2 bytes): "A$", "X%", etc.  │
├────────────────────────────────────┤
│ Type (1 byte): $ % ! # or none    │
├────────────────────────────────────┤
│ Dimensions (1 byte): # of dims     │
├────────────────────────────────────┤
│ Dim sizes (2 bytes each)           │ e.g., 10, 20 for DIM A(10, 20)
├────────────────────────────────────┤
│ Data (variable size)               │ Actual array elements
└────────────────────────────────────┘
```

**Data size calculation**:
- Integer (%): 2 bytes per element
- Single precision (default): 4 bytes per element
- Double precision (#): 8 bytes per element
- String ($): 3 bytes per element (see String Descriptors below)

### Array Allocation Algorithm

```python
def allocate_array(name, type_suffix, dimensions):
    """Allocate array in array area."""
    # Calculate total elements
    total_elements = 1
    for dim_size in dimensions:
        total_elements *= (dim_size + 1)  # +1 because 0-based

    # Calculate bytes needed
    header_size = 4 + (2 * len(dimensions))  # name + type + ndims + dim sizes

    if type_suffix == '%':
        element_size = 2
    elif type_suffix == '#':
        element_size = 8
    elif type_suffix == '$':
        element_size = 3  # String descriptor
    else:
        element_size = 4  # Single precision

    data_size = total_elements * element_size
    total_size = header_size + data_size

    # Check if space available
    if ARYEND - total_size < STREND:
        raise "OUT OF MEMORY"

    # Allocate by moving ARYEND down
    ARYEND -= total_size

    # Initialize array header at ARYEND
    write_array_header(ARYEND, name, type_suffix, dimensions)

    # Zero-initialize data
    zero_memory(ARYEND + header_size, data_size)

    return ARYEND
```

### Array Access

Arrays are accessed by computing offset from base address:

```python
def get_array_element_address(array_base, subscripts):
    """Calculate address of array element."""
    # Read header
    dimensions = read_dimensions(array_base)
    element_size = read_element_size(array_base)
    header_size = calculate_header_size(dimensions)

    # Calculate linear offset using row-major order
    offset = 0
    multiplier = 1

    for i in reversed(range(len(subscripts))):
        offset += subscripts[i] * multiplier
        multiplier *= (dimensions[i] + 1)

    # Return address
    return array_base + header_size + (offset * element_size)
```

## String Management

### Two-Part String System

Strings are stored in two parts:

1. **String descriptors** - Fixed-size metadata (3 bytes each)
2. **String space** - Actual string character data

### String Descriptors

String descriptors can be stored in:
- Static variable area (for simple string variables)
- Array area (for string array elements)
- Temporary expression area (for intermediate results)

**Descriptor format (3 bytes)**:
```
┌─────────────────────────────────┐
│ Length (1 byte): 0-255 chars    │
├─────────────────────────────────┤
│ Address (2 bytes): pointer to   │
│   actual string data in string  │
│   space                          │
└─────────────────────────────────┘
```

### String Space

Actual string characters are stored in the string space area, growing upward from STREND.

**Key property**: Strings are **read-only** after allocation.

### String Allocation

```python
def allocate_string(text):
    """Allocate string in string space."""
    length = len(text)

    # Check space available
    if STREND + length > ARYEND:
        # Try garbage collection first
        garbage_collect_strings()
        if STREND + length > ARYEND:
            raise "OUT OF MEMORY"

    # Allocate by advancing STREND
    string_addr = STREND
    STREND += length

    # Copy string data
    write_memory(string_addr, text)

    # Return descriptor
    return (length, string_addr)
```

### String Operations - Zero Copy Optimization

Because strings are **read-only**, substring operations can return pointers into existing strings without copying:

```python
def string_left(descriptor, n):
    """LEFT$(str, n) - return leftmost n characters."""
    length, address = descriptor
    new_length = min(n, length)
    return (new_length, address)  # Same address, shorter length!

def string_right(descriptor, n):
    """RIGHT$(str, n) - return rightmost n characters."""
    length, address = descriptor
    new_length = min(n, length)
    new_address = address + (length - new_length)
    return (new_length, new_address)  # Offset address!

def string_mid(descriptor, start, length):
    """MID$(str, start, length) - return substring."""
    orig_length, address = descriptor
    # Clamp to bounds
    actual_start = min(max(start - 1, 0), orig_length)  # BASIC is 1-indexed
    actual_length = min(length, orig_length - actual_start)
    return (actual_length, address + actual_start)  # Offset address!
```

**Example**:
```basic
10 A$ = "HELLO WORLD"      ' Allocates 11 bytes in string space
20 B$ = LEFT$(A$, 5)        ' No allocation! Points to first 5 chars of A$
30 C$ = RIGHT$(A$, 5)       ' No allocation! Points to "WORLD" in A$
40 D$ = MID$(A$, 7, 5)      ' No allocation! Points to "WORLD" in A$
50 E$ = B$                  ' No allocation! Just copies 3-byte descriptor
60 F$ = "NEW" + B$          ' Allocation! Creates new string "NEWHELLO"
```

### String Assignment - Costly Operation

Assignment **always allocates** new string space:

```python
def assign_string(variable, descriptor):
    """Assign string to variable - always allocates."""
    length, address = descriptor

    # Read the string data
    text = read_memory(address, length)

    # Allocate new string space
    new_descriptor = allocate_string(text)

    # Update variable descriptor
    write_descriptor(variable, new_descriptor)
```

**Why costly?**
1. Must read original string
2. Must allocate new space
3. Must copy all characters
4. Creates fragmentation in string space

## String Space Garbage Collection

### Problem

As strings are allocated and variables are reassigned, the string space becomes fragmented with unreachable strings.

### Solution: Compact Garbage Collection

```python
def garbage_collect_strings():
    """Compact string space by removing unreachable strings."""
    # Phase 1: Mark - Find all reachable strings
    reachable = set()

    # Mark strings from simple variables
    for var in simple_string_variables:
        _, address = var.descriptor
        reachable.add(address)

    # Mark strings from arrays
    for array in string_arrays:
        for element in array.elements:
            _, address = element
            reachable.add(address)

    # Mark strings from expression stack
    for expr in expression_stack:
        if is_string(expr):
            _, address = expr.descriptor
            reachable.add(address)

    # Phase 2: Compact - Copy reachable strings to new area
    new_strend = MEMSIZ - stack_sizes
    address_map = {}  # Old address -> new address

    for old_address in sorted(reachable):
        length = find_string_length(old_address)
        text = read_memory(old_address, length)

        new_strend -= length
        write_memory(new_strend, text)
        address_map[old_address] = new_strend

    # Phase 3: Update - Fix all descriptors
    for var in simple_string_variables:
        length, old_address = var.descriptor
        var.descriptor = (length, address_map[old_address])

    for array in string_arrays:
        for i, element in enumerate(array.elements):
            length, old_address = element
            array.elements[i] = (length, address_map[old_address])

    # Update STREND
    STREND = new_strend
```

## Critical: In-Place Garbage Collection

### Problem

With read-only strings, every assignment creates garbage:

**Example**:
```basic
10 A$ = "HELLO"            ' Allocates 5 bytes
20 FOR I = 1 TO 1000
30   A$ = A$ + " WORLD"    ' Allocates 1000 times! Old strings become garbage
40 NEXT I                   ' Result: ~6MB of garbage for 6KB final string!
```

**Why pre-allocation won't work**:
- Strings are read-only, so can't update in place
- Pre-allocated mutable buffer would break zero-copy substring optimization
- Pre-allocation wastes memory that could be used for arrays or other strings

### Solution: Efficient In-Place Garbage Collection

The key optimization is **frequent, efficient garbage collection** that compacts strings without allocating temporary memory.

#### Constraint: In-Place Compaction

**Problem**: Cannot allocate temporary space for new pointer table (not enough memory on 8080)

**Solution**: Two-pass in-place algorithm

### In-Place String Compaction Algorithm

#### Pass 1: Calculate New Addresses (Mark)

Walk through all string descriptors and mark strings as reachable. Calculate where each string will be after compaction.

```python
def calculate_new_addresses():
    """Pass 1: Determine new addresses without moving anything."""
    # Sort all reachable strings by current address
    reachable = []

    # Collect from simple variables
    for var in simple_string_variables:
        length, address = var.descriptor
        reachable.append((address, length, var))

    # Collect from string arrays
    for array in string_arrays:
        for i, element in enumerate(array.elements):
            length, address = element
            reachable.append((address, length, (array, i)))

    # Collect from expression stack
    for expr in expression_stack:
        if is_string(expr):
            length, address = expr.descriptor
            reachable.append((address, length, expr))

    # Sort by current address (ascending)
    reachable.sort(key=lambda x: x[0])

    # Calculate new addresses by packing from MEMSIZ downward
    new_strend = MEMSIZ - stack_sizes
    address_map = {}  # old_address -> (new_address, length, owner)

    for old_address, length, owner in reachable:
        # Skip duplicates (same string pointed to by multiple vars)
        if old_address in address_map:
            continue

        new_strend -= length
        address_map[old_address] = (new_strend, length, owner)

    return address_map, new_strend
```

#### Pass 2: Compact Strings (Sweep)

Move strings to their new locations, updating descriptors as we go.

**Key challenge**: Strings may overlap during compaction!

**Solution**: Process in correct order to avoid overwriting

```python
def compact_strings_in_place(address_map, new_strend):
    """Pass 2: Move strings to new locations without temporary buffer."""

    # Separate into two groups:
    # 1. Moving DOWN (new_addr < old_addr) - process LOW to HIGH
    # 2. Moving UP (new_addr > old_addr) - process HIGH to LOW

    moving_down = []
    moving_up = []

    for old_addr, (new_addr, length, owner) in address_map.items():
        if new_addr < old_addr:
            moving_down.append((old_addr, new_addr, length, owner))
        elif new_addr > old_addr:
            moving_up.append((old_addr, new_addr, length, owner))
        # else: no move needed (new_addr == old_addr)

    # Process moving DOWN first (low addresses to high)
    # This is safe because we're moving toward lower memory
    for old_addr, new_addr, length, owner in sorted(moving_down, key=lambda x: x[0]):
        # Read string (may overlap destination, but we're moving down so it's safe)
        text = read_memory(old_addr, length)

        # Write to new location
        write_memory(new_addr, text)

        # Update descriptor
        update_descriptor(owner, (length, new_addr))

    # Process moving UP next (high addresses to low)
    # This is safe because we're moving toward higher memory
    for old_addr, new_addr, length, owner in sorted(moving_up, key=lambda x: x[0], reverse=True):
        # Read string (safe because we're moving up)
        text = read_memory(old_addr, length)

        # Write to new location
        write_memory(new_addr, text)

        # Update descriptor
        update_descriptor(owner, (length, new_addr))

    # Update global STREND pointer
    STREND = new_strend
```

#### When to Trigger GC

Trigger garbage collection in these situations:

1. **String allocation fails** - Try GC, then retry allocation
2. **STREND gets close to ARYEND** - Proactive GC when < 1KB free
3. **After loop execution** - Clean up loop-generated garbage
4. **Before large array allocation** - Make space for arrays

```python
def allocate_string_with_gc(text):
    """Allocate string, with automatic GC if needed."""
    length = len(text)

    # Try direct allocation
    if STREND + length <= ARYEND:
        return allocate_string_direct(text)

    # Not enough space - try garbage collection
    garbage_collect_strings()

    # Retry allocation
    if STREND + length <= ARYEND:
        return allocate_string_direct(text)

    # Still not enough - out of memory
    raise "OUT OF MEMORY"
```

### Compiler Optimizations for GC

#### 1. Insert Explicit GC Calls

Compiler can insert GC calls at strategic points:

```basic
10 FOR I = 1 TO 10000
20   A$ = A$ + "X"
30 NEXT I
```

Compiled to:
```assembly
; Start of loop
LOOP_START:
    ; ... loop body ...
    CALL STRING_CONCAT
    CALL ASSIGN_STRING

    ; Every 100 iterations, do GC
    LD A, (LOOP_COUNTER)
    AND 63                  ; Check if counter & 63 == 0 (every 64 iterations)
    CALL Z, GARBAGE_COLLECT ; GC if zero

    ; ... loop control ...
    JP LOOP_START
```

#### 2. Hoist Loop-Invariant Strings

If string expressions don't change in loop, evaluate once:

```basic
10 FOR I = 1 TO 1000
20   A$ = "PREFIX_" + B$    ' B$ doesn't change in loop
30 NEXT I
```

Optimized to:
```basic
10 TEMP$ = "PREFIX_" + B$   ' Calculate once before loop
20 FOR I = 1 TO 1000
30   A$ = TEMP$              ' Just copy descriptor
40 NEXT I
```

#### 3. Dead String Elimination

Mark variables as "dead" after last use, allowing GC to reclaim immediately:

```basic
10 A$ = "TEMP"              ' A$ allocated
20 PRINT A$                  ' A$ last use - mark descriptor as dead
30 B$ = "OTHER"              ' GC can reclaim A$ here
```

### Benefits

1. **No temporary buffer needed**: In-place compaction uses minimal extra memory
2. **Handles overlaps correctly**: Two-pass algorithm prevents overwrites
3. **Compiler-driven**: Strategic GC placement reduces overhead
4. **Memory efficient**: Reclaims garbage frequently in tight loops

### Trade-offs

1. **GC overhead**: Compaction takes time (must move all strings)
2. **Pause time**: GC causes brief pause in program execution
3. **Compiler complexity**: Requires liveness analysis for optimization

### Performance Characteristics

**Time complexity**:
- Mark phase: O(n) where n = number of string variables/array elements
- Sweep phase: O(m) where m = total bytes of reachable strings
- Total: O(n + m)

**Space complexity**:
- No temporary buffers needed
- Address map can reuse expression stack space (not in use during GC)
- Worst case: O(n) for address map (one entry per reachable string)

**When is GC fast?**:
- Few reachable strings (most are garbage)
- Strings already mostly compacted (little movement needed)
- Small total string space

**When is GC slow?**:
- Many reachable strings (lots to move)
- Strings heavily fragmented (lots of movement)
- Large individual strings (memcpy overhead)

## Implementation Phases

### Phase 1: Basic Memory Management (Complete)
- [x] Separate array and string spaces
- [x] Array allocation with dimension tracking
- [x] String descriptor system
- [x] Basic string allocation

### Phase 2: String Optimization (Current)
- [ ] Implement zero-copy substring operations (LEFT$, RIGHT$, MID$)
- [ ] In-place string space garbage collection
  - [ ] Pass 1: Mark reachable strings and calculate new addresses
  - [ ] Pass 2: Compact strings in-place (handle overlaps correctly)
  - [ ] Update all descriptors during compaction
- [ ] Proper memory overflow detection with GC retry

### Phase 3: Compiler-Driven GC Optimization (Future)
- [ ] Static analysis for string liveness
- [ ] Insert strategic GC calls (loop boundaries, after large allocations)
- [ ] Dead string elimination
- [ ] Loop-invariant string hoisting
- [ ] Configurable GC aggressiveness
- [ ] Performance benchmarking (with/without optimizations)

## Testing Strategy

### Test Cases

1. **Array allocation**
   ```basic
   10 DIM A%(100, 100)   ' Large 2D array
   20 DIM B$(50)         ' String array
   30 DIM C#(10, 10, 10) ' 3D double array
   ```

2. **String operations**
   ```basic
   10 A$ = "HELLO WORLD"
   20 B$ = LEFT$(A$, 5)
   30 C$ = RIGHT$(A$, 5)
   40 D$ = MID$(A$, 7, 5)
   50 PRINT B$; " "; C$; " "; D$
   ```

3. **Memory limits**
   ```basic
   10 DIM HUGE%(1000, 1000)  ' Should fail with OUT OF MEMORY
   ```

4. **Garbage collection**
   ```basic
   10 FOR I = 1 TO 1000
   20   A$ = "TEST" + STR$(I)
   30 NEXT I
   40 REM String space should be compacted
   ```

5. **Garbage collection efficiency**
   ```basic
   10 A$ = ""
   20 FOR I = 1 TO 10000
   30   A$ = A$ + "X"
   40 NEXT I
   50 PRINT LEN(A$)
   60 REM Should trigger GC multiple times during loop
   ```

### Benchmarks

Compare with and without GC optimizations:
- Execution time
- Memory usage (peak and average)
- Number of GC cycles triggered
- GC pause times
- String space fragmentation ratio

## References

- MBASIC 5.21 source code (CP/M version)
- Intel 8080 assembly language reference
- "CP/M 2.2 Operating System Manual"
- Original MBASIC memory layout diagrams

## Future Enhancements

1. **String interning**: Deduplicate identical string literals at compile time
2. **Incremental garbage collection**: Spread GC work over multiple allocations to avoid long pauses
3. **Generational GC**: Separate short-lived from long-lived strings
4. **Lazy concatenation**: Build rope structure, defer flatten until string accessed
5. **Reference counting**: Fast reclamation of temporary strings (combined with GC for cycles)
6. **String pooling**: Intern common strings like "" and single characters

## Notes

- Current MBASIC implementation uses immediate allocation everywhere
- **In-place GC is essential** for memory-constrained systems like 8080
- Read-only strings enable zero-copy substring operations (major win!)
- Must maintain compatibility with existing BASIC programs
- Memory layout must match original MBASIC for data file compatibility
- GC pause times must be bounded for interactive programs
