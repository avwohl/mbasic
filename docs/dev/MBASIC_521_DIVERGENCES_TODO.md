# Divergences from MBASIC 5.21 still outstanding

Found by cross-checking `basic/dev/tests_with_results/` against the real binary
under cpmemu, and by a sweep of the whole error catalogue. Everything here was
measured against `com/mbasic.com`, and most of it was also traced back to the
reconstructed 5.21 assembler in
`/home/wohl/src/mbasic2025/mbasic_521/mbasic_src/`.

What has been fixed is in
[TESTS_VERIFIED_AGAINST_BINARY.md](TESTS_VERIFIED_AGAINST_BINARY.md): PRINT
USING, the TRON trace, MOD and `\`, operator precedence, zero-trip FOR, and
untrapped error reporting. This file is the remainder.

Each open difference has a GitHub issue (#30 to #57). The issue has a
reproduction on the binary, the cause in our code and a proposed fix. When an
issue is closed, change its entry here to "Done", or remove the entry.


## 1. Errors that were not detected - mostly done

The reporting is right now - `<message> in <line>`, no `?`, program stops - and
25 provocations match the binary exactly. The conditions that we did not
notice before are now detected:

Done (GitHub issues 30 to 33, `docs/dev/STRING_SPACE_AND_FILE_ERRORS.md`):

- Done (#30): a string expression that needs more than 10 string temporaries
  gives `String formula too complex` (error 16), as on the binary. The test
  recipe is a nest of eleven `CHR$(65)+(...)`. The old recipe
  (`STRING$(200,65)` and twelve concatenations) gives `String too long`.
  The body of a DEF FN function is not counted.
- Done (#31): `Out of string space` (error 14) when the live strings do not fit
  in the string space. The space is a byte budget (39168 at start-up, as FRE
  reports), not a memory model, so the error comes a little later than on the
  binary. `CLEAR ,n` and `CLEAR ,,n` change the budget, and `FRE` reports the
  string space less the live strings.
  Only a literal (class `ProgramString`) is free. A result of `LEFT$`, `RIGHT$`,
  `MID$` or `+` counts, also when it equals the whole literal. A `DEF FN` that
  returns a variable or a parameter counts (a copy on the binary); a `DEF FN` with a
  literal body (also through a chain of `DEF FN` calls), and a string read from `DATA`, are free.
- Done (#32): `OPEN "R"` keeps the record length (0 to 128, default 128), `FIELD`
  gives `FIELD overflow` when the widths are more than the record length, and
  `GET` and `PUT` use the record length. The binary binds the variables
  before the one that overflows. The interpreter changes nothing.
- Done (#33): `Bad file name` and `Too many files` for names that CP/M cannot
  hold, in OPEN, KILL, NAME, LOAD, SAVE, MERGE, CHAIN and RUN in a program. A name
  with a slash or backslash passes as a host path, and the setting
  `cpm_file_names` turns the check off. A command typed at the prompt is not
  checked.
- The JavaScript and C backends do not raise any of these four errors.

Done (#34, #35, #36): `LOAD` and `MERGE` of a file stop reading at the first bad
line, as the binary does. The bad line is a line over 255 bytes (`Line buffer
overflow in <number>`, 0 if the line has no number), a line with no number
(`Direct statement in file`) or a bare number of a missing line (`Undefined
line number`). The message is bare. The lines read before it stay: `LOAD` of a
file with a bad first line leaves an empty program, and `MERGE` keeps the old
program. A bare number of a missing line typed at the prompt also prints
`Undefined line number`. Inside a running program the binary prints the bare
message, does not run any `ON ERROR` handler and stops the program; ours does
the same. `RUN "file"` of a file with a bad line stops after the message and
does not run. The Tk and curses UIs print the same
message. The web UI loads files through the editor and does not use the loader.

`CHAIN` and `CHAIN MERGE` use the same loader (`cmd_chain` in
`src/interactive.py`), so they follow the same rules. Measured: after the bad
line the program stops with the bare message. `CHAIN` leaves the lines read
before the bad line (an empty program for a bad first line). `CHAIN MERGE`
keeps the old program and the lines merged before the bad line. Before this,
`cmd_chain` read the file with its own loop and ignored the bad lines, and
`CHAIN MERGE` of a bare number of a missing line looped for ever. The curses
and Tk `cmd_load` and `cmd_merge` now return True after a read abort, so a
running program stops there too. Tests:
`tests/regression/integration/test_chain_file_errors.py`. The curses and Tk UIs
now have a `cmd_chain` (`chain_into_program` in `src/ui/ui_helpers.py`); it
loads the file and starts the program with `cmd_run`, as `RUN "file"` does.

After a read abort in the CLI (`LOAD`, `MERGE`, `CHAIN`, `CHAIN MERGE`) the
variables, arrays and FOR/GOSUB state are cleared and `CONT` gives
`Can't continue` (measured). `CHAIN` with a start line now begins at that line;
a start line that the new program lacks prints a bare `Undefined line number`.
`CHAIN MERGE` with `DELETE a-b` now parses the range (before, `100-110` was read
as the number -10 and the range was lost, so the merge looped for ever) and
deletes those lines from the old program before the merge, even the CHAIN line.
The file is opened first: a missing file deletes nothing. A missing first or
last line of the range is `Illegal function call` at the CHAIN line, with
nothing deleted. `CHAIN MERGE` without `ALL` clears the variables (only COMMON
variables pass on), as `CHAIN` does. The web UI uses the same order and rules.
`DELETE a-` (open range) is `Illegal function call` on the binary; ours is a
syntax error. The curses, Tk and web read-abort paths do not clear the
variables yet.

