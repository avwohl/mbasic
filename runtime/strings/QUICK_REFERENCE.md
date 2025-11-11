# String System Quick Reference for Code Generation

## Setup (at top of generated C file)
```c
#define MB25_NUM_STRINGS <count>  /* Compiler calculates */
#define MB25_POOL_SIZE <size>      /* Default 8192 */
#include "mb25_string.h"

/* String ID defines */
#define STR_VARNAME 0  /* One per string variable */
```

## Initialization
```c
if (mb25_init(MB25_POOL_SIZE) != MB25_SUCCESS) {
    fprintf(stderr, "?Out of memory\n");
    return 1;
}
/* ... program ... */
mb25_cleanup();
```

## BASIC → C Translation Table

| BASIC Operation | Generated C Code | Notes |
|-----------------|------------------|-------|
| `A$ = "literal"` | `mb25_string_alloc_const(STR_A, "literal")` | No heap use |
| `A$ = B$` | `mb25_string_copy(STR_A, STR_B)` | May share data |
| `A$ = B$ + C$` | `mb25_string_concat(STR_A, STR_B, STR_C)` | |
| `A$ = B$ + "x"` | `mb25_string_alloc_const(TEMP, "x");`<br>`mb25_string_concat(STR_A, STR_B, TEMP)` | Need temp |
| `A$ = LEFT$(B$, n)` | `mb25_string_left(STR_A, STR_B, n)` | Shares data |
| `A$ = RIGHT$(B$, n)` | `mb25_string_right(STR_A, STR_B, n)` | Shares data |
| `A$ = MID$(B$, s, n)` | `mb25_string_mid(STR_A, STR_B, s, n)` | 1-based index |
| `MID$(A$, s) = "x"` | `mb25_string_mid_assign(STR_A, s, "x", len)` | Copy-on-write |
| `LEN(A$)` | `mb25_get_length(STR_A)` | Returns uint8_t |
| `IF A$ = B$` | `if (mb25_string_compare(STR_A, STR_B) == 0)` | |
| `IF A$ < B$` | `if (mb25_string_compare(STR_A, STR_B) < 0)` | |
| `PRINT A$` | `char *s = mb25_to_c_string(STR_A);`<br>`printf("%s", s); free(s);` | Must free |
| `INPUT A$` | `fgets(buf, 256, stdin);`<br>`mb25_string_alloc_init(STR_A, buf)` | |

## String ID Assignment Strategy

1. **Simple variables**: Sequential from 0
2. **Arrays**: Contiguous block per array
3. **Temporaries**: At end of range
4. **Reusable temps**: Share within statement

```c
/* Example for: DIM A$(10), B$(5,5) */
#define STR_A_BASE 0   /* A$(0) through A$(9): IDs 0-9 */
#define STR_B_BASE 10  /* B$(0,0) through B$(4,4): IDs 10-34 */
#define STR_TEMP_1 35  /* Temporary 1 */
#define STR_TEMP_2 36  /* Temporary 2 */

/* Array access */
/* A$(i) */ → STR_A_BASE + i
/* B$(i,j) */ → STR_B_BASE + (i * 5 + j)
```

## Key Implementation Rules

1. **String count MUST be compile-time constant**
   - Count all variables, array cells, temps
   - Define as `MB25_NUM_STRINGS`

2. **All strings are in static array `mb25_strings[]`**
   - No malloc for descriptors
   - Access by ID: `mb25_strings[STR_A]`

3. **Garbage collection is automatic**
   - Happens when allocation fails
   - Preserves string sharing
   - O(n log n) performance

4. **Writeable flag is transparent**
   - Never check it in generated code
   - Runtime handles copy-on-write

5. **String literals are free**
   - Use `mb25_string_alloc_const()`
   - No heap allocation
   - Points to program memory

6. **Substrings share memory**
   - LEFT$/RIGHT$/MID$ don't copy
   - Source becomes immutable
   - Sharing preserved during GC

## Memory Layout

```
Static descriptor array (compile-time size):
[0][1][2]...[MB25_NUM_STRINGS-1]
 ↓  ↓  ↓
String pool (malloc'd at runtime):
[string data...][free space]
```

## Error Handling

Simple (BASIC-like):
```c
/* Ignore errors - BASIC continues on error */
mb25_string_concat(STR_C, STR_A, STR_B);
```

Robust:
```c
if (mb25_string_concat(STR_C, STR_A, STR_B) == MB25_ERR_OUT_OF_MEMORY) {
    fprintf(stderr, "?Out of string space\n");
    /* Handle error */
}
```

## Common Patterns

### Concatenating multiple strings
```basic
RESULT$ = A$ + "," + B$ + ";" + C$
```
```c
mb25_string_alloc_const(TEMP1, ",");
mb25_string_concat(TEMP2, STR_A, TEMP1);
mb25_string_alloc_const(TEMP1, ";");  /* Reuse TEMP1 */
mb25_string_concat(TEMP3, STR_B, TEMP1);
mb25_string_concat(TEMP1, TEMP2, TEMP3);
mb25_string_concat(STR_RESULT, TEMP1, STR_C);
```

### String in expression
```basic
IF LEN(A$) > 5 AND LEFT$(A$, 3) = "ABC" THEN
```
```c
if (mb25_get_length(STR_A) > 5) {
    mb25_string_left(TEMP1, STR_A, 3);
    mb25_string_alloc_const(TEMP2, "ABC");
    if (mb25_string_compare(TEMP1, TEMP2) == 0) {
        /* ... */
    }
}
```

## Don't Forget!

- ✓ Count ALL strings at compile time
- ✓ Include temporaries for complex expressions
- ✓ Call `mb25_init()` at program start
- ✓ Call `mb25_cleanup()` at program end
- ✓ Free result from `mb25_to_c_string()`
- ✓ Use 1-based indexing for MID$
- ✓ String IDs are 0-based array indices