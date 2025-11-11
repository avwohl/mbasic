/*
 * mb25_string.c - MBASIC 2025 String Allocator and Garbage Collector Implementation
 *
 * Provides O(n log n) garbage collection for MBASIC 2025 string management.
 * Supports constant strings, writeable strings, and shared substring references.
 *
 * Copyright (C) 2025
 */

#include "mb25_string.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

/* Global string management state */
mb25_globals_t mb25_global = {0};

/* Static array of string descriptors - size known at compile time */
mb25_string_t mb25_strings[MB25_NUM_STRINGS];

/* Forward declarations for internal functions */
static int compare_by_data_ptr(const void *a, const void *b);
static int compare_by_str_id(const void *a, const void *b);
static void compact_strings(void);
static mb25_error_t allocate_from_pool(uint16_t str_id, uint16_t size);
static void mark_immutable(uint16_t str_id);

/* ===== Error Handling ===== */

const char *mb25_error_string(mb25_error_t error) {
    switch (error) {
        case MB25_SUCCESS:           return "Success";
        case MB25_ERR_OUT_OF_MEMORY: return "Out of string space";
        case MB25_ERR_STRING_TOO_LONG: return "String too long";
        case MB25_ERR_INVALID_STR_ID: return "Invalid string ID";
        case MB25_ERR_NULL_POINTER:   return "Null pointer";
        case MB25_ERR_POOL_CORRUPTED: return "String pool corrupted";
        default:                      return "Unknown error";
    }
}

/* ===== Initialization and Cleanup ===== */

mb25_error_t mb25_init(uint16_t pool_size) {
    /* Clean up any existing state */
    if (mb25_global.pool != NULL) {
        mb25_cleanup();
    }

    /* Allocate string pool */
    mb25_global.pool = (uint8_t *)malloc(pool_size);
    if (mb25_global.pool == NULL) {
        return MB25_ERR_OUT_OF_MEMORY;
    }

    /* Initialize state */
    mb25_global.pool_size = pool_size;
    mb25_global.allocator = 0;
    mb25_global.total_allocs = 0;
    mb25_global.total_gcs = 0;
    mb25_global.max_used = 0;

    /* Initialize static string descriptors with IDs */
    for (uint16_t i = 0; i < MB25_NUM_STRINGS; i++) {
        mb25_strings[i].str_id = i;
        mb25_strings[i].is_const = 0;
        mb25_strings[i].writeable = 0;
        mb25_strings[i].len = 0;
        mb25_strings[i].data = NULL;
    }

    return MB25_SUCCESS;
}

void mb25_cleanup(void) {
    if (mb25_global.pool != NULL) {
        free(mb25_global.pool);
        mb25_global.pool = NULL;
    }
    memset(&mb25_global, 0, sizeof(mb25_global));

    /* Clear static string descriptors */
    for (uint16_t i = 0; i < MB25_NUM_STRINGS; i++) {
        mb25_strings[i].is_const = 0;
        mb25_strings[i].writeable = 0;
        mb25_strings[i].len = 0;
        mb25_strings[i].data = NULL;
    }
}

void mb25_reset(void) {
    /* Clear all strings */
    for (uint16_t i = 0; i < MB25_NUM_STRINGS; i++) {
        mb25_strings[i].is_const = 0;
        mb25_strings[i].writeable = 0;
        mb25_strings[i].len = 0;
        mb25_strings[i].data = NULL;
    }

    /* Reset allocator */
    mb25_global.allocator = 0;
}

/* ===== Core Allocation Functions ===== */

mb25_error_t mb25_string_alloc_const(uint16_t str_id, const char *const_str) {
    if (!MB25_VALID_ID(str_id)) {
        return MB25_ERR_INVALID_STR_ID;
    }
    if (const_str == NULL) {
        return MB25_ERR_NULL_POINTER;
    }

    mb25_string_pt str = &mb25_strings[str_id];
    size_t len = strlen(const_str);

    if (len > MB25_MAX_STRING_LEN) {
        return MB25_ERR_STRING_TOO_LONG;
    }

    /* Point to constant data - no heap allocation */
    str->is_const = 1;
    str->writeable = 0;
    str->len = (uint8_t)len;
    str->data = (uint8_t *)const_str;

    return MB25_SUCCESS;
}

