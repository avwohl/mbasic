# MBASIC 2025 String Allocator and Garbage Collection Specification

## Overview

This document provides the complete specification for the MBASIC 2025 string allocation and garbage collection system designed for compilation to z88dk/Z80. The new system eliminates the O(n²) performance problem of the original MBASIC 5.21 while maintaining compatibility with BASIC string semantics.

## Historical Context

The original MBASIC 5.21 string garbage collector suffered from quadratic time complexity:
- For N strings, it performed N scans of all string descriptors
- This resulted in O(n²) performance, causing minutes or hours of delay with hundreds of strings
- The algorithm moved strings one at a time from highest to lowest address

## New Design Goals

1. **Linear or linearithmic performance**: O(n log n) worst case for garbage collection
2. **Memory efficiency**: Support for constant strings without heap allocation
3. **Writeable optimization**: Reuse allocated space when possible
4. **Substring sharing**: Allow LEFT$, RIGHT$, MID$ to share data when safe
5. **Compile-time optimization**: Known string count at compile time

## Data Structures

### String Descriptor

```c
struct mb25_string_R {
    uint16_t str_id:14;      // String identifier (supports up to 16K strings)
    uint16_t is_const:1;      // 1 if points to constant/ROM data
    uint16_t writeable:1;     // 1 if data can be modified in-place
    uint8_t  len;             // String length (0-255 characters)
    uint8_t  *data;           // Pointer to string data
};

typedef struct mb25_string_R mb25_string_t;
typedef mb25_string_t *mb25_string_pt;
```

### Global State

```c
struct mb25_globals_R {
    uint16_t pool_size;       // Total size of string pool
    uint16_t allocator;       // Current allocation position
    uint8_t  *pool;           // Pointer to malloc'd string pool
    uint16_t num_strings;     // Total number of string descriptors
    mb25_string_t *strings;   // Array of string descriptors
};
```

## String Categories

### 1. Constant Strings
- Strings assigned from literal constants: `A$ = "foo"`
- `is_const = 1`, `writeable = 0`
- `data` points to constant data in ROM/program memory
- No heap space used

### 2. Writeable Strings
- Newly allocated strings from operations or user input
- `is_const = 0`, `writeable = 1`
- Can be overwritten in-place if new data fits
- Reduces fragmentation

### 3. Shared/Immutable Strings
- Result of substring operations or assignments between variables
- `is_const = 0`, `writeable = 0`
- Multiple descriptors may share the same data
- Becomes immutable when shared

## Memory Layout

```
String Pool:
[allocated strings...][free space][allocator position]
^                                 ^
pool                              pool + allocator

String Descriptors Array:
[0][1][2]...[num_strings-1]
Each contains: str_id, flags, len, data pointer
```

## Core Operations

### String Allocation

#### Allocating Constant String
```c
void mb25_string_alloc_const(uint16_t str_id, const char *const_str);
```
- Sets is_const = 1
- Points to constant data
- No heap allocation

#### Allocating Heap String
```c
void mb25_string_alloc(uint16_t str_id, uint16_t size);
```
- Allocates from heap
- Triggers GC if insufficient space
- Sets writeable = 1

#### Copying String
```c
void mb25_string_copy(uint16_t dest_id, uint16_t src_id);
```
- Handles const/writeable cases
- May reuse space or share data

### Garbage Collection Algorithm

The new algorithm achieves O(n log n) performance:

1. **Sort Phase** (O(n log n))
   - Sort string descriptors by data pointer address
   - Identifies live strings in address order

2. **Compaction Phase** (O(n))
   - Single pass through sorted strings
   - Move each string down to eliminate gaps
   - Update data pointers

3. **Restore Phase** (O(n log n))
   - Sort descriptors back by str_id
   - Restores original access order

### String Operations

#### LEFT$(string, n)
- If source is long-lived: return shared pointer
- Sets source writeable = 0 (becomes immutable)
- No data copy needed

#### RIGHT$(string, n)
- Similar to LEFT$, adjusts pointer and length
- Shares data when possible

#### MID$(string, start, length)
- Non-assignment version shares data
- Assignment version requires new allocation

## Memory Management Policies

### Allocation Strategy
1. Try to allocate from free space at end of pool
2. If insufficient space, run garbage collection once
3. If still insufficient after GC, report "Out of string space"

### Reuse Policy
- If destination is writeable and new data fits: overwrite in place
- If destination shares data: allocate new space
- Constants are never modified

### Sharing Policy
- Variables can share data when assigned: `B$ = C$`
- Sharing disabled when either string becomes writeable
- Substring operations create shared references

## Performance Characteristics

| Operation | Old MBASIC 5.21 | MBASIC 2025 |
|-----------|-----------------|-------------|
| Garbage Collection | O(n²) | O(n log n) |
| String Assignment | O(1) + possible GC | O(1) + possible GC |
| Substring (LEFT$/RIGHT$/MID$) | O(n) copy | O(1) share |
| Concatenation | O(n) + possible GC | O(n) + possible GC |

## Error Conditions

1. **Out of String Space**: Allocation fails after GC
2. **String Too Long**: Attempt to create string > 255 characters
3. **Invalid String ID**: Access to uninitialized descriptor
4. **Null Pointer**: Corrupted string descriptor

## Compile-Time Configuration

```c
#define MB25_NUM_STRINGS      100  // Total string descriptors
#define MB25_POOL_SIZE        8192 // String pool size in bytes
#define MB25_MAX_STRING_LEN   255  // Maximum string length
#define MB25_ENABLE_DEBUG     0    // Debug output enable
```

## Implementation Notes

### Thread Safety
- Single-threaded design (Z80 target)
- No locking required

### Endianness
- Z80 is little-endian
- Data structures match native byte order

### Memory Alignment
- No alignment requirements on Z80
- Packed structures acceptable

### Debugging Support
- Optional debug output for allocation/GC events
- String descriptor dump function
- Pool fragmentation report

## Compatibility with MBASIC 5.21

### Preserved Behavior
- String length limited to 255 characters
- All string operations return new descriptors
- Garbage collection transparent to user

### Improvements
- Dramatically faster garbage collection
- Support for constant strings
- Better memory utilization through sharing

### Differences
- Internal representation completely different
- GC timing may differ (but much faster)
- Memory layout not binary compatible

## Future Enhancements

1. **String Interning**: Cache frequently used strings
2. **Incremental GC**: Spread collection over multiple calls
3. **Memory Pools**: Multiple pools for different string sizes
4. **Reference Counting**: Alternative to mark-and-sweep
5. **Compression**: Store long strings compressed

## Testing Strategy

### Unit Tests
- Allocator correctness
- GC compaction verification
- String operation semantics

### Performance Tests
- GC time vs. string count
- Memory utilization
- Fragmentation patterns

### Stress Tests
- Maximum strings
- Rapid allocation/deallocation
- Mixed operation patterns

### Compatibility Tests
- Run original MBASIC 5.21 programs
- Verify identical output
- Compare memory usage

## Conclusion

This specification provides a modern, efficient string management system for MBASIC 2025 that eliminates the performance problems of the original while maintaining compatibility and adding useful optimizations for constant and shared strings.