# MBASIC Compiler - Variable Types and Naming

## Overview

In MBASIC, variables with the same base name but different type suffixes are **separate variables**. This document explains how the BASIC-to-C and BASIC-to-JavaScript compilers handle variable types and naming.

## BASIC Type Suffixes

| Suffix | Type | Example | C Type | JS Coercion |
|--------|------|---------|--------|-------------|
| `%` | INTEGER | `FOO%` | `int` | `_toInt()` |
| `!` | SINGLE | `FOO!` | `float` | none (default) |
| `#` | DOUBLE | `FOO#` | `double` | none |
| `$` | STRING | `FOO$` | string pool | `_str` suffix |

## Same Name, Different Types = Different Variables

In BASIC, `FOO`, `FOO%`, `FOO!`, `FOO#`, and `FOO$` can ALL exist in the same program as separate variables:

```basic
10 FOO = 3.14159      ' SINGLE precision (default)
20 FOO% = 42          ' INTEGER - different variable!
30 FOO# = 2.718281828 ' DOUBLE - different variable!
40 FOO$ = "hello"     ' STRING - different variable!
50 PRINT FOO; FOO%; FOO#; FOO$
```

### Generated C Code

The C backend adds type suffixes to variable names to distinguish them:

```c
float foo;        // FOO (SINGLE - default, no suffix)
int foo_int;      // FOO% (INTEGER)
double foo_dbl;   // FOO# (DOUBLE)
// FOO$ uses string pool ID, not a C variable
```

### Generated JavaScript Code

```javascript
let foo = 0;       // FOO (SINGLE - default)
let foo_int = 0;   // FOO% (INTEGER)
let foo_dbl = 0;   // FOO# (DOUBLE)
let foo_str = "";  // FOO$ (STRING)
```

## Variables Without Explicit Type Suffix

When a variable has no explicit type suffix, its type is determined by:

1. **DEFINT/DEFSNG/DEFDBL/DEFSTR statements** - Define default type by first letter
2. **Default** - SINGLE precision (`!`) if no DEF statement applies

### Example with DEF Statements

```basic
10 DEFINT I-N       ' Variables starting with I-N are INTEGER
20 DEFDBL D         ' Variables starting with D are DOUBLE
30 I = 100          ' INTEGER (from DEFINT)
40 X = 3.14         ' SINGLE (default)
50 D = 2.71828      ' DOUBLE (from DEFDBL)
```

Generated symbol table keys:
- `I` → `I%` (INTEGER, from DEFINT)
- `X` → `X!` (SINGLE, default)
- `D` → `D#` (DOUBLE, from DEFDBL)

### Internal Representation

The compiler's symbol table uses the full name with suffix as the key:

| BASIC Variable | Symbol Table Key | Generated Name (C) | Generated Name (JS) |
|----------------|------------------|--------------------|--------------------|
| `FOO` (SINGLE) | `FOO!` | `foo` | `foo` |
| `FOO%` | `FOO%` | `foo_int` | `foo_int` |
| `FOO#` | `FOO#` | `foo_dbl` | `foo_dbl` |
| `FOO$` | `FOO$` | (string pool) | `foo_str` |
| `FOO(1)` (array) | `FOO!` | `foo_arr` (a string array: `STR_FOO__`) | (not covered here) |

## Type Coercion at Assignment

Both backends apply type coercion when assigning values to typed variables:

### INTEGER Variables (`%`)

```basic
I% = 3.7    ' Truncates to 3 (toward zero)
I% = -3.7   ' Truncates to -3 (toward zero)
I% = 32768  ' Clamps to 32767 (max INTEGER)
I% = -32769 ' Clamps to -32768 (min INTEGER)
```

- **C backend**: `mb25_cint()` rounds to the nearest integer, halves away from zero, as the interpreter does (`3.7` gives 4). A value outside 16 bits wraps and does not clamp.
- **JS backend**: Uses `_toInt()` function (truncate toward zero, clamp to -32768..32767)

### SINGLE Variables (`!`)

```basic
X! = 1/3    ' Single precision: 0.3333333
```

- **C backend**: Uses C `float` type (32-bit)
- **JS backend**: Uses `Math.fround()` (ES6 single precision)

### DOUBLE Variables (`#`)

```basic
D# = 1/3    ' Double precision: 0.333333333333333
```

- **C backend**: Uses C `double` type. With uc80 this is 32 bits, the same as `float`, so a double keeps about 7 digits ([C_BACKEND.md](C_BACKEND.md))
- **JS backend**: Native JS Number (already 64-bit double)

## Semantic Equivalence

Both the C and JavaScript backends produce semantically equivalent output for the same BASIC program. The same numeric values will be printed (within floating-point precision limits).

This allows programs to be compiled to either target and produce identical results, which is useful for:
- Testing (compare C output vs JS output)
- Cross-platform deployment (CP/M vs browser)
- Debugging (JS is easier to debug than compiled C)

## Implementation Details

### Symbol Table

The semantic analyzer (`src/semantic_analyzer.py`) stores variables with their full key:
- `_get_var_key(var_node)` returns the uppercase name with suffix (e.g., `'FOO%'`, `'FOO$'`)
- Variables without explicit suffix get the default suffix based on DEF statements or `'!'` for SINGLE

### C Backend

`src/codegen_backend.py`:
- `_mangle_variable_name()` converts BASIC names to C identifiers
- Adds `_int` suffix for INTEGER, `_dbl` suffix for DOUBLE
- String variables use the string pool system (not C variables)

### JavaScript Backend

`src/codegen_js_backend.py`:
- `_mangle_var_name()` converts BASIC names to JS identifiers
- Adds `_int`, `_dbl`, `_str` suffixes as needed
- `_apply_type_coercion()` wraps assignments with type conversion functions