static mb25_error_t allocate_from_pool(uint16_t str_id, uint16_t size) {
    mb25_string_pt str = &mb25_strings[str_id];

    /* Check available space */
    uint16_t available = mb25_global.pool_size - mb25_global.allocator;

    if (available >= size) {
        /* Allocate from pool */
        str->data = mb25_global.pool + mb25_global.allocator;
        mb25_global.allocator += size;

        /* Update statistics */
        mb25_global.total_allocs++;
        if (mb25_global.allocator > mb25_global.max_used) {
            mb25_global.max_used = mb25_global.allocator;
        }

        return MB25_SUCCESS;
    }

    return MB25_ERR_OUT_OF_MEMORY;
}

mb25_error_t mb25_string_alloc(uint16_t str_id, uint16_t size) {
    if (!MB25_VALID_ID(str_id)) {
        return MB25_ERR_INVALID_STR_ID;
    }
    if (size > MB25_MAX_STRING_LEN) {
        return MB25_ERR_STRING_TOO_LONG;
    }

    mb25_string_pt str = &mb25_strings[str_id];

    /* Try to allocate */
    mb25_error_t result = allocate_from_pool(str_id, size);

    if (result != MB25_SUCCESS) {
        /* Try garbage collection once */
        mb25_garbage_collect();
        result = allocate_from_pool(str_id, size);

        if (result != MB25_SUCCESS) {
            return MB25_ERR_OUT_OF_MEMORY;
        }
    }

    /* Set up descriptor */
    str->is_const = 0;
    str->writeable = 1;
    str->len = 0;  /* Allocated but not yet initialized */

    return MB25_SUCCESS;
}

mb25_error_t mb25_string_alloc_init(uint16_t str_id, const char *init_str) {
    if (init_str == NULL) {
        return MB25_ERR_NULL_POINTER;
    }

    size_t len = strlen(init_str);
    if (len > MB25_MAX_STRING_LEN) {
        return MB25_ERR_STRING_TOO_LONG;
    }

    /* Allocate space */
    mb25_error_t result = mb25_string_alloc(str_id, (uint16_t)len);
    if (result != MB25_SUCCESS) {
        return result;
    }

    /* Copy data */
    mb25_string_pt str = &mb25_strings[str_id];
    memcpy(str->data, init_str, len);
    str->len = (uint8_t)len;

    return MB25_SUCCESS;
}

void mb25_string_free(uint16_t str_id) {
    if (MB25_VALID_ID(str_id)) {
        mb25_string_pt str = &mb25_strings[str_id];
        str->is_const = 0;
        str->writeable = 0;
        str->len = 0;
        str->data = NULL;
    }
}

/* ===== String Operations ===== */

mb25_error_t mb25_string_copy(uint16_t dest_id, uint16_t src_id) {
    if (!MB25_VALID_ID(dest_id) || !MB25_VALID_ID(src_id)) {
        return MB25_ERR_INVALID_STR_ID;
    }

    mb25_string_pt dest = &mb25_strings[dest_id];
    mb25_string_pt src = &mb25_strings[src_id];

    /* If source is empty, clear destination */
    if (src->data == NULL || src->len == 0) {
        mb25_string_clear(dest_id);
        return MB25_SUCCESS;
    }

    /* If source is constant, destination can share it */
    if (src->is_const) {
        dest->is_const = 1;
        dest->writeable = 0;
        dest->len = src->len;
        dest->data = src->data;
        return MB25_SUCCESS;
    }

    /* If destination is writeable and has enough space, copy in place */
    if (dest->writeable && dest->data != NULL) {
        /* Since both len fields are uint8_t and max is 255, just copy */
        memcpy(dest->data, src->data, src->len);
        dest->len = src->len;
        return MB25_SUCCESS;
    }

    /* Otherwise, share the data and mark both as immutable */
    mark_immutable(src_id);
    dest->is_const = 0;
    dest->writeable = 0;
    dest->len = src->len;
    dest->data = src->data;

    return MB25_SUCCESS;
}

