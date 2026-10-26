# The C backend

`mbasic prog.bas --compile-c out` compiles a BASIC program to C and builds a CP/M
`.com` file. The compiler is `src/codegen_backend.py`. The C runtime is in
`runtime/strings/` (`mb25_string.c` and `mb25_string.h`). The default toolchain is
uc80 (see [TOOLCHAIN_POLICY.md](TOOLCHAIN_POLICY.md)). This page tells what the
backend does and where it differs from the interpreter.

## A construct that the compiler cannot compile

The backend never writes C that behaves differently from the interpreter without
a message. There are two kinds of message:

- An error stops the compile. `--compile-c` prints each error with its line number,
  writes no C file, and exits with status 1.
- A warning gives advice. `--compile-c` prints each warning and continues.
  `WIDTH`, `CLEAR` with memory sizes, and double precision on uc80 give warnings.

The backend gives an error for a statement or function that it does not have. It
also gives an error for a string where a number is needed (`Type mismatch`).
Before this change the backend filled `self.warnings` and nobody showed it. It wrote
an unsupported construct to the C file as a comment.

Examples of errors: `PRINT USING`, `INKEY$`, `INPUT$`, `TRON`, `RUN`, `FILES`,
`NAME`, `CHAIN` options, string-valued `DEF FN`, and a FOR loop without a NEXT below
it. The code for `PRINT USING` printed the text `%.*f` for most formats, because the
uc80 `printf` has no `*` width.

## Numbers

`PRINT` writes every number through the runtime. The rules are the rules of
`src/number_format.py` (`format_for_print`):

- A number that is not negative has a space before it. Every number has a space after it.
- There is no leading zero: `.333333`, not `0.333333`.
- A single-precision value shows 6 digits. The rounding has the same two steps as
  the interpreter (7 digits, then 6).
- A value that is too big or too small for plain notation uses `E` notation:
  `1E+06`, `1.5E-09`.
- `STR$` gives the same text with a space before a number that is not negative and no
  space after it. `WRITE` gives the digits alone.

The number of digits comes from the type of the expression, not from the value.
The backend asks `number_format.numeric_digits()`, the function that the interpreter uses.

`/` always gives a floating-point result: `5/2` is 2.5. `\` and `MOD` round their
operands to integers. A rounded operand of `\`, `MOD`, `AND`, `OR`, `XOR`, `EQV`,
`IMP` or `NOT` outside -32768..32767 stops the program with `Overflow`, and `\` or
`MOD` by 0 stops it with `Division by zero`. A comparison gives -1 for true.
`AND`, `OR`, `XOR`, `EQV`, `IMP` and `NOT` work bit by bit on 16-bit integers.
`^` with a whole exponent uses
repeated multiplication, because the uc80 `pow()` is not exact (`3^8` gave 6560.98).

The formatter builds the exact decimal value of the float in a digit array and then
rounds it. It needs no `printf` and no 64-bit integers. The code is `mb25_fmt_num()`
in `mb25_string.c`. A test compared it with `format_number()` for 3000 random
single-precision values, and all of them agreed.

### Code size

The `.com` size of the program in issue 29 (`PRINT "HI";2+3` and the next lines):

- Before: 22144 bytes, with the `--printf float` converter linked in.
- After: 23808 bytes. The number formatter and the output routines add about
  4 KB. The build now passes only the `--printf` and `--scanf` converters that the
  generated C uses, which saves about 2.3 KB.

A program that uses strings also links string functions that were not reachable
before (`CHR$`, `HEX$`, `INSTR` and others), so these programs grow more.

## Output

`PRINT` goes through `mb25_print_*` in the runtime, which tracks the cursor column.
So the runtime does the comma zones of 14 columns, `TAB`, `SPC` and the 80-column
wrap. After `INPUT` the column is 0. `PRINT #n` and `WRITE #n` send the same text to
a file, with CR LF at the end of each line. `LPRINT` writes to the console.

## Arrays

A numeric array is a flat C array. A string array is a run of consecutive
descriptors in the string pool, so element n has the ID of the array plus n.

- `DIM` does nothing when the program runs. The sizes must be constants (the
  semantic analyzer checks this). The program start sets all storage to zero.
- An array that has no `DIM` has 11 elements for each subscript.
- `OPTION BASE 1` works. The program rounds every subscript to an integer and checks
  it. A subscript above the array stops the program with `Subscript out of range in 40`.
  A negative subscript gives `Illegal function call in 40`.
- A string array element works wherever a string variable works: assignment,
  expressions, `PRINT`, `INPUT`, `LINE INPUT`, `READ`, `SWAP`, `MID$` assignment,
  `LSET` and `RSET`.
- `ERASE` deletes the array, as on MBASIC 5.21. The next use makes the array again
  with the bounds 0 to 10 (1 to 10 with `OPTION BASE 1`), and all elements are 0
  or the empty string. A `DIM` after `ERASE` can give the array any size and any
  number of subscripts. An array that an `ERASE` names has its shape as run-time
  state (`ea_<name>_n`, `_rk` and `_st` in the C code, handled by `mb25_ea_*` in
  `runtime/strings/mb25_string.c`). The storage has the size of the largest shape
  that a `DIM` or a use can give, so a loop of `DIM` and `ERASE` does not use
  more memory. `ERASE` of an array that does not exist is `Illegal function
  call`, `DIM` of an array that exists is `Duplicate Definition`, and a use with
  the wrong number of subscripts is `Subscript out of range`. A second `DIM` of
  an array that no `ERASE` names is a compile error.
