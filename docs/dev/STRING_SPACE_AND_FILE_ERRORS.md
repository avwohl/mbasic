# String space, string temporaries, FIELD and file names

**Status:** Done (GitHub issues 30, 31, 32 and 33).
**Code:** `src/interpreter.py`, `src/runtime.py`, `src/cpm_names.py`.
**Tests:** `tests/regression/integration/test_string_temporaries.py`,
`test_string_space_function_results.py`,
`test_out_of_string_space.py`, `test_field_record_length.py`,
`test_cpm_file_names.py`.

All numbers in this file were measured on `com/mbasic.com` under cpmemu.

## String formula too complex (issue 30)

MBASIC 5.21 has 10 string temporaries (`numtmp` in `bistrs.mac`). A string
literal, a string function result and the result of `+` each use one until the
parent operator or function has used it. A string variable and an array element
use none.

A left operand, or an earlier argument, stays in its temporary while the next
operand is evaluated. A nest such as `CHR$(65)+(CHR$(65)+(...))` therefore
needs one more temporary at each level. Measured:

- 10 `CHR$` terms in a nest work. 11 terms stop with
  `String formula too complex` (error 16).
- Literals count the same as `CHR$` results. Variables do not count: a nest of
  13 variables works.
- 15 terms added from the left work, because `+` frees both operands.

`Interpreter._string_temps` works out, once for each expression node, the most
temporaries that the node needs. `evaluate_binaryop` and `evaluate_functioncall`
raise error 16 before they evaluate a node that needs more than 10. The body of a
DEF FN function is not counted.

## Out of string space (issue 31)

On the binary, string data lives in the free memory that `FRE` reports. That is
39168 bytes after start-up. When the strings do not fit, even after garbage
collection, the error is `Out of string space` (error 14).

The interpreter has no memory model (see `NO_MEMORY_MODEL.md`). It uses a byte
budget for the string data, which is not a model of memory:

- The budget is `Runtime.string_space_size`: 39168 bytes at start-up.
- The live string variables and array elements are counted against the budget
  when a string is stored. The count runs only when the bytes stored since the
  last count could fill the budget. Garbage collection on the binary works in the
  same way, and a program that replaces its strings all the time is not slow.
- The old value of the variable that is set counts until the new value is stored.
- `FRE(0)` and `FRE("")` return the budget less the live string bytes.

The budget is an estimate. The binary also spends memory on the program text,
and on the variables and arrays themselves. In the recipe of issue 31 it holds
190 strings of 200 bytes. The interpreter holds 195. A string literal or DATA item
takes no string space on the binary (it points into the program text), and
the interpreter does not count one either. The evaluator gives a literal as a
`ProgramString` (a `str` subclass in `src/runtime.py`), and only that class costs
nothing. A string that a function or operator makes is a plain `str` and counts,
even when it equals the whole literal (`LEFT$(L$,LEN(L$))`, `MID$(L$,1)`, `L$+""`).
A `DEF FN` that returns a variable or a parameter gives a plain `str` too. A string
from `DATA` is a literal and keeps the mark. On the binary these results are copies in string space (measured: error 14 at
I=371 in a loop of 100-character strings, as for `STRING$`). A program that comes near the limit gets the error at a different place.
A program that is far over the limit gets the same error as on the binary.

`CLEAR ,n` sets the highest memory address and `CLEAR ,,n` sets the stack
space. The number before the first comma is read as an integer and not used:
more than 32767 or less than -32768 is `Overflow`, and a negative number is
`Illegal function call`. Measured:

- The free memory changes by the same amount as the address. The default
  address is 64766. `CLEAR ,40000` gives 14409 free bytes.
- A stack space of 512 is the default. A larger stack takes the difference from
  the free memory. The least stack space that works is 82.
- 0 for either number is `Illegal function call`. A number outside the 16-bit
  range is `Overflow`. -1 is 65535. A string space that is less than zero, and
  a stack space under 82, are `Out of memory`.
- A plain `CLEAR` keeps the numbers of the last `CLEAR ,n`.

The parser (`parse_clear`) now keeps the number after the first comma in
`ClearStatementNode.memory_top`. Before, `CLEAR ,60000` dropped the number.

## FIELD overflow (issue 32)

`OPEN "R"` stores the record length in the file entry (`record_length`). The
default is 128. Measured:

- 0 to 128 work. 129 and more, and negative numbers, are `Illegal function
  call`. 65536 is `Overflow`. 0 is accepted, and then every FIELD with a
  width above 0 overflows.
- `FIELD` adds the widths. It raises `FIELD overflow` (error 50) when the total is
  more than the record length. A width below 0 or above 255 is `Illegal function call`
  (checked before the overflow). A fraction is rounded.
- `OPEN` with mode I or O and a record length is a `Syntax error`.
- Each FIELD statement starts at the first byte of the record.
- The record buffer is as long as the record length. `GET` and `PUT` use this
  length, so a short FIELD list leaves the rest of the record as it was.

The binary binds the variables before the one that overflows, and then stops.
The interpreter checks all the widths first, and it changes nothing when the
total is too large.

## Bad file name and Too many files (issue 33)

`src/cpm_names.py` has the rules. `namfil` in `dcpm.mac` makes a CP/M file
control block from the name. It gives `Bad file name` (error 64) when the name
is empty, when the drive letter before a colon is not a letter, when nothing
follows the drive colon, when nothing comes before the dot, and when a second dot
comes after the type has begun (`ABCDEFGHI.DAT`, `A.B.C`, `.DAT`, `1:X`).
Longer names are cut. The name keeps 8 characters and the type keeps 3. A name
with no dot keeps 11 characters.

The CP/M file system under MBASIC refuses some characters in the 11
characters that remain. These are the control characters, the characters
`% ( ) * , / : ; < = > [ \ ] ^ |` and a dot. The top bit of a character is
ignored. A statement that makes a file (`OPEN "O"`, `OPEN "R"`, `SAVE`) gives
`Too many files` (error 67). A statement that reads a file gives `File not found`.
`?` and the space are allowed. A name of only spaces is refused.

The new name of `NAME ... AS` is checked too, but less: a name that is not well
formed is `Bad file name`, and a drive letter from A to Z is `Illegal function
call` (the rename would cross drives). The refused characters are not checked.

The check runs in `OPEN`, `KILL`, `NAME`, `LOAD`, `SAVE`, `MERGE`, `CHAIN` and
`RUN "file"`, in a program. `FILES` is not checked, because it takes
wildcards. A command that is typed at the prompt (`LOAD "x"`) is not checked.

The rules refuse names that are good on a host: `inputfile.txt` is a
`Bad file name`. Two things keep host use possible:

- A name with a slash or a backslash is a host path and passes. (The binary gives
  `Too many files` for these.) The tests use such names.
- The setting `cpm_file_names` (default on) turns the check off.
