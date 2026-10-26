# JavaScript backend: DIM and ERASE

The JavaScript backend (`--compile-js`) checks `DIM` and `ERASE` when the
program runs, as MBASIC 5.21 does. The expected results come from the binary
under cpmemu. The test is
`tests/regression/integration/test_js_dim_erase_runtime.py`.

## What the binary does

- `ERASE` of an array that does not exist is `Illegal function call`. The
  arrays that the same `ERASE` names before the bad one are erased already.
- `DIM` of an array that exists is `Duplicate Definition`. An array that a
  use made (`A(1)=1`) exists. The old array keeps its size.
- A bound is any expression. A string is `Type mismatch`, a number above
  32767 is `Overflow`, and a negative number is `Illegal function call`.
  `DIM A(2.5)` is `DIM A(3)`.
- With `OPTION BASE 1`, a bound of 0 is `Subscript out of range`. This check
  comes before the `Duplicate Definition` check.
- A `DIM` that fails stops at the bad declaration. The earlier declarations
  of the same statement are made. The later ones are not made.
- All of these errors can be trapped. `ERR` and `ERL` give the `DIM` or
  `ERASE` line, and `RESUME NEXT` goes on after the statement.

## How the generated code works

Most programs have one `DIM` per array with constant bounds, at the start of
the program. The generated code makes these arrays when it starts, and each
access is a plain index. The `DIM` only sets a flag: if the `DIM` runs a
second time (a jump back), it gives `Duplicate Definition`.

An array is a run-time array when one of these is true:

- An `ERASE` names the array.
- The array has more than one `DIM`.
- A use of the array comes before the `DIM` in the text.
- A bound is not a constant, is negative, or is above 32767.
- The program has a `CLEAR` after the first `DIM`. `CLEAR` deletes every
  array, so a `DIM` can follow it. `CLEAR` sets the bounds of the run-time
  arrays to `null`. A `CLEAR` before the first `DIM` changes nothing.
- The `DIM` is not in the first lines of the program. The first lines are
  those before any statement that can jump (`GOTO`, `GOSUB`, `IF`, `FOR`,
  `ON ERROR` and so on). A jump can skip such a `DIM` or run it again.

The run-time arrays have a bounds variable (`_bd_<name>`) that is `null`
while the array does not exist. `_dm_<name>` is the `DIM`, `_ar_<name>` gives
the array for a use (and makes it with bounds 0 to 10 if it does not exist),
and `ERASE` sets the bounds to `null`. `_db` checks one bound. Each access
to a run-time array goes through a function call, so it is slower than a
fixed array. The semantic analyzer gets the `runtime_dims` option for the
JavaScript backend. With the option, a bad `DIM` is not a compile error.

## Differences that remain

- `DIM A(32767)` and other sizes that do not fit in the memory of the binary
  are made here (there is no memory model). Only a total above 16 million
  elements is `Out of memory`.
- A variable and an array with the same name (`P$` and `P$(1)`) share one
  JavaScript name. The fault is older, and this change does not fix it.
