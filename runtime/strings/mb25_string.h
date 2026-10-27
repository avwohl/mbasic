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
#include <stdio.h>

/* Configuration - set at compile time based on BASIC program analysis */
#ifndef MB25_NUM_STRINGS
#define MB25_NUM_STRINGS      100    /* Default number of string descriptors */
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

/* Static array of string descriptors - size known at compile time.
 *
 * Declared UNSIZED on purpose.  Repeating the size here (`[MB25_NUM_STRINGS]`)
 * beside the sized definition in mb25_string.c crashes uc80:
 *     uc80: internal error: '<' not supported between instances of 'Token' and 'Token'
 * (uc80/codegen.py:2769, _merge_array_size).  An unsized extern is valid C, is
 * accepted by both compilers, and sidesteps it.  See docs/dev/TOOLCHAIN_POLICY.md.
 */
extern mb25_string_t mb25_strings[];

/* Global state for string management */
typedef struct mb25_globals_R {
    uint16_t pool_size;       /* Total size of string pool */
    uint16_t allocator;       /* Current allocation position */
    uint8_t  *pool;          /* Pointer to string pool (provided by caller) */

    /* Statistics */
    uint32_t total_allocs;    /* Total allocations */
    uint32_t total_gcs;       /* Total garbage collections */
    uint16_t max_used;        /* Maximum pool usage */
} mb25_globals_t;

/* Global instance */
extern mb25_globals_t mb25_global;

/* ===== Initialization and Cleanup ===== */

/* Initialize the string system with pool at given address and size.
 * Pool memory is provided by caller (typically from __BSS_tail to SP-stack_reserve).
 * No malloc/heap required. */
mb25_error_t mb25_init(uint8_t *pool, uint16_t pool_size);

/* Reset the string system (clear all strings, reset allocator) */
void mb25_reset(void);

/* ===== Core Allocation Functions ===== */

/* Allocate a constant string (no pool space used) */
mb25_error_t mb25_string_alloc_const(uint16_t str_id, const char *cstr);

/* Allocate a pool string with given size */
mb25_error_t mb25_string_alloc(uint16_t str_id, uint16_t size);

/* Allocate and initialize a pool string from C string */
mb25_error_t mb25_string_alloc_init(uint16_t str_id, const char *init_str);

/* Free a string (mark descriptor as unused) */
void mb25_string_free(uint16_t str_id);

/* ===== String Operations ===== */

/* Copy string from source to destination */
mb25_error_t mb25_string_copy(uint16_t dest_id, uint16_t src_id);

/* Assign string value (may reuse space if writeable) */
mb25_error_t mb25_string_assign(uint16_t dest_id, const uint8_t *data, uint8_t len);

/* Set string from fixed-width buffer (trims trailing spaces) */
mb25_error_t mb25_string_set_from_buf(uint16_t dest_id, const uint8_t *buf, uint8_t width);

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

/* Convert string to C string (null-terminated) - caller must free.
 * Only available on host builds (uses malloc). Not available on CP/M. */
#ifndef __Z88DK
char *mb25_to_c_string(uint16_t str_id);
#endif

/* Create string from C string */
mb25_error_t mb25_from_c_string(uint16_t str_id, const char *c_str);

/* Clear string (set to empty) */
void mb25_string_clear(uint16_t str_id);

/* Duplicate string to new ID */
mb25_error_t mb25_string_dup(uint16_t dest_id, uint16_t src_id);

/* Print string directly using putchar (no malloc, efficient) */
void mb25_print_string(uint16_t str_id);

/* Print string to file using fputc (no malloc, efficient) */
void mb25_fprint_string(FILE *fp, uint16_t str_id);

/* String functions: build the result in descriptor id and return id */
uint16_t mb25_chr(uint16_t id, int code);
uint16_t mb25_string_of(uint16_t id, int n, int ch);          /* SPACE$, STRING$ */
uint16_t mb25_string_of_first(uint16_t id, int n, uint16_t src);
uint16_t mb25_radix(uint16_t id, int v, int base);            /* HEX$, OCT$ */
int mb25_asc(uint16_t id);
double mb25_val(uint16_t id);
double mb25_val_cstr(const char *s);  /* VAL of a C string; READ of a text DATA item */
double mb25_atof(const char *s);      /* library atof fails on uc80 */
int mb25_instr(int start, uint16_t a, uint16_t b);