- A variable and an array can have the same name (`A` and `A(1)`). The C names are
  different: arrays end in `_arr`, and a string array has its own `STR_` macro.
- The limit is 16383 string descriptors in all (the IDs have 14 bits).

## Loops and control flow

`FOR` and `NEXT` compile to labels and `goto`. A `NEXT` pairs with the nearest `FOR`
above it in the text, as in the JavaScript backend. `NEXT J,I` closes two loops.
A negative `STEP` counts down. Some programs jump into the middle of a loop, and
their `NEXT` belongs to a `FOR` further down the text. These programs give an error.

`IF ... THEN statement ELSE line` works in all mixed forms. `ON GOSUB`, and `GOSUB`
inside an `IF`, have return labels. `RETURN` without `GOSUB` stops the program.

## Differences from the interpreter

These differences are known. They are not fixed.

- **Double precision is 32 bits on uc80.** A `#` variable keeps about 7 digits, and
  the output uses `D` notation with 7 digits. The compiler gives a warning for a
  program that uses double precision.
- **Integer arithmetic wraps.** `I%*J%` wraps at 16 bits. The interpreter turns an
  integer result that does not fit into a single-precision number. The compiler
  works out a constant such as `200*200` itself and writes 40000. The compiler
  gives a warning when a program does `+`, `-` or `*` on integers.
- **Some float results are not exact.** uc80 does not round a multiplication like
  IEEE binary32. `PRINT 1/3*3=1` gives 0 (false), and the interpreter gives -1.
  `2/3*3=2` and `1/10*10=1` have the same fault. The printed value is correct
  because the formatter rounds to 7 digits, but a test for equality on a computed
  float can go wrong. Compare with a small tolerance in a program that is to be
  compiled. See `UC80_BUGS_TODO.md`.
- **Error handling is not supported.** `ON ERROR GOTO line`, `RESUME`, `ERROR`, `ERR`
  and `ERL` are compile errors, because the compiled program has no error handler.
  `ON ERROR GOTO 0` is accepted. A run-time error ends the program.
- **Run-time errors** (`Subscript out of range`, `Illegal function call`,
  `String too long`, `Out of DATA`, `RETURN without GOSUB`, `File not found`,
  `File not open`) print a new line when the cursor is not in column 1, then
  `message in LINE`, as MBASIC 5.21 does (no `?` in front). The C program keeps the line number in
  `mb25_line` (one store at the start of each line). Not all checks of MBASIC
  exist: `SQR(-8)` gives 0, `LOG(0)` gives a large negative number, and
  `MID$(x,0)` and `LEFT$(x,-1)` give no error, where MBASIC gives
  `Illegal function call`. A string longer than 255 characters stops the program
  with `String too long`.
- **A floating-point result can differ in the last digit.** `basic/dev/bas_tests/asciiart.bas`
  differs in one character out of 2000.
- **Most arithmetic has no run-time errors.** Division by zero gives the largest
  number (`1.70141E+38`) without the `Division by zero` message that MBASIC prints
  before it carries on. `ON ERROR` does not see it. The operators `\`, `MOD`, `AND`,
  `OR`, `XOR`, `EQV`, `IMP` and `NOT` are an exception: they stop with `Overflow` or
  `Division by zero` (the program ends, as for any run-time error). `+`, `-` and `*`
  on integers wrap at 16 bits and do not give `Overflow`. The compiler warns when
  it can happen. A float product that is too large also gives `1.70141E+38` and not `Overflow`.
- **`-32768 \ -1` gives -32768.** MBASIC gives 32768, because the quotient does
  not fit in an integer. The result of `\` is an integer in the compiled program, so
  the quotient wraps. `-32768 MOD -1` is 0 in both.
- **The float range is that of uc80**: about 1.2E-38 to 1.7E38. A number in the program
  outside this range is wrong in the compiled program (`3E38` prints as `2.59085E-39`,
  `-1E-38` as `0`), and the compiler warns about such a number. `2^126` prints with one
  digit less than MBASIC. `INT` and `FIX` work on the whole float range.
- **INPUT** reads a whole line. It does not give `?Redo from start`, and with several
  variables it does not ask again for missing values. At the end of the input the
  program ends.
- **Bad data** in `READ` and `VAL` gives 0 and not an error.
- **A tab character** in the output is not expanded by the CP/M console.
- **Random-access files** (`FIELD`, `GET`, `PUT`) do not build with uc80.
- `STOP` prints `Break in <line>` and ends the program. There is no `CONT`.

## Tests

`tests/regression/integration/test_c_backend.py` compiles programs with uc80, runs
them under cpmemu, and compares the output with `python3 mbasic prog.bas --ui cli`.
The tests skip when uc80, um80, ul80 or cpmemu is missing. The test finds cpmemu
through the environment variable `MBASIC_CPMEMU` (a path to the binary) or on `PATH`.
It finds the uc80 libraries in the way that `--compile-c` does (`MBASIC_UC80_LIB`, or
the uc80 package).

To check the formatter without a Z80 toolchain, compile `mb25_string.c` with a host
compiler. `mb25_fmt_num()` has no other dependency.

## Faults in uc80

The backend works around several faults in uc80. See
[UC80_BUGS_TODO.md](UC80_BUGS_TODO.md), the section about the C backend.
