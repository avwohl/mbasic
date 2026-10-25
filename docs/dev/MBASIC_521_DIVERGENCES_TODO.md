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
25 provocations match the binary exactly. What is left is conditions we simply
do not notice. Each prints nothing at all where the binary raises:

| provocation | binary says | issue |
|---|---|---|
| a string expression with more than 10 pending function results, such as twelve nested `CHR$(65)+(...)` | `String formula too complex in 10` | #30 |
| `DIM A$(300)` filled with 200-character strings | `Out of string space in 20` | #31 |
| `FIELD #1, 100 AS A$` on a 16-byte record | `FIELD overflow in 20` | #32 |
| `OPEN "O",1,"A:B:C*?.X Y"` | `Too many files in 10` | #33 |
| `LOAD` of a file with a line longer than the 255-byte buffer (a typed line gives no error) | `Line buffer overflow in 10` | #34 |
| `LOAD` of a file with a line that has no number | `Direct statement in file` | #35 |
| `LOAD` or `MERGE` of a file with a bare line number for a missing line | `Undefined line number` (the REPL gives the same error) | #36 |
| running off the end of the program inside a handler | `No RESUME in <last line>` | #37 |

The old recipe for `String formula too complex` (`STRING$(200,65)` and twelve
concatenations) gives `String too long` on the binary and here. Use the recipe
in #30.

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
- The text of an `Overflow` or `Division by zero` message that does not stop the
  program is not wrapped at the `WIDTH` limit. The binary sends the message
  through the width logic, so with `WIDTH 40` and the cursor near the right edge
  it splits the word (`Overf` / `low`). The interpreter and the JavaScript
  backend print the word whole (#40).
- The JavaScript backend reports a fatal error as `?Overflow`. It has no
  `in <line>` text (#41).

`src/error_codes.py` still carries nine codes 5.21 has not got - 24, 25, 68-72,
75 and 76, all `Unprintable error` on the binary. `ERROR 24` prints the name of
the code here (#42).

FRCINT's 16-bit range check is applied to `\` and MOD operands and to `%`
assignment, but not yet everywhere the binary applies it: `A(40000)`,
`TAB(1E38)`, `STRING$(40000,65)`, `LEFT$("AB",1E38)`, `PEEK(70000)`,
`MKI$(40000)`, `SPACE$(40000)` and `CHR$(40000)` are all `Overflow`
there (#43). (`CINT`, `HEX$` and `OCT$` now check.)


## 2. ON ERROR, and what happens around a handler

The common path works - a trapped error reaches the handler with the right ERR
and ERL, and RESUME NEXT lands in the right place. The edges do not:

- `ON ERROR GOTO 0` inside a live handler should disable the handler **and**
  re-raise the pending error, reported at the line that originally failed. We
  only disarm and carry on (#44).
- `ON ERROR GOTO <line that does not exist>` is `Undefined line number` at the
  `ON ERROR` statement on the binary - checked when it executes, not when it
  fires (#45).
- A handler that ends with `END` makes us re-raise the original error at the
  END line. The binary just prints `Ok` (#46).
- An error raised inside a handler crashes us with a Python `AttributeError`
  about `on_error_goto` (#47, high severity).
- The first ^C prints `Break in <line>` once, and CONT resumes. After CONT, a
  second ^C prints a bare `Break`, and CONT then gives `Can't continue`. The
  binary prints `Break in <line>` each time, and CONT works each time. A ^C
  at an `INPUT` prompt does not break until the user types the next line
  (#48). (The older note said that `Break in` prints twice. The double
  `Break` does not occur now.)


## 3. No `Ok` prompt

The binary prints `Ok` after every direct statement and after every program
stop, error or not. The CLI never prints `Ok`. The CLI prints `Ready` at start-up
and after NEW, LOAD and MERGE only (#49). Typing three commands at the prompt
gives

    binary    Illegal function call / Ok / RETURN without GOSUB / Ok / Type mismatch / Ok
    ours      Illegal function call / RETURN without GOSUB / Type mismatch

It is a visible piece of the 5.21 feel and the messages themselves now match,
so this is the largest remaining difference in an interactive session. The
curses, Tk and web UIs have their own status areas, so #49 changes the CLI
only.


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
Curses and Tk set `interactive_mode` and define `cmd_renum`, so RENUM in the
immediate line works there. Two differences are left:

- The web UI sets `interactive_mode` only when RUN starts, and it defines only
  `cmd_new`. RENUM, DELETE, LOAD, SAVE, MERGE and CHAIN in the immediate line
  fail (#50).
- Tk prints `Renumbered (a to b)` after RENUM. Real MBASIC prints nothing, and
  the CLI and curses print nothing (#51).


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
  and NOT work bit by bit on 16-bit integers. The check of the operands for
  16-bit overflow is Done (#54), see the AND, OR, XOR entry below.
- `src/codegen_js_backend.py` `_start_ok` (in `_generate_for`) is
  `(_step > 0) ? (v <= end) : (v >= end)`, which gets STEP 0 wrong in the
  opposite direction from the bug fixed in the interpreter. The C backend
  also gets STEP 0 wrong. The C part is Done (#55): the C backend ends a
  STEP 0 loop only when the variable equals the end, at FOR and at NEXT. The
  JavaScript part is still open (#55).
- AND, OR, XOR, EQV, IMP and NOT: the JavaScript backend now matches real
  MBASIC (GitHub issue 15, `docs/dev/JS_LOGICAL_OPERATORS.md`). The
  interpreter does not: it truncates a fractional operand (`NOT 2.7` is -3,
  real MBASIC -4) and it accepts operands outside -32768..32767
  (`40000 OR 1` is 40001, real MBASIC stops with Overflow) (#56). The C
  backend matches real MBASIC. Done (#54): it rounds a fractional operand, and
  an operand outside -32768..32767 after rounding is Overflow. `\` and MOD with
  a zero divisor are Division by zero. One edge stays open: `-32768 \ -1`
  wraps to -32768 in the C backend, where MBASIC gives 32768.
- `src/codegen_js_backend.py` writes WHILE and WEND as a JavaScript `while`
  block, so a WHILE and its WEND on different lines make invalid JavaScript
  (`Unexpected token 'case'`). The same fault is listed in
  `docs/dev/JS_CONTROL_FLOW.md` (#57, high severity).
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
