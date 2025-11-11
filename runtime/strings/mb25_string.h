/*
 * mb25_string.h - MBASIC 2025 String Allocator and Garbage Collector
 *
 * This header defines the string management system for MBASIC 2025
 * compiled to z88dk/Z80. It provides O(n log n) garbage collection
 * instead of the O(n²) performance of the original MBASIC 5.21.
 *
 * Copyright (C) 2025
 */

#ifndef MB25_STRING_H
#define MB25_STRING_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Configuration - set at compile time based on BASIC program analysis */
#ifndef MB25_NUM_STRINGS
#define MB25_NUM_STRINGS      100    /* Default number of string descriptors */
#endif

#ifndef MB25_POOL_SIZE
#define MB25_POOL_SIZE        8192   /* Default string pool size in bytes */
#endif

#define MB25_MAX_STRING_LEN   255    /* Maximum string length (BASIC limit) */
#define MB25_INVALID_STR_ID   0xFFFF /* Invalid string ID marker */

/* Debug configuration */
#ifndef MB25_ENABLE_DEBUG
#define MB25_ENABLE_DEBUG     0
#endif

/* Error codes */
typedef enum {
    MB25_SUCCESS = 0,
    MB25_ERR_OUT_OF_MEMORY,
    MB25_ERR_STRING_TOO_LONG,
    MB25_ERR_INVALID_STR_ID,
    MB25_ERR_NULL_POINTER,
    MB25_ERR_POOL_CORRUPTED
} mb25_error_t;

/* String descriptor structure */
typedef struct mb25_string_R {
    uint16_t str_id:14;      /* String identifier (0-16383) */
    uint16_t is_const:1;      /* 1 if points to constant/ROM data */
    uint16_t writeable:1;     /* 1 if data can be modified in-place */
    uint8_t  len;            /* Current string length (0-255) */
    uint8_t  *data;          /* Pointer to string data */
} mb25_string_t;

typedef mb25_string_t *mb25_string_pt;

/* Static array of string descriptors - size known at compile time */
extern mb25_string_t mb25_strings[MB25_NUM_STRINGS];

/* Global state for string management */
typedef struct mb25_globals_R {
    uint16_t pool_size;       /* Total size of string pool */
    uint16_t allocator;       /* Current allocation position */
    uint8_t  *pool;          /* Pointer to malloc'd string pool */

    /* Statistics */
    uint32_t total_allocs;    /* Total allocations */
    uint32_t total_gcs;       /* Total garbage collections */
    uint16_t max_used;        /* Maximum pool usage */
} mb25_globals_t;

/* Global instance */
extern mb25_globals_t mb25_global;

/* ===== Initialization and Cleanup ===== */

/* Initialize the string system with given pool size */
mb25_error_t mb25_init(uint16_t pool_size);

/* Cleanup and free all resources */
void mb25_cleanup(void);

/* Reset the string system (clear all strings, reset allocator) */
void mb25_reset(void);

/* ===== Core Allocation Functions ===== */

/* Allocate a constant string (no heap space used) */
mb25_error_t mb25_string_alloc_const(uint16_t str_id, const char *const_str);

/* Allocate a heap string with given size */
mb25_error_t mb25_string_alloc(uint16_t str_id, uint16_t size);

/* Allocate and initialize a heap string from C string */
mb25_error_t mb25_string_alloc_init(uint16_t str_id, const char *init_str);

/* Free a string (mark descriptor as unused) */
void mb25_string_free(uint16_t str_id);

/* ===== String Operations ===== */

/* Copy string from source to destination */
mb25_error_t mb25_string_copy(uint16_t dest_id, uint16_t src_id);

/* Assign string value (may reuse space if writeable) */
mb25_error_t mb25_string_assign(uint16_t dest_id, const uint8_t *data, uint8_t len);

/* Concatenate two strings into destination */
mb25_error_t mb25_string_concat(uint16_t dest_id, uint16_t str1_id, uint16_t str2_id);

/* Compare two strings (returns -1, 0, 1 like strcmp) */
int mb25_string_compare(uint16_t str1_id, uint16_t str2_id);

/* ===== Substring Operations (with sharing) ===== */

/* LEFT$(string, n) - return leftmost n characters */
mb25_error_t mb25_string_left(uint16_t dest_id, uint16_t src_id, uint8_t n);

/* RIGHT$(string, n) - return rightmost n characters */
mb25_error_t mb25_string_right(uint16_t dest_id, uint16_t src_id, uint8_t n);

/* MID$(string, start, length) - return substring */
mb25_error_t mb25_string_mid(uint16_t dest_id, uint16_t src_id, uint8_t start, uint8_t length);

/* MID$ statement (assignment) - replace part of string */
mb25_error_t mb25_string_mid_assign(uint16_t dest_id, uint8_t start, const uint8_t *data, uint8_t len);

/* ===== String Access Functions ===== */

/* Get string descriptor by ID */
mb25_string_pt mb25_get_string(uint16_t str_id);

/* Get string data pointer (returns NULL if invalid) */
uint8_t *mb25_get_data(uint16_t str_id);

/* Get string length */
uint8_t mb25_get_length(uint16_t str_id);

/* Check if string is empty */
bool mb25_is_empty(uint16_t str_id);

/* Check if string is constant */
bool mb25_is_const(uint16_t str_id);

/* Check if string is writeable */
bool mb25_is_writeable(uint16_t str_id);

/* ===== Garbage Collection ===== */

/* Run garbage collection manually */
void mb25_garbage_collect(void);

/* Check if GC is needed (returns true if pool is fragmented) */
bool mb25_gc_needed(void);

/* Get available free space */
uint16_t mb25_get_free_space(void);

/* Get fragmentation percentage (0-100) */
uint8_t mb25_get_fragmentation(void);

/* ===== Utility Functions ===== */

/* Convert string to C string (null-terminated) - caller must free */
char *mb25_to_c_string(uint16_t str_id);

/* Create string from C string */
mb25_error_t mb25_from_c_string(uint16_t str_id, const char *c_str);

/* Clear string (set to empty) */
void mb25_string_clear(uint16_t str_id);

/* Duplicate string to new ID */
mb25_error_t mb25_string_dup(uint16_t dest_id, uint16_t src_id);

/* ===== Debug Functions ===== */

#if MB25_ENABLE_DEBUG
/* Dump string descriptor info */
void mb25_dump_string(uint16_t str_id);

/* Dump all string descriptors */
void mb25_dump_all_strings(void);

/* Dump pool usage map */
void mb25_dump_pool(void);

/* Validate pool integrity */
bool mb25_validate_pool(void);

/* Get statistics */
void mb25_get_stats(uint32_t *total_allocs, uint32_t *total_gcs, uint16_t *max_used);
#endif

/* ===== Helper Macros ===== */

/* Check if string ID is valid */
#define MB25_VALID_ID(id) ((id) < MB25_NUM_STRINGS)

/* Get string descriptor pointer quickly (no bounds check) */
#define MB25_STRING_PTR(id) (&mb25_strings[id])

/* Check if string is allocated */
#define MB25_IS_ALLOCATED(id) (MB25_VALID_ID(id) && mb25_strings[id].data != NULL)

/* Error string conversion */
const char *mb25_error_string(mb25_error_t error);

#endif /* MB25_STRING_H */