/* CINT rounding, the subscript check and SWAP for the compiled program */
int mb25_cint(double v);
int mb25_int16(double v);             /* CINT that stops with Overflow out of range */
int mb25_idiv(int a, int b);          /* \ with Division by zero */
int mb25_imod(int a, int b);          /* MOD with Division by zero */
double mb25_idivd(int a, int b);      /* \ whose quotient may be 32768 */
void mb25_warn(const char *msg);      /* Division by zero / Overflow, then go on */
double mb25_fdiv(double a, double b); /* / */
double mb25_fmul(double a, double b); /* * on floats */
double mb25_fadd(double a, double b); /* + on floats */
double mb25_fsub(double a, double b); /* - on floats */
int mb25_iadd(int a, int b);          /* + of two integers, Overflow if it does not fit */
int mb25_isub(int a, int b);          /* - of two integers, Overflow if it does not fit */
int mb25_chk32(long v);                /* a 32-bit result of integer + - *, Overflow if it does not fit */
double mb25_exp(double v);            /* EXP */
double mb25_log(double v);            /* LOG */
int mb25_byte(int v);                 /* 0..255 or Illegal function call */
int mb25_start(int v);                /* 1..255 or Illegal function call */
int mb25_word(double v);              /* HEX$ and OCT$ argument */
double mb25_int(double v);               /* INT */
double mb25_fix(double v);               /* FIX */
double mb25_sqr(double v);               /* SQR */
double mb25_pow(double x, double y);   /* x ^ y */
int mb25_subscript(int i, int n, int base);
/* arrays that ERASE can delete: see mb25_string.c */
int mb25_ea_first(char *st, int *rk, int *n, int k, int dflt, int i, int base);
int mb25_ea_next(int acc, int *n, int j, int i, int base);
void mb25_ea_dim(char *st, int *rk, int k);
int mb25_ea_erase(char *st, int *rk, int *n);
int mb25_ea_clear(char *st, int *rk, int *n);
extern unsigned int mb25_line;                /* the BASIC line that is running */
void mb25_fail(const char *msg);     /* print ?msg in LINE and stop */
int mb25_eof(FILE *fp);                /* EOF(n) */
int mb25_input_eof(void);              /* end of keyboard input: ends the program */
void mb25_chomp(char *s);              /* strip the line end after fgets */
void mb25_string_swap(uint16_t a, uint16_t b);

/* ===== PRINT output =====
 *
 * Every PRINT item goes through these, so the runtime knows the cursor column
 * (for comma zones, TAB and the 80-column wrap) and formats numbers the way
 * MBASIC does (src/number_format.py).  mb25_set_out(fp) sends the output to a
 * PRINT# file; mb25_set_out(NULL) goes back to the console.  kind is 0 for a
 * single-precision value and 1 for a double. */
void mb25_set_out(FILE *fp);
void mb25_set_col(int col);          /* the console column, e.g. 0 after INPUT */
int mb25_pos(void);                  /* POS(x): the console column, 1-based */
void mb25_putc(int c);
void mb25_print_cstr(const char *s);
void mb25_print_nl(void);
void mb25_print_zone(void);          /* PRINT ',' */
void mb25_print_tab(int n);
void mb25_print_spc(int n);
void mb25_print_int(int v);          /* " 7 " */
void mb25_print_num(double v, int kind);
void mb25_write_int(int v);          /* WRITE: no padding spaces */
void mb25_write_num(double v, int kind);

/* Number to text, as PRINT shows it but without the padding spaces.  buf
 * needs 40 bytes; the return value is the length. */
int mb25_fmt_num(char *buf, double v, int kind);
int mb25_fmt_int(char *buf, int v);

/* STR$: the number as a string, with a leading space unless negative. */
mb25_error_t mb25_str_num(uint16_t dest_id, double v, int kind);
mb25_error_t mb25_str_int(uint16_t dest_id, int v);

/* Get C string (null-terminated) using temp pool - NO MALLOC! */
char *mb25_get_c_string_temp(uint16_t src_id, uint16_t temp_id);

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