mb25_error_t mb25_string_assign(uint16_t dest_id, const uint8_t *data, uint8_t len) {
    if (!MB25_VALID_ID(dest_id)) {
        return MB25_ERR_INVALID_STR_ID;
    }
    if (data == NULL && len > 0) {
        return MB25_ERR_NULL_POINTER;
    }

    mb25_string_pt dest = &mb25_strings[dest_id];

    /* If destination is writeable and has space, reuse it */
    if (dest->writeable && dest->data != NULL) {
        /* len is uint8_t, max 255, so always fits */
        memcpy(dest->data, data, len);
        dest->len = len;
        return MB25_SUCCESS;
    }

    /* Allocate new space */
    mb25_error_t result = mb25_string_alloc(dest_id, len);
    if (result != MB25_SUCCESS) {
        return result;
    }

    /* Copy data */
    memcpy(dest->data, data, len);
    dest->len = len;

    return MB25_SUCCESS;
}

mb25_error_t mb25_string_concat(uint16_t dest_id, uint16_t str1_id, uint16_t str2_id) {
    if (!MB25_VALID_ID(dest_id) || !MB25_VALID_ID(str1_id) || !MB25_VALID_ID(str2_id)) {
        return MB25_ERR_INVALID_STR_ID;
    }

    mb25_string_pt str1 = &mb25_strings[str1_id];
    mb25_string_pt str2 = &mb25_strings[str2_id];

    uint16_t total_len = str1->len + str2->len;
    if (total_len > MB25_MAX_STRING_LEN) {
        return MB25_ERR_STRING_TOO_LONG;
    }

    /* Allocate space for result */
    mb25_error_t result = mb25_string_alloc(dest_id, total_len);
    if (result != MB25_SUCCESS) {
        return result;
    }

    mb25_string_pt dest = &mb25_strings[dest_id];

    /* Copy both strings */
    if (str1->len > 0 && str1->data != NULL) {
        memcpy(dest->data, str1->data, str1->len);
    }
    if (str2->len > 0 && str2->data != NULL) {
        memcpy(dest->data + str1->len, str2->data, str2->len);
    }

    dest->len = (uint8_t)total_len;

    return MB25_SUCCESS;
}

int mb25_string_compare(uint16_t str1_id, uint16_t str2_id) {
    if (!MB25_VALID_ID(str1_id) || !MB25_VALID_ID(str2_id)) {
        return 0;  /* Invalid strings are equal */
    }

    mb25_string_pt str1 = &mb25_strings[str1_id];
    mb25_string_pt str2 = &mb25_strings[str2_id];

    /* Handle empty strings */
    if (str1->data == NULL || str1->len == 0) {
        if (str2->data == NULL || str2->len == 0) {
            return 0;  /* Both empty */
        }
        return -1;  /* str1 empty, str2 not */
    }
    if (str2->data == NULL || str2->len == 0) {
        return 1;  /* str2 empty, str1 not */
    }

    /* Compare data */
    uint8_t min_len = (str1->len < str2->len) ? str1->len : str2->len;
    int cmp = memcmp(str1->data, str2->data, min_len);

    if (cmp != 0) {
        return cmp;
    }

    /* Strings are equal up to min_len, compare lengths */
    if (str1->len < str2->len) return -1;
    if (str1->len > str2->len) return 1;
    return 0;
}

/* ===== Substring Operations ===== */

static void mark_immutable(uint16_t str_id) {
    if (MB25_VALID_ID(str_id)) {
        mb25_strings[str_id].writeable = 0;
    }
}

