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

A built-in with the wrong number of arguments (`ABS(1,2)`) and `WIDTH n, device`
are errors too. The interpreter gives Syntax error for them when the line runs; the C
backend has no run-time errors, so it stops at compile time.

The backend gives an error for a statement or function that it does not have. It
also gives an error for a string where a number is needed (`Type mismatch`).
The error is at compile time on purpose; the JavaScript backend raises it at
run time (`docs/dev/JS_TYPE_MISMATCH.md`).
Before this change the backend filled `self.warnings` and nobody showed it. It wrote
an unsupported construct to the C file as a comment.

Examples of errors: `INKEY$`, `INPUT$`, `TRON`, `RUN`, `FILES`,
`NAME`, `CHAIN` options, string-valued `DEF FN`, and a FOR loop without a NEXT below
it. `PRINT USING` was an error too until 2026-10-27 (the code for it printed the text
`%.*f`, because the uc80 `printf` has no `*` width); see [PRINT USING](#print-using).

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
The mode of `OPEN` must be a string literal. The compiler stops with `Unknown
file mode` for `OPEN M$,#1,F$`, which the interpreter and the JavaScript
compiler accept.

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
  an array that no `ERASE` names is a compile error. A `DIM` after `ERASE` must have
  constant sizes (a size that depends on a variable is a compile error, as for
  all `DIM` in this backend).
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
- **Integer arithmetic wraps in some places.** `+`, `-` and `*` of two integers give
  a single-precision number when the result does not fit 16 bits, as in MBASIC, in
  these places: `PRINT`, `STR$`, a store into a single or double variable, an operand
  of `/` and `^`, a comparison, and an operand of `\`, `MOD`, `AND` and the like (where
  `Overflow` follows). A store into an INTEGER variable gives `Overflow` (`A%=A%+1`
  at 32767). In other places (a subscript, an argument of a function, a `FOR` limit)
  the integer result wraps at 16 bits. The compiler works out a constant such as
  `200*200` itself and writes 40000. The compiler gives a warning when a program does
  `+`, `-` or `*` on integers. A store into an INTEGER variable works in 32 bits when
  the expression is small enough (fast), and in double otherwise. The `NEXT` of a loop
  with an INTEGER counter gives `Overflow` when it steps past 32767 or -32768.
- **Some float results are not exact.** uc80 does not round a multiplication like
  IEEE binary32. `PRINT 1/3*3=1` gives 0 (false), and the interpreter gives -1.
  `2/3*3=2` and `1/10*10=1` have the same fault. The printed value is correct
  because the formatter rounds to 7 digits, but a test for equality on a computed
  float can go wrong. Compare with a small tolerance in a program that is to be
  compiled. See `UC80_BUGS_TODO.md`.
- **Error handling** works as in MBASIC 5.21: see [ON ERROR GOTO](#on-error-goto).
- **Run-time errors** (`Subscript out of range`, `Illegal function call`,
  `String too long`, `Out of DATA`, `RETURN without GOSUB`, `File not found`,
  `Bad file number`) print a new line when the cursor is not in column 1, then
  `message in LINE`, as MBASIC 5.21 does (no `?` in front). The C program keeps the line number in
  `mb25_line` (one store at the start of each line). `SQR` of a negative number, `LOG` of
  zero or less, a negative base with a fraction as exponent, `ASC("")`, a count or code outside
  0..255 in `LEFT$`, `RIGHT$`, `MID$`, `CHR$`, `SPACE$` and `STRING$`, and a `MID$` or
  `INSTR` start outside 1..255 give `Illegal function call`. `CINT`, a store into an
  INTEGER variable, a subscript, and the argument of `HEX$` and `OCT$` give `Overflow`
  outside the range. A string longer than 255 characters stops the program
  with `String too long`.
- **A floating-point result can differ in the last digit.** `basic/dev/bas_tests/asciiart.bas`
  differs in one character out of 2000.
- **Float errors that MBASIC reports and goes on from.** A float division by zero,
  `0^-1`, a float sum, difference, product or power that is too large, `EXP` of
  87.34 or more, and a constant above the largest float print `Division by zero` or
  `Overflow` on a line of their own and go on with the largest float (`1.70141E+38`),
  as MBASIC does. (A constant above the range gives no message, as in MBASIC.)
  `EXP` of a number below -88.72 is 0, and `A^B` gives `Overflow` from `2^126`.
  With `ON ERROR GOTO` set, these errors go to the handler, as in MBASIC. The
  operators `\`, `MOD`, `AND`, `OR`, `XOR`, `EQV`, `IMP` and `NOT` give `Overflow` or
  `Division by zero` as a run-time error (the handler, or the end of the program).
- **Not done: `DIM` with a negative size or a second `DIM`.**
  The compiler refuses a `DIM` with a constant negative
  size or a second `DIM` of the same array, with a message at compile time (MBASIC
  gives `Illegal function call` or `Duplicate Definition` at run time).
- **Not done: `A^127`.** MBASIC prints only `Overflow`. The C backend prints the
  largest float after `Overflow`.
- **`\` and the minus sign on an integer give a float when they can give 32768.**
  `-32768 \ -1` and `-A%` with `A% = -32768` are 32768 (also in `STR$`), as in MBASIC, because the
  compiler types such an expression as single precision. A `\` with a constant divisor
  other than -1 stays an integer. A store of 32768 into an INTEGER variable is `Overflow`.
  `-32768 MOD -1` is 0 in both.
- **The float range is that of uc80**: about 1.2E-38 to 1.7E38. A number in the program
  below this range is wrong in the compiled program (`1E-38` prints as `0`; a number
  above the range is the largest float, as in MBASIC), and the compiler warns about such a number. `2^126` prints with one
  digit less than MBASIC. `INT` and `FIX` work on the whole float range.
- **INPUT** reads a whole line. It does not give `?Redo from start`, and with several
  variables it does not ask again for missing values. At the end of the input the
  program ends.
- **Bad data** in `READ` is an error, as in MBASIC. Some items are bad for a
  numeric variable: a quoted item, and text that is not a number. `READ` stores the
  number that the text starts with. Then it gives `Syntax error` in the line of the
  `DATA`. `&O8` is a `Syntax error` in the
  line of the `READ`. A number too large is `Overflow`. A quoted item with text after
  it (`"a"b`) is a `Syntax error` for a string too. The next `READ` starts again at
  the first item of the statement that failed. The compiler finds these items when it
  compiles (`_data_item_flag`). `VAL` of bad text gives 0, as in MBASIC.
- **The program must fit in memory.** The build stops with an error when the code,
  the data and the stack reserve go above FD00h. A larger program overwrites CP/M
  when it starts.
- **A tab character** in the output is not expanded by the CP/M console.
- **Random-access files** (`FIELD`, `GET`, `PUT`) do not build with uc80.
- `STOP` prints `Break in <line>` and ends the program. There is no `CONT`.

## ON ERROR GOTO

Every run-time error goes through `mb25_fail(code)` in the runtime, with the
error code of MBASIC (`src/error_codes.py`). The runtime has one table of the
messages. A code without a message prints `Unprintable error`. `Division by zero`
and `Overflow` in a float expression go through `mb25_warn(code)`, which prints the
message and goes on, or calls `mb25_fail` when `ON ERROR GOTO` is set.

When `ON ERROR GOTO n` is set and the handler is not running, `mb25_fail` sets `ERR`,
`ERL` and the number of the statement, and calls `longjmp`. `main()` calls `setjmp`
once, before the first line, and goes to the line of the handler. Because of the
`longjmp`, the variables, arrays, GOSUB stack and file tables of `main()` are
`static` in a program with `ON ERROR GOTO n`.

`RESUME` and `RESUME NEXT` must go back to a statement. When a program has one of
them, each statement gets a label `p_N` before it and stores `N` in `mb25_stmt`.
`RESUME` goes to `p_N` of the statement with the error, and `RESUME NEXT` goes to
`p_(N+1)`, the label after it. The cost is one store and one `switch` case for each
statement. A program with only `RESUME n` has no labels.

The rules are those of MBASIC 5.21 (measured, see
`tests/regression/integration/test_c_backend_on_error_using.py`):

- `RESUME`, `RESUME NEXT` and `RESUME n` set `ERR` to 0 and keep `ERL`. Until the next
  line starts, an error is reported in `ERL`.
- After an error in the condition of an `IF`, `RESUME NEXT` goes on at the second
  statement of the THEN part. MBASIC looks for the next `:`.
- An error in the handler stops the program, in the line of the handler.
  `ON ERROR GOTO 0` in the handler stops it with the error of the handler, in
  `ERL`. A handler that goes past the last line is `No RESUME`.
- `RESUME` with no error is `RESUME without error`, and a handler can trap it.
  `ON ERROR GOTO` to a line that is not in the program is `Undefined line number`
  when the statement runs.
- `ERROR 0` and `ERROR 256` are `Illegal function call`.
- A `FOR` that fails (`FOR I%=1E10`) starts no loop, so after `RESUME NEXT` its
  `NEXT` is `NEXT without FOR`. With `ON ERROR GOTO`, each loop has a flag that the
  `FOR` sets and the end of the loop clears. A `FOR` with a double variable is
  `Type mismatch` in every program, as in MBASIC.

## PRINT USING

The runtime formats each value when the program has calculated it.
`mb25_using_begin` takes the format. `mb25_using_num` and `mb25_using_str` take one
value each. `mb25_using_end` prints the rest of the format up to the next field,
and the new line. The code is a port of the `_using_*` functions of the
JavaScript runtime (`src/codegen_js_backend.py`), which are a port of
`UsingFormatter` in `src/basic_builtins.py`. A value of the wrong type for its field
is `Type mismatch`, after the text that came before it. A double has 7 digits
under uc80 (its doubles are 32 bits), so a field for more digits shows zeros.

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

## CLEAR

`CLEAR` sets the variables to 0 or "", deletes the arrays (as `ERASE`),
empties the GOSUB stack, sends the DATA pointer back, forgets
`ON ERROR GOTO` and closes the files. The FOR loops are jumps in the C code,
so `CLEAR` does not end them. `CLEAR` does not reset OPTION BASE, `DEF FN` or
the DEF types: the types follow the DEFINT, DEFSNG, DEFDBL and DEFSTR
statements in the text.
