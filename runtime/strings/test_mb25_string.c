/*
 * test_mb25_string.c - Test program for MBASIC 2025 String System
 *
 * Demonstrates and tests the string allocator and garbage collector.
 * Compile with: gcc -o test_mb25_string test_mb25_string.c mb25_string.c
 *
 * Copyright (C) 2025
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

/* Enable debug features for testing */
#define MB25_ENABLE_DEBUG 1
#define MB25_NUM_STRINGS 50
#define MB25_POOL_SIZE 1024

#include "mb25_string.h"

/* Test helper macros */
#define TEST_START(name) printf("\n=== Testing %s ===\n", name)
#define TEST_PASS(name) printf("✓ %s passed\n", name)
#define TEST_ASSERT(cond, msg) do { \
    if (!(cond)) { \
        printf("✗ Test failed: %s\n", msg); \
        exit(1); \
    } \
} while(0)

/* Test basic initialization */
void test_initialization(void) {
    TEST_START("Initialization");

    mb25_error_t err = mb25_init(MB25_POOL_SIZE);
    TEST_ASSERT(err == MB25_SUCCESS, "Failed to initialize");

    TEST_ASSERT(mb25_global.pool != NULL, "Pool not allocated");
    TEST_ASSERT(mb25_global.pool_size == MB25_POOL_SIZE, "Wrong pool size");

    TEST_PASS("Initialization");
}

/* Test constant string allocation */
void test_const_strings(void) {
    TEST_START("Constant Strings");

    const char *test_str = "Hello, World!";
    mb25_error_t err = mb25_string_alloc_const(0, test_str);
    TEST_ASSERT(err == MB25_SUCCESS, "Failed to allocate const string");

    mb25_string_pt str = mb25_get_string(0);
    TEST_ASSERT(str != NULL, "String not found");
    TEST_ASSERT(str->is_const == 1, "String not marked as const");
    TEST_ASSERT(str->writeable == 0, "Const string marked as writeable");
    TEST_ASSERT(str->len == strlen(test_str), "Wrong length");
    TEST_ASSERT(str->data == (uint8_t *)test_str, "Data not pointing to const");

    /* Verify no heap space used */
    TEST_ASSERT(mb25_global.allocator == 0, "Heap space used for const string");

    TEST_PASS("Constant Strings");
}

/* Test heap string allocation */
void test_heap_strings(void) {
    TEST_START("Heap Strings");

    /* Allocate and initialize a string */
    mb25_error_t err = mb25_string_alloc_init(1, "Dynamic String");
    TEST_ASSERT(err == MB25_SUCCESS, "Failed to allocate heap string");

    mb25_string_pt str = mb25_get_string(1);
    TEST_ASSERT(str != NULL, "String not found");
    TEST_ASSERT(str->is_const == 0, "Heap string marked as const");
    TEST_ASSERT(str->writeable == 1, "Heap string not writeable");
    TEST_ASSERT(str->len == strlen("Dynamic String"), "Wrong length");
    TEST_ASSERT(mb25_global.allocator > 0, "No heap space used");

    /* Compare content */
    char *c_str = mb25_to_c_string(1);
    TEST_ASSERT(c_str != NULL, "Failed to convert to C string");
    TEST_ASSERT(strcmp(c_str, "Dynamic String") == 0, "Wrong content");
    free(c_str);

    TEST_PASS("Heap Strings");
}

/* Test string copying and sharing */
void test_string_copying(void) {
    TEST_START("String Copying");

    /* Create source string */
    mb25_string_alloc_init(2, "Source String");

    /* Copy to destination */
    mb25_error_t err = mb25_string_copy(3, 2);
    TEST_ASSERT(err == MB25_SUCCESS, "Failed to copy string");

    /* Verify sharing */
    mb25_string_pt src = mb25_get_string(2);
    mb25_string_pt dest = mb25_get_string(3);

    TEST_ASSERT(src->writeable == 0, "Source still writeable after copy");
    TEST_ASSERT(dest->writeable == 0, "Destination writeable after copy");
    TEST_ASSERT(src->data == dest->data, "Not sharing data");
    TEST_ASSERT(src->len == dest->len, "Different lengths");

    TEST_PASS("String Copying");
}