mb25_error_t mb25_string_left(uint16_t dest_id, uint16_t src_id, uint8_t n) {
    if (!MB25_VALID_ID(dest_id) || !MB25_VALID_ID(src_id)) {
        return MB25_ERR_INVALID_STR_ID;
    }

    mb25_string_pt src = &mb25_strings[src_id];
    mb25_string_pt dest = &mb25_strings[dest_id];

    /* Handle edge cases */
    if (src->data == NULL || src->len == 0 || n == 0) {
        mb25_string_clear(dest_id);
        return MB25_SUCCESS;
    }

    /* Limit n to actual string length */
    if (n > src->len) {
        n = src->len;
    }

    /* Share the data - mark source as immutable */
    mark_immutable(src_id);

    dest->is_const = src->is_const;
    dest->writeable = 0;
    dest->len = n;
    dest->data = src->data;

    return MB25_SUCCESS;
}

mb25_error_t mb25_string_right(uint16_t dest_id, uint16_t src_id, uint8_t n) {
    if (!MB25_VALID_ID(dest_id) || !MB25_VALID_ID(src_id)) {
        return MB25_ERR_INVALID_STR_ID;
    }

    mb25_string_pt src = &mb25_strings[src_id];
    mb25_string_pt dest = &mb25_strings[dest_id];

    /* Handle edge cases */
    if (src->data == NULL || src->len == 0 || n == 0) {
        mb25_string_clear(dest_id);
        return MB25_SUCCESS;
    }

    /* Limit n to actual string length */
    if (n > src->len) {
        n = src->len;
    }

    /* Share the data - mark source as immutable */
    mark_immutable(src_id);

    dest->is_const = src->is_const;
    dest->writeable = 0;
    dest->len = n;
    dest->data = src->data + (src->len - n);

    return MB25_SUCCESS;
}

mb25_error_t mb25_string_mid(uint16_t dest_id, uint16_t src_id, uint8_t start, uint8_t length) {
    if (!MB25_VALID_ID(dest_id) || !MB25_VALID_ID(src_id)) {
        return MB25_ERR_INVALID_STR_ID;
    }

    mb25_string_pt src = &mb25_strings[src_id];
    mb25_string_pt dest = &mb25_strings[dest_id];

    /* BASIC uses 1-based indexing, convert to 0-based */
    if (start > 0) start--;

    /* Handle edge cases */
    if (src->data == NULL || src->len == 0 || length == 0 || start >= src->len) {
        mb25_string_clear(dest_id);
        return MB25_SUCCESS;
    }

    /* Adjust length if necessary */
    if (start + length > src->len) {
        length = src->len - start;
    }

    /* Share the data - mark source as immutable */
    mark_immutable(src_id);

    dest->is_const = src->is_const;
    dest->writeable = 0;
    dest->len = length;
    dest->data = src->data + start;

    return MB25_SUCCESS;
}

mb25_error_t mb25_string_mid_assign(uint16_t dest_id, uint8_t start, const uint8_t *data, uint8_t len) {
    if (!MB25_VALID_ID(dest_id)) {
        return MB25_ERR_INVALID_STR_ID;
    }
    if (data == NULL && len > 0) {
        return MB25_ERR_NULL_POINTER;
    }

    mb25_string_pt dest = &mb25_strings[dest_id];

    /* BASIC uses 1-based indexing */
    if (start > 0) start--;

    /* Check bounds */
    if (start >= dest->len) {
        return MB25_SUCCESS;  /* No-op if start is beyond string */
    }

    /* Calculate how many characters to replace */
    uint8_t replace_len = len;
    if (start + replace_len > dest->len) {
        replace_len = dest->len - start;
    }

    /* If not writeable, make a copy first */
    if (!dest->writeable) {
        /* Save the original data pointer and length */
        uint8_t *orig_data = dest->data;
        uint8_t orig_len = dest->len;

        /* Allocate space for a copy */
        mb25_error_t result = mb25_string_alloc(dest_id, orig_len);
        if (result != MB25_SUCCESS) {
            return result;
        }

        /* Copy the original data to the new location */
        memcpy(dest->data, orig_data, orig_len);
        dest->len = orig_len;

        /* Now dest is writeable and points to the copy */
    }

    /* Replace characters in place */
    memcpy(dest->data + start, data, replace_len);

    return MB25_SUCCESS;
}

