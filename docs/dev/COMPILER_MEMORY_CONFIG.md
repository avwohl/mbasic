# Compiler Memory Configuration

## Overview

The MBASIC-2025 compiler generates CP/M programs with configurable memory settings. Understanding CP/M memory management is essential for optimal configuration.

## CP/M Memory Model

### Stack Pointer Auto-Detection

**The stack pointer is NOT hardcoded!**

z88dk automatically detects the stack location from the BDOS entry point (stored at address `0x0006H`). This is correct CP/M behavior because:

- Not all CP/M systems have 64K RAM (some have 16K, 32K, 48K)
- The BDOS entry point varies by system configuration
- Standard CP/M practice: `LHLD 0006H` then `SPHL` (set SP from BDOS address)

**We only configure STACK SIZE, not location.**

### Memory Layout

```
CP/M Memory (varies by system):

0x0000 ┌─────────────────────────┐
       │  CP/M System (CCP/BDOS) │
0x0100 ├─────────────────────────┤ TPA Start
       │                         │
       │  Your Program Code      │
       │  (compiled from BASIC)  │
       │                         │
       ├─────────────────────────┤
       │  Static Variables       │
       ├─────────────────────────┤
       │                         │
       │  Heap (malloc)          │ ← CLIB_MALLOC_HEAP_SIZE
       │                         │
       │  Contains:              │
       │  - String pool (2048)   │ ← MB25_POOL_SIZE
       │  - GC temp (2048 peak)  │
       │  - C string temps       │
       │  - File I/O buffers     │
       │                         │
       ├─────────────────────────┤
       │  ↓ Stack (grows down)   │ ← CRT_STACK_SIZE (512 bytes)
?????? ├─────────────────────────┤ ← SP (auto-detected from BDOS)
       │  BDOS Entry Point       │
       │  (varies by system)     │
0xFFFF └─────────────────────────┘
```

## Default Settings

```python
{
    'stack_size': 512,           # 512 bytes for call stack (GOSUB/functions)
    'string_pool_size': 2048,    # 2KB for BASIC string storage
    'heap_size': 5120,           # Auto: 2*pool + 1024 = 2*2048 + 1024
}
```

### Why These Defaults?

**stack_size = 512**
- Sufficient for typical GOSUB nesting and function calls
- BASIC programs rarely need deep call stacks

**string_pool_size = 2048**
- This is the PRIMARY memory for BASIC string data
- Doubled from 1KB because strings are the main data type in BASIC

**heap_size = 2 * string_pool_size + 1024**
- The string pool is allocated FROM the heap via `malloc()`
- Heap must hold:
  - String pool itself: 2048 bytes (permanent)
  - GC temp buffer: 2048 bytes (peak during garbage collection)
  - C string conversions: ~512 bytes (transient)
  - File I/O buffers: ~512 bytes
  - **Total: 5120 bytes minimum**

## Heap vs String Pool

**Critical:** The string pool is **allocated from the heap**, not separate!

```c
// This happens at program startup:
mb25_global.pool = malloc(MB25_POOL_SIZE);  // 2048 bytes from heap
```

