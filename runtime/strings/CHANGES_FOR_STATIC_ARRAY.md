# Changes for Static String Descriptor Array

## Summary
Updated the MBASIC 2025 string system to use a static array of string descriptors as originally proposed, eliminating dynamic allocation and enabling in-place sorting.

## Key Changes

### 1. Static String Descriptor Array
- **Before**: String descriptors were malloc'd at runtime
- **After**: Static array `mb25_string_t mb25_strings[MB25_NUM_STRINGS]` - size known at compile time
- **Benefit**: More efficient for microprocessors, no dynamic allocation overhead
- **Declaration note**: `mb25_string.h` declares the array *unsized*
  (`extern mb25_string_t mb25_strings[];`); only `mb25_string.c` states the size.
  Giving the size in both places is the ordinary C idiom, but it crashes uc80 - the
  preferred compiler - with an internal error in `_merge_array_size` (the alternate
  z88dk accepts it). The unsized extern is valid C and builds with both.
  See [../../docs/dev/TOOLCHAIN_POLICY.md](../../docs/dev/TOOLCHAIN_POLICY.md).

### 2. Removed Sort Buffer
- **Before**: Used `mb25_global.sort_buffer` for sorting pointers during GC
- **After**: Sort the descriptor array in place using the `str_id` field
- **Benefit**: No extra memory allocation, simpler code

### 3. In-Place Garbage Collection
- **Before**: Sorted pointers in a separate buffer
- **After**:
  1. Sort descriptors in place by data pointer address
  2. Compact strings in the pool
  3. Sort descriptors back by str_id to restore normal access order
- **Benefit**: The str_id field allows restoration of original order after GC

### 4. Simplified Initialization
- **Before**: `mb25_init(pool_size, num_strings)` with dynamic allocation
- **After**: `mb25_init(pool, pool_size)` - pool address provided by caller
- **Benefit**: No malloc needed at all, pool uses memory from __BSS_tail to SP

### 5. No Malloc/Heap Required (2025-11-23)
- **Before**: Pool allocated via malloc() from z88dk heap
- **After**: Pool memory provided directly from __BSS_tail
- **Benefit**: ~56KB pool on 64K system (vs ~39KB with malloc), smaller binary

### 6. Shell Sort Replaces qsort (2025-11-23)
- **Before**: Used stdlib qsort() for sorting descriptors
- **After**: Inline shell sort functions (sort_by_data_ptr, sort_by_str_id)
- **Benefit**: No stdlib dependency, no function pointer overhead

## Performance Impact
- **Memory**: No malloc overhead, pool uses all available memory
- **Speed**: Same O(n log n) complexity with shell sort
- **Code Size**: No malloc/free, no qsort linked in

## Files Modified
- `mb25_string.h`: Updated structures and function signatures
- `mb25_string.c`: Implemented static array and in-place sorting
- `test_mb25_string.c`: Updated for new API

## Testing
All existing tests pass with the new implementation, confirming:
- Correct garbage collection
- String operations work as expected
- No memory corruption
- Performance improvements maintained

## Original Design Intent
This implementation now correctly follows the original proposal where:
- String count is known at compile time
- Descriptors are a static array
- The str_id field enables sorting and restoration
- No dynamic allocation at all (pool uses direct memory from __BSS_tail)