/* ===== String Access Functions ===== */

mb25_string_pt mb25_get_string(uint16_t str_id) {
    if (MB25_VALID_ID(str_id)) {
        return &mb25_strings[str_id];
    }
    return NULL;
}

uint8_t *mb25_get_data(uint16_t str_id) {
    if (MB25_VALID_ID(str_id)) {
        return mb25_strings[str_id].data;
    }
    return NULL;
}

uint8_t mb25_get_length(uint16_t str_id) {
    if (MB25_VALID_ID(str_id)) {
        return mb25_strings[str_id].len;
    }
    return 0;
}

bool mb25_is_empty(uint16_t str_id) {
    if (MB25_VALID_ID(str_id)) {
        mb25_string_pt str = &mb25_strings[str_id];
        return (str->data == NULL || str->len == 0);
    }
    return true;
}

bool mb25_is_const(uint16_t str_id) {
    if (MB25_VALID_ID(str_id)) {
        return mb25_strings[str_id].is_const;
    }
    return false;
}

bool mb25_is_writeable(uint16_t str_id) {
    if (MB25_VALID_ID(str_id)) {
        return mb25_strings[str_id].writeable;
    }
    return false;
}

/* ===== Garbage Collection ===== */

static int compare_by_data_ptr(const void *a, const void *b) {
    const mb25_string_t *pa = (const mb25_string_t *)a;
    const mb25_string_t *pb = (const mb25_string_t *)b;

    /* Null pointers sort to the end */
    if (pa->data == NULL) return 1;
    if (pb->data == NULL) return -1;

    /* Skip constant strings (not in pool) */
    if (pa->is_const) return 1;
    if (pb->is_const) return -1;

    /* Compare addresses */
    if (pa->data < pb->data) return -1;
    if (pa->data > pb->data) return 1;

    /* If addresses are the same, sort longer string first */
    /* This ensures parent strings are moved before substrings */
    if (pa->len > pb->len) return -1;
    if (pa->len < pb->len) return 1;

    return 0;
}

static int compare_by_str_id(const void *a, const void *b) {
    const mb25_string_t *pa = (const mb25_string_t *)a;
    const mb25_string_t *pb = (const mb25_string_t *)b;

    if (pa->str_id < pb->str_id) return -1;
    if (pa->str_id > pb->str_id) return 1;
    return 0;
}