A floating-point overflow is now reported. The binary prints a bare `Overflow`
(no line number, no `Ok`). It substitutes machine infinity with the sign of the
true result, and the program goes on. With `ON ERROR` armed it is ERR 6.

The interpreter and the JavaScript backend do the same for a result that is
infinite in the IEEE format of its precision (binary32 for single, binary64 for
double). Examples are `10^40`, `1.7E38*10`, `EXP(100)`, `1E38*1E38`,
`CSNG(1D39)`, `A! = 1D39` and `VAL("1E400")`.

A literal that is too big, such as `1E39`, gets `Overflow` when the line is
entered. Machine infinity takes its place. `0^-1` is a non-fatal
`Division by zero`. These are `Illegal function call`: a negative base with a
fractional exponent, `SQR` of a negative number, and `LOG` of zero or a
negative number. `CINT(40000)` is `Overflow`.

What is still different:

- The MBF range is not emulated (section 10). `PRINT 2^127`, `EXP(88)` and
  `EXP(100#)` are legal here and `Overflow` on the binary. `1D300/1D-300`
  is `Overflow` here and `Division by zero` on the binary, because MBF cannot
  hold 1D-300. `1D300^2` and `EXP(1000#)` print a single-precision machine
  infinity on the binary and a double one here.
- MBF has no denormal numbers. A result below about 1.5E-39 is 0 on the
  binary (`PRINT EXP(-100)` and `PRINT 1E-20*1E-20` print 0). IEEE gives a
  denormal number here (`3.78351E-44`). This follows from the IEEE decision
  in section 10.
- `PRINT USING` with `^^^^` and a value that is close to a power of ten
  (such as 9.99999E30): the binary scales the value by a product of powers
  of ten in MBF. Two effects follow. (1) The scaled value can round to
  exactly 1, and then the binary does renormalize. With a single-precision
  value, `"##.#^^^^"` gives `1.0E+22` for 9.99999E21 and `1.0E-20` for
  9.99999E-21, and `"#.##^^^^"` gives `0.10E-19` for 9.99999E-21. We give
  `10.0E+21`, `10.0E-21` and `1.00E-20`. This shows for exponents of about
  21 to 37 and about -21 to -39. (2) The binary truncates the scaled value
  when the exponent is about 12 to 26 (`"##.#^^^^"` gives `9.9E+12` for
  9.95E12 and `9.9E+26` for 9.95E26). We round and give `10.0E+12`. Double
  values differ in the same way (`"#.##^^^^"` with 9.99999999999999D+99
  gives `0.17D+39` on the binary, a value in the MBF range). Issue #22 is
  only partly fixed: the case of a carry that is not caused by the MBF
  scaling agrees. We do not emulate the MBF multiplication.
- The sign of machine infinity after a double division by zero is erratic on
  the binary (it depends on what was computed before). We use the sign of the
  dividend.
