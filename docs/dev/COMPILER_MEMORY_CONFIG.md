# Compiler Memory Configuration

## Overview

The MBASIC-2025 compiler allows you to customize memory settings for compiled CP/M programs. This is useful for:

- **Programs with large string operations** - Increase string pool size
- **Deep recursion or complex expressions** - Increase stack size
- **Dynamic memory allocation** - Increase heap size
- **Systems with limited RAM** - Reduce memory footprint
- **Systems with more RAM** - Use higher memory for stack pointer

## Default Settings

The compiler uses these defaults (optimized for typical CP/M systems with 64K RAM):

```python
{
    'stack_pointer': '0xF000',      # 60K - Stack location in memory
    'stack_size': 512,               # 512 bytes for call stack
    'heap_size': 2048,               # 2KB for malloc/dynamic allocation
    'string_pool_size': 1024,        # 1KB for string storage
}
```

## Memory Map

```
CP/M Memory Layout (64K system):

0x0000 ┌─────────────────────────┐
       │  CP/M System (CCP/BDOS) │
0x0100 ├─────────────────────────┤
       │                         │
       │  Your Program Code      │
       │                         │
       ├─────────────────────────┤
       │  Static Variables       │
       ├─────────────────────────┤
       │  Heap (malloc)          │ ← CLIB_MALLOC_HEAP_SIZE
       ├─────────────────────────┤
       │  String Pool            │ ← MB25_POOL_SIZE
       ├─────────────────────────┤
       │  ↓ Stack (grows down)   │ ← CRT_STACK_SIZE
0xF000 ├─────────────────────────┤ ← REGISTER_SP
       │  BDOS Entry Point       │
0xFFFF └─────────────────────────┘
```

## Customizing Memory Settings

### Method 1: Using Z88dkCBackend directly

```python
from src.codegen_backend import Z88dkCBackend

# Custom configuration
config = {
    'stack_pointer': '0xFC00',      # 63K - for systems with more RAM
    'stack_size': 1024,              # 1KB stack
    'heap_size': 4096,               # 4KB heap
    'string_pool_size': 2048,        # 2KB string pool
}

# Create backend with custom config
backend = Z88dkCBackend(symbol_table, config=config)
c_code = backend.generate(program)
```

### Method 2: Modifying semantic_analyzer.compile()

```python
# Future enhancement - pass config to compile()
analyzer.compile(program, backend_name='z88dk',
                output_file='myprogram',
                memory_config=config)
```

## Configuration Parameters

### stack_pointer
**Type:** String (hex address)
**Default:** `'0xF000'` (60K)
**Range:** `0xDC00` to `0xFC00` typically

Sets where the stack starts in memory. Common values:
- `0xDC00` (56K) - Conservative, works on most systems
- `0xF000` (60K) - Default, good for typical 64K systems
- `0xFC00` (63K) - Maximum, requires full 64K RAM

**Choose lower values if:**
- Your CP/M system has less than 64K RAM
- You get "Out of memory" errors at runtime
- The BDOS entry point is lower (check with `STAT`)

### stack_size
**Type:** Integer (bytes)
**Default:** `512`
**Range:** `256` to `2048` typically

Size of the call stack for function calls, local variables, and GOSUB returns.

**Increase if:**
- Your program has deep GOSUB nesting
- You use many DEF FN functions
- You get stack overflow errors

**Decrease if:**
- Memory is tight and program is simple

### heap_size
**Type:** Integer (bytes)
**Default:** `2048` (2KB)
**Range:** `512` to `8192` typically

Size of heap for `malloc()` - used for:
- Temporary string conversions (`mb25_to_c_string`)
- File I/O buffers
- Dynamic allocations

**Increase if:**
- Many string operations in single statement
- Large file I/O operations
- You get "Out of memory" errors

### string_pool_size
**Type:** Integer (bytes)
**Default:** `1024` (1KB)
**Range:** `256` to `8192` typically

Size of the mb25 string pool for BASIC string storage.

**Check with:** `FRE("")` returns free space in this pool

**Increase if:**
- Program uses many/long strings
- `FRE("")` returns low values
- You get "Out of string space" errors

**Formula:**
```
string_pool_size >= (max_string_length × number_of_strings)
```

## Example: Large String Program

```python
# Program that manipulates many large strings
config = {
    'string_pool_size': 4096,  # 4KB for strings
    'heap_size': 4096,         # 4KB for conversions
}

backend = Z88dkCBackend(symbols, config=config)
```

## Example: Minimal Memory

```python
# Simple program, minimal memory footprint
config = {
    'stack_pointer': '0xDC00',  # Conservative
    'stack_size': 256,           # Small stack
    'heap_size': 512,            # Minimal heap
    'string_pool_size': 256,     # Few strings
}

backend = Z88dkCBackend(symbols, config=config)
```

## Monitoring Memory Usage

### At Compile Time

The compiler reports:
- `MB25_NUM_STRINGS` - Number of string descriptors allocated

### At Runtime

Use BASIC functions:
- `FRE(0)` - Returns total free memory (currently simulated as 16384)
- `FRE("")` - Returns actual free space in string pool

Example:
```basic
10 PRINT "String pool free:", FRE("")
20 A$ = "Long string..."
30 PRINT "After allocation:", FRE("")
```

## Troubleshooting

### "Out of memory" at startup
- **Cause:** `mb25_init()` failed to allocate string pool
- **Solution:** Reduce `string_pool_size` or increase `REGISTER_SP`

### Stack overflow during execution
- **Symptom:** Program crashes in GOSUB/function calls
- **Solution:** Increase `stack_size`

### "Out of string space" during execution
- **Symptom:** String operations fail
- **Solution:** Increase `string_pool_size`
- **Check:** Use `FRE("")` to monitor usage

### Compilation fails with "Out of memory"
- **Solution:** Reduce total memory usage or check z88dk limits

## z88dk Pragmas Reference

The config generates these z88dk pragmas:

```c
#pragma output REGISTER_SP = 0xF000           // Stack pointer location
#pragma output CRT_STACK_SIZE = 512           // Stack size in bytes
#pragma output CLIB_MALLOC_HEAP_SIZE = 2048   // Heap size for malloc

#define MB25_NUM_STRINGS 10        // Number of string descriptors
#define MB25_POOL_SIZE 1024        // String pool size in bytes
```

## See Also

- [mb25_string.h](/test_compile/mb25_string.h) - String system implementation
- [z88dk documentation](https://github.com/z88dk/z88dk/wiki) - Compiler details
- CP/M memory map documentation