static void compact_strings(void) {
    uint16_t new_allocator = 0;
    uint8_t *temp_buffer = NULL;
    uint16_t temp_size = 0;

    /* Track the last moved string for sharing detection */
    uint8_t *last_old_start = NULL;
    uint8_t *last_old_end = NULL;
    uint8_t *last_new_start = NULL;

#if MB25_ENABLE_DEBUG > 1
    printf("DEBUG: Starting compaction (with sharing preservation)\n");
#endif

    /* First pass: calculate total size needed (skip shared substrings) */
    for (uint16_t i = 0; i < MB25_NUM_STRINGS; i++) {
        mb25_string_pt str = &mb25_strings[i];
        if (str->data != NULL && !str->is_const &&
            str->data >= mb25_global.pool &&
            str->data < mb25_global.pool + mb25_global.pool_size) {

            /* Check if this string shares data with the previous string */
            bool is_shared = false;
            if (i > 0) {
                mb25_string_pt prev = &mb25_strings[i-1];
                if (prev->data != NULL && !prev->is_const &&
                    str->data >= prev->data &&
                    str->data + str->len <= prev->data + prev->len) {
                    /* This string is a substring of the previous one */
                    is_shared = true;
                }
            }

            if (!is_shared) {
                temp_size += str->len;
            }
        }
    }

    /* Allocate temporary buffer */
    if (temp_size > 0) {
        temp_buffer = (uint8_t *)malloc(temp_size);
        if (temp_buffer == NULL) {
            /* Can't compact without temp buffer, just return */
            return;
        }
    }

    /* Second pass: copy strings to temp buffer and update pointers */
    uint16_t temp_offset = 0;
    for (uint16_t i = 0; i < MB25_NUM_STRINGS; i++) {
        mb25_string_pt str = &mb25_strings[i];

        /* Skip null and constant strings */
        if (str->data == NULL || str->is_const) {
            continue;
        }

        /* Check if string is in the pool */
        if (str->data >= mb25_global.pool &&
            str->data < mb25_global.pool + mb25_global.pool_size) {

            /* Check if this string points into the last moved string */
            if (last_old_start != NULL && last_old_end != NULL &&
                str->data >= last_old_start &&
                str->data + str->len <= last_old_end) {

                /* This is a substring - adjust pointer to share with moved parent */
                uint16_t offset_in_parent = str->data - last_old_start;
                str->data = last_new_start + offset_in_parent;

#if MB25_ENABLE_DEBUG > 1
                printf("DEBUG: String id=%u shares with previous (offset=%u)\n",
                       str->str_id, offset_in_parent);
#endif

            } else {
                /* This is a new string - copy it */
#if MB25_ENABLE_DEBUG > 1
                printf("DEBUG: Copying string id=%u from %p to temp+%u (len=%u)\n",
                       str->str_id, str->data, temp_offset, str->len);
#endif

                /* Remember this string for sharing detection */
                last_old_start = str->data;
                last_old_end = str->data + str->len;
                last_new_start = mb25_global.pool + new_allocator;

                /* Copy to temp buffer */
                memcpy(temp_buffer + temp_offset, str->data, str->len);

                /* Update pointer to new location in pool */
                str->data = last_new_start;

                temp_offset += str->len;
                new_allocator += str->len;
            }
        }
    }

    /* Copy everything back from temp buffer to pool */
    if (temp_size > 0) {
        memcpy(mb25_global.pool, temp_buffer, temp_size);
        free(temp_buffer);
    }

    mb25_global.allocator = new_allocator;
#if MB25_ENABLE_DEBUG > 1
    printf("DEBUG: Compaction complete, new allocator=%u\n", new_allocator);
#endif
}

void mb25_garbage_collect(void) {
    /* Sort descriptors in place by data pointer address - O(n log n) */
    qsort(mb25_strings, MB25_NUM_STRINGS,
          sizeof(mb25_string_t), compare_by_data_ptr);

    /* Compact strings in single pass - O(n) */
    compact_strings();

    /* Sort back by str_id to restore normal access order - O(n log n) */
    qsort(mb25_strings, MB25_NUM_STRINGS,
          sizeof(mb25_string_t), compare_by_str_id);

    /* Update statistics */
    mb25_global.total_gcs++;
}

bool mb25_gc_needed(void) {
    /* Simple heuristic: GC needed if more than 50% fragmented */
    return mb25_get_fragmentation() > 50;
}

uint16_t mb25_get_free_space(void) {
    return mb25_global.pool_size - mb25_global.allocator;
}

uint8_t mb25_get_fragmentation(void) {
    if (mb25_global.pool_size == 0) {
        return 0;
    }

    /* Calculate actual used space */
    uint32_t actual_used = 0;
    for (uint16_t i = 0; i < MB25_NUM_STRINGS; i++) {
        mb25_string_pt str = &mb25_strings[i];
        if (str->data != NULL && !str->is_const &&
            str->data >= mb25_global.pool &&
            str->data < mb25_global.pool + mb25_global.pool_size) {
            actual_used += str->len;
        }
    }

    if (mb25_global.allocator == 0) {
        return 0;
    }

    /* Fragmentation = (allocated - actual) / allocated * 100 */
    uint32_t fragmented = mb25_global.allocator - actual_used;
    return (uint8_t)((fragmented * 100) / mb25_global.allocator);
}

/* ===== Utility Functions ===== */

char *mb25_to_c_string(uint16_t str_id) {
    if (!MB25_VALID_ID(str_id)) {
        return NULL;
    }

    mb25_string_pt str = &mb25_strings[str_id];
    if (str->data == NULL) {
        return strdup("");  /* Return empty string */
    }

    /* Allocate and copy */
    char *result = (char *)malloc(str->len + 1);
    if (result != NULL) {
        memcpy(result, str->data, str->len);
        result[str->len] = '\0';
    }

    return result;
}