- Done (#38): `LOAD`, `MERGE` and the command-line load print `Overflow` for
  each numeric literal that is too big (such as `1E39`), while they read the
  file, as a typed line does. `LIST` shows the text as typed.
- Done (#39): a line with an `&H` constant of more than four digits, or an
  `&O` constant above 65535, is refused with `Overflow` and not stored. A
  refused replacement leaves the old line. `LOAD` and `MERGE` stop reading the
  file at such a line, as the binary does (the lines after it are not loaded).
  The JavaScript compiler stops with a compilation error, and the compilation
  error stays.
- Done (#39, DATA): DATA text is not crunched, so a DATA line with `&O9`,
  `&O8` or `&O19` is stored, listed and loaded. `READ A$` gives a numeric DATA
  item as it was typed (`&H12345`, `&O999`, `1E39`, `1.50`). Outside DATA the
  refusal stays. The lexer splits the rest of a DATA statement into raw items
  (up to a comma or a colon). A clean number goes through the number reader;
  every other item (`1 2`, `12abc`, `&OA`, `&H12G`, `X+1`, `(1)`, `PRINT`) is a
  string with the case kept and the trailing spaces dropped, as on the binary.
  An empty item is an empty string. A signed item such as `+3` reads as `+3`
  into `A$`. The JavaScript compiler does the same. Not done: the binary gives
  a Syntax error for text after a closing quote (`"q"x`); we drop that text.
  READ into a number variable parses the text of an unquoted item at READ
  time, as the binary does (`data_text_to_number` in `src/interpreter.py`, and
  the same code in the JavaScript compiler). Spaces inside the digits are
  ignored (`1 2` is 12), `1E` is 1, a type suffix at the end is accepted, and
  `&H`, `&O` and `&` take digits only. A bad item is a Syntax error reported
  at the DATA line (`abc`, `12abc`, `1.5.5`, `&HG`, a quoted item, a sign
  before `&`); `&O8`, `&O19` and `&9` are reported at the READ line; a value
  over 65535 is an Overflow at the READ line. `ERL` is the DATA line, and
  `RESUME NEXT` goes on after the READ, and the bad item stays the next item
  to read (`READ B$` after the trapped error gets it). Not done: `ON ERROR GOTO 0` inside
  the handler reports the READ line, not the DATA line.
  Test: `tests/regression/integration/test_entry_time_forms.py`.
- Done: a line number stops at 6553. MBASIC takes no more digits once the value
  is 6553 or more, so `70000 PRINT 1` is line 7000 with the text `0 PRINT 1`,
  and a bare `70000` is line 7000 with the text `0`. `65529` is a line number.
  The prompt, `LOAD` and `MERGE` do this (`src/line_number_split.py`).
- Done (#40): the text of an `Overflow` or `Division by zero` message that
  does not stop the program goes through the width logic of PRINT, one
  character at a time, in the interpreter and in the JavaScript backend. With
  `WIDTH 40` and the cursor near the right edge the word is split (`Overflo` /
  `w`), as the binary does. Test: `tests/regression/integration/test_notice_width_wrap.py`.
- Done (#41): the JavaScript backend stops with `<message> in <line>` with no
  `?`, as the interpreter does. `ERROR n` uses the message of code n. A
  fatal `RETURN` in a program with no `GOSUB` is `RETURN without GOSUB in
  <line>` (it was a JavaScript ReferenceError). `STOP` prints `Break in
  <line>`, also inside a handler, and starts a new line first when the
  cursor is not in column 0. The interpreter does the same now. `RESUME` to
  a line that does not exist is error 8 at the `RESUME`, so a handler that
  is still armed catches it again, as the binary does (it was fatal). An
  `ERROR 9` inside a handler prints `Subscript out of range in <line>`, in
  the interpreter and in the JavaScript backend.
  Test: `tests/regression/integration/test_js_fatal_error_line.py`.

Done (#42): `src/error_codes.py` no longer carries the nine codes 5.21 has not
got - 24, 25, 68-72, 75 and 76. `ERROR 24` prints `Unprintable error`, as the
binary does, and ERR stays 24. The JavaScript backend prints `Unprintable
error in 10` too.

Done for the interpreter (#43): the
interpreter applies FRCINT's 16-bit range check, and CONINT's second test,
wherever the binary does. An integer argument is rounded and must fit
-32768..32767, or the result is `Overflow`. A byte argument (`LEFT$`,
`RIGHT$`, `MID$`, `SPACE$`, `STRING$`, `CHR$`, the start of `INSTR`, `INP`,
`OUT`, the value of `POKE`, `ON...GOTO`, file numbers and `INPUT$`) must then
be 0 to 255, or the result is `Illegal function call` (so `LEFT$("AB",300)`
and `SPACE$(256)` stop with an error, as on the binary). A negative array
subscript or `DIM` bound is `Illegal function call`. `TAB`, `SPC`, `MKI$`,
`RANDOMIZE` and `WIDTH` check 16 bits. `PEEK` and the address of `POKE`
accept -32768 to 65535; `PEEK` still returns a random byte.

The same checks cover these statements:

- `ERROR n`: 0 and above 255 are `Illegal function call`, 5.6 rounds to 6.
- The `MID$` statement: start and length are checked. A start of 0, or a
  start beyond the end of the target with a length above 0, is `Illegal
  function call` (also for an empty or undefined target). A numeric
  right-hand side is `Type mismatch`.
- `FIELD`: widths are checked, and widths that add up to more than the
  record length of `OPEN` (128 when `LEN` is left out) are `FIELD overflow`.
- `GET` and `PUT`: a record number that rounds to 0 is `Bad record number`,
  a negative one is `Illegal function call`.
- `OPEN ... LEN`: above 128, the default `/S:` size, is `Illegal function
  call`.
- `WAIT`: the operands are checked as bytes. The interpreter has no ports,
  so a `WAIT` that would wait for ever stops with `Illegal function call`.

A double is taken to single precision before FRCINT rounds it, so
`2.49999999# AND 3` is 3.

Done for the JavaScript backend (#43): the runtime has `_frcint` and
`_conint`, which copy `to_frcint` and `to_conint`. `STRING$`, `SPACE$`,
`LEFT$`, `RIGHT$`, `MID$`, `CHR$`, the start of `INSTR`, `ON...GOTO` and
`ON...GOSUB`, `INP`, `OUT` and the value of `POKE` use the byte check. `TAB` and
`SPC` in PRINT check 16 bits, and the argument is evaluated when its turn
comes, so `PRINT "A";TAB(40000)` prints the A first. `PEEK` and the address of
`POKE` accept -32768 to 65535. `RANDOMIZE`, `WIDTH` and `ERROR n` check as the
interpreter does. The `MID$` statement is a runtime function with the same
checks as the interpreter, and it no longer deletes characters when the
replacement is shorter than the length. Every array subscript goes through
`_ix`: Overflow above 16 bits, `Illegal function call` when negative,
`Subscript out of range` above the bound of its dimension. Before, an
out-of-range write grew the array. The JavaScript compile path keeps one
subscript per dimension (`SemanticAnalyzer(flatten_arrays=False)`), because
the nested arrays of the generated code did not work with the flat index of
the C backend. An array that is not in a `DIM` gets as many dimensions as its
uses have subscripts. `DIM A(2.5)` rounds (also for the C backend), and a
`DIM` bound above 32767 is `Overflow` when the `DIM` runs. Test:
`tests/regression/integration/test_js_range_checks.py`. Not done in the
JavaScript backend: `DIM A(-1)` stays a compilation error, and the bounds of a
`DIM` must be constants. The file statements `FIELD`, `GET`, `PUT`, `OPEN ...
LEN` and file numbers do not have the checks. A double is not taken to
single precision before FRCINT rounds it, except in the logical operators.

Round 2 of the JavaScript backend: `READ` and `SWAP` with array elements use
the subscripts and the bounds check (before, they assigned the whole array).
`OPTION BASE 1` is used by the bounds check. An array used with the wrong
number of subscripts is `Subscript out of range`, in JavaScript and in the
interpreter. The interpreter now checks the second and later dimensions
against their own bound (`A(2,6)` on `DIM A(5,5)`). `RESUME` with no error
is `RESUME without error`, and a handler that falls off the end reports `No
RESUME in <last line>`. `ON ERROR GOTO 0` in a handler reports the line of
the first error. `ERASE` deletes the array in JavaScript: the next use makes
it again with the bounds 0 to 10, as on the binary. A fatal `ERROR n` in a
handler, where n has no message, prints `Unprintable error`. `INSTR` gives 0 for
an empty string and for a start beyond the end, also with an empty search
string (interpreter and JavaScript). `MID$(A$,2,3)=A$` copies byte by byte over
itself, so `hello` gives `hhhho`. Not done: `ERASE A` followed by `DIM A` is
still a compile error (the array cannot be resized), and the target shared
through `B$=A$` does not give the byte-by-byte copy.

Done for the interpreter (#43, second part). Each item was measured on the
binary:

- `MID$(A$,2)=X$` with no length is accepted. It replaces as much of `A$` as
  `X$` fills, as the three-argument form does with a length of 255. A start of
  0 or beyond the end is `Illegal function call`, a number on the right is
  `Type mismatch`. The JavaScript backend does the same.
- `CLEAR` already agreed with the binary: the numbers are read as 16-bit
  values (`CLEAR 70000` and `CLEAR ,70000` are `Overflow`), `CLEAR -1`,
  `CLEAR 0,0` and `CLEAR ,0` are `Illegal function call`, a string is
  `Type mismatch`. Tests now cover this.
- `USR` and `USR0` to `USR9`: the argument is evaluated (`USR(1E40)` prints
  `Overflow` first), then the call is `Illegal function call`, with or
  without `DEF USR`: there is no machine code to run. The argument can be of
  any type (`USR("A")` is `Illegal function call`, not `Type mismatch`).
- `DEF USR[n]=address` is a statement now (it was a Syntax error). The
  address is -32768 to 65535 and is not kept: 65536 is `Overflow`, a string is
  `Type mismatch`. `DEF USR10=1` is a Syntax error, as on the binary.
  The lexer ends the reserved word `USR` before a digit, so `DEF USR 4=100`
  works and a name that starts with `USR` (`USRX`, `USR1X`, `USR10`,
  `USR10(1)`) is a Syntax error, as on the binary. Other reserved words are
  not split off the front of a name.
- A missing right-hand side is `Missing operand` (22) when the statement
  ends there (end of line, `:` or `ELSE`) and a Syntax error before `,` or
  `)`, as on the binary: `A=`, `DEF USR=`, `WIDTH LPRINT`, `MID$(A$,2)=`.
  `MID$(A,2)="X"` with a number `A` is `Type mismatch`.
- `LPOS(x)` is a function now (it was an array). The argument is any type and
  is not used. The value is 1, the leftmost column of a printer: `LPRINT` is
  not implemented, so there is no printer column. `LPOS` with no argument is a
  Syntax error.
- `WIDTH 0` is accepted. The width is a byte (`WIDTH 256` is `Illegal function
  call`, `WIDTH 70000` is `Overflow`) and 0.4 rounds to 0. With width 0 the
  binary prints a line break before the first character of a line and never
  wraps again, and `TAB` and `SPC` are `Division by zero` (error 11) because
  they divide by the width. `WIDTH LPRINT n` is a statement now (it was a Syntax
  error) and checks the byte only. Test:
  `tests/regression/integration/test_mid_clear_usr_lpos_width0.py`.

Left out on purpose, with the reason:

- `DIM A(32767)` is `Subscript out of range` on the binary because the array
  does not fit in its memory. There is no memory model (see
  `docs/dev/NO_MEMORY_MODEL.md`), so here the array is made.
- The maximum number of files: with the default `/F:3` the binary says `Bad
  file number` for `CLOSE #4`. This interpreter allows 15 files on purpose.

Found while measuring, not done:

- A wrong number of arguments to a built-in function (`ABS()`, `POS(1,2)`,
  `USR()`, `LPOS(1,2)`) is `Illegal function call` here and `Syntax error`
  on the binary.
- `WIDTH 40,1` is a Syntax error on the binary (after it has set the
  width); here the device form is accepted and ignored.
- A `CLEAR` that succeeds also forgets `ON ERROR GOTO`, so the next error is
  fatal on the binary. Here the handler stays.
- A `MID$` statement whose value is the target string, as in
  `MID$(A$,3)=A$`, copies one byte at a time inside the one string on the
  binary (`HEHEH`). The interpreter and the JavaScript backend do the same.
  When the value is a separate string (`LEFT$(A$,5)`, `A$+""`, another
  variable), the copy is from the old value (`HEHEL`), as on the binary.
- The `MID$` statement needs `MID$(` with no space. `MID$ (A$,2)=X$` is a
  Syntax error, as on the binary; the function form `MID$ (A$,2,2)` allows
  the space. `CLEAR` with more than three arguments is a Syntax error found
  before any argument runs, as on the binary.
- `A=ELSE` is `Missing operand` (22) as on the binary, but `RESUME NEXT` then
  runs the `ELSE` and gives a Syntax error; the binary goes on with the next
  line.


## 2. ON ERROR, and what happens around a handler

The common path works - a trapped error reaches the handler with the right ERR
and ERL, and RESUME NEXT lands in the right place. The edges do not:

- Done (#44): `ON ERROR GOTO 0` inside a live handler disables the handler
  and raises the pending error again, reported at the line that first failed.
- Done (#45): `ON ERROR GOTO <line that does not exist>` is `Undefined line
  number` at the `ON ERROR` statement, checked when the statement runs.
- Done (#46): a handler that ends with `END` ends the program with no error
  (the binary prints `Ok`).
- Done (#47): an error inside a handler is reported with its own message at
  its own line, and is not trapped. It was a Python `AttributeError`.
- Done (#37): a handler that runs off the end of the program is `No RESUME in
  <last line>`.
- The interpreter keeps the error a handler works on in `state.pending_error`.
  `state.error_info` is only a fatal error, so the UIs and the run loops no
  longer see a handled error as a failure. Only RESUME ends a handler. A GOTO
  out of a handler does not end it: the binary leaves the next error
  untrapped, and so do we now.
- The JavaScript compiler has the same edges (it prints ` in <line>` since
  #41). After `ON ERROR GOTO 0` in a handler it names the line that first
  failed, and a handler that runs off the end is `No RESUME in <last line>`,
  as on the binary. One difference stays: it does not check `A$=A` at run
  time. The C backend refuses programs with `ON ERROR`, so it has no handler
  edges.
- Done: `ON ERROR GOSUB` is a `Syntax error` on the binary, at the prompt and
  (for a stored line) when the line runs, as for any bad statement. The
  interpreter and the JavaScript compiler do the same.
- Done (#48): after CONT, a second ^C prints `Break in <line>` and CONT works
  again, as on the binary. CONT arms the break handler, as RUN does. A ^C at
  an `INPUT` prompt breaks at once, and CONT asks the question again. Tests:
  `tests/regression/ui/test_cli_break.py`.
- Done (#48): CONT after a run-time error runs the failing statement again
  (also in the middle of a line and in a FOR loop). It prints the same error
  until the cause is fixed at the prompt. CONT after END resumes at the
  statement after the END. After the program ran off its end, CONT prints
  only `Ok`. An edit after the error gives `Can't continue`. All measured on
  the binary in a pty. Only the CLI does this. A direct statement that fails
  after the program stopped on an error prints the bare message, with no
  ` in <line>` (as the binary does). Tests:
  `tests/regression/integration/test_cont_after_error_and_end.py`.
- Done (#49): `python3 mbasic FILE` with a line over 255 bytes now prints the
  bare message and stays at the prompt, also when the first line is the long
  line and the program is empty. The binary also does this. The binary RUNs
  a loaded file at once when it is on the command line; we wait for RUN.


## 3. No `Ok` prompt - done

Done (#49): the CLI prints `Ok` once at start-up (in place of `Ready`), after
every direct command, after an error message and after a program stops or
breaks. A numbered line and a blank line print no `Ok`, as on the binary.
Tests:
`tests/regression/ui/test_cli_ok_prompt.py`. The curses, Tk and web UIs have
their own status areas and did not change.


## 4. Errors reach the user through `print()`, not through the I/O handler

The *wording* is now consistent everywhere - see
[TESTS_VERIFIED_AGAINST_BINARY.md](TESTS_VERIFIED_AGAINST_BINARY.md) - but
`src/interactive.py` still writes roughly forty of its messages with a bare
`print(...)` rather than `self.io.output(...)`. Only the CLI uses
`InteractiveMode`, and in the CLI `print()` and the I/O handler write to the
same terminal. Thus the user sees no difference, and the `print()` calls have
no issue. The change to `self.io.output()` is code cleanup.

The UI backends each carry their own copy of the command handlers - `cmd_load`,
`cmd_merge` and the rest exist four times over, once per backend,
which is why the same message had to be fixed in four places. Collapsing the
handlers onto one implementation that reports through the I/O handler is
also code cleanup.

RENUM is already collapsed: all backends call `ui_helpers.renum_program()`.
Curses, Tk and the web UI set `interactive_mode` and define `cmd_renum`, so
RENUM in the immediate line works in all of them.

- Done (#50): the web UI sets `interactive_mode` when it starts, and defines
  `cmd_renum`, `cmd_delete`, `cmd_load`, `cmd_save`, `cmd_merge`, `cmd_list`,
  `cmd_run`, `cmd_cont`, `cmd_chain` and `cmd_system`. LOAD, SAVE and MERGE use the
  session's in-memory files, never the server disk. CHAIN in the immediate
  line loads the file and runs it. CHAIN inside a running program gives an
  error: the web UI has no way to restart a running program with a new
  program (this limit is not part of #50). Tests: `tests/regression/ui/test_web_immediate_commands.py`.
- Done (#51): Tk prints nothing after RENUM. A reference to a missing line is
  still reported. Tests: `tests/regression/ui/test_tk_renum_silent.py`.


## 5. Reserved words followed by a type suffix - done (#52)

`NAME$`, `LEN%`, `FOR$`, `TO%`, `ERR`, `ERL` are all syntax errors on the real
binary. Done (#52): the lexer now gives the same result. Two of the tests here
were written using `NAME$` and died at that line on the binary; they have been
renamed to `NM$`.

MBASIC's CRUNCH (`bintrp.mac`, the `tstanm` call around line 2504) treats a
reserved word as a keyword **only when the character after it is not a letter,
not a digit and not `.`**. That single rule gives:

    NAME$   FOR$   LEN%   TO%   ERR   ERL        Syntax error
    TOTAL   NAMES$   FORM   COST   NAME.X       fine - all accepted
    FORX=1TO3                                    Syntax error (TO is followed by 3)

So the folklore that a variable name may not *contain* a reserved word is
false for 5.21; what matters is only what follows the word.

Our lexer (`read_identifier` in `src/lexer.py`) reads the identifier with
maximal munch, and looks the whole string up in `KEYWORDS` first. `MID$` and
`STR$` work because those entries are stored *with* the dollar. When the
whole string is not a keyword, but the string without its type character is a
reserved word, the lexer returns the keyword and leaves the type character in
the input. The `RESERVED_STEMS` set in `src/lexer.py` holds the reserved words
of the CRUNCH table. The words this implementation adds (`HELP`, `SHOW`,
`SETTINGS` and so on) are not in the set, so `SHOW%` is a plain variable. The
stray type character is a Syntax error when the statement runs (section 6).

Two traps for the rule, both handled:

- `INPUT$(n)` is legal on 5.21 and must keep working. `INPUT$` is not in the
  reserved list at all - `INPUT` crunches and the `$` stays an ordinary
  character.
- `TIME$` is *not* reserved in the CP/M build, and `LEFT` and `CHR` without the
  dollar are ordinary variables.


## 6. Syntax errors are found at the wrong time - done (#53)

The binary crunches a line at entry without a message, stores it, and reports
`Syntax error in 10` at RUN, when execution reaches the bad statement. The
statements before the bad one on the line run first, and `RESUME NEXT` goes on
with the statement behind the next `:`. After an untrapped error the binary
opens the line editor on the line.

Done (#53): the interpreter does the same. A statement that does not parse
becomes a `SyntaxErrorStatementNode` (see `ProgramManager.parse_single_line`
with `defer_syntax_errors`, and the parser and lexer flags of the same idea).
It holds the text of the bad statement, up to the next `:` or ELSE. Typed
lines, `LOAD`, `MERGE`, `EDIT`, `AUTO`, `CHAIN` and `RENUM` (also a bad line that
RENUM numbers again) store the line
and print nothing. `LIST`, `SAVE` and `RENUM` use the text of the line, so
they keep it as typed. When the statement runs it raises error 2, which
`ON ERROR` can trap. After an untrapped error the CLI starts the `EDIT`
command on the line. The `EDIT` prompt now has the space after the line number
that the binary prints (`20 PRINT`, not `20PRINT`). The full-screen and window
UIs still refuse a bad line when it is typed in their editors, because they
show the error at once. They keep a bad line that `LOAD` or `MERGE` reads.

The JavaScript and C backends turn the same statement into a run-time Syntax
error (`--compile-js`, `--compile-c`). The JavaScript runtime prints
`?Syntax error` without the line number (#41). A line number that is too large
or missing, and an `&H` or `&O` overflow, still stop the compilation.

An unterminated string is still a Syntax error here, where the binary accepts
`PRINT "abc` and prints `abc`. This difference is older than #53.

One case is fixed. `WRITE` with a `,` or `;` after the last item (`WRITE 1;`,
`WRITE #1,2,`) is accepted at entry and on LOAD, and LIST and RENUM keep its
text. When the line runs, the interpreter and the JavaScript runtime write the
items and a `,` with no end of line, then raise `Missing operand` (error 22).
The same happens in a file. `WRITE #1,` with no items writes an empty line.
`WRITE #1` with no comma and no items is a Syntax error (error 2) when it
runs. A `,` or `;` before the first item or twice in a row (`WRITE ,1`,
`WRITE 1,,2`, `WRITE ;`) is also accepted at entry and on LOAD. When the line
runs, the items before the bad separator and a `,` go out with no end of line
(nothing, if no item comes first), then Syntax error (error 2) occurs.
The interpreter, the JavaScript runtime and the C backend all do this. The C
backend writes the error text to the error stream and stops, as it does for
other errors without an `ON ERROR` handler.

## 7. The compiler backends are out of step with the interpreter

The precedence fix is in the parser, so every backend gets it. The operator
semantics are not:

- Done: the JavaScript backend rounds the operands of `\` and MOD to integers
  and checks their 16-bit range, as the interpreter does. `7.6 MOD 3` is 2,
  and `40000 MOD 3` is `Overflow` (ERR 6).
- Done (GitHub issues 28 and 29, `docs/dev/C_BACKEND.md`): the C backend
  has `\` and MOD (operands rounded to integers, as CINT does), `/` always gives
  a floating-point result, comparisons give -1, and AND, OR, XOR, EQV, IMP
  and NOT work bit by bit on 16-bit integers.
- Done (#54): the C backend rounds a fractional operand of `\`, MOD, AND,
  OR, XOR, EQV, IMP and NOT, and an operand outside -32768..32767 after
  rounding is `Overflow`. `\` and MOD with a zero divisor are `Division by
  zero`. One edge stays open: `-32768 \ -1` wraps to -32768 in the C backend,
  where MBASIC gives 32768.
- Done (#55): FOR and NEXT end a loop when the sign of (v - end) equals the
  sign of the step, in the JavaScript backend (`_for_done(v, end, step)`) and
  in the C backend. With STEP 0 the loop ends only when the variable equals
  the limit. Test: `tests/regression/integration/test_js_for_step_zero.py`
  and `tests/regression/integration/test_c_backend_ops.py`.
- Done (#56): AND, OR, XOR, EQV, IMP and NOT. The JavaScript backend matches
  real MBASIC (GitHub issue 15, `docs/dev/JS_LOGICAL_OPERATORS.md`), and the
  interpreter now does too: it rounds a fractional operand (`NOT 2.7` is -4)
  and stops with `Overflow` for an operand outside -32768..32767
  (`40000 OR 1`), which `ON ERROR` can trap.
- Done (#57): WHILE and WEND in the JavaScript backend are jumps, as FOR and
  NEXT are (`docs/dev/JS_CONTROL_FLOW.md`). A WHILE and its WEND on different
  lines work. Test: `tests/regression/integration/test_js_while_wend.py`.
- Done (GitHub issue 25, `docs/dev/JS_BROWSER_YIELD.md`): the browser build
  gives the page time to run in long loops and at INKEY$; Node reads INKEY$
  from stdin.
- Done (GitHub issue 13): NEXT pairs with FOR by position in the text, the
  loop-back and GOSUB return points are statements in the middle of a line, and
  `NEXT J,I` passes the semantic analyzer. See `docs/dev/JS_CONTROL_FLOW.md`.


## 8. `serialize_expression` and a unary minus - done

`serialize_expression` in `src/ui/ui_helpers.py` now puts brackets around the
operand of a unary minus or NOT when the operand binds looser. `-(A + B)` and
`-(A * B)` keep their brackets.
`tests/regression/interpreter/test_parser_forms.py` covers the unary
cases. RENUM does not call the serializer (it edits the text of each line, see
`src/renum.py`).


## 9. Statements where we are ahead of 5.21

Each item here is a place where a program that works here does not work on
the real thing. The two items that were here (`OPEN "A"` and `MERGE` in a
running program) are now decisions. See section 10.


## 10. Deliberate, and staying that way

MBASIC's arithmetic is Microsoft Binary Format and ours is IEEE - a project
decision, see `src/number_format.py` and the note in
`docs/dev/TESTS_VERIFIED_AGAINST_BINARY.md`. These differ and should:

    CDBL of a single 3.14      real 3.139999866485596   ours 3.140000104904175
    5 ^ 2 = 25                 real false (EXP/LOG gives 24.999998)
    VAL("99.99") = 99.99       real false, and by a different amount than ours

The MBF *range* goes with it: an MBF result between 1.7E38 and the IEEE limit
(3.4E38 for single) overflows there and does not here. Only a result that is
infinite in the IEEE format of its precision is an `Overflow` here (section 1).
Machine infinity, 1.70141E+38, is nonetheless reproduced where it is
observable - a float divide by zero and an overflow yield it, as they do on the
binary.

Two statements accept more than 5.21 does. The user decided on 2026-10-26 to
keep them as extensions:

- `OPEN "A"` opens a sequential file for append. The file is made if it is
  not there. 5.21 has no append mode and answers `Bad file mode`. The
  interpreter, the JavaScript backend and the C backend all accept `"A"`.
  `test_file_io.bas` uses `OPEN "A"`, so that test is not binary-verified.
- `MERGE` in a running program merges the file and then the program
  continues at the next statement. On 5.21, MERGE always returns to command
  level. The summary line that MERGE prints at command level does not show
  when a running program merges, as on the binary.
