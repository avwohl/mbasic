# Compiler Memory Configuration

## Overview

The MBASIC-2025 compiler generates CP/M programs that use all available memory for
strings.

The layout below is the same whichever C toolchain builds the program — uc80 (with
um80/ul80), the preferred compiler, or z88dk, the supported alternate. What differs is
the *name* of the symbol marking the end of BSS and how C reaches it; both are covered
under "Finding the end of BSS" below. See
[TOOLCHAIN_POLICY.md](TOOLCHAIN_POLICY.md).

## CP/M Memory Layout

```
CP/M Memory Map:

0x0000 ┌─────────────────────────┐
       │  Warm boot jump (3)     │
0x0003 │  IOBYTE, Disk byte (2)  │
0x0005 │  BDOS entry jump (3)    │
       │  (address at 0x0006)    │
       ├─────────────────────────┤
0x005C │  Default FCB            │
0x0080 │  Command line / DMA     │
0x0100 ├─────────────────────────┤ TPA Start
       │                         │
       │  Program Code           │
       │  (compiled from BASIC)  │
       │                         │
       ├─────────────────────────┤
       │  Static Variables       │
       │  String Descriptors     │
       │  GOSUB Return Stack     │ ← int gosub_stack[100] array
       │  File Control Blocks    │ ← FCBs are static, not heap
       ├─────────────────────────┤ end of BSS
       │                         │
       │  STRING POOL            │ ← All available memory (~56KB on 64K)
       │  (dynamic size)         │
       │                         │
       ├─────────────────────────┤ SP - 1024 (stack reserve)
       │  Stack reserve          │
       ├─────────────────────────┤ SP
       │  ↑ Stack (grows down)   │
       ├─────────────────────────┤
       │  BDOS                   │
0xFFFF └─────────────────────────┘
```

## String Pool Allocation

The string pool uses **all available memory** from the end of BSS to
`SP - stack_reserve`.

**No heap/malloc needed** - the pool is allocated directly at startup:

```c
uint16_t pool_size = SP - 1024 - (uint16_t)bss_end;
mb25_init((uint8_t *)bss_end, pool_size);
```

Key points:
- The end-of-BSS symbol marks the end of program data
- File I/O buffers (FCBs) are in BSS, not heap - already counted at that boundary
- 1024 bytes reserved for stack safety margin
- Typical pool size: ~56KB on 64K CP/M system

## Finding the end of BSS

This is the one part of the layout that is compiler-specific.

**uc80 (preferred)** exposes `__END__`, `__BSS_START`, and `__BSS_END` from the
linker, but C cannot name them directly. uc80 prefixes every C identifier with `_`, so
`extern char __END__[];` emits `EXTRN ___END__` and fails to link. Reach them through
an assembly shim instead — the same `mb25_uc80_shim.mac` that supplies `mb25_get_sp`,
assembled separately with `um80` and linked as a `.rel`. (Passing a hand-written `.mac`
to `uc80` itself puts the code in BSS, where `crt0` zeroes it.)

**z88dk (alternate)** exposes the boundary as `__BSS_tail`, which C can name directly:

```c
extern unsigned char __BSS_tail;
uint16_t pool_size = SP - 1024 - (uint16_t)&__BSS_tail;
mb25_init((uint8_t *)&__BSS_tail, pool_size);
```

## String Descriptor Table

The descriptor array sits in BSS, sized by `MB25_NUM_STRINGS`. Two declaration details
exist because of uc80:

- The header declares the array **unsized** (`extern mb25_string_t mb25_strings[];`).
  An `extern T a[N];` followed by `T a[N];` — the ordinary header-declares,
  source-defines idiom — crashes uc80 outright. The unsized form is valid C and works
  with both compilers.
- `MB25_NUM_STRINGS` must be passed on the command line (`-DMB25_NUM_STRINGS=N`), not
  `#define`d in one `.c` file. uc80 merges all translation units into one compilation,
  so generated code defining 4 while the runtime saw the default of 100 is not two
  independent builds — it is a mismatched array size and memory corruption. Under
  z88dk's separate compilation the same code happened to work.

## GOSUB Stack

GOSUB/RETURN uses a compiler-generated array, NOT the C call stack:

```c
int gosub_stack[100];  /* Return IDs */
int gosub_sp = 0;      /* Stack pointer */
```

The C stack is only for C library function calls (z88dk sizes it with
`CRT_STACK_SIZE`).

## Garbage Collection

GC uses in-place compaction with shell sort (no stdlib required):

1. Sort string descriptors by address (shell sort - O(n log n))
2. Compact strings forward using memmove (handles overlaps)
3. Re-sort descriptors by ID (shell sort)
4. Reset allocator to end of compacted data

**No temporary buffer** - compaction happens in-place within the pool.
**No stdlib** - inline shell sort avoids qsort function pointer overhead.

## Monitoring at Runtime

```basic
10 PRINT "String pool free:", FRE("")
```

`FRE("")` returns free space in the string pool.

## Implementation Files

- `runtime/strings/mb25_string.c` - String system implementation
- `runtime/strings/mb25_string.h` - String system header
- `src/codegen_backend.py` - Code generation (pool initialization)
