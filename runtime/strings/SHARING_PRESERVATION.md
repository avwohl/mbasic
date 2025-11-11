# String Sharing Preservation During Garbage Collection

## Overview
Enhanced the garbage collector to preserve string sharing relationships created by LEFT$, RIGHT$, and MID$ operations. This optimization maintains memory efficiency even after compaction.

## The Problem
When substring operations create shared references:
```basic
10 B$ = "ABCDEFGHIJKLMNOP"  ' Parent string (16 bytes)
20 C$ = LEFT$(B$, 4)        ' Points to start of B$ (shares data)
30 D$ = MID$(B$, 5, 4)      ' Points into middle of B$ (shares data)
40 E$ = RIGHT$(B$, 4)       ' Points to end of B$ (shares data)
```

Without sharing preservation, garbage collection would copy each string separately, using 16+4+4+4 = 28 bytes instead of just 16 bytes.

## The Solution

### 1. Enhanced Sort Comparison
```c
/* If addresses are the same, sort longer string first */
/* This ensures parent strings are moved before substrings */
if (pa->len > pb->len) return -1;
if (pa->len < pb->len) return 1;
```

When two strings start at the same address, the longer one is sorted first. This ensures:
- Parent strings are processed before their substrings
- Substrings can detect they point into a parent

### 2. Sharing Detection During Compaction
The compactor tracks the last moved string and checks if subsequent strings point into it:

```c
/* Track the last moved string for sharing detection */
uint8_t *last_old_start = NULL;
uint8_t *last_old_end = NULL;
uint8_t *last_new_start = NULL;

/* Check if this string points into the last moved string */
if (last_old_start != NULL && last_old_end != NULL &&
    str->data >= last_old_start &&
    str->data + str->len <= last_old_end) {
    /* This is a substring - adjust pointer to share with moved parent */
    uint16_t offset_in_parent = str->data - last_old_start;
    str->data = last_new_start + offset_in_parent;
}
```

## Benefits

### Memory Efficiency
- Substrings continue to share memory with parent strings
- No unnecessary duplication during garbage collection
- Maintains the O(1) memory advantage of substring operations

### Performance
- Reduces memory copying during GC (fewer unique strings to move)
- Better cache locality (related strings remain together)
- Smaller memory footprint allows more strings in the pool

## Example Scenario

Before GC:
```
Pool: [ABCDEFGHIJKLMNOP][gap][XYZ][gap]
B$ -> points to A
C$ -> points to A (LEFT$ 4)
D$ -> points to E (MID$ 5,4)
E$ -> points to M (RIGHT$ 4)
```

After GC (with sharing preserved):
```
Pool: [ABCDEFGHIJKLMNOP][XYZ]
B$ -> points to A
C$ -> points to A (same offset)
D$ -> points to E (same offset)
E$ -> points to M (same offset)
```

Memory used: 19 bytes (16 + 3) instead of 31 bytes if sharing was lost.

## Testing
The `test_sharing_gc.c` program verifies:
1. Substrings maintain correct offsets into parent strings
2. Content remains correct after GC
3. Memory usage is minimized
4. Nested substrings (substring of substring) work correctly

## Compatibility
This enhancement is completely transparent to BASIC programs. String operations behave identically, but with better memory efficiency maintained across garbage collections.