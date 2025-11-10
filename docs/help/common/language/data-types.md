---
description: BASIC-80 data types and type suffixes
keywords:
- data types
- integer
- single
- double
- string
- type suffix
- variables
title: Data Types
type: reference
---

# Data Types

BASIC-80 supports four data types.

## Type Suffixes

Variables are typed by their suffix character:

| Suffix | Type | Range | Precision |
|--------|------|-------|-----------|
| **%** | INTEGER | -32768 to 32767 | Whole numbers |
| **!** | SINGLE | ±2.938736×10^-39 to ±1.701412×10^38 | ~7 significant digits |
| **#** | DOUBLE | ±2.938736×10^-308 to ±1.797693×10^308 | approximately 16 digits |
| **$** | STRING | 0 to 255 characters | Text |

## INTEGER (%)

Whole numbers from -32768 to 32767.

**Examples:**
```basic
COUNT% = 10
INDEX% = -5
SIZE% = 32767
```

**Uses:**
- Loop counters
- Array subscripts
- Counting operations
- Fast arithmetic (no decimal calculations)

## SINGLE Precision (!)

Floating-point numbers with ~7 significant digits of precision.

**Examples:**
```basic
PRICE! = 19.99
RATE! = 0.05
VALUE! = 3.14159
```

**Range:** Approximately 2.938736×10^-39 to 1.701412×10^38

**Uses:**
- Prices and money (with rounding)
- Measurements
- General calculations

**Default type:** Variables without a suffix are SINGLE by default.

## DOUBLE Precision (#)

Floating-point numbers with about 16 decimal digits of precision.

**Examples:**
```basic
PI# = 3.141592653589793
BIGNUM# = 1.23456789012345D+100
PRECISE# = 0.123456789012345
```

**Range:** Approximately 2.938736×10^-308 to 1.797693×10^308 (much larger range than single-precision, with greater precision)

**Uses:**
- Scientific calculations
- High-precision mathematics
- Astronomy, physics calculations

**Exponent Notation:**
- D notation (e.g., 1.5D+10) forces double-precision, required for exponents beyond single-precision range
- E notation (e.g., 1.5E+10) uses single-precision by default, converts to double if assigned to # variable
- For values within single-precision range, D and E are interchangeable when assigned to # variables

## STRING ($)

Text data, up to 255 characters per string.

**Examples:**
```basic
NAME$ = "Alice"
MESSAGE$ = "Hello, World!"
EMPTY$ = ""
```

**String Operations:**
- Concatenation: `A$ + B$`
- Comparison: `A$ = B$`, `A$ < B$`
- Functions: `LEFT$`, `RIGHT$`, `MID$`, `LEN`, `INSTR`

## Type Conversion

### Automatic Conversion

BASIC automatically converts between numeric types when needed:

```basic
10 A% = 5         ' INTEGER
20 B! = 10.5      ' SINGLE
30 C = A% + B!    ' Result is SINGLE (10.5 + 5 = 15.5)
```

### Explicit Conversion Functions

| Function | Converts To | Description |
|----------|-------------|-------------|
| [CINT](functions/cint.md) | INTEGER | Rounds to nearest integer |
| [CSNG](functions/csng.md) | SINGLE | Converts to single precision |
| [CDBL](functions/cdbl.md) | DOUBLE | Converts to double precision |
| [STR$](functions/str_dollar.md) | STRING | Converts number to string |
| [VAL](functions/val.md) | Number | Converts string to number |

**Example:**
```basic
10 X! = 3.7
20 I% = CINT(X!)      ' I% = 4 (rounded)
30 S$ = STR$(X!)      ' S$ = " 3.7"
40 Y = VAL("123.45")  ' Y = 123.45
```

## Default Types

You can set default types for variable names using DEF statements:

```basic
10 DEFINT A-Z        ' All variables are INTEGER by default
20 DEFSNG A-C        ' Variables A-C are SINGLE
30 DEFDBL D-F        ' Variables D-F are DOUBLE
40 DEFSTR S          ' Variables starting with S are STRING
```

See: [DEFINT/SNG/DBL/STR](statements/defint-sng-dbl-str.md)

## Type Coercion Rules

When mixing types in expressions:

1. **INTEGER + INTEGER** = INTEGER
2. **INTEGER + SINGLE** = SINGLE
3. **INTEGER + DOUBLE** = DOUBLE
4. **SINGLE + DOUBLE** = DOUBLE

The result takes the "wider" type (DOUBLE > SINGLE > INTEGER).

## Overflow and Underflow

**INTEGER Overflow:**
```basic
10 X% = 32767
20 X% = X% + 1     ' ERROR: Overflow (Error 6 - OV)
```

**Solution:** Use SINGLE or DOUBLE for larger numbers.

**Floating-Point Overflow:**
```basic
10 X# = 1D+308
20 X# = X# * 10    ' ERROR: Overflow (Error 6 - OV)
```

See [Error Codes](appendices/error-codes.md) for more information on error 6 (OV - Overflow).

**Underflow** (too small):
```basic
10 X# = 1D-308
20 X# = X# / 10    ' Becomes 0 (underflow - no error)
```

## String Length Limit

Strings are limited to 255 characters:

```basic
10 S$ = STRING$(256, "X")   ' ERROR: String too long
```

## Memory Usage

| Type | Bytes | Memory Efficiency |
|------|-------|-------------------|
| INTEGER | 2 | Most efficient |
| SINGLE | 4 | Moderate |
| DOUBLE | 8 | Least efficient |
| STRING | 3 + length | Variable |

**Tip:** Use INTEGER when possible for faster arithmetic and less memory.

## See Also

- [Variables](../getting-started.md#variables) - Using variables
- [Operators](operators.md) - Arithmetic and logical operators
- [Type Conversion Functions](functions/index.md) - CINT, CSNG, CDBL, STR$, VAL
- [DEFINT/SNG/DBL/STR](statements/defint-sng-dbl-str.md) - Set default types