mb25_error_t mb25_from_c_string(uint16_t str_id, const char *c_str) {
    if (c_str == NULL) {
        mb25_string_clear(str_id);
        return MB25_SUCCESS;
    }

    return mb25_string_alloc_init(str_id, c_str);
}

void mb25_string_clear(uint16_t str_id) {
    if (MB25_VALID_ID(str_id)) {
        mb25_string_pt str = &mb25_strings[str_id];
        str->is_const = 0;
        str->writeable = 0;
        str->len = 0;
        str->data = NULL;
    }
}

mb25_error_t mb25_string_dup(uint16_t dest_id, uint16_t src_id) {
    if (!MB25_VALID_ID(dest_id) || !MB25_VALID_ID(src_id)) {
        return MB25_ERR_INVALID_STR_ID;
    }

    mb25_string_pt src = &mb25_strings[src_id];

    /* Allocate new space for copy */
    mb25_error_t result = mb25_string_alloc(dest_id, src->len);
    if (result != MB25_SUCCESS) {
        return result;
    }

    mb25_string_pt dest = &mb25_strings[dest_id];

    /* Copy data */
    if (src->len > 0 && src->data != NULL) {
        memcpy(dest->data, src->data, src->len);
    }
    dest->len = src->len;

    return MB25_SUCCESS;
}

/* ===== Debug Functions ===== */

#if MB25_ENABLE_DEBUG

void mb25_dump_string(uint16_t str_id) {
    if (!MB25_VALID_ID(str_id)) {
        printf("Invalid string ID: %u\n", str_id);
        return;
    }

    mb25_string_pt str = &mb25_strings[str_id];
    printf("String[%u]: len=%u, const=%d, write=%d, data=%p",
           str_id, str->len, str->is_const, str->writeable, str->data);

    if (str->data != NULL && str->len > 0) {
        printf(" \"");
        for (uint8_t i = 0; i < str->len && i < 50; i++) {
            if (str->data[i] >= 32 && str->data[i] < 127) {
                putchar(str->data[i]);
            } else {
                printf("\\x%02x", str->data[i]);
            }
        }
        if (str->len > 50) printf("...");
        printf("\"");
    }
    printf("\n");
}

void mb25_dump_all_strings(void) {
    printf("=== String Descriptors ===\n");
    for (uint16_t i = 0; i < MB25_NUM_STRINGS; i++) {
        if (mb25_strings[i].data != NULL) {
            mb25_dump_string(i);
        }
    }
}

void mb25_dump_pool(void) {
    printf("=== String Pool ===\n");
    printf("Pool size: %u, Allocated: %u, Free: %u\n",
           mb25_global.pool_size, mb25_global.allocator,
           mb25_global.pool_size - mb25_global.allocator);
    printf("Fragmentation: %u%%\n", mb25_get_fragmentation());
}

bool mb25_validate_pool(void) {
    for (uint16_t i = 0; i < MB25_NUM_STRINGS; i++) {
        mb25_string_pt str = &mb25_strings[i];

        if (str->data != NULL && !str->is_const) {
            /* Check if pointer is within pool */
            if (str->data < mb25_global.pool ||
                str->data >= mb25_global.pool + mb25_global.pool_size) {
                printf("String %u has invalid data pointer\n", i);
                return false;
            }

            /* Check if string fits in pool */
            if (str->data + str->len > mb25_global.pool + mb25_global.pool_size) {
                printf("String %u extends beyond pool\n", i);
                return false;
            }
        }
    }

    return true;
}

void mb25_get_stats(uint32_t *total_allocs, uint32_t *total_gcs, uint16_t *max_used) {
    if (total_allocs) *total_allocs = mb25_global.total_allocs;
    if (total_gcs) *total_gcs = mb25_global.total_gcs;
    if (max_used) *max_used = mb25_global.max_used;
}

#endif /* MB25_ENABLE_DEBUG */