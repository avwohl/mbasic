/*
 * test_sharing_gc.c - Test that string sharing is preserved during garbage collection
 *
 * Compile: gcc -o test_sharing_gc test_sharing_gc.c mb25_string.c
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

#define MB25_ENABLE_DEBUG 2  /* Enable detailed debug output */
#define MB25_NUM_STRINGS 10
#define MB25_POOL_SIZE 512

#include "mb25_string.h"

int main(void) {
    printf("=== Testing String Sharing During Garbage Collection ===\n\n");

    /* Initialize string system */
    if (mb25_init(MB25_POOL_SIZE) != MB25_SUCCESS) {
        fprintf(stderr, "Failed to initialize\n");
        return 1;
    }

    /* Create a parent string */
    printf("1. Creating parent string 'ABCDEFGHIJKLMNOP' (id=0)\n");
    mb25_string_alloc_init(0, "ABCDEFGHIJKLMNOP");

    /* Create substrings that share data */
    printf("2. Creating LEFT$ substring 'ABCD' (id=1)\n");
    mb25_string_left(1, 0, 4);  /* "ABCD" */

    printf("3. Creating MID$ substring 'EFGH' (id=2)\n");
    mb25_string_mid(2, 0, 5, 4);  /* "EFGH" (1-based indexing) */

    printf("4. Creating RIGHT$ substring 'MNOP' (id=3)\n");
    mb25_string_right(3, 0, 4);  /* "MNOP" */

    /* Create another independent string to fragment memory */
    printf("5. Creating independent string 'XYZ' (id=4)\n");
    mb25_string_alloc_init(4, "XYZ");

    /* Verify sharing before GC */
    printf("\n=== Before Garbage Collection ===\n");
    uint8_t *parent_data = mb25_strings[0].data;
    uint8_t *left_data = mb25_strings[1].data;
    uint8_t *mid_data = mb25_strings[2].data;
    uint8_t *right_data = mb25_strings[3].data;

    printf("Parent[0]: data=%p, len=%d\n", parent_data, mb25_strings[0].len);
    printf("LEFT$[1]:  data=%p, len=%d (offset=%ld)\n",
           left_data, mb25_strings[1].len, (long)(left_data - parent_data));
    printf("MID$[2]:   data=%p, len=%d (offset=%ld)\n",
           mid_data, mb25_strings[2].len, (long)(mid_data - parent_data));
    printf("RIGHT$[3]: data=%p, len=%d (offset=%ld)\n",
           right_data, mb25_strings[3].len, (long)(right_data - parent_data));

    /* Verify they share memory */
    assert(left_data == parent_data);  /* LEFT$ starts at beginning */
    assert(mid_data == parent_data + 4);  /* MID$ starts at offset 4 */
    assert(right_data == parent_data + 12);  /* RIGHT$ starts at offset 12 */

    /* Create some more strings to force fragmentation */
    printf("\n6. Creating more strings to fragment memory...\n");
    mb25_string_alloc_init(5, "111");
    mb25_string_alloc_init(6, "222");
    mb25_string_free(5);  /* Free to create gap */

    printf("7. Pool usage before GC: %u bytes\n", mb25_global.allocator);

    /* Run garbage collection */
    printf("\n8. Running garbage collection...\n");
    mb25_garbage_collect();

    /* Check sharing after GC */
    printf("\n=== After Garbage Collection ===\n");
    parent_data = mb25_strings[0].data;
    left_data = mb25_strings[1].data;
    mid_data = mb25_strings[2].data;
    right_data = mb25_strings[3].data;

    printf("Parent[0]: data=%p, len=%d\n", parent_data, mb25_strings[0].len);
    printf("LEFT$[1]:  data=%p, len=%d (offset=%ld)\n",
           left_data, mb25_strings[1].len, (long)(left_data - parent_data));
    printf("MID$[2]:   data=%p, len=%d (offset=%ld)\n",
           mid_data, mb25_strings[2].len, (long)(mid_data - parent_data));
    printf("RIGHT$[3]: data=%p, len=%d (offset=%ld)\n",
           right_data, mb25_strings[3].len, (long)(right_data - parent_data));

    printf("9. Pool usage after GC: %u bytes\n", mb25_global.allocator);

    /* Verify sharing is maintained */
    printf("\n=== Verifying Sharing Maintained ===\n");

    /* Check that substrings still point into parent */
    if (left_data == parent_data) {
        printf("✓ LEFT$ still shares with parent (offset=0)\n");
    } else {
        printf("✗ LEFT$ no longer shares with parent!\n");
        return 1;
    }

    if (mid_data == parent_data + 4) {
        printf("✓ MID$ still shares with parent (offset=4)\n");
    } else {
        printf("✗ MID$ no longer shares with parent!\n");
        return 1;
    }

    if (right_data == parent_data + 12) {
        printf("✓ RIGHT$ still shares with parent (offset=12)\n");
    } else {
        printf("✗ RIGHT$ no longer shares with parent!\n");
        return 1;
    }

    /* Verify content is correct */
    char *parent_str = mb25_to_c_string(0);
    char *left_str = mb25_to_c_string(1);
    char *mid_str = mb25_to_c_string(2);
    char *right_str = mb25_to_c_string(3);

    assert(strcmp(parent_str, "ABCDEFGHIJKLMNOP") == 0);
    assert(strcmp(left_str, "ABCD") == 0);
    assert(strcmp(mid_str, "EFGH") == 0);
    assert(strcmp(right_str, "MNOP") == 0);

    printf("✓ All string contents correct after GC\n");

    free(parent_str);
    free(left_str);
    free(mid_str);
    free(right_str);

    /* Test edge case: substring of substring */
    printf("\n=== Testing Substring of Substring ===\n");
    printf("10. Creating substring of LEFT$ substring\n");
    mb25_string_left(7, 1, 2);  /* First 2 chars of "ABCD" = "AB" */

    uint8_t *sub_sub_data = mb25_strings[7].data;
    printf("Sub-substring[7]: data=%p, len=%d (offset from parent=%ld)\n",
           sub_sub_data, mb25_strings[7].len, (long)(sub_sub_data - parent_data));

    assert(sub_sub_data == parent_data);  /* Should point to start of parent */

    printf("✓ Substring of substring shares correctly\n");

    /* Cleanup */
    mb25_cleanup();

    printf("\n=== All Sharing Tests Passed! ===\n");
    return 0;
}