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


## 1. Errors that are still not detected

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
  binary. `CLEAR ,n` and `CLEAR ,,n` change the budget, and `FRE` reports the string space less the live strings.
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
- The interpreter prints the `Overflow` message of a numeric literal when a
  line is typed. It does not print the message when `LOAD` or the command line
  reads the program from a file, and `LIST` shows the text as typed (#38).
- The binary refuses a line with an `&H` constant of more than four digits, or
  an `&O` constant above 65535. It prints `Overflow` and does not store the
  line. The interpreter prints `Overflow` too, but it keeps the line: `LIST`
  shows the line, and `RUN` skips the statement with no error (#39). The
  JavaScript compiler stops with a compilation error, and the compilation
  error stays.
- Done (#40): the text of an `Overflow` or `Division by zero` message that
  does not stop the program goes through the width logic of PRINT, one
  character at a time, in the interpreter and in the JavaScript backend. With
  `WIDTH 40` and the cursor near the right edge the word is split (`Overflo` /
  `w`), as the binary does. Test: `tests/regression/integration/test_notice_width_wrap.py`.
- Done (#41): the JavaScript backend stops with `<message> in <line>` with no
  `?`, as the interpreter does. `ERROR n` uses the message of code n.
  Test: `tests/regression/integration/test_js_fatal_error_line.py`.

Done (#42): `src/error_codes.py` no longer carries the nine codes 5.21 has not
got - 24, 25, 68-72, 75 and 76. `ERROR 24` prints `Unprintable error`, as the
binary does, and ERR stays 24. (The JavaScript backend prints `Error 24 at line
10` for every ERROR code; that is the separate difference about `in <line>`
text.)

Done for the interpreter (#43, open for the JavaScript backend): the
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

Still open: the JavaScript backend gaps for `STRING$`, `SPACE$`, `LEFT$`,
`RIGHT$`, `TAB`, `CHR$`, `PEEK` and array subscripts (the issue lists them);
the arguments of `CLEAR`, `USR`, `LPOS` and `WIDTH 0`; the maximum number of
files (`CLOSE #4` is `Bad file number` on the binary with the default 3
files); the two-argument form `MID$(A$,2)=X$`, which the parser rejects; and
`DIM A(32767)`, which is `Subscript out of range` on the binary (memory) and
works here.


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
- The JavaScript compiler has the same edges, except that it prints no
  ` in <line>` for any error and does not check `A$=A` at run time. The C
  backend refuses programs with `ON ERROR`, so it has no handler edges.
- `ON ERROR GOSUB` is a `Syntax error` on the binary. The interpreter and the
  JavaScript compiler still accept the form.
- Done (#48): after CONT, a second ^C prints `Break in <line>` and CONT works
  again, as on the binary. CONT arms the break handler, as RUN does. A ^C at
  an `INPUT` prompt breaks at once, and CONT asks the question again. Tests:
  `tests/regression/ui/test_cli_break.py`.


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


## 5. Reserved words followed by a type suffix

`NAME$`, `LEN%`, `FOR$`, `TO%`, `ERR`, `ERL` are all syntax errors on the real
binary, and we accept them (#52). Two of the tests here were written using
`NAME$` and died at that line on the binary; they have been renamed to `NM$`,
but the lexer rule is untouched.

MBASIC's CRUNCH (`bintrp.mac`, the `tstanm` call around line 2504) treats a
reserved word as a keyword **only when the character after it is not a letter,
not a digit and not `.`**. That single rule gives:

    NAME$   FOR$   LEN%   TO%   ERR   ERL        Syntax error
    TOTAL   NAMES$   FORM   COST   NAME.X       fine - all accepted
    FORX=1TO3                                    Syntax error (TO is followed by 3)

So the folklore that a variable name may not *contain* a reserved word is
false for 5.21; what matters is only what follows the word.

Our lexer (`src/lexer.py:250-267`) does maximal munch, pulls the trailing
suffix into the identifier, and then looks the whole string up in `KEYWORDS`.
`MID$` and `STR$` only work because those entries are stored *with* the dollar.

Two traps for anyone implementing the real rule:

- `INPUT$(n)` is legal on 5.21 and must keep working. `INPUT$` is not in the
  reserved list at all - `INPUT` crunches and the `$` stays an ordinary
  character.
- `TIME$` is *not* reserved in the CP/M build, and `LEFT` and `CHR` without the
  dollar are ordinary variables.


## 6. Syntax errors are found at the wrong time

We reject a bad line when it is *entered*, print the complaint there, store the
line anyway, and then silently skip it when the program runs. The binary
crunches the line at entry without complaint and reports `Syntax error in 10`
at RUN - after which it opens the line editor on the offending line, which is
its own piece of behaviour we do not have (#53).


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

Not bugs so much as decisions to record - each one is a place where a program
that works here would not work on the real thing.

- `OPEN "A"` (append) is not a 5.21 file mode; the binary answers
  `Bad file mode`. `test_file_io.bas` uses it, which is why that test is not
  binary-verified.
- `MERGE` returns to command level on 5.21 - the rest of the program does not
  run. We carry on. (The summary line MERGE used to print is now suppressed
  when a running program merges, which is what the binary does.)


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
