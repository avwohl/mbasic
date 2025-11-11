# MBASIC 2025 String System Usage Guide

## Overview

This guide explains how to integrate and use the MBASIC 2025 string allocator and garbage collector in compiled BASIC programs. The system provides O(n log n) garbage collection performance compared to the original O(n²) algorithm.

## Building and Testing

### Compile the Test Suite

```bash
# Compile the string system with test program
gcc -o test_mb25_string utils/test_mb25_string.c utils/mb25_string.c

# Run tests
./test_mb25_string
```

### Include in Your Project

```c
#define MB25_NUM_STRINGS 100  /* Set based on your program's needs */
#define MB25_POOL_SIZE 8192   /* String pool size in bytes */
#include "mb25_string.h"
```

## Integration with MBASIC Compiler

### Compiler Analysis Phase

The compiler must analyze the BASIC program to determine:

1. **Simple string variables**: Count all variables ending with `$`
2. **String arrays**: Count total cells in DIM statements
3. **Function parameters**: Count string parameters
4. **Temporaries**: Estimate based on expression complexity

Example BASIC program analysis:
```basic
10 DIM NAMES$(10), BUFFER$(5,5)
20 DEFSTR A-C
30 INPUT "Name: ", NAME$
40 TEMP$ = LEFT$(NAME$, 3) + RIGHT$(NAME$, 2)
```

Compiler output:
```c
#define MB25_NUM_STRINGS 42  /* Calculated: 10 + 25 + 3 + 1 + 3 temps */
```

### Code Generation Examples

#### String Assignment from Constant

BASIC:
```basic
10 A$ = "Hello"
```

Generated C:
```c
mb25_string_alloc_const(STR_A, "Hello");
```

#### String Input

BASIC:
```basic
20 INPUT A$
```

Generated C:
```c
char input_buffer[256];
fgets(input_buffer, 256, stdin);
mb25_string_alloc_init(STR_A, input_buffer);
```

#### String Concatenation

BASIC:
```basic
30 C$ = A$ + B$
```

Generated C:
```c
mb25_string_concat(STR_C, STR_A, STR_B);
```

#### Substring Operations

BASIC:
```basic
40 L$ = LEFT$(A$, 5)
50 R$ = RIGHT$(A$, 3)
60 M$ = MID$(A$, 2, 4)
```

Generated C:
```c
mb25_string_left(STR_L, STR_A, 5);
mb25_string_right(STR_R, STR_A, 3);
mb25_string_mid(STR_M, STR_A, 2, 4);
```

#### MID$ Statement (Assignment)

BASIC:
```basic
70 MID$(A$, 3) = "XXX"
```

Generated C:
```c
mb25_string_mid_assign(STR_A, 3, (uint8_t *)"XXX", 3);
```

## Memory Management Strategies

### 1. Constant String Optimization

When a string is assigned a literal constant, no heap space is used:

```c
/* This uses no heap space */
mb25_string_alloc_const(0, "This is stored in program memory");

/* Heap space only used for dynamic strings */
mb25_string_alloc(1, 50);  /* Allocate 50 bytes */
```

### 2. Writeable String Reuse

Strings marked as writeable can be overwritten in place:

```c
/* Initial allocation */
mb25_string_alloc(0, 100);
mb25_string_assign(0, "Initial", 7);

/* Later assignment reuses same memory if it fits */
mb25_string_assign(0, "Changed", 7);  /* No new allocation */
```

### 3. Substring Sharing

Substring operations share data when possible:

```c
/* Create source string */
mb25_string_alloc_init(0, "ABCDEFGHIJ");

/* These share data with source, no copying */
mb25_string_left(1, 0, 3);   /* Points to "ABC" */
mb25_string_right(2, 0, 3);  /* Points to "HIJ" */

/* Source becomes immutable after sharing */
```

## Complete Example Program

### BASIC Source

```basic
10 REM String manipulation example
20 DIM WORDS$(10)
30 INPUT "Enter text: ", TEXT$
40 FOR I = 1 TO 10
50   WORDS$(I) = MID$(TEXT$, I, 5)
60 NEXT I
70 RESULT$ = ""
80 FOR I = 1 TO 10
90   RESULT$ = RESULT$ + WORDS$(I) + " "
100 NEXT I
110 PRINT "Result: "; RESULT$
```

### Generated C Code

