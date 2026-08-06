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


## 1. Errors that are still not detected

The reporting is right now - `<message> in <line>`, no `?`, program stops - and
25 provocations match the binary exactly. What is left is conditions we simply
do not notice. Each prints nothing at all where the binary raises:

| provocation | binary says |
|---|---|
| `A$=STRING$(200,65)` then twelve nested concatenations | `String formula too complex in 20` |
| `DIM A$(300)` filled with 200-character strings | `Out of string space in 20` |
| `FIELD #1, 100 AS A$` on a 16-byte record | `FIELD overflow in 20` |
| `OPEN "O",1,"A:B:C*?.X Y"` | `Too many files in 10` |
| a line longer than the 255-byte buffer | `Line buffer overflow in 10` |
| `LOAD` of a file with a line that has no number | `Direct statement in file` |
| running off the end of the program inside a handler | `No RESUME in <last line>` |

One more is wrong rather than missing:

- `PRINT 1E38*1E38` gives `1E+76`. On the binary a *floating-point* overflow is
  a warning like division by zero - it prints `Overflow`, substitutes machine
  infinity and carries on. Ours has no MBF range to overflow out of, which is
  the deliberate IEEE decision in section 9; the message is the part that is
  missing. The integer overflows (`C% = 40000`, `40000 \ 2`, `CINT(40000)`)
  are fatal and do now match.

`src/error_codes.py` still carries nine codes 5.21 has not got - 24, 25, 68-72,
75 and 76, all `Unprintable error` on the binary. Harmless, since nothing
produces them, but they are not 5.21.

FRCINT's 16-bit range check is applied to `\` and MOD operands and to `%`
assignment, but not yet everywhere the binary applies it: `A(40000)`,
`TAB(1E38)`, `STRING$(40000,65)`, `LEFT$("AB",1E38)`, `PEEK(70000)`,
`MKI$(40000)`, `SPACE$(40000)`, `HEX$(1E38)`, `OCT$(1E38)` are all `Overflow`
there.


## 2. ON ERROR, and what happens around a handler

The common path works - a trapped error reaches the handler with the right ERR
and ERL, and RESUME NEXT lands in the right place. The edges do not:

- `ON ERROR GOTO 0` inside a live handler should disable the handler **and**
  re-raise the pending error, reported at the line that originally failed. We
  only disarm and carry on.
- `ON ERROR GOTO <line that does not exist>` is `Undefined line number` at the
  `ON ERROR` statement on the binary - checked when it executes, not when it
  fires.
- A handler that ends with `END` makes us re-raise the original error at the
  END line. The binary just prints `Ok`.
- An error raised inside a handler crashes us with a Python `AttributeError`
  about `on_error_goto`.
- `Break in <line>` is printed twice, and CONT re-prints it instead of
  resuming.


## 3. Errors are reported, but not everywhere

`print_error` in `src/interactive.py` is now the single formatter, and the CLI
goes through it. The other five backends do not: `src/ui/curses_ui.py`,
`src/ui/tk_ui.py` and `src/ui/web/nicegui_backend.py` between them carry about
ninety hand-rolled format strings - boxed "┌─ Runtime Error ─┐" displays,
`f"Error at line {n}: {msg}"`, `f"{type(e).__name__}: {e}"` - each inventing
its own wording. They should call `format_error_message(error_code_for(e), n)`.

Also in `interactive.py`, roughly forty `print(...)` calls bypass `self.io`
entirely, so in curses, Tk and the web UI they go to a terminal nobody is
looking at.


## 4. Reserved words followed by a type suffix

`NAME$`, `LEN%`, `FOR$`, `TO%`, `ERR`, `ERL` are all syntax errors on the real
binary, and we accept them. Two of the tests here were written using `NAME$`
and died at that line on the binary; they have been renamed to `NM$`, but the
lexer rule is untouched.

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


## 5. Syntax errors are found at the wrong time

We reject a bad line when it is *entered*, print the complaint there, store the
line anyway, and then silently skip it when the program runs. The binary
crunches the line at entry without complaint and reports `Syntax error in 10`
at RUN - after which it opens the line editor on the offending line, which is
its own piece of behaviour we do not have.


## 6. The compiler backends are out of step with the interpreter

The precedence fix is in the parser, so every backend gets it. The operator
semantics are not:

- `src/codegen_js_backend.py` - `\` now truncates rather than flooring, but
  neither `\` nor MOD rounds its operands to integers first, and neither
  range-checks them. `7.6 MOD 3` is 2 in the interpreter and 1.6 here.
- `src/codegen_backend.py` - the C backend has no entry for `\` or MOD in its
  operator map at all (`_generate_binary_op`, around line 3324), so it emits
  `(a ? b)`. This predates the current work.
- `src/codegen_js_backend.py` `_match_for_next` (line ~236) pairs NEXT with FOR
  by *variable name* and jumps to a line rather than a statement, so it cannot
  reproduce `NEXT J`, `NEXT J,I` or a mid-line skip. Its `_start_ok`
  (line ~2091) is `(_step > 0) ? (v <= end) : (v >= end)`, which gets STEP 0
  wrong in the opposite direction from the bug fixed in the interpreter.


## 7. `serialize_expression` does not bracket under a unary minus

Found while checking the precedence change did not break RENUM. Pre-existing,
and unrelated to any of the above:

    -(A + B)   comes back out as   -A + B
    -(A * B)   comes back out as   -A * B

`_serialize_operand` in `src/ui/ui_helpers.py` is only reached from the binary
path; `UnaryOpNode` emits its operand with no brackets whatever it is. Every
binary case round-trips - `tests/regression/serializer/test_operator_brackets.py`
covers 34 of them - so the fix is to give the unary path the same treatment,
bracketing an operand whose precedence is looser than unary minus.

`-(A \ B)` happens to be safe (truncating division is odd-symmetric, so
`-(a \ b)` and `(-a) \ b` agree), but `-(A + B)` is a plain wrong answer.


## 8. Statements where we are ahead of 5.21

Not bugs so much as decisions to record - each one is a place where a program
that works here would not work on the real thing.

- `OPEN "A"` (append) is not a 5.21 file mode; the binary answers
  `Bad file mode`. `test_file_io.bas` uses it, which is why that test is not
  binary-verified.
- `MERGE` returns to command level on 5.21 - the rest of the program does not
  run. We carry on. (The summary line MERGE used to print is now suppressed
  when a running program merges, which is what the binary does.)


## 9. Deliberate, and staying that way

MBASIC's arithmetic is Microsoft Binary Format and ours is IEEE - a project
decision, see `src/number_format.py` and the note in
`docs/dev/TESTS_VERIFIED_AGAINST_BINARY.md`. These differ and should:

    CDBL of a single 3.14      real 3.139999866485596   ours 3.140000104904175
    5 ^ 2 = 25                 real false (EXP/LOG gives 24.999998)
    VAL("99.99") = 99.99       real false, and by a different amount than ours

The MBF *range* goes with it: 1E38*1E38 overflows there and does not here.
Machine infinity, 1.70141E+38, is nonetheless reproduced where it is
observable - a float divide by zero yields it, as it does on the binary.
