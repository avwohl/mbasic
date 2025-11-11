/*
 * compiler_example.c - Example of compiler-generated code for a BASIC program
 *
 * This shows what the MBASIC compiler should generate for this BASIC program:
 *
 * 10 REM String manipulation demo
 * 20 DIM WORDS$(5)
 * 30 INPUT "Enter text: ", TEXT$
 * 40 FIRST$ = LEFT$(TEXT$, 5)
 * 50 LAST$ = RIGHT$(TEXT$, 5)
 * 60 FOR I = 1 TO 5
 * 70   WORDS$(I) = MID$(TEXT$, I, 3)
 * 80 NEXT I
 * 90 RESULT$ = FIRST$ + " ... " + LAST$
 * 100 MID$(RESULT$, 3) = "XXX"
 * 110 PRINT "Result: "; RESULT$
 * 120 FOR I = 1 TO 5
 * 130   PRINT "Word "; I; ": "; WORDS$(I)
 * 140 NEXT I
 *
 * Compile: gcc -o compiler_example compiler_example.c mb25_string.c
 */

/* ===== Compiler-generated header ===== */

/* Step 1: Count strings needed
 * Simple vars: TEXT$, FIRST$, LAST$, RESULT$ = 4
 * Array: WORDS$(1..5) = 5 (0 is unused in BASIC but allocated)
 * Temporaries: " ... " temp, concat temps = 3
 * Total: 4 + 6 + 3 = 13
 */
#define MB25_NUM_STRINGS 13
#define MB25_POOL_SIZE 1024

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "mb25_string.h"

/* Step 2: Assign string IDs */
#define STR_TEXT     0
#define STR_FIRST    1
#define STR_LAST     2
#define STR_RESULT   3
#define STR_WORDS_BASE 4  /* WORDS$(0) through WORDS$(5) = IDs 4-9 */
#define STR_TEMP_1   10
#define STR_TEMP_2   11
#define STR_TEMP_3   12

/* ===== Main program (compiler-generated) ===== */

int main(void) {
    char input_buffer[256];
    char *print_str;
    int i;  /* Loop variable */

    /* Initialize string system */
    if (mb25_init(MB25_POOL_SIZE) != MB25_SUCCESS) {
        fprintf(stderr, "?Out of memory error\n");
        return 1;
    }

    /* Line 20: DIM WORDS$(5) - already allocated in descriptor array */
    /* Initialize array elements to empty */
    for (i = 0; i <= 5; i++) {
        mb25_string_clear(STR_WORDS_BASE + i);
    }

    /* Line 30: INPUT "Enter text: ", TEXT$ */
    printf("Enter text: ");
    if (fgets(input_buffer, 256, stdin)) {
        /* Remove newline */
        size_t len = strlen(input_buffer);
        if (len > 0 && input_buffer[len-1] == '\n') {
            input_buffer[len-1] = '\0';
        }
        mb25_string_alloc_init(STR_TEXT, input_buffer);
    }

    /* Line 40: FIRST$ = LEFT$(TEXT$, 5) */
    mb25_string_left(STR_FIRST, STR_TEXT, 5);

    /* Line 50: LAST$ = RIGHT$(TEXT$, 5) */
    mb25_string_right(STR_LAST, STR_TEXT, 5);

    /* Lines 60-80: FOR I = 1 TO 5 : WORDS$(I) = MID$(TEXT$, I, 3) : NEXT */
    for (i = 1; i <= 5; i++) {
        mb25_string_mid(STR_WORDS_BASE + i, STR_TEXT, i, 3);
    }

    /* Line 90: RESULT$ = FIRST$ + " ... " + LAST$ */
    mb25_string_alloc_const(STR_TEMP_1, " ... ");
    mb25_string_concat(STR_TEMP_2, STR_FIRST, STR_TEMP_1);
    mb25_string_concat(STR_RESULT, STR_TEMP_2, STR_LAST);

    /* Line 100: MID$(RESULT$, 3) = "XXX" */
    mb25_string_mid_assign(STR_RESULT, 3, (uint8_t *)"XXX", 3);

    /* Line 110: PRINT "Result: "; RESULT$ */
    printf("Result: ");
    print_str = mb25_to_c_string(STR_RESULT);
    if (print_str) {
        printf("%s", print_str);
        free(print_str);
    }
    printf("\n");

    /* Lines 120-140: FOR I = 1 TO 5 : PRINT "Word "; I; ": "; WORDS$(I) : NEXT */
    for (i = 1; i <= 5; i++) {
        printf("Word %d: ", i);
        print_str = mb25_to_c_string(STR_WORDS_BASE + i);
        if (print_str) {
            printf("%s", print_str);
            free(print_str);
        }
        printf("\n");
    }

    /* Cleanup */
    mb25_cleanup();
    return 0;
}

/*
 * Key points demonstrated:
 *
 * 1. String count determined at compile time (MB25_NUM_STRINGS)
 * 2. Each string variable gets a unique ID
 * 3. Arrays use contiguous IDs (WORDS$(i) = STR_WORDS_BASE + i)
 * 4. Temporaries reused where possible
 * 5. String literals use mb25_string_alloc_const (no heap)
 * 6. Substring operations create shared references
 * 7. MID$ statement handles copy-on-write transparently
 * 8. PRINT requires mb25_to_c_string + free
 * 9. INPUT requires buffer processing
 * 10. No explicit garbage collection needed (automatic)
 *
 * Memory efficiency:
 * - TEXT$ shares data with FIRST$, LAST$, and WORDS$(1..5)
 * - String literals (" ... ", "XXX") use no heap
 * - Garbage collection preserves sharing
 */