```c
#include <stdio.h>
#include <stdlib.h>

#define MB25_NUM_STRINGS 14  /* TEXT$, WORDS$(10), RESULT$, 2 temps */
#define MB25_POOL_SIZE 2048

#include "mb25_string.h"

/* String IDs */
#define STR_TEXT 0
#define STR_WORDS_BASE 1  /* WORDS$(1) through WORDS$(10) */
#define STR_RESULT 11
#define STR_TEMP1 12
#define STR_TEMP2 13

int main(void) {
    /* Initialize string system */
    if (mb25_init(MB25_POOL_SIZE, MB25_NUM_STRINGS) != MB25_SUCCESS) {
        fprintf(stderr, "Failed to initialize string system\n");
        return 1;
    }

    /* Line 30: INPUT "Enter text: ", TEXT$ */
    printf("Enter text: ");
    char input_buffer[256];
    if (fgets(input_buffer, 256, stdin) == NULL) {
        input_buffer[0] = '\0';
    }
    /* Remove newline */
    size_t len = strlen(input_buffer);
    if (len > 0 && input_buffer[len-1] == '\n') {
        input_buffer[len-1] = '\0';
    }
    mb25_string_alloc_init(STR_TEXT, input_buffer);

    /* Lines 40-60: FOR loop with MID$ */
    for (int i = 1; i <= 10; i++) {
        mb25_string_mid(STR_WORDS_BASE + (i-1), STR_TEXT, i, 5);
    }

    /* Line 70: RESULT$ = "" */
    mb25_string_alloc_const(STR_RESULT, "");

    /* Lines 80-100: Concatenation loop */
    for (int i = 1; i <= 10; i++) {
        /* RESULT$ = RESULT$ + WORDS$(I) */
        mb25_string_concat(STR_TEMP1, STR_RESULT, STR_WORDS_BASE + (i-1));

        /* + " " */
        mb25_string_alloc_const(STR_TEMP2, " ");
        mb25_string_concat(STR_RESULT, STR_TEMP1, STR_TEMP2);
    }

    /* Line 110: PRINT */
    printf("Result: ");
    char *result = mb25_to_c_string(STR_RESULT);
    if (result) {
        printf("%s\n", result);
        free(result);
    }

    /* Cleanup */
    mb25_cleanup();
    return 0;
}
```

## Performance Considerations

### When Garbage Collection Occurs

1. **Automatic**: When allocation fails due to insufficient space
2. **Manual**: Can be called explicitly when convenient
3. **Never during**: String constant assignments or substring operations

### Best Practices

1. **Use constants when possible**: `A$ = "constant"` uses no heap
2. **Preallocate arrays**: Size arrays appropriately at compile time
3. **Batch operations**: Group string operations to minimize GC
4. **Monitor fragmentation**: Use debug functions to track pool health

### Performance Comparison

| Operation | Original MBASIC | MBASIC 2025 | Improvement |
|-----------|----------------|-------------|-------------|
| GC with 100 strings | O(10,000) | O(664) | 15x faster |
| GC with 1000 strings | O(1,000,000) | O(9,965) | 100x faster |
| Substring creation | O(n) copy | O(1) share | n times faster |
| Const assignment | Heap alloc | No alloc | ∞ faster |

## Debugging

### Enable Debug Output

```c
#define MB25_ENABLE_DEBUG 1
#include "mb25_string.h"

/* In your code */
mb25_dump_all_strings();  /* Show all string descriptors */
mb25_dump_pool();         /* Show pool usage */
mb25_validate_pool();     /* Check for corruption */
```

### Common Issues and Solutions

| Problem | Cause | Solution |
|---------|-------|----------|
| "Out of string space" | Pool too small | Increase MB25_POOL_SIZE |
| Strings corrupted after GC | Invalid pointers | Check all string IDs are valid |
| Memory leak | Strings not freed | Ensure mb25_cleanup() called |
| Slow performance | Frequent GC | Increase pool size or reduce temps |

## Advanced Features

### Custom Memory Management

```c
/* Override pool size at runtime */
mb25_error_t err = mb25_init(16384, 200);  /* 16KB pool, 200 strings */

/* Monitor memory usage */
uint16_t free_space = mb25_get_free_space();
uint8_t fragmentation = mb25_get_fragmentation();

/* Trigger GC at convenient times */
if (mb25_gc_needed()) {
    mb25_garbage_collect();
}
```

### String Validation

```c
/* Check if string is valid before use */
if (MB25_IS_ALLOCATED(str_id)) {
    /* Safe to use string */
    uint8_t len = mb25_get_length(str_id);
    uint8_t *data = mb25_get_data(str_id);
}
```

### Error Handling

```c
mb25_error_t err = mb25_string_concat(dest, src1, src2);
if (err != MB25_SUCCESS) {
    fprintf(stderr, "String error: %s\n", mb25_error_string(err));
    /* Handle error appropriately */
}
```

## Migration from Python Implementation

For teams migrating from the Python MBASIC interpreter:

1. **Analyze program**: Count all string usage
2. **Set constants**: Define MB25_NUM_STRINGS and MB25_POOL_SIZE
3. **Generate includes**: Add mb25_string.h to generated C
4. **Map variables**: Assign each BASIC string a unique ID
5. **Translate operations**: Convert BASIC string ops to mb25 calls
6. **Add error handling**: Check return values
7. **Test thoroughly**: Verify behavior matches original

## Conclusion

The MBASIC 2025 string system provides dramatic performance improvements while maintaining full compatibility with BASIC string semantics. By eliminating the O(n²) garbage collection bottleneck and adding optimizations for constants and sharing, programs with hundreds of strings run orders of magnitude faster than the original MBASIC 5.21.