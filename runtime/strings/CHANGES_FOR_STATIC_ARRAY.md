# Changes for Static String Descriptor Array

## Summary
Updated the MBASIC 2025 string system to use a static array of string descriptors as originally proposed, eliminating dynamic allocation and enabling in-place sorting.

## Key Changes

### 1. Static String Descriptor Array
- **Before**: String descriptors were malloc'd at runtime
- **After**: Static array `mb25_string_t mb25_strings[MB25_NUM_STRINGS]` - size known at compile time
- **Benefit**: More efficient for microprocessors, no dynamic allocation overhead

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
- **After**: `mb25_init(pool_size)` - only allocates the string pool
- **Benefit**: Simpler API, fewer failure points

## Performance Impact
- **Memory**: Saves memory for sort buffer (was `num_strings * sizeof(pointer)`)
- **Speed**: Same O(n log n) complexity but with better cache locality
- **Code Size**: Smaller code without malloc/free for descriptors

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
- No dynamic allocation except for the string pool itself