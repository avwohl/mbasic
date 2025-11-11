/*
 * test_mid_assign.c - Test MID$ assignment with writeable and non-writeable strings
 *
 * Compile: gcc -o test_mid_assign test_mid_assign.c mb25_string.c
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

#define MB25_ENABLE_DEBUG 1
#define MB25_NUM_STRINGS 10
#define MB25_POOL_SIZE 512

#include "mb25_string.h"

int main(void) {
    printf("=== Testing MID$ Assignment ===\n\n");

    /* Initialize string system */
    if (mb25_init(MB25_POOL_SIZE) != MB25_SUCCESS) {
        fprintf(stderr, "Failed to initialize\n");
        return 1;
    }

    /* Test 1: MID$ assignment on writeable string */
    printf("Test 1: MID$ assignment on writeable string\n");
    mb25_string_alloc_init(0, "ABCDEFGH");
    printf("  Original: %s (writeable=%d)\n",
           mb25_to_c_string(0), mb25_strings[0].writeable);

    /* MID$(str, 3) = "XXX" - should modify in place */
    mb25_error_t err = mb25_string_mid_assign(0, 3, (uint8_t *)"XXX", 3);
    assert(err == MB25_SUCCESS);

    char *result = mb25_to_c_string(0);
    printf("  After MID$(str,3)='XXX': %s\n", result);
    assert(strcmp(result, "ABXXXFGH") == 0);
    free(result);

    /* Test 2: MID$ assignment on shared (non-writeable) string */
    printf("\nTest 2: MID$ assignment on shared string\n");
    mb25_string_alloc_init(1, "12345678");
    mb25_string_left(2, 1, 8);  /* Share the entire string */

    printf("  Original[1]: %s (writeable=%d)\n",
           mb25_to_c_string(1), mb25_strings[1].writeable);
    printf("  Shared[2]: %s (writeable=%d)\n",
           mb25_to_c_string(2), mb25_strings[2].writeable);

    /* Both should point to the same data */
    assert(mb25_strings[1].data == mb25_strings[2].data);
    printf("  Sharing confirmed: both point to %p\n", mb25_strings[1].data);

    /* MID$ assignment on the shared string - should make a copy */
    err = mb25_string_mid_assign(2, 4, (uint8_t *)"ZZ", 2);
    assert(err == MB25_SUCCESS);

    char *orig = mb25_to_c_string(1);
    char *modified = mb25_to_c_string(2);
    printf("  Original[1] after: %s\n", orig);
    printf("  Modified[2] after MID$(str,4)='ZZ': %s\n", modified);

    /* Original should be unchanged */
    assert(strcmp(orig, "12345678") == 0);
    /* Modified should have the change */
    assert(strcmp(modified, "123ZZ678") == 0);
    /* They should no longer share data */
    assert(mb25_strings[1].data != mb25_strings[2].data);
    printf("  No longer sharing: [1]=%p, [2]=%p\n",
           mb25_strings[1].data, mb25_strings[2].data);

    free(orig);
    free(modified);

    /* Test 3: MID$ assignment on constant string */
    printf("\nTest 3: MID$ assignment on constant string\n");
    mb25_string_alloc_const(3, "CONSTANT");
    printf("  Constant: %s (is_const=%d, writeable=%d)\n",
           mb25_to_c_string(3), mb25_strings[3].is_const, mb25_strings[3].writeable);

    /* MID$ assignment should make a copy since it's const */
    err = mb25_string_mid_assign(3, 2, (uint8_t *)"YY", 2);
    assert(err == MB25_SUCCESS);

    result = mb25_to_c_string(3);
    printf("  After MID$(str,2)='YY': %s\n", result);
    assert(strcmp(result, "CYYSTANT") == 0);
    /* Should no longer be const */
    assert(mb25_strings[3].is_const == 0);
    assert(mb25_strings[3].writeable == 1);
    printf("  Now writeable: is_const=%d, writeable=%d\n",
           mb25_strings[3].is_const, mb25_strings[3].writeable);
    free(result);

    /* Test 4: MID$ assignment beyond string length (should be no-op) */
    printf("\nTest 4: MID$ assignment beyond string length\n");
    mb25_string_alloc_init(4, "SHORT");
    err = mb25_string_mid_assign(4, 10, (uint8_t *)"XXX", 3);
    assert(err == MB25_SUCCESS);  /* Should succeed but do nothing */

    result = mb25_to_c_string(4);
    printf("  String unchanged: %s\n", result);
    assert(strcmp(result, "SHORT") == 0);
    free(result);

    /* Test 5: MID$ assignment that extends past end (should truncate) */
    printf("\nTest 5: MID$ assignment extending past end\n");
    mb25_string_alloc_init(5, "ABCDEF");
    err = mb25_string_mid_assign(5, 5, (uint8_t *)"12345", 5);
    assert(err == MB25_SUCCESS);

    result = mb25_to_c_string(5);
    printf("  MID$(str,5)='12345' on 'ABCDEF': %s\n", result);
    assert(strcmp(result, "ABCD12") == 0);  /* Only 2 chars replaced */
    free(result);

    /* Cleanup */
    mb25_cleanup();

    printf("\n=== All MID$ Assignment Tests Passed! ===\n");
    return 0;
}