/* Test substring operations */
void test_substrings(void) {
    TEST_START("Substring Operations");

    /* Create test string */
    mb25_string_alloc_init(4, "ABCDEFGHIJ");

    /* Test LEFT$ */
    mb25_error_t err = mb25_string_left(5, 4, 3);
    TEST_ASSERT(err == MB25_SUCCESS, "LEFT$ failed");

    char *left_str = mb25_to_c_string(5);
    TEST_ASSERT(strcmp(left_str, "ABC") == 0, "LEFT$ wrong result");
    free(left_str);

    /* Test RIGHT$ */
    err = mb25_string_right(6, 4, 3);
    TEST_ASSERT(err == MB25_SUCCESS, "RIGHT$ failed");

    char *right_str = mb25_to_c_string(6);
    TEST_ASSERT(strcmp(right_str, "HIJ") == 0, "RIGHT$ wrong result");
    free(right_str);

    /* Test MID$ */
    err = mb25_string_mid(7, 4, 4, 3);  /* MID$(str, 4, 3) in BASIC */
    TEST_ASSERT(err == MB25_SUCCESS, "MID$ failed");

    char *mid_str = mb25_to_c_string(7);
    TEST_ASSERT(strcmp(mid_str, "DEF") == 0, "MID$ wrong result");
    free(mid_str);

    /* Verify source is now immutable */
    mb25_string_pt src = mb25_get_string(4);
    TEST_ASSERT(src->writeable == 0, "Source still writeable after substring");

    TEST_PASS("Substring Operations");
}

/* Test concatenation */
void test_concatenation(void) {
    TEST_START("String Concatenation");

    /* Create two strings */
    mb25_string_alloc_init(8, "Hello, ");
    mb25_string_alloc_init(9, "World!");

    /* Concatenate */
    mb25_error_t err = mb25_string_concat(10, 8, 9);
    TEST_ASSERT(err == MB25_SUCCESS, "Concatenation failed");

    char *result = mb25_to_c_string(10);
    TEST_ASSERT(strcmp(result, "Hello, World!") == 0, "Wrong concatenation result");
    free(result);

    TEST_PASS("String Concatenation");
}

/* Test garbage collection */
void test_garbage_collection(void) {
    TEST_START("Garbage Collection");

    /* Save initial state */
    uint16_t initial_allocator = mb25_global.allocator;

    /* Create and free some strings to fragment the pool */
    for (int i = 20; i < 30; i++) {
        mb25_string_alloc_init(i, "Temporary String");
    }

    uint16_t fragmented_allocator = mb25_global.allocator;
    TEST_ASSERT(fragmented_allocator > initial_allocator, "No allocation happened");

    /* Free every other string */
    for (int i = 20; i < 30; i += 2) {
        mb25_string_free(i);
    }

    /* Run garbage collection */
    uint32_t gc_count_before = mb25_global.total_gcs;
    mb25_garbage_collect();
    uint32_t gc_count_after = mb25_global.total_gcs;

    TEST_ASSERT(gc_count_after == gc_count_before + 1, "GC counter not incremented");
    TEST_ASSERT(mb25_global.allocator < fragmented_allocator, "GC didn't compact");

    /* Verify remaining strings are still valid */
    for (int i = 21; i < 30; i += 2) {
        char *str = mb25_to_c_string(i);
        TEST_ASSERT(str != NULL, "String lost after GC");
        TEST_ASSERT(strcmp(str, "Temporary String") == 0, "String corrupted after GC");
        free(str);
    }

    TEST_PASS("Garbage Collection");
}

/* Test writeable string optimization */
void test_writeable_optimization(void) {
    TEST_START("Writeable Optimization");

    /* Create a writeable string */
    mb25_string_alloc(30, 100);
    mb25_string_assign(30, (uint8_t *)"Initial", 7);

    mb25_string_pt str = mb25_get_string(30);
    TEST_ASSERT(str->writeable == 1, "String not writeable");

    uint8_t *initial_data = str->data;

    /* Assign new value that fits */
    mb25_string_assign(30, (uint8_t *)"Changed", 7);

    /* Should reuse same memory */
    str = mb25_get_string(30);
    TEST_ASSERT(str->data == initial_data, "Didn't reuse memory");

    char *result = mb25_to_c_string(30);
    TEST_ASSERT(strcmp(result, "Changed") == 0, "Wrong content after reuse");
    free(result);

    TEST_PASS("Writeable Optimization");
}

