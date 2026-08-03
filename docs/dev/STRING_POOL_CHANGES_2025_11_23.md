# String Pool Memory Allocation Changes (2025-11-23)

## Summary
Changed from malloc-based heap allocation to direct memory allocation from BSS_tail.

## Toolchain note

The scheme itself is compiler-independent — the pool always occupies the gap between the
end of BSS and the stack. What differs is how the program obtains those two addresses:

- **uc80** (preferred, with um80/ul80): it has no inline assembly, and C cannot name the
  linker symbols directly (`extern char __BSS_END[]` emits `EXTRN ___BSS_END` and fails
  to link). Both the BSS end and the stack pointer therefore come from the assembly shim
  `runtime/strings/mb25_uc80_shim.mac`, which is assembled separately with `um80` and
  linked in as its own `.rel`.
- **z88dk** (alternate): supplies `__BSS_tail` and accepts a `__naked` function with
  inline `__asm__`. That is the form shown below, because z88dk was the only toolchain
  in use when this change was made.

See [TOOLCHAIN_POLICY.md](TOOLCHAIN_POLICY.md) for the full comparison.

## OLD SYSTEM (REMOVED)
- String pool allocated via `malloc()` from z88dk heap
- Compiled with `-DAMALLOC` flag to enable heap
- `mb25_init(pool_size)` called malloc internally
- `mb25_cleanup()` called free()
- Fixed pool size (default 2048 bytes, configurable)
- Max usable: ~39KB due to heap management overhead
- Extra ~1KB code for heap allocator

## NEW SYSTEM
- String pool uses memory directly from `__BSS_tail` to `SP - stack_reserve`
- No `-DAMALLOC` flag (no heap linked in)
- `mb25_init(pool_address, pool_size)` receives pre-calculated values
- No malloc/free needed
- Dynamic pool size based on available memory
- Max usable: ~56KB on 64K CP/M system
- Smaller binary (no heap code)

## Memory Layout
```
0x0100 ┌─────────────────────┐ TPA Start
       │  Program Code       │
       │  Static Variables   │
       │  FCBs (file I/O)    │ ← File buffers in BSS, not heap!
       ├─────────────────────┤ __BSS_tail
       │                     │
       │  STRING POOL        │ ← All free memory for strings
       │  (dynamic size)     │
       │                     │
       ├─────────────────────┤ SP - 1024
       │  Stack reserve      │
       └─────────────────────┘ SP
```

## Key Findings
1. **File I/O doesn't use heap** - FCBs are static arrays in BSS
2. **z88dk heap adds overhead** - both code size and memory management
3. **Direct allocation is simpler** - just use the memory after BSS

## Files Changed
- `runtime/strings/mb25_string.c` - New init signature, no malloc/free
- `runtime/strings/mb25_string.h` - Updated function signature
- `src/codegen_backend.py` - Remove -DAMALLOC, generate pool calculation code

## Codegen Changes
Generated startup code now includes (z88dk form; under uc80 the same two values arrive
through the `.mac` shim described in the toolchain note above):
```c
/* Get BSS end and SP for pool calculation */
extern unsigned char __BSS_tail;
static uint16_t _get_sp(void) __naked {
    __asm__("ld hl,0\n add hl,sp\n ret");
}

int main(void) {
    uint16_t pool_start = (uint16_t)&__BSS_tail;
    uint16_t pool_size = _get_sp() - 1024 - pool_start;
    mb25_init((uint8_t*)pool_start, pool_size);
    ...
}
```

## Additional: Shell Sort Replaces qsort

The garbage collector now uses inline shell sort instead of stdlib's qsort:
- Avoids linking qsort from stdlib (no stdlib.h needed)
- Shell sort is efficient for small arrays (typically <100 strings)
- Same O(n log n) complexity as qsort
- Implemented in `sort_by_data_ptr()` and `sort_by_str_id()`
