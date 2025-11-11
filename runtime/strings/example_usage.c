/*
 * example_usage.c - Example of how compiled MBASIC would use the string system
 *
 * This shows how a BASIC program would be translated to C using the
 * static string descriptor array.
 */

#include <stdio.h>
#include <stdlib.h>

/* The compiler determines this at compile time based on BASIC program analysis */
#define MB25_NUM_STRINGS 10  /* Example: program uses 10 strings total */
#define MB25_POOL_SIZE 1024  /* 1KB string pool */

#include "mb25_string.h"

/* String ID assignments (compiler-generated) */
#define STR_NAME    0  /* NAME$ */
#define STR_CITY    1  /* CITY$ */
#define STR_RESULT  2  /* RESULT$ */
#define STR_TEMP1   3  /* Temporary for concatenation */
#define STR_TEMP2   4  /* Temporary for substring */
/* IDs 5-9 reserved for future use */

int main(void) {
    /* Initialize string system - only pool is allocated */
    if (mb25_init(MB25_POOL_SIZE) != MB25_SUCCESS) {
        fprintf(stderr, "Failed to initialize string system\n");
        return 1;
    }

    /* BASIC: 10 NAME$ = "John" */
    mb25_string_alloc_const(STR_NAME, "John");

    /* BASIC: 20 CITY$ = "New York" */
    mb25_string_alloc_const(STR_CITY, "New York");

    /* BASIC: 30 RESULT$ = NAME$ + ", " + CITY$ */
    mb25_string_alloc_const(STR_TEMP1, ", ");
    mb25_string_concat(STR_TEMP2, STR_NAME, STR_TEMP1);
    mb25_string_concat(STR_RESULT, STR_TEMP2, STR_CITY);

    /* BASIC: 40 PRINT RESULT$ */
    char *result = mb25_to_c_string(STR_RESULT);
    if (result) {
        printf("%s\n", result);
        free(result);
    }

    /* The static array mb25_strings[] contains all descriptors */
    printf("\nString descriptor array status:\n");
    for (int i = 0; i < MB25_NUM_STRINGS; i++) {
        if (mb25_strings[i].data != NULL) {
            printf("  [%d] str_id=%d, len=%d, const=%d, write=%d\n",
                   i, mb25_strings[i].str_id, mb25_strings[i].len,
                   mb25_strings[i].is_const, mb25_strings[i].writeable);
        }
    }

    /* Cleanup - only frees the pool, not the static array */
    mb25_cleanup();

    return 0;
}

/*
 * Key Points:
 *
 * 1. MB25_NUM_STRINGS is defined at compile time by the BASIC compiler
 * 2. The mb25_strings[] array is static - no malloc required
 * 3. String IDs are assigned by the compiler for each string variable
 * 4. During GC, the array is sorted in place by data pointer, then
 *    sorted back by str_id to restore original access order
 * 5. This design is optimal for microprocessors with limited memory
 */