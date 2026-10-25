# JavaScript output prints numbers the MBASIC way

**Status:** Done (GitHub issue 9)
**Test:** `tests/regression/integration/test_js_print_format.py`

## Problem

The JavaScript that `--compile-js` makes printed numbers with JavaScript
rules. `PRINT 42` gave `42`, not ` 42 `. `PRINT 1/3` gave
`0.3333333333333333`. `STR$` and `WRITE` had the same fault.

## What the compiler does now

The code generator reads the type of each expression with
`numeric_digits()` in `src/number_format.py`. The interpreter uses the same
function. The type is 0 (integer), 6 (single) or 16 (double). The compiler
writes this number into the JavaScript next to each value.

The JavaScript runtime has these parts:

* `_fmt_num` and `_fmt_print` are a port of `format_number` and
  `format_for_print`. They follow the same rounding rules. The code rounds a single
  twice (7 digits, then 6) from its shortest decimal form. The code rounds a
  double once from its exact binary value.
* `_print_list` handles one PRINT statement. It keeps the cursor column, so
  the comma zones (14 characters), `TAB` and `SPC` work across statements.
  It also works for `PRINT #n`. It wraps lines at `_width` (set by `WIDTH`,
  80 at the start) and follows the TAB and comma rules of real MBASIC. The
  rules are in [PRINT_COLUMNS.md](PRINT_COLUMNS.md).
* `_sg` rounds the result of single-precision arithmetic to binary32
  (`Math.fround`). It leaves whole numbers alone, as the interpreter does.
  The code rounds single literals and the results of `SQR`, `SIN`, `COS`,
  `TAN`, `ATN`, `LOG`, `EXP` and `RND` the same way.
* `_str` takes the digits of its argument, so `STR$(1/3#)` has 16 digits.
* `_write_format` leaves out the padding spaces around numbers.
* `_print_using` is a port of `UsingFormatter`.
  For a double, the port starts from the shortest decimal form of the value,
  as `UsingFormatter` does. The exact binary of 1D-11 is just below 1E-11, and
  the real binary has no carry there, so `##.##^^^^` shows 1.00D-11.
  A fixed field with a value of 1E16 or more prints `%`, a space and the PRINT
  form of the number (`% 1E+16`, `% 1.70141E+38` for the clamped 10^40). The
  sign, `$` and trailing sign are dropped, as on the real binary.
* `_toInt` rounds halves away from zero and raises Overflow outside
  -32768 to 32767, like the interpreter.
* Arithmetic follows the interpreter (`docs/dev/MBASIC_521_DIVERGENCES_TODO.md`,
  section 1). `_sg` (single) and `_dg` (double) turn a result that is infinite
  in its precision into `Overflow`. `_overflow` and `_divzero` print the
  message, give machine infinity with the sign of the true result, and carry
  on. When `ON ERROR` is armed they raise ERR 6 or ERR 11 instead. `_div`,
  `_pow`, `_sqr`, `_log`, `_idiv` and `_mod` raise `Division by zero` or
  `Illegal function call`. `\` and `MOD` round their operands and need 16
  bits.
* `_error` gives the error an ERR number. With `ON ERROR` in the program the
  main loop catches it, sets `ERR` and `ERL`, and jumps to the handler.
  `RESUME NEXT` goes to the line after the line that failed.
* `_val` and `_radix_word` follow `val_text` and `radix_word`. `&HFFFF` is -1
  and `HEX$(-1)` is `FFFF`.
* A comparison gives -1 or 0. AND, OR, XOR, EQV, IMP and NOT are 16-bit
  integer operators (see `docs/dev/JS_LOGICAL_OPERATORS.md`).

## Changes in the interpreter

* `STR$` uses the type of its argument (it always used single before).
* `WRITE` uses the number format of `PRINT` (it printed Python floats).
* The parser keeps the separator list in step with the expression list.
  `PRINT ,X` and `PRINT A,,B` get an empty string item. `PRINT "A" "B"`
  gets an implied `;`.
* `/` and `^` of two integers are single, so `5%/2%` is 2.5.
* The parser accepts a sign on the exponent: `2^-3` is .125 and `0^-1` is a
  division by zero. It was a syntax error.

## Test method

`fixtures/js_print_format/*.bas` run in the interpreter and in Node.js. The
two outputs must be equal byte for byte. The test compares the issue example with
real MBASIC 5.21. A random test compares `_fmt_print` with `format_for_print`
for 3000 values.

`fixtures/number_semantics/*.bas` have a `.real` file with the output of real
MBASIC 5.21. The interpreter test and the Node.js test both compare with it.
They cover overflow, domain errors, `VAL`, `&H` and `&O` constants, and
`HEX$` and `OCT$`.

## Differences that remain

Real MBASIC 5.21 and the interpreter differ in these cases. The JavaScript
output follows the interpreter.

* A double literal with 16 or more digits (`3.14159265358979#`, `1D-20`) is
  not the same as in real MBASIC. Real MBASIC reads decimal text a little
  inexactly (see `to_single` in `src/number_format.py`).
* `SQR(2#)` and the other maths functions keep double precision here. Real
  MBASIC gives a single.
* Doubles that come from MBF arithmetic can differ in the last digit.
* `1D300^2` and `EXP(1000#)` give a double machine infinity here. Real MBASIC
  gives a single one. The MBF range is not emulated (see
  MBASIC_521_DIVERGENCES_TODO.md, section 10).
* A single value below about 2.9E-39 prints as a binary32 denormal
  (`1.4013E-45`). Real MBASIC reads such a value as 0. The interpreter
  prints the same text as the JavaScript.
* `^` with a double base and a fractional exponent keeps double precision
  (`X#^.5`). Real MBASIC gives a single.
* A fatal error stops the JavaScript with `<message> in <line>`, for example
  `Overflow in 20`, as real MBASIC does. The JavaScript starts a new line
  first when the cursor is not in column 0, as real MBASIC does.
* `LPRINT` shows the number format only. `PRINT #n, USING` works.
* A single-precision whole number above 2^24 is not rounded, because the
  interpreter keeps Python integers exact.