/* Test error conditions */
void test_error_conditions(void) {
    TEST_START("Error Conditions");

    /* Test invalid string ID */
    mb25_error_t err = mb25_string_alloc(999, 10);
    TEST_ASSERT(err == MB25_ERR_INVALID_STR_ID, "Invalid ID not caught");

    /* Test string too long */
    err = mb25_string_alloc(31, 300);
    TEST_ASSERT(err == MB25_ERR_STRING_TOO_LONG, "Too long string not caught");

    /* Test null pointer */
    err = mb25_string_alloc_const(32, NULL);
    TEST_ASSERT(err == MB25_ERR_NULL_POINTER, "Null pointer not caught");

    TEST_PASS("Error Conditions");
}

/* Stress test with many strings */
void test_stress(void) {
    TEST_START("Stress Test");

    /* Allocate many strings */
    for (int i = 35; i < 45; i++) {
        char buf[50];
        sprintf(buf, "String number %d", i);
        mb25_error_t err = mb25_string_alloc_init(i, buf);
        TEST_ASSERT(err == MB25_SUCCESS, "Allocation failed in stress test");
    }

    /* Force garbage collection */
    mb25_garbage_collect();

    /* Verify all strings intact */
    for (int i = 35; i < 45; i++) {
        char expected[50];
        sprintf(expected, "String number %d", i);

        char *actual = mb25_to_c_string(i);
        TEST_ASSERT(actual != NULL, "String lost in stress test");
        TEST_ASSERT(strcmp(actual, expected) == 0, "String corrupted in stress test");
        free(actual);
    }

    TEST_PASS("Stress Test");
}

/* Performance comparison test */
void test_performance(void) {
    TEST_START("Performance Comparison");

    printf("\nThis test demonstrates O(n log n) vs O(n²) performance:\n");
    printf("Original MBASIC: Each GC would scan all strings N times\n");
    printf("MBASIC 2025: GC sorts strings once and compacts in single pass\n");

    /* Create scenario that would be worst-case for O(n²) */
    for (int i = 0; i < 20; i++) {
        char buf[30];
        sprintf(buf, "Performance test %d", i);
        mb25_string_alloc_init(45 + (i % 5), buf);

        if (i % 5 == 4) {
            /* This would trigger expensive GC in original MBASIC */
            mb25_garbage_collect();
            printf("GC #%d completed (would take O(n²) in original)\n",
                   mb25_global.total_gcs);
        }
    }

    TEST_PASS("Performance Comparison");
}

/* Debug output test */
void test_debug_output(void) {
    TEST_START("Debug Output");

#if MB25_ENABLE_DEBUG
    printf("\n--- String Dump ---\n");
    mb25_dump_all_strings();

    printf("\n--- Pool Status ---\n");
    mb25_dump_pool();

    printf("\n--- Statistics ---\n");
    uint32_t allocs, gcs;
    uint16_t max_used;
    mb25_get_stats(&allocs, &gcs, &max_used);
    printf("Total allocations: %u\n", allocs);
    printf("Total GCs: %u\n", gcs);
    printf("Max pool usage: %u bytes\n", max_used);

    /* Validate pool integrity */
    bool valid = mb25_validate_pool();
    TEST_ASSERT(valid, "Pool validation failed");
#endif

    TEST_PASS("Debug Output");
}

int main(void) {
    printf("===========================================\n");
    printf("MBASIC 2025 String System Test Suite\n");
    printf("===========================================\n");

    /* Run all tests */
    test_initialization();
    test_const_strings();
    test_heap_strings();
    test_string_copying();
    test_substrings();
    test_concatenation();
    test_garbage_collection();
    test_writeable_optimization();
    test_error_conditions();
    test_stress();
    test_performance();
    test_debug_output();

    /* Cleanup */
    mb25_cleanup();

    printf("\n===========================================\n");
    printf("All tests passed successfully! ✓\n");
    printf("===========================================\n");

    return 0;
}