Therefore:
- ❌ **Wrong:** `heap=2048, string_pool=1024` (heap can't hold pool + GC)
- ✅ **Correct:** `heap=5120, string_pool=2048` (heap >= 2*pool + overhead)

The formula is:
```
heap_size >= (string_pool_size * 2) + 1024
```

## Customizing Memory

### Example: Large String Program

```python
config = {
    'string_pool_size': 4096,    # 4KB for strings
    'heap_size': 9216,           # 2*4096 + 1024 (auto-calculated if omitted)
}

backend = Z88dkCBackend(symbols, config=config)
```

### Example: Minimal Memory

```python
config = {
    'stack_size': 256,           # Smaller stack
    'string_pool_size': 512,     # Few/short strings
    # heap_size auto: 2*512 + 1024 = 2048
}
```

### Example: Override Heap Calculation

```python
config = {
    'string_pool_size': 2048,
    'heap_size': 6144,           # Manual override (must be >= 2*2048+1024)
}
```

## Configuration Parameters

### stack_size
**Type:** Integer (bytes)
**Default:** `512`
**Typical Range:** `256` to `2048`

Size of the call stack for:
- GOSUB/RETURN
- DEF FN function calls
- Expression evaluation
- System library calls

**Increase if:**
- Deep GOSUB nesting
- Many DEF FN functions
- Complex nested expressions
- Stack overflow errors

### string_pool_size
**Type:** Integer (bytes)
**Default:** `2048` (2KB)
**Typical Range:** `512` to `8192`

BASIC string storage pool. This is the MAIN memory for your program's string data.

**Monitor with:** `FRE("")` returns free space in this pool at runtime

**Increase if:**
- Program uses many strings
- Program uses long strings
- `FRE("")` returns low values
- "Out of string space" errors

**Formula:**
```
string_pool_size >= (max_string_length * number_of_strings)
```

### heap_size
**Type:** Integer (bytes)
**Default:** `2 * string_pool_size + 1024`
**Typical Range:** `2048` to `16384`

Heap for `malloc()` - contains:
1. String pool allocation (permanent)
2. GC temp buffer (during collection)
3. Temporary C strings (for printf)
4. File I/O buffers

**Must satisfy:**
```
heap_size >= (2 * string_pool_size) + 1024
```

**Override only if:**
- You understand the memory model
- You need extra heap for libraries
- You're reducing for minimal systems

## Generated Code

With defaults:

```c
/* Memory configuration */
/* Stack pointer auto-detected by z88dk from BDOS (address 0x0006) */
#pragma output CRT_STACK_SIZE = 512
#pragma output CLIB_MALLOC_HEAP_SIZE = 5120

#define MB25_NUM_STRINGS 10
#define MB25_POOL_SIZE 2048  /* String pool size */
```

## Monitoring Memory at Runtime

### String Pool Usage

```basic
10 PRINT "String pool free:", FRE("")
20 A$ = "Test string"
30 PRINT "After allocation:", FRE("")
40 PRINT "Bytes used:", FRE("") - (old value)
```

### Total Memory

```basic
10 F = FRE(0)
20 PRINT "Total free memory:", F
```

Note: `FRE(0)` currently returns a simulated value (16384). String pool monitoring via `FRE("")` is accurate.

## Troubleshooting

### "Out of memory" at startup
**Symptom:** `?Out of memory` when program starts
**Cause:** `mb25_init()` can't allocate string pool from heap
**Solution:**
- Reduce `string_pool_size`
- Increase `heap_size`
- Check: heap >= 2*pool + 1024

### "Out of string space" during execution
**Symptom:** String operations fail at runtime
**Cause:** String pool exhausted
**Solution:**
- Increase `string_pool_size`
- Increase `heap_size` proportionally
- Monitor with `FRE("")`

### Stack overflow
**Symptom:** Program crashes in GOSUB or function calls
**Solution:** Increase `stack_size`

### Program won't run on small CP/M system
**Symptom:** Works in emulator, fails on real hardware
**Cause:** Real system has less RAM (16K-48K vs 64K)
**Solution:**
- Reduce all memory settings
- Test in emulator with accurate RAM size
- Remember: z88dk auto-detects available TPA

## Why Not Hardcode Stack Pointer?

Early versions incorrectly set:
```c
#pragma output REGISTER_SP = 0xF000  // ❌ WRONG!
```

This is **incorrect** because:
1. Assumes 64K RAM (many systems have less)
2. Assumes BDOS at fixed location (it varies)
3. Breaks on CP/M 2.2 vs 3.0 systems
4. Ignores CP/M standard practice

**Correct approach:** Let z88dk read BDOS location at runtime from address `0x0006H`.

## See Also

- [mb25_string.h](../../test_compile/mb25_string.h) - String system implementation
- [test_custom_memory.py](../../test_compile/test_custom_memory.py) - Configuration example
- [z88dk CP/M Platform](https://github.com/z88dk/z88dk/wiki/Platform---CPM)
