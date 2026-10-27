/*
 * mb25_string.c - MBASIC 2025 String Allocator and Garbage Collector Implementation
 *
 * Provides O(n log n) garbage collection for MBASIC 2025 string management.
 * Supports constant strings, writeable strings, and shared substring references.
 *
 * Copyright (C) 2025
 */

#include "mb25_string.h"
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

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

/* ===== Initialization ===== */

mb25_error_t mb25_init(uint8_t *pool, uint16_t pool_size) {
    /* Validate pool */
    if (pool == NULL || pool_size < 256) {
        return MB25_ERR_OUT_OF_MEMORY;
    }

    /* Initialize state - pool provided by caller, no malloc needed */
    mb25_global.pool = pool;
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

mb25_error_t mb25_string_alloc_const(uint16_t str_id, const char *cstr) {
    if (!MB25_VALID_ID(str_id)) {
        return MB25_ERR_INVALID_STR_ID;
    }
    if (cstr == NULL) {
        return MB25_ERR_NULL_POINTER;
    }

    mb25_string_pt str = &mb25_strings[str_id];
    size_t len = strlen(cstr);

    if (len > MB25_MAX_STRING_LEN) {
        return MB25_ERR_STRING_TOO_LONG;
    }

    /* Point to constant data - no heap allocation */
    str->is_const = 1;
    str->writeable = 0;
    str->len = (uint8_t)len;
    str->data = (uint8_t *)cstr;

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

mb25_error_t mb25_string_set_from_buf(uint16_t dest_id, const uint8_t *buf, uint8_t width) {
    if (!MB25_VALID_ID(dest_id)) {
        return MB25_ERR_INVALID_STR_ID;
    }
    if (buf == NULL && width > 0) {
        return MB25_ERR_NULL_POINTER;
    }

    /* Trim trailing spaces to get actual string length */
    uint8_t len = width;
    while (len > 0 && buf[len - 1] == ' ') {
        len--;
    }

    /* Use mb25_string_assign to set the string */
    return mb25_string_assign(dest_id, buf, len);
}

mb25_error_t mb25_string_concat(uint16_t dest_id, uint16_t str1_id, uint16_t str2_id) {
    if (!MB25_VALID_ID(dest_id) || !MB25_VALID_ID(str1_id) || !MB25_VALID_ID(str2_id)) {
        return MB25_ERR_INVALID_STR_ID;
    }

    mb25_string_pt str1 = &mb25_strings[str1_id];
    mb25_string_pt str2 = &mb25_strings[str2_id];

    uint16_t total_len = str1->len + str2->len;
    if (total_len > MB25_MAX_STRING_LEN) {
        mb25_fail(MB25_E_STRING_LONG);
    }

    /* Build the result in a local buffer first: dest may be str1 or str2,
       or may share its data with them, and the allocation clears dest. */
    uint8_t buf[MB25_MAX_STRING_LEN];
    uint8_t l1 = str1->len;
    uint8_t l2 = str2->len;
    if (l1 > 0 && str1->data != NULL) {
        memcpy(buf, str1->data, l1);
    } else {
        l1 = 0;
    }
    if (l2 > 0 && str2->data != NULL) {
        memcpy(buf + l1, str2->data, l2);
    } else {
        l2 = 0;
    }
    total_len = (uint16_t)(l1 + l2);

    /* Allocate space for result */
    mb25_error_t result = mb25_string_alloc(dest_id, total_len);
    if (result != MB25_SUCCESS) {
        return result;
    }

    mb25_string_pt dest = &mb25_strings[dest_id];
    if (total_len > 0) {
        memcpy(dest->data, buf, total_len);
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

/* Compare two strings by data pointer (for sorting before compaction) */
/* Returns true if a should come before b */
static bool data_ptr_less(const mb25_string_t *a, const mb25_string_t *b) {
    /* Null pointers sort to the end */
    if (a->data == NULL) return false;
    if (b->data == NULL) return true;
    /* Skip constant strings (not in pool) */
    if (a->is_const) return false;
    if (b->is_const) return true;
    /* Compare addresses */
    if (a->data < b->data) return true;
    if (a->data > b->data) return false;
    /* Same address: longer string first (parent before substring) */
    return (a->len > b->len);
}

/* Shell sort by data pointer - avoids qsort overhead */
static void sort_by_data_ptr(void) {
    uint16_t n = MB25_NUM_STRINGS;
    uint16_t gap, i, j;
    mb25_string_t temp;

    /* Shell sort gaps: 701, 301, 132, 57, 23, 10, 4, 1 */
    for (gap = n / 2; gap > 0; gap /= 2) {
        for (i = gap; i < n; i++) {
            temp = mb25_strings[i];
            for (j = i; j >= gap && data_ptr_less(&temp, &mb25_strings[j - gap]); j -= gap) {
                mb25_strings[j] = mb25_strings[j - gap];
            }
            mb25_strings[j] = temp;
        }
    }
}

/* Shell sort by str_id - restore original order after compaction */
static void sort_by_str_id(void) {
    uint16_t n = MB25_NUM_STRINGS;
    uint16_t gap, i, j;
    mb25_string_t temp;

    for (gap = n / 2; gap > 0; gap /= 2) {
        for (i = gap; i < n; i++) {
            temp = mb25_strings[i];
            for (j = i; j >= gap && temp.str_id < mb25_strings[j - gap].str_id; j -= gap) {
                mb25_strings[j] = mb25_strings[j - gap];
            }
            mb25_strings[j] = temp;
        }
    }
}

static void compact_strings(void) {
    uint16_t new_allocator = 0;

    /* Track the last moved string for sharing detection */
    uint8_t *last_old_start = NULL;
    uint8_t *last_old_end = NULL;
    uint8_t *last_new_start = NULL;

#if MB25_ENABLE_DEBUG > 1
    printf("DEBUG: Starting in-place compaction (with sharing preservation)\n");
#endif

    /* Single pass: move strings in-place using memmove (handles overlaps) */
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
                /* This is a new string - move it in-place */
                uint8_t *new_location = mb25_global.pool + new_allocator;

#if MB25_ENABLE_DEBUG > 1
                printf("DEBUG: Moving string id=%u from %p to %p (len=%u)\n",
                       str->str_id, str->data, new_location, str->len);
#endif

                /* Remember this string for sharing detection */
                last_old_start = str->data;
                last_old_end = str->data + str->len;
                last_new_start = new_location;

                /* Move in-place using memmove (handles overlapping memory) */
                if (str->data != new_location) {
                    memmove(new_location, str->data, str->len);
                }

                /* Update pointer to new location */
                str->data = new_location;

                new_allocator += str->len;
            }
        }
    }

    mb25_global.allocator = new_allocator;
#if MB25_ENABLE_DEBUG > 1
    printf("DEBUG: Compaction complete, new allocator=%u\n", new_allocator);
#endif
}

void mb25_garbage_collect(void) {
    /* Sort descriptors by data pointer address - O(n log n) shell sort */
    sort_by_data_ptr();

    /* Compact strings in single pass - O(n) */
    compact_strings();

    /* Sort back by str_id to restore normal access order - O(n log n) */
    sort_by_str_id();

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

/* mb25_to_c_string uses malloc - only available on host (not CP/M) */
#ifndef __Z88DK
#include <stdlib.h>
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
#endif /* __Z88DK */

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

/* ===== String functions that build a result in a descriptor =====
 *
 * Each returns the ID it was given, so the compiler can use the call as the
 * value of a string expression. */

uint16_t mb25_chr(uint16_t id, int code) {
    char t[2];
    uint8_t *d;
    t[0] = (char)code;
    t[1] = 0;
    if (code == 0) {                 /* CHR$(0) has a length of 1 but no C text */
        mb25_string_alloc(id, 1);
        d = mb25_get_data(id);
        if (d) {
            d[0] = 0;
            mb25_strings[id].len = 1;
        }
        return id;
    }
    mb25_string_alloc_init(id, t);
    return id;
}

/* SPACE$(n) and STRING$(n, code) */
uint16_t mb25_string_of(uint16_t id, int n, int ch) {
    uint8_t *d;
    if (n <= 0 || n > 255) {
        mb25_string_clear(id);
        return id;
    }
    mb25_string_alloc(id, n);
    d = mb25_get_data(id);
    if (d) {
        memset(d, ch, n);
        mb25_strings[id].len = (uint8_t)n;
    }
    return id;
}

/* STRING$(n, string$): the first character of the string, repeated */
uint16_t mb25_string_of_first(uint16_t id, int n, uint16_t src) {
    uint8_t *d = mb25_get_data(src);
    return mb25_string_of(id, n, (d && mb25_get_length(src) > 0) ? d[0] : ' ');
}

/* HEX$ and OCT$: the value as an unsigned 16-bit word, so HEX$(-1) is FFFF */
uint16_t mb25_radix(uint16_t id, int v, int base) {
    char t[8];
    uint8_t *d;
    int n = 0, i;
    unsigned int u = (unsigned int)v & 0xFFFF;
    do {
        i = u % base;
        t[n++] = (char)(i < 10 ? '0' + i : 'A' + i - 10);
        u /= base;
    } while (u);
    mb25_string_alloc(id, n);
    d = mb25_get_data(id);
    if (d) {
        for (i = 0; i < n; i++) {
            d[i] = (uint8_t)t[n - 1 - i];
        }
        mb25_strings[id].len = (uint8_t)n;
    }
    return id;
}

int mb25_asc(uint16_t id) {
    uint8_t *d = mb25_get_data(id);
    if (!d || mb25_get_length(id) == 0) {
        mb25_fail(MB25_E_ILLEGAL_FUNC);
    }
    return d[0];
}

/* The number at the start of a text, as BASIC reads it: leading blanks, a
 * sign, digits with a point, and an optional E or D exponent.  Reading stops
 * at the first character that does not belong.  The library atof is not
 * used: it fails on uc80. */
double mb25_atof(const char *s) {
    double v = 0, scale;
    int neg = 0, frac = 0, seen_point = 0, e = 0, eneg = 0, digits = 0, i;
    while (*s == ' ' || *s == '\t') {
        s++;
    }
    if (*s == '-' || *s == '+') {
        neg = (*s == '-');
        s++;
    }
    for (; (*s >= '0' && *s <= '9') || (*s == '.' && !seen_point); s++) {
        if (*s == '.') {
            seen_point = 1;
        } else {
            v = v * 10 + (*s - '0');
            digits++;
            if (seen_point) {
                frac++;
            }
        }
    }
    if (digits && (*s == 'E' || *s == 'e' || *s == 'D' || *s == 'd')) {
        s++;
        if (*s == '-' || *s == '+') {
            eneg = (*s == '-');
            s++;
        }
        while (*s >= '0' && *s <= '9') {
            if (e < 1000) {
                e = e * 10 + (*s - '0');
            }
            s++;
        }
        if (eneg) {
            e = -e;
        }
    }
    e -= frac;
    if (e < -38) {
        e = -38;
    }
    if (e > 38) {
        e = 38;
    }
    scale = 1;
    for (i = (e < 0 ? -e : e); i > 0; i--) {
        scale *= 10;
    }
    if (e < 0) {
        v = v / scale;
    } else {
        v = v * scale;
    }
    return neg ? -v : v;
}

/* VAL of a text: &H and &O numbers are read as 16-bit words (&HFFFF is -1);
 * anything else is a decimal number. */
double mb25_val_cstr(const char *s) {
    int base = 0, digit;
    double v = 0;
    while (*s == ' ' || *s == '\t') {
        s++;
    }
    if (*s == '&') {
        if (s[1] == 'H' || s[1] == 'h') {
            base = 16;
        } else if (s[1] == 'O' || s[1] == 'o' || (s[1] >= '0' && s[1] <= '7')) {
            base = 8;
        }
    }
    if (!base) {
        /* VAL skips blanks, tabs and line feeds anywhere in a decimal number:
         * VAL(" 1 2") is 12 and VAL("3 E 2") is 300 (measured) */
        char packed[256];
        int k = 0;
        for (; *s && k < 255; s++) {
            if (*s != ' ' && *s != '\t' && *s != '\n') {
                packed[k++] = *s;
            }
        }
        packed[k] = 0;
        return mb25_atof(packed);
    }
    s += (s[1] == 'H' || s[1] == 'h' || s[1] == 'O' || s[1] == 'o') ? 2 : 1;
    for (;; s++) {
        if (*s >= '0' && *s <= '9') {
            digit = *s - '0';
        } else if (*s >= 'A' && *s <= 'F') {
            digit = *s - 'A' + 10;
        } else if (*s >= 'a' && *s <= 'f') {
            digit = *s - 'a' + 10;
        } else {
            break;
        }
        if (digit >= base) {
            break;
        }
        v = v * base + digit;
        if (v > 65535.0) {
            mb25_fail(MB25_E_OVERFLOW);
        }
    }
    return v > 32767.0 ? (v - 65536.0) : v;
}

double mb25_val(uint16_t id) {
    char t[256];
    uint8_t *d = mb25_get_data(id);
    int n = mb25_get_length(id);
    if (!d) {
        return 0;
    }
    memcpy(t, d, n);
    t[n] = 0;
    return mb25_val_cstr(t);
}

/* INSTR([start,] a$, b$): 1-based position of b$ in a$, or 0 */
int mb25_instr(int start, uint16_t a, uint16_t b) {
    uint8_t *da = mb25_get_data(a), *db = mb25_get_data(b);
    int la = mb25_get_length(a), lb = mb25_get_length(b), i, j;
    if (start < 1) {
        start = 1;
    }
    if (start > la) {
        return 0;
    }
    if (lb == 0) {
        return start;
    }
    if (!da || !db) {
        return 0;
    }
    for (i = start - 1; i + lb <= la; i++) {
        for (j = 0; j < lb && da[i + j] == db[j]; j++) {
        }
        if (j == lb) {
            return i + 1;
        }
    }
    return 0;
}

/* ===== Numbers and subscripts ===== */

/* SQR.  The uc80 sqrt() can come out one unit low for a perfect square
 * (sqrt(9) is 2.9999998), and then a test such as INT(SQR(N))*INT(SQR(N)) = N
 * fails.  A whole-number root is returned exactly. */
double mb25_sqr(double v) {
    double r;
    int n;
    if (v < 0) {
        mb25_fail(MB25_E_ILLEGAL_FUNC);
    }
    if (v == 0) {
        return 0;
    }
    r = sqrt(v);
    if (r < 32000) {
        n = (int)(r + 0.5);
        if ((double)n * (double)n == v) {
            return n;
        }
    }
    return r;
}

/* x ^ y.  A whole-number exponent is worked out by repeated multiplication,
 * which is exact where the library pow() on uc80 is not (3 ^ 8 comes out as
 * 6560.98). */
static double mb25_big(int negative);
static double mb25_checked(double r);

static double mb25_pow_raw(double x, double y) {
    double r = 1;
    int n, neg;
    if (y == 0) {
        return 1;
    }
    n = (int)y;
    if ((double)n == y && n > -64 && n < 64) {
        neg = (n < 0);
        if (neg) {
            n = -n;
        }
        while (n) {
            if (n & 1) {
                r *= x;
            }
            x *= x;
            n >>= 1;
        }
        return neg ? 1 / r : r;
    }
    return pow(x, y);
}

/* x^y: MBASIC works it out with LOG and EXP, so it gives Overflow from 2^126
 * up (87.3365 = log of 2^126), earlier than the largest float. */
double mb25_pow(double x, double y) {
    if (x == 0 && y < 0) {
        mb25_warn(MB25_E_DIV_ZERO);
        return mb25_big(0);
    }
    if (x == 0) {
        return y == 0 ? 1 : 0;   /* 0^.5 is 0; the uc80 pow() goes through log(0) */
    }
    if (x < 0 && floor(y) != y) {
        mb25_fail(MB25_E_ILLEGAL_FUNC);
    }
    if (x != 0 && y > 0 && y * log(x < 0 ? -x : x) >= 87.3365) {
        mb25_warn(MB25_E_OVERFLOW);
        return mb25_big(x < 0 && ((int)y & 1));
    }
    return mb25_checked(mb25_pow_raw(x, y));
}

/* The operand of \, MOD, AND, OR, XOR, EQV, IMP and NOT, and the value of
 * CINT, of a subscript and of a store into an INTEGER variable: round half
 * away from zero, then MBASIC stops with Overflow for a value outside
 * -32768..32767 (32767.5 and -32768.5 included).  The test is on the double,
 * so nothing wraps first. */
int mb25_int16(double v) {
    /* Work on the size: uc80 gets a comparison of two negative floats wrong. */
    int negative = v < 0;
    double size = floor((negative ? -v : v) + 0.5);
    if (size > (negative ? 32768.0 : 32767.0)) {
        mb25_fail(MB25_E_OVERFLOW);
    }
    return negative ? -(int)size : (int)size;
}

/* The value of integer + - * that was worked out in 32 bits: a result outside
 * -32768..32767 is Overflow. */
int mb25_chk32(long v) {
    if (v < -32768L || v > 32767L) {
        mb25_fail(MB25_E_OVERFLOW);
    }
    return (int)v;
}

int mb25_cint(double v) {
    return mb25_int16(v);
}

/* A message that MBASIC prints and then carries on: Division by zero and
 * Overflow in a floating-point expression.  The value that goes on is the
 * largest float, with the sign of the true result.  MBASIC prints no new line
 * before the message, whatever the column. */
void mb25_warn(int code) {
    if (mb25_on_error) {
        mb25_fail(code);           /* with ON ERROR GOTO armed it is an error */
    }
    fputs(mb25_message(code), stdout);
    putchar('\n');
    mb25_set_col(0);
}

static double mb25_big(int negative) {
    double big = 1.7014117E+38;
    return negative ? -big : big;
}

/* A floating-point result at or beyond the largest float is Overflow. */
static double mb25_checked(double r) {
    double size = r < 0 ? -r : r;
    if (size >= 1.70141E+38) {
        mb25_warn(MB25_E_OVERFLOW);
        return mb25_big(r < 0);
    }
    return r;
}

double mb25_fdiv(double a, double b) {
    if (b == 0) {
        mb25_warn(MB25_E_DIV_ZERO);
        return mb25_big(a < 0);
    }
    return a / b;
}

/* The product is tested before it is made: a float product that is too large
 * wraps round on uc80 and is never seen as large. */
double mb25_fmul(double a, double b) {
    double sa = a < 0 ? -a : a, sb = b < 0 ? -b : b;
    if (sa != 0 && sb != 0 && sb > mb25_big(0) / sa) {
        mb25_warn(MB25_E_OVERFLOW);
        return mb25_big((a < 0) != (b < 0));
    }
    return a * b;
}

/* EXP: MBASIC gives Overflow from 87.3365 (log of 2^126) up, and 0 below
 * -88.7228 (log of 2^-128). */
double mb25_exp(double v) {
    if (v >= 87.3365) {
        mb25_warn(MB25_E_OVERFLOW);
        return mb25_big(0);
    }
    /* The size is compared, not v: uc80 gets two negative floats wrong. */
    if (v < 0 && -v > 88.7228) {
        return 0;
    }
    return exp(v);
}

/* + and - on floats.  A sum beyond the largest float wraps round on uc80, so
 * the sizes are compared before the sum is made. */
double mb25_fadd(double a, double b) {
    double sa = a < 0 ? -a : a, sb = b < 0 ? -b : b;
    if (((a < 0) == (b < 0)) && sa > mb25_big(0) - sb) {
        mb25_warn(MB25_E_OVERFLOW);
        return mb25_big(a < 0);
    }
    return a + b;
}

double mb25_fsub(double a, double b) {
    return mb25_fadd(a, -b);
}

/* + and - on two integers whose result goes into an INTEGER: a result outside
 * -32768..32767 is Overflow. */
int mb25_iadd(int a, int b) {
    int r = a + b;
    if (((a ^ r) & (b ^ r)) < 0) {
        mb25_fail(MB25_E_OVERFLOW);
    }
    return r;
}

int mb25_isub(int a, int b) {
    int r = a - b;
    if (((a ^ b) & (a ^ r)) < 0) {
        mb25_fail(MB25_E_OVERFLOW);
    }
    return r;
}

double mb25_log(double v) {
    if (v <= 0) {
        mb25_fail(MB25_E_ILLEGAL_FUNC);
    }
    return log(v);
}

/* A value for a string length, a character code or a count: 0..255, or
 * Illegal function call. */
int mb25_byte(int v) {
    if (v < 0 || v > 255) {
        mb25_fail(MB25_E_ILLEGAL_FUNC);
    }
    return v;
}

/* The start of MID$ or INSTR: 1..255. */
int mb25_start(int v) {
    if (v < 1 || v > 255) {
        mb25_fail(MB25_E_ILLEGAL_FUNC);
    }
    return v;
}

/* The argument of HEX$ and OCT$: -32768..65535 (Overflow outside), read as a
 * 16-bit word. */
int mb25_word(double v) {
    int negative = v < 0;
    double size = floor((negative ? -v : v) + 0.5);
    if (size > (negative ? 32768.0 : 65535.0)) {
        mb25_fail(MB25_E_OVERFLOW);
    }
    if (negative) {
        return -(int)size;
    }
    return size > 32767.0 ? (int)(size - 65536.0) : (int)size;
}

/* \ and MOD.  The operands are checked for Overflow before the divisor is
 * tested, as MBASIC does. */
int mb25_idiv(int a, int b) {
    if (b == 0) {
        mb25_fail(MB25_E_DIV_ZERO);
    }
    return a / b;
}

/* \ where the quotient may not fit an integer: -32768 \ -1 is 32768. */
double mb25_idivd(int a, int b) {
    if (b == 0) {
        mb25_fail(MB25_E_DIV_ZERO);
    }
    if (b == -1) {
        return -(double)a;
    }
    return a / b;
}

int mb25_imod(int a, int b) {
    if (b == 0) {
        mb25_fail(MB25_E_DIV_ZERO);
    }
    return a % b;
}

/* INT and FIX.  The library floor() and trunc() go through a 32-bit integer
 * and stop at 2^31; a float above 2^23 has no fraction, so it is returned as
 * it is. */
double mb25_int(double v) {
    /* Compare the size, not v: uc80 gets two negative floats wrong. */
    double size = v < 0 ? -v : v;
    if (size >= 8388608.0) {
        return v;
    }
    return floor(v);
}

double mb25_fix(double v) {
    return v < 0 ? -mb25_int(-v) : mb25_int(v);
}

/* Check an array subscript (already moved down by OPTION BASE) against the
 * number of elements.  BASIC stops with an error; writing past a C array
 * would corrupt the string pool instead.  Only a subscript that is negative
 * before the move gives "Illegal function call"; A$(0) under OPTION BASE 1
 * is "Subscript out of range". */
int mb25_subscript(int i, int n, int base) {
    if (i < 0 || i >= n) {
        mb25_fail(i + base < 0 ? MB25_E_ILLEGAL_FUNC : MB25_E_SUBSCRIPT);
    }
    return i;
}

/* Arrays that an ERASE names.  Their storage is fixed (the largest shape the
 * program can give them) but their shape is not: st is 0 while the array does
 * not exist, rk is its number of subscripts and n[] the number of elements
 * along each one.  A use of an array that does not exist dimensions it with
 * dflt elements per subscript (0..10, or 1..10 under OPTION BASE 1). */

/* The first subscript of an element: creates the array if needed, checks the
 * number of subscripts k and the first subscript i. */
int mb25_ea_first(char *st, int *rk, int *n, int k, int dflt, int i, int base) {
    int j;
    if (!*st) {
        *st = 1;
        *rk = k;
        for (j = 0; j < k; j++) {
            n[j] = dflt;
        }
    }
    if (*rk != k) {
        mb25_fail(MB25_E_SUBSCRIPT);
    }
    return mb25_subscript(i, n[0], base);
}

/* The next subscript: acc * n[j] + i, with i checked against n[j]. */
int mb25_ea_next(int acc, int *n, int j, int i, int base) {
    return acc * n[j] + mb25_subscript(i, n[j], base);
}

/* DIM of an array with k subscripts: the caller then fills in n[]. */
void mb25_ea_dim(char *st, int *rk, int k) {
    if (*st) {
        mb25_fail(MB25_E_DUPLICATE);
    }
    *st = 1;
    *rk = k;
}

/* ERASE: the array stops existing.  Returns how many elements it had, for
 * the caller to clear. */
int mb25_ea_erase(char *st, int *rk, int *n) {
    int j;
    int total = 1;
    if (!*st) {
        mb25_fail(MB25_E_ILLEGAL_FUNC);
    }
    for (j = 0; j < *rk; j++) {
        total *= n[j];
    }
    *st = 0;
    return total;
}

/* CLEAR: like ERASE, but an array that does not exist is no error. */
int mb25_ea_clear(char *st, int *rk, int *n) {
    int j;
    int total = 1;
    if (!*st) {
        return 0;
    }
    for (j = 0; j < *rk; j++) {
        total *= n[j];
    }
    *st = 0;
    return total;
}

/* SWAP two strings: exchange everything in the descriptors except the IDs. */
void mb25_string_swap(uint16_t a, uint16_t b) {
    mb25_string_t t;
    if (!MB25_VALID_ID(a) || !MB25_VALID_ID(b)) {
        return;
    }
    t = mb25_strings[a];
    mb25_strings[a] = mb25_strings[b];
    mb25_strings[b] = t;
    mb25_strings[a].str_id = a;
    mb25_strings[b].str_id = b;
}

/* EOF(n): -1 when the next read would find the end of the file, else 0.
 * feof() alone says 0 until a read has already failed. */
int mb25_eof(FILE *fp) {
    int ch;
    if (fp == NULL) {
        return -1;
    }
    ch = fgetc(fp);
    if (ch == EOF || ch == 0x1A) {      /* the end, or CP/M's ^Z */
        return -1;
    }
    ungetc(ch, fp);
    return 0;
}

/* The keyboard input has ended: BASIC stops the program. */
int mb25_input_eof(void) {
    exit(0);
    return 0;
}

/* Remove the line end (LF, CR LF or CR) that fgets leaves on a line of input. */
void mb25_chomp(char *s) {
    size_t n = strlen(s);
    while (n > 0 && (s[n - 1] == '\n' || s[n - 1] == '\r')) {
        s[--n] = '\0';
    }
}

/* ===== PRINT output: column tracking, zones, MBASIC number format ===== */

/* Console line width and comma-zone width, as in the interpreter
 * (src/print_column.py).  A file has a width of 255 and never wraps. */
#define MB25_SCREEN_WIDTH 80
#define MB25_FILE_WIDTH   255
#define MB25_ZONE_WIDTH   14

static FILE *mb25_out_fp;      /* NULL = console, else the PRINT# file */
static int mb25_con_col;       /* 0-based cursor column of the console */
static int mb25_file_col;      /* the same for the current file */

void mb25_set_out(FILE *fp) {
    mb25_out_fp = fp;
}

void mb25_set_col(int col) {
    mb25_con_col = col;
}

/* POS(x): the console column, 1 for the leftmost */
int mb25_pos(void) {
    return mb25_con_col + 1;
}

static int mb25_width(void) {
    return mb25_out_fp ? MB25_FILE_WIDTH : MB25_SCREEN_WIDTH;
}

/* One raw character to the console or file.  A newline in a file is CR LF. */
static void mb25_raw(int c) {
    if (mb25_out_fp) {
        if (c == '\n') {
            fputc('\r', mb25_out_fp);
        }
        fputc(c, mb25_out_fp);
    } else {
        putchar(c);
    }
}

/* One character, with the column bookkeeping of advance_column() and the
 * lazy wrap of wrap_text(): a printable character at a full line starts a
 * new line first. */
void mb25_putc(int c) {
    int col = mb25_out_fp ? mb25_file_col : mb25_con_col;
    if (c == '\n' || c == '\r') {
        col = 0;
    } else if (c == '\t') {
        col = (col / 8 + 1) * 8;
    } else if (c == '\b') {
        if (col > 0) {
            col--;
        }
    } else if (c >= ' ') {
        if (col >= mb25_width()) {
            mb25_raw('\n');
            col = 0;
        }
        col++;
    }
    mb25_raw(c);
    if (mb25_out_fp) {
        mb25_file_col = col;
    } else {
        mb25_con_col = col;
    }
}

/* A PRINT item: it starts on a new line when it does not fit in the rest of
 * the console line. */
static void mb25_emit(const uint8_t *p, int len) {
    int col = mb25_out_fp ? mb25_file_col : mb25_con_col;
    if (col > 0 && col + len > mb25_width() && !mb25_out_fp) {
        mb25_putc('\n');
    }
    while (len-- > 0) {
        mb25_putc(*p++);
    }
}

void mb25_print_cstr(const char *s) {
    mb25_emit((const uint8_t *)s, (int)strlen(s));
}

void mb25_print_nl(void) {
    mb25_putc('\n');
}

void mb25_print_zone(void) {
    int col = mb25_out_fp ? mb25_file_col : mb25_con_col;
    int zone = (col / MB25_ZONE_WIDTH + 1) * MB25_ZONE_WIDTH;
    if (!mb25_out_fp && zone + MB25_ZONE_WIDTH > mb25_width()) {
        mb25_putc('\n');
        return;
    }
    while (col < zone) {
        mb25_putc(' ');
        col++;
    }
}

void mb25_print_tab(int n) {
    int col = mb25_out_fp ? mb25_file_col : mb25_con_col;
    int target = (n < 1) ? 0 : (n - 1) % mb25_width();
    if (col > target) {
        mb25_putc('\n');
        col = 0;
    }
    while (col < target) {
        mb25_putc(' ');
        col++;
    }
}

void mb25_print_spc(int n) {
    if (n < 0) {
        n = 0;
    }
    n %= mb25_width();
    while (n-- > 0) {
        mb25_putc(' ');
    }
}

/* ---- Number to text ---- */

/* Single values keep 6 significant figures, doubles 16.  uc80 has no 64-bit
 * float (sizeof(double) is 4 there), so a double can only be trusted to 7. */
#define MB25_SINGLE_DIGITS 6
#define MB25_DOUBLE_DIGITS (sizeof(double) > 4 ? 16 : 7)

/* The exact decimal expansion of a float is built in a digit array,
 * least significant digit first.  120 digits holds any 32-bit float. */
#define MB25_FMT_MAX 120
static uint8_t mb25_fd[MB25_FMT_MAX];
static int mb25_fn;

static void mb25_fd_mul(unsigned int m) {
    unsigned int carry = 0, v;
    int i;
    for (i = 0; i < mb25_fn; i++) {
        v = mb25_fd[i] * m + carry;
        mb25_fd[i] = (uint8_t)(v % 10);
        carry = v / 10;
    }
    while (carry && mb25_fn < MB25_FMT_MAX) {
        mb25_fd[mb25_fn++] = (uint8_t)(carry % 10);
        carry /= 10;
    }
}

static void mb25_fd_add(unsigned int b) {
    int i = 0;
    while (b && i < MB25_FMT_MAX) {
        if (i == mb25_fn) {
            mb25_fd[mb25_fn++] = 0;
        }
        b += mb25_fd[i];
        mb25_fd[i++] = (uint8_t)(b % 10);
        b /= 10;
    }
}

/* Round the digit string d[0..n) (most significant first) to `keep` figures,
 * halves up.  Returns the new count; *e10 grows by one on a carry out of the
 * leading digit (9.99 -> 10.0). */
static int mb25_round_digits(char *d, int n, int keep, int *e10) {
    int i;
    if (n <= keep) {
        return n;
    }
    i = (d[keep] >= '5');
    n = keep;
    while (i && n > 0) {
        if (d[n - 1] == '9') {
            d[--n] = '0';
        } else {
            d[n - 1]++;
            i = 0;
        }
    }
    if (i) {                       /* every digit was 9: 999 -> 1000 */
        d[0] = '1';
        n = 1;
        (*e10)++;
    }
    return n;
}

/* A positive single as m * 2^e, m in [2^23, 2^24).  The steps of FOUT
 * below work on m with integer arithmetic: uc80's float operations do not
 * round the way MBASIC's do (1E20 printed 9.99999E+19), and these are exact
 * on any compiler. */
static void mb25_sng_split(double v, unsigned long *m, int *e) {
    int k;
    double f = frexp(v, &k);       /* v = f * 2^k, f in [0.5, 1) */
    *m = (unsigned long)ldexp(f, 24);
    *e = k - 24;
}

/* p * 2^e rounded to 24 bits, a tie up, as MBASIC rounds; p < 2^31 */
static void mb25_sng_norm(unsigned long p, int *e, unsigned long *m) {
    int s = 0;
    unsigned long low = 0, half;
    while ((p >> s) >= 0x1000000UL) {
        s++;
    }
    if (s > 0) {
        half = 1UL << (s - 1);
        low = p & ((1UL << s) - 1);
        p >>= s;
        if (low >= half) {
            p++;
            if (p == 0x1000000UL) {
                p >>= 1;
                s++;
            }
        }
    }
    *m = p;
    *e += s;
}

/* The six digits MBASIC's FOUT prints for a positive single (foutnv in
 * f4.mac): divide or multiply by ten, one single-precision step at a time,
 * until the number lies in 99999.95 .. 999999.5, then add .5 and drop the
 * fraction (number_format._single_fout_digits).  Puts the digits in d, the
 * power of ten of the leading one in *e10, and returns the count. */
static int mb25_fout_single(char *d, double v, int *e10) {
    unsigned long m, k;
    int e, i, x = 0;
    mb25_sng_split(v, &m, &e);
    if (ldexp((double)m, e) >= 999999.5) {
        while (ldexp((double)m, e) >= 999999.5) {
            /* m / 10 with 7 more bits, then back to 24 bits */
            unsigned long q = (m << 7) / 10;
            e -= 7;
            mb25_sng_norm(q, &e, &m);
            x++;
        }
    } else {
        while (ldexp((double)m, e) < 99999.953125) {
            mb25_sng_norm(m * 10, &e, &m);
            x--;
        }
    }
    /* + .5 in single precision, then the integer part; here e is -4 to -7 */
    k = m + (1UL << (-e - 1));
    mb25_sng_norm(k, &e, &k);
    k >>= -e;
    for (i = 5; i >= 0; i--) {
        d[i] = (char)('0' + k % 10);
        k /= 10;
    }
    *e10 = x + 5;
    return 6;
}

/* The significant digits PRINT shows for a number v > 0, most significant
 * first and without trailing zeros, in d; *e10 is the power of ten of the
 * first.  kind 0 is single (FOUT's six digits), 1 is double.  Returns the
 * count. */
static int mb25_num_digits(char *d, double v, int kind, int *e10) {
    int digits = kind ? (int)MB25_DOUBLE_DIGITS : MB25_SINGLE_DIGITS;
    int n, i, e, p, x;
    double m;
    unsigned int b;

    if (kind == 0) {
        n = mb25_fout_single(d, v, &x);
    } else {
        /* v = m * 2^e with m in [0.5, 1).  Peel m into bytes: N * 2^(e-k). */
        m = frexp(v, &e);
        mb25_fn = 1;
        mb25_fd[0] = 0;
        p = e;
        while (m != 0) {
            m *= 256;
            b = (unsigned int)m;
            m -= b;
            mb25_fd_mul(256);
            mb25_fd_add(b);
            p -= 8;
        }
        x = 0;                         /* the integer in mb25_fd times 10^x */
        if (p > 0) {
            while (p-- > 0) {
                mb25_fd_mul(2);
            }
        } else {
            x = p;
            while (p++ < 0) {
                mb25_fd_mul(5);
            }
        }
        n = mb25_fn;
        for (i = 0; i < n; i++) {
            d[i] = (char)('0' + mb25_fd[n - 1 - i]);
        }
        x += n - 1;                    /* power of ten of the leading digit */
        n = mb25_round_digits(d, n, digits, &x);
    }
    while (n > 1 && d[n - 1] == '0') {
        n--;
    }
    *e10 = x;
    return n;
}

/* The characters MBASIC prints for a number, without the padding spaces
 * (number_format.format_number).  kind 0 is single, 1 is double.  buf needs
 * 40 bytes.  Returns the length. */
int mb25_fmt_num(char *buf, double v, int kind) {
    char d[MB25_FMT_MAX + 2];
    int digits = kind ? (int)MB25_DOUBLE_DIGITS : MB25_SINGLE_DIGITS;
    int i, x, s, neg = 0, len = 0, scaled;

    if (v != v) {
        v = 0;
    }
    if (v < 0) {
        neg = 1;
        v = -v;
    }
    if (v == 0) {
        buf[0] = '0';
        buf[1] = 0;
        return 1;
    }
    if (v > 3.4e38) {              /* MBASIC's machine infinity */
        strcpy(buf, neg ? "-1.70141E+38" : "1.70141E+38");
        return neg ? 12 : 11;
    }

    s = mb25_num_digits(d, v, kind, &x);

    if (x >= 0) {
        scaled = (x + 1) > digits;
    } else {
        scaled = (-x - 1) + s > digits + 1;
    }

    if (neg) {
        buf[len++] = '-';
    }
    if (!scaled) {
        if (x >= 0) {
            for (i = 0; i <= x; i++) {
                buf[len++] = (i < s) ? d[i] : '0';
            }
            if (s > x + 1) {
                buf[len++] = '.';
                for (i = x + 1; i < s; i++) {
                    buf[len++] = d[i];
                }
            }
        } else {
            buf[len++] = '.';
            for (i = 0; i < -x - 1; i++) {
                buf[len++] = '0';
            }
            for (i = 0; i < s; i++) {
                buf[len++] = d[i];
            }
        }
    } else {
        buf[len++] = d[0];
        if (s > 1) {
            buf[len++] = '.';
            for (i = 1; i < s; i++) {
                buf[len++] = d[i];
            }
        }
        buf[len++] = kind ? 'D' : 'E';
        if (x < 0) {
            buf[len++] = '-';
            x = -x;
        } else {
            buf[len++] = '+';
        }
        if (x >= 100) {
            buf[len++] = (char)('0' + x / 100);
            x %= 100;
        }
        buf[len++] = (char)('0' + x / 10);
        buf[len++] = (char)('0' + x % 10);
    }
    buf[len] = 0;
    return len;
}

/* The same for an INTEGER-typed value. */
int mb25_fmt_int(char *buf, int v) {
    char t[8];
    int len = 0, n = 0;
    unsigned int u = (v < 0) ? (unsigned int)(-v) : (unsigned int)v;
    if (v < 0) {
        buf[len++] = '-';
    }
    do {
        t[n++] = (char)('0' + u % 10);
        u /= 10;
    } while (u);
    while (n) {
        buf[len++] = t[--n];
    }
    buf[len] = 0;
    return len;
}

/* PRINT item: a space before a number that is not negative, one after. */
static void mb25_print_padded(char *buf, int len) {
    char out[44];
    int o = 0;
    if (buf[0] != '-') {
        out[o++] = ' ';
    }
    memcpy(out + o, buf, len);
    o += len;
    out[o++] = ' ';
    mb25_emit((const uint8_t *)out, o);
}

void mb25_print_num(double v, int kind) {
    char buf[40];
    mb25_print_padded(buf, mb25_fmt_num(buf, v, kind));
}

void mb25_print_int(int v) {
    char buf[40];
    mb25_print_padded(buf, mb25_fmt_int(buf, v));
}

/* WRITE: the number without padding spaces. */
void mb25_write_num(double v, int kind) {
    char buf[40];
    mb25_emit((const uint8_t *)buf, mb25_fmt_num(buf, v, kind));
}

void mb25_write_int(int v) {
    char buf[40];
    mb25_emit((const uint8_t *)buf, mb25_fmt_int(buf, v));
}

/* STR$: a leading space unless negative, no trailing space. */
static mb25_error_t mb25_str_buf(uint16_t dest_id, char *buf) {
    char out[44];
    int o = 0;
    if (buf[0] != '-') {
        out[o++] = ' ';
    }
    strcpy(out + o, buf);
    return mb25_string_alloc_init(dest_id, out);
}

mb25_error_t mb25_str_num(uint16_t dest_id, double v, int kind) {
    char buf[40];
    mb25_fmt_num(buf, v, kind);
    return mb25_str_buf(dest_id, buf);
}

mb25_error_t mb25_str_int(uint16_t dest_id, int v) {
    char buf[40];
    mb25_fmt_int(buf, v);
    return mb25_str_buf(dest_id, buf);
}

void mb25_print_string(uint16_t str_id) {
    mb25_string_pt str;
    if (!MB25_VALID_ID(str_id)) {
        return;
    }
    str = &mb25_strings[str_id];
    if (str->data == NULL || str->len == 0) {
        return;  /* Empty string - print nothing */
    }
    mb25_emit(str->data, str->len);
}

void mb25_fprint_string(FILE *fp, uint16_t str_id) {
    FILE *saved = mb25_out_fp;
    if (fp == NULL) {
        return;
    }
    mb25_out_fp = fp;
    mb25_print_string(str_id);
    mb25_out_fp = saved;
}

char *mb25_get_c_string_temp(uint16_t src_id, uint16_t temp_id) {
    /* Create null-terminated C string using temp pool - NO MALLOC! */
    if (!MB25_VALID_ID(src_id) || !MB25_VALID_ID(temp_id)) {
        return NULL;
    }

    mb25_string_pt src = &mb25_strings[src_id];
    if (src->data == NULL || src->len == 0) {
        /* Empty string - allocate 1 byte for null terminator */
        mb25_string_alloc(temp_id, 1);
        uint8_t *data = mb25_get_data(temp_id);
        if (data) {
            data[0] = '\0';
        }
        return (char *)data;
    }

    /* Allocate temp with room for null terminator */
    mb25_string_alloc(temp_id, src->len + 1);
    uint8_t *data = mb25_get_data(temp_id);
    if (data) {
        memcpy(data, src->data, src->len);
        data[src->len] = '\0';
    }
    return (char *)data;
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

/* The BASIC line that is running.  The generated code sets it at the start
 * of each line, so an error can say "in 40" like MBASIC does.  A line number
 * goes up to 65529, so it is unsigned. */
unsigned int mb25_line;

/* ON ERROR GOTO state (see mb25_string.h).  ERL is the line that was
 * running; RESUME goes back to statement mb25_err_stmt. */
jmp_buf mb25_jmp;
unsigned int mb25_on_error;
char mb25_in_trap;
int mb25_err;
unsigned int mb25_erl;
unsigned int mb25_stmt;
unsigned int mb25_err_stmt;

/* MBASIC 5.21's messages by error code (src/error_codes.py); 0 for a code
 * that has none, which prints as Unprintable error. */
static const char *const mb25_messages[] = {
    "NEXT without FOR",
    "Syntax error",
    "RETURN without GOSUB",
    "Out of DATA",
    "Illegal function call",
    "Overflow",
    "Out of memory",
    "Undefined line number",
    "Subscript out of range",
    "Duplicate Definition",
    "Division by zero",
    "Illegal direct",
    "Type mismatch",
    "Out of string space",
    "String too long",
    "String formula too complex",
    "Can't continue",
    "Undefined user function",
    "No RESUME",
    "RESUME without error",
    "Unprintable error",
    "Missing operand",
    "Line buffer overflow",
    0,
    0,
    "FOR Without NEXT",
    0,
    0,
    "WHILE without WEND",
    "WEND without WHILE",
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    "FIELD overflow",
    "Internal error",
    "Bad file number",
    "File not found",
    "Bad file mode",
    "File already open",
    0,
    "Disk I/O error",
    "File already exists",
    0,
    0,
    "Disk full",
    "Input past end",
    "Bad record number",
    "Bad file name",
    0,
    "Direct statement in file",
    "Too many files",
};

const char *mb25_message(int code) {
    const char *m = (code >= 1 && code <= 67) ? mb25_messages[code - 1] : 0;
    return m ? m : "Unprintable error";
}

/* Print an error message "in" a line and stop.  MBASIC starts a new line
 * when the cursor is not in column 1. */
static void mb25_stop(int code, unsigned int line) {
    char t[6];
    int n = 0;
    mb25_set_out(NULL);
    if (mb25_con_col != 0) {
        putchar('\n');
    }
    fputs(mb25_message(code), stdout);
    if (line > 0) {
        fputs(" in ", stdout);
        while (line) {
            t[n++] = (char)('0' + line % 10);
            line /= 10;
        }
        while (n) {
            putchar(t[--n]);
        }
    }
    putchar('\n');
    exit(1);
}

/* A run-time error.  With ON ERROR GOTO armed and no error being handled it
 * goes to the handler; otherwise the program stops with the message.  An
 * error inside the handler stops it too, in the handler's line (measured). */
void mb25_fail(int code) {
    if (mb25_on_error && !mb25_in_trap) {
        mb25_err = code;
        mb25_erl = mb25_line;
        mb25_err_stmt = mb25_stmt;
        mb25_in_trap = 1;
        longjmp(mb25_jmp, 1);
    }
    mb25_stop(code, mb25_line);
}

/* ERROR n: n is a byte and not 0 (ERROR 0 and ERROR 256 are Illegal
 * function call).  A code with no message is Unprintable error. */
void mb25_error(double n) {
    int code = mb25_cint(n);
    if (code <= 0 || code > 255) {
        mb25_fail(MB25_E_ILLEGAL_FUNC);
    }
    mb25_fail(code);
}

/* ON ERROR GOTO 0.  Inside the handler it stops the program with the error
 * being handled, in ERL (measured: "Division by zero in 20"). */
void mb25_trap_off(void) {
    if (mb25_in_trap) {
        mb25_stop(mb25_err, mb25_erl);
    }
    mb25_on_error = 0;
}

/* RESUME, before it jumps: RESUME without error, else the error is done and
 * ERR is 0 again (ERL stays).  Until the next line starts, the line is ERL
 * again (an error there is reported in ERL, as on the binary). */
void mb25_resume(void) {
    if (!mb25_in_trap) {
        mb25_fail(MB25_E_NO_ERROR);
    }
    mb25_in_trap = 0;
    mb25_err = 0;
    mb25_line = mb25_erl;
}

/* ===== PRINT USING =====
 *
 * A port of UsingFormatter (src/basic_builtins.py) by way of the JavaScript
 * runtime's _using_* functions.  The generated code calls
 * mb25_using_begin with the format, then mb25_using_num or mb25_using_str
 * for each value as it is worked out, then mb25_using_end.  Each value
 * prints the format's text up to the next field (going back to the start of
 * the format when it runs out) and then itself in that field. */
static char mb25_u_fmt[MB25_MAX_STRING_LEN + 1];
static int mb25_u_len, mb25_u_pos;

/* A numeric field.  lead is the room before the decimal point (with a
 * leading +), trail the room from the point on (0 when there is none). */
typedef struct {
    int lead, trail;
    char leading_sign, trailing_sign, trailing_minus, dollar, star, comma, expo;
} mb25_u_spec;

enum { MB25_U_END, MB25_U_FIRST, MB25_U_FULL, MB25_U_FIXED, MB25_U_NUM };

static void mb25_u_text(const uint8_t *s, int len) {
    while (len-- > 0) {
        mb25_putc(*s++);
    }
}

static int mb25_u_at(int i, const char *s) {
    while (*s) {
        if (i >= mb25_u_len || mb25_u_fmt[i] != *s) {
            return 0;
        }
        i++;
        s++;
    }
    return 1;
}

/* Parse a numeric field at mb25_u_fmt[i]; returns its digit count (0: not
 * a field) and the position after it in *end. */
static int mb25_u_numeric(int i, mb25_u_spec *f, int *end) {
    int digits = 0, after = 0, point = 0;
    memset(f, 0, sizeof(*f));
    if (mb25_u_at(i, "**$")) {
        f->star = f->dollar = 1;
        digits = 3;
        i += 3;
    } else if (mb25_u_at(i, "**")) {
        f->star = 1;
        digits = 2;
        i += 2;
    } else if (mb25_u_at(i, "$$")) {
        f->dollar = 1;
        digits = 2;
        i += 2;
    } else if (mb25_u_fmt[i] == '+') {
        f->leading_sign = 1;
        i++;
    }
    while (i < mb25_u_len) {
        char c = mb25_u_fmt[i];
        if (c == '#') {
            digits++;
            if (point) {
                after++;
            }
        } else if (c == '.' && !point) {
            point = 1;
        } else if (c == ',') {
            f->comma = 1;
            digits++;
        } else {
            break;
        }
        i++;
    }
    if (mb25_u_at(i, "^^^^")) {
        f->expo = 1;
        i += 4;
    }
    if (i < mb25_u_len && !f->leading_sign) {
        if (mb25_u_fmt[i] == '+') {
            f->trailing_sign = 1;
            i++;
        } else if (mb25_u_fmt[i] == '-') {
            f->trailing_minus = 1;
            i++;
        }
    }
    *end = i;
    f->lead = digits - after + f->leading_sign;
    f->trail = point ? after + 1 : 0;
    return digits;
}

/* Print the format's text from mb25_u_pos up to the next field and parse
 * that field.  At the end of the format: MB25_U_END, or with wrap, go on
 * from the start (the caller knows that the format has a field). */
static int mb25_u_next(mb25_u_spec *f, int *width, int wrap) {
    int i, j, end;
    for (;;) {
        if (mb25_u_pos >= mb25_u_len) {
            if (!wrap) {
                return MB25_U_END;
            }
            mb25_u_pos = 0;
        }
        i = mb25_u_pos;
        switch (mb25_u_fmt[i]) {
        case '_':
            if (i + 1 < mb25_u_len) {
                mb25_putc(mb25_u_fmt[i + 1]);
                mb25_u_pos = i + 2;
                continue;
            }
            break;
        case '!':
            mb25_u_pos = i + 1;
            return MB25_U_FIRST;
        case '&':
            mb25_u_pos = i + 1;
            return MB25_U_FULL;
        case '\\':
            for (j = i + 1; j < mb25_u_len && mb25_u_fmt[j] == ' '; j++) {
            }
            if (j < mb25_u_len && mb25_u_fmt[j] == '\\') {
                *width = j - i + 1;
                mb25_u_pos = j + 1;
                return MB25_U_FIXED;
            }
            break;
        case '#': case '.': case '+': case '-': case '*': case '$':
            if ((mb25_u_fmt[i] != '*' || mb25_u_at(i, "**") || mb25_u_at(i, "*$"))
                    && (mb25_u_fmt[i] != '$' || mb25_u_at(i, "$$"))
                    && mb25_u_numeric(i, f, &end)) {
                mb25_u_pos = end;
                return MB25_U_NUM;
            }
            break;
        }
        mb25_putc(mb25_u_fmt[i]);
        mb25_u_pos = i + 1;
    }
}

/* Whether the format has a field at all (a value with none is Illegal
 * function call, after the text). */
static int mb25_u_has_field(void) {
    int save = mb25_u_pos, kind = MB25_U_END;
    mb25_u_spec f;
    for (mb25_u_pos = 0; mb25_u_pos < mb25_u_len; ) {
        int i = mb25_u_pos, end;
        char c = mb25_u_fmt[i];
        if (c == '!' || c == '&') {
            kind = MB25_U_FIRST;
            break;
        }
        if (c == '\\') {
            int j;
            for (j = i + 1; j < mb25_u_len && mb25_u_fmt[j] == ' '; j++) {
            }
            if (j < mb25_u_len && mb25_u_fmt[j] == '\\') {
                kind = MB25_U_FIXED;
                break;
            }
        }
        if (c == '_' && i + 1 < mb25_u_len) {
            mb25_u_pos = i + 2;
            continue;
        }
        if ((c == '#' || c == '.' || c == '+' || c == '-'
                || (c == '*' && (mb25_u_at(i, "**") || mb25_u_at(i, "*$")))
                || (c == '$' && mb25_u_at(i, "$$"))) && mb25_u_numeric(i, &f, &end)) {
            kind = MB25_U_NUM;
            break;
        }
        mb25_u_pos = i + 1;
    }
    mb25_u_pos = save;
    return kind != MB25_U_END;
}

void mb25_using_begin(const char *s, int len) {
    if (len <= 0) {
        mb25_fail(MB25_E_ILLEGAL_FUNC);
    }
    memcpy(mb25_u_fmt, s, (size_t)len);
    mb25_u_len = len;
    mb25_u_pos = 0;
}

void mb25_using_begin_id(uint16_t id) {
    mb25_using_begin((const char *)mb25_get_data(id), mb25_get_length(id));
}

/* The field for the next value: Type mismatch when it is not of the kind
 * the value needs, and Illegal function call when the format has none. */
static int mb25_u_field(mb25_u_spec *f, int *width, int numeric) {
    int kind;
    if (!mb25_u_has_field()) {
        mb25_u_next(f, width, 0);  /* the text, then the error */
        mb25_fail(MB25_E_ILLEGAL_FUNC);
    }
    kind = mb25_u_next(f, width, 1);
    if ((kind == MB25_U_NUM) != numeric) {
        mb25_fail(MB25_E_TYPE);
    }
    return kind;
}

void mb25_using_text(const char *s, int len) {
    mb25_u_spec f;
    int width = 0, kind = mb25_u_field(&f, &width, 0);
    if (kind == MB25_U_FIRST) {
        mb25_putc(len > 0 ? (uint8_t)s[0] : ' ');
    } else if (kind == MB25_U_FULL) {
        mb25_u_text((const uint8_t *)s, len);
    } else {
        mb25_u_text((const uint8_t *)s, len < width ? len : width);
        while (len++ < width) {
            mb25_putc(' ');
        }
    }
}

void mb25_using_str(uint16_t id) {
    char copy[MB25_MAX_STRING_LEN + 1];
    int len = mb25_get_length(id);
    memcpy(copy, mb25_get_data(id), (size_t)len);
    mb25_using_text(copy, len);
}

/* Round the digits d (n of them, the first worth 10^x) to `decimals`
 * places: the integer digits without leading zeros go to ip, the decimals
 * to fp. */
static void mb25_u_fixed(const char *d, int n, int x, int decimals, char *ip, char *fp) {
    char all[80];
    int i, k, len = 0, int_len, carry;
    if (x >= 0) {
        int_len = x + 1;
        for (i = 0; i < int_len + decimals + 1; i++) {
            all[len++] = (i < n) ? d[i] : '0';
        }
    } else {
        int_len = 1;
        all[len++] = '0';
        for (i = 0; i < decimals + 1; i++) {
            int k = i - (-x - 1);
            all[len++] = (k >= 0 && k < n) ? d[k] : '0';
        }
    }
    /* all = the integer digits, the decimals and one more: round on it */
    carry = all[len - 1] >= '5';
    len--;
    for (i = len - 1; carry && i >= 0; i--) {
        if (all[i] == '9') {
            all[i] = '0';
        } else {
            all[i]++;
            carry = 0;
        }
    }
    k = 0;
    if (carry) {
        ip[k++] = '1';
    }
    for (i = 0; i < int_len; i++) {
        if (k > 0 || all[i] != '0') {  /* no leading zeros: 0.5 has none */
            ip[k++] = all[i];
        }
    }
    ip[k] = 0;
    memcpy(fp, all + int_len, (size_t)decimals);
    fp[decimals] = 0;
}

/* kind 0 single, 1 double, 2 integer */
void mb25_using_num(double v, int kind) {
    mb25_u_spec f;
    char d[MB25_FMT_MAX + 2], ip[64], fp[32], body[96], out[128], suffix[6];
    int width = 0, n, x, decimals, negative, needed, sign_slot, trailing, i, len, fill;
    mb25_u_field(&f, &width, 1);
    decimals = f.trail ? f.trail - 1 : 0;
    if (f.lead + f.trail > 24) {
        mb25_fail(MB25_E_ILLEGAL_FUNC);
    }
    if (kind == 2) {
        v = (double)(long)v;
    }
    negative = v < 0;
    if (negative) {
        v = -v;
    }
    if (v == 0) {
        d[0] = '0';
        n = 1;
        x = 0;
    } else {
        n = mb25_num_digits(d, v, kind == 1, &x);
    }
    suffix[0] = 0;
    if (!f.expo && x >= 16) {
        /* too big for the layout: '%' and the PRINT form, sign dropped */
        out[0] = '%';
        out[1] = ' ';
        len = 2 + mb25_fmt_num(out + 2, v, kind == 1);
        mb25_u_text((const uint8_t *)out, len);
        return;
    }
    trailing = f.trailing_sign || f.trailing_minus;
    if (f.expo) {
        int int_digits = trailing ? f.lead : f.lead - 1, exponent = 0, e;
        if (!(n == 1 && d[0] == '0')) {
            exponent = x + 1 - int_digits;
            mb25_u_fixed(d, n, x - exponent, decimals, ip, fp);
        } else {
            mb25_u_fixed("0", 1, 0, decimals, ip, fp);
        }
        e = exponent < 0 ? -exponent : exponent;
        suffix[0] = kind == 1 ? 'D' : 'E';
        suffix[1] = exponent >= 0 ? '+' : '-';
        suffix[2] = (char)('0' + e / 10);
        suffix[3] = (char)('0' + e % 10);
        suffix[4] = 0;
    } else {
        mb25_u_fixed(d, n, x, decimals, ip, fp);
        if (f.comma) {
            char c[96];
            int l = (int)strlen(ip), k = 0;
            for (i = 0; i < l; i++) {
                if (i > 0 && (l - i) % 3 == 0) {
                    c[k++] = ',';
                }
                c[k++] = ip[i];
            }
            c[k] = 0;
            strcpy(ip, c);
        }
    }
    sign_slot = !trailing && (negative || f.leading_sign);
    needed = (int)strlen(ip) + f.dollar + sign_slot;
    if (!ip[0] && (needed + 1 <= f.lead || !f.trail)) {
        strcpy(ip, "0");
        needed++;
    }
    len = 0;
    if (sign_slot) {
        body[len++] = negative ? '-' : '+';
    }
    if (f.dollar) {
        body[len++] = '$';
    }
    strcpy(body + len, ip);
    if (f.trail) {
        strcat(body, ".");
        strcat(body, fp);
    }
    strcat(body, suffix);
    len = 0;
    if (needed > f.lead) {
        out[len++] = '%';
    } else {
        fill = f.lead + f.trail + (int)strlen(suffix) - (int)strlen(body);
        while (fill-- > 0) {
            out[len++] = f.star ? '*' : ' ';
        }
    }
    strcpy(out + len, body);
    len = (int)strlen(out);
    if (f.trailing_sign) {
        out[len++] = negative ? '-' : '+';
    } else if (f.trailing_minus) {
        out[len++] = negative ? '-' : ' ';
    }
    mb25_u_text((const uint8_t *)out, len);
}

/* The end of the list: the text up to the next field, and the new line
 * unless the list ended with ';' or ','. */
void mb25_using_end(int newline) {
    mb25_u_spec f;
    int width;
    mb25_u_next(&f, &width, 0);
    if (newline) {
        mb25_putc('\n');
    }
}
