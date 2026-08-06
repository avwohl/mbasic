# The expected outputs, checked against the real 5.21 binary

`basic/dev/tests_with_results/` holds pairs: `NAME.bas` and `NAME.txt`.
`utils/run_tests.py` runs each program through the interpreter and compares the
output with the `.txt` exactly.

Those `.txt` files were originally captured from **our own output**, which makes
them a record of what we did print rather than of what MBASIC prints. That is a
trap: fix a formatting bug and the tests break, because they were pinning the
bug. Eighteen of them had drifted that way.

They are now taken from the real binary. `utils/crosscheck_tests.py` runs every
test twice - once through `com/mbasic.com` under cpmemu, once through us - and
reports whether the two agree:

    python3 utils/crosscheck_tests.py

**34 of the 39 tests match the real binary character for character.** The five
that do not are listed below, each for a reason, and their `.txt` files hold
our output.


## What the cross-check found

Six areas, all confirmed against the binary and against the reconstructed 5.21
assembler in `/home/wohl/src/mbasic2025/mbasic_521/` - PRINT USING, error
reporting, the TRON trace, MOD and `\`, operator precedence, and zero-trip FOR.

### PRINT USING

Seven separate faults in one statement, all fixed (`src/basic_builtins.py`).
Four of them in the field formatting:

| | real 5.21 | was |
|---|---|---|
| `PRINT USING "##,###.##"; 12345.67` | `12,345.70` | `12,345.67` |
| `PRINT USING "##.##"; 1.005` | ` 1.01` | ` 1.00` |
| `PRINT USING "####"; -1234` | `%-1234` | `-1234` |
| `PRINT USING "#.###"; -0.5` | `-.500` | `-0.500` |
| `PRINT USING "#.#^^^^"; 1.5` | `0.2E+01` | ` 1.5E+00` |

- The value goes through the same conversion routine `PRINT` uses, so it is six
  significant figures for a single and sixteen for a double *before* the field
  rounds it to its own decimal places. This is the one the drift caught.
- The field's rounding is half away from zero, not Python's half to even.
- A minus sign, or the `+` of a `+` field, uses up one of the digit positions
  to the left of the point; a trailing sign does not.
- The zero in front of the point is printed only while there is room for it.
- A `^^^^` mantissa takes its integer-digit count from the field rather than
  normalising to one digit, and a double prints `D` where a single prints `E`.

118 forms were probed against the binary; all 118 now agree. Thirty-eight of
them are pinned in `tests/regression/interpreter/test_number_format.py`.

Three further PRINT USING faults came out of the same probing:

- **The format string is reused** until the value list is exhausted.
  `PRINT USING "###"; 1; 2; 3` is `  1  2  3` on the binary; we printed `  1`
  and dropped the rest. Scanning stops the moment a *field* finds no value,
  after the literal text passed on the way has already gone out - which is why
  `"### ###"` with three values ends in a trailing space.
- **A comma delimits the value list** as readily as a semicolon.
  `PRINT USING "###"; 1, 2` was a syntax error here. That alone was why
  `brutef.bas` and `simcvt.bas` sat in `basic/dev/bad_syntax/`; both now parse
  clean.
- **A trailing `;` or `,` suppresses the newline**, as on a plain PRINT.
- **Punctuation with no digit positions after it is a literal.** `"A.B"` prints
  `A.B` and then stops with `Illegal function call`, having never found a field
  to put the value in; `"+###+"` of 42 is ` +42+`; `"-#"` of 5 is `-5`.

### Untrapped error reporting

The message was built out of the Python exception:

    ?RuntimeError in 50: Cannot open NOSUCH.DAT: Cannot open NOSUCH.DAT: No such file or directory
      50 OPEN "I",1,"NOSUCH.DAT"

against the binary's

    File not found in 50

There is no leading `?`, no exception class name, no Python text and no echo of
the source line. Direct mode drops the ` in <line>` and prints the message
alone. The Python detail still reaches stderr through `debug_log_error`, which
is where it belongs. `src/error_codes.py` had the message table all along and
nothing imported it; `error_code_for()` now recovers the MBASIC code from what
was raised, and the *canonical* text is what gets printed.

Two behaviours went with it:

- **A failed CHAIN or MERGE now stops the program.** It reported the failure by
  printing, which left the PC alone, so execution ran on to the next line.
- **A float divide by zero is not an error at all.** With no handler armed the
  binary prints a bare `Division by zero`, substitutes machine infinity
  (1.70141E+38, keeping the dividend's sign) and carries on inside the
  expression. We stopped the program. The integer forms, `5 \ 0` and
  `5 MOD 0`, go through a different path in the binary and really are fatal.
  With `ON ERROR` armed it is an ordinary trappable error, ERR 11.

Six conditions were not detected at all and now are: `A$ = 5` and `A = "X"`
(`Type mismatch`), `C% = 40000` (`Overflow`), a second `DIM` of the same array
(`Duplicate Definition`), `MID$("A",0)` (`Illegal function call`), and a `FOR`
or `WHILE` with no terminator. `GOTO 9999` reported `Invalid PC: PC(9999.0)` at
line 9999; it is `Undefined line number` at the line doing the jumping.

ERR was 5, `Illegal function call`, for a dozen errors that have codes of
their own - the reporter and the ERR variable were reading two different copies
of the same guesswork. Both now go through `src/error_codes.py`, so `ERROR 21`
is error 21 and prints `Unprintable error`, which is what the binary calls any
code with no message of its own.

Making `DIM` refuse to re-dimension also turned up an older bug in `ERASE`,
twice over: it deleted under the name as written while `DIM` stores under the
resolved one, and the parser resolved `DIM M(64)` against a `DEFINT` while
leaving `ERASE M` alone. The `ERASE M : DIM M(64)` idiom had been silently
erasing nothing at all.

25 error provocations were run on both engines; all 25 now agree, message and
halting alike. They are pinned in
`tests/regression/interpreter/test_error_messages.py`.

### The TRON trace

`[nnn]` is written with no newline of its own, and only when execution *enters*
a line, so the binary gives

    [130][140][150][160]Result: 50

We printed one bracket per line, re-traced on RETURN into the middle of a line,
and traced lines whose `TRON` only ran part way along them.

### MOD and `\`

Both truncate toward zero rather than flooring, both round their operands to
integers first with halves away from zero, and both require the result to fit
16 bits:

    -10 MOD 3   real -1     was 2          (the remainder takes the dividend's sign)
    -10 \ 3     real -3     was -4
    7.6 MOD 3   real  2     was 1.6        (operands are CINT'd, so 7.6 is 8)
    40000 \ 2   real Overflow  was 20000

### Operator precedence

`*` and `/`, `\`, `MOD`, and `+` and `-` are four separate levels in MBASIC's
operator table, not three. `\` and `MOD` were sharing a level with `*`:

    12 \ 2 * 3     real 2     was 18       (it is 12 \ 6)
    12 MOD 5 * 2   real 2     was 4        (it is 12 MOD 10)

### Zero-trip FOR

`FOR I = 10 TO 1` must not run its body at all, and must leave I at 10. We ran
it once and left I at 11.

MBASIC never falls into the body: `FOR` scans forward for its `NEXT` and jumps
*to* it with the increment suppressed, so the ordinary termination test is what
ends the loop. Entering through the `NEXT` rather than skipping past it is what
makes

    10 FOR I=10 TO 1 / 20 PRINT "BODY" / 30 NEXT J

report `NEXT without FOR in 30` - the NEXT still runs, and still checks the name
it was given. The termination test is a sign comparison, which is why
`FOR I = 1 TO 0 STEP 0` runs for ever and `FOR I = 5 TO 5 STEP 0` does not run
at all.


## The five that do not match

### Microsoft Binary Format, deliberately

Our arithmetic is IEEE binary32/64; MBASIC's is MBF. That is a project
decision - see `src/number_format.py` - so these differ and should.

- **log10k** - `Error: .5461504873501326` against our `.5457254793072934`,
  accumulated over the benchmark.
- **test_type_conversion** - `CDBL` of a single 3.14 is `3.139999866485596`
  there and `3.140000104904175` here.
- **test_math_functions** - the binary does *not* print `PASS: ^ works` or
  `PASS: Trig functions work`, because `5 ^ 2 = 25` is false on it: `^` is
  computed as `EXP(Y*LOG(X))` and lands on 24.999998, which prints as 25 and
  compares as less than it.
- **test_random_files** - one line. `A = VAL("99.99")` does not compare equal to
  the literal `99.99` on the binary, because its ASCII-to-float routine is a
  little less accurate than IEEE's correct rounding.

### A statement 5.21 has not got

- **test_file_io** - `OPEN "A"` (append) is not a 5.21 file mode; the binary
  answers `Bad file mode in 270` and stops. Everything before that line matches.
  Append is ours; see `docs/dev/MBASIC_521_DIVERGENCES_TODO.md`.


## What the fixes changed elsewhere

Zero-trip FOR, the MOD/`\` semantics and the error reporting reach every
program, so all 536 `.bas` files under `basic/` were run against a pristine
tree and against the patched one and the outputs diffed - three times, once
after each round of changes. Discounting programs whose output depends on where
a 15-second timeout happened to cut them, **200 changed on the final pass, and
every one traces to an intended fix**:

    164   the error message reformatted - one canonical line where there had
          been "?PythonError in N: ..." and an echo of the source
     27   the program stops earlier, or prints fewer lines: an untrapped error
          now halting, the source echo gone, or a trailing ';' on PRINT USING
          no longer breaking the line
      5   the tests in this directory, changed on purpose
      4   the program gets *further* - charfreq.bas past its division by zero,
          brutef.bas past the PRINT USING comma, xlabels and bmodem1 to a more
          accurate error

The earlier pass, before the error work, is the one worth reading for the loop
change. 27 programs changed then, and they divide into:

- **Zero-trip FOR, correcting a real failure.** `basic/games/superstartrek.bas`
  used to die on its first command with `ASC of empty string`, because
  `9450 FOR I=1 TO LEN(ZZ$)` ran once on an empty string. It now plays.
  `cpm-pert.bas`, `handplot.bas`, `prime1.bas`, `charfreq.bas` and nine games
  are the same shape: a loop bounded by a count that came out zero.
- **Programs that were never MBASIC.** `xlabels.bas` and seven files in
  `basic/dev/bad_syntax/` still fail, at a different point or with a different
  message. Two were checked: `surround.bas` now says `Type mismatch` rather
  than `Division by zero` for `"a" \ "b"`, which is what the binary says, and
  `hexbin11.bas` reaches an undefined line instead of a bad subscript.

Two genuine regressions turned up in those sweeps and were fixed. IEEE's
negative zero was being treated as a negative number, so
`PRINT USING "$$#####.##"` of `TD * (-1)` printed `-$0.00` - MBF has no signed
zero, and every zero total in `basic/business/budget.bas` had a minus in front
of it. And once the FOR/NEXT scan became unconditional, its blind spot for
clause statements became fatal: `basic/utilities/million.bas` waits for a key
with

    0 PRINT "...":FOR I=-32767 TO 32767:X$=INKEY$:IF LEN(X$)=1 THEN GOTO 1 ELSE NEXT I

and counting only top-level statements found no NEXT at all. The scan now looks
inside THEN and ELSE clauses, as MBASIC's does.

## Test programs that had to change to be checkable at all

Four could never have matched, whatever the interpreter did.

- **test_file_io**, **test_random_files** - opened `/tmp/test_file.txt` and
  friends, which CP/M cannot name. They now use 8.3 names in the working
  directory and tidy up after themselves.
- **test_chain**, **test_merge** - CHAINed and MERGEd `/tmp/chain_target.bas`
  and `/tmp/merge_overlay.bas`, which have never existed in this repo, so both
  engines only ever produced a file-not-found. They now write the program they
  are going to chain to or merge, then use it, then delete it. Both are
  binary-verified, `CHAIN ... , , ALL` variable passing included.
- **test_deftypes**, **test_input** - used `NAME$` as a variable. `NAME` is a
  reserved word on the binary (the CP/M file-rename statement), so both died
  with a syntax error at that line and lost every test after it. Renamed to
  `NM$`.

Two interpreter fixes came out of that work: `CHAIN "CHNTGT.BAS"` was looking
for `CHNTGT.BAS.bas`, and a MERGE inside a running program was printing a
summary the binary does not print.
