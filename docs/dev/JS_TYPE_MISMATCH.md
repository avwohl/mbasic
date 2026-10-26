# Type mismatch in the generated JavaScript

MBASIC 5.21 gives `Type mismatch` (error 13) when a statement uses a string
where it needs a number, or a number where it needs a string. The error comes
when the statement runs. `ON ERROR` can trap the error, and `ERL` gives the
line of the statement. All measurements here are from `com/mbasic.com` under
cpmemu.

## What the compiler does

The type of an expression is known from the program text. A name with `$`,
a string in quotes and a string function are strings. Everything else is a
number. `src/js_type_check.py` finds the type (`expr_kind`) and finds the
mismatches. The compiler writes the check into the code of the statement
that has the mismatch. For example, `PRINT 1+"a"` becomes
`(1.0, "a", _error("Type mismatch"))`.

A program with no mismatch gets no extra code and no run-time cost.
A statement that is never reached gives no error.

## Rules (measured)

- A string and a number under any operator: `Type mismatch`.
- Two strings: only `+` and the six comparisons are allowed. `-`, `*`, `/`,
  `^`, `\`, MOD, AND, OR, XOR, EQV and IMP give `Type mismatch`.
- Unary `-` and NOT on a string give `Type mismatch`. Unary `+` on a string
  is allowed: `PRINT +"a"` prints `a`.
- A comparison gives a number (-1 or 0), also for two strings.
- Assignment: `A$=1`, `A="x"`, `A=1:A$=A`, `DEFSTR S:S=1`, array elements,
  and `FOR A$=1 TO 2` give `Type mismatch`.
- IF and WHILE need a number: `IF "a" THEN` gives `Type mismatch`.
  `IF "a"="a" THEN` is a number and works.
- FOR start, limit and STEP, `ON x GOTO`, `MID$` as a statement, `LSET`,
  `RSET`, `SWAP A,A$` and RANDOMIZE follow the same rule.
- Built-in functions: `LEN`, `ASC`, `VAL`, `CVI`, `CVS` and `CVD` need a
  string. `ABS`, `INT`, `SQR`, `CHR$`, `STR$`, `SPACE$`, `HEX$`, `OCT$`,
  `PEEK`, `TAB`, `SPC` and the other number functions need a number.
  `LEFT$`, `RIGHT$` and `MID$` need a string and then numbers.
  `STRING$(n, x)` takes a number or a string as `x`. `FRE` and `POS` take
  either type.
- DEF FN: the arguments must match the parameters, and the value of the body
  must match the type of the function name. `DEF FNA$(X$)=1` gives the error
  when `FNA$` is called, not at DEF.
  A function name without a suffix takes its type from the DEFtype of the
  letter after FN (FNA uses the rule for A), not the letter F. A parameter
  without a suffix takes the DEFtype of its own letter. The parser applies
  both rules to the definition and to each call.
- OPEN, CLOSE, PRINT #, CLEAR and KILL/NAME: file numbers and sizes must be
  numbers, file names must be strings.
- PRINT USING: the format must be a string. A string goes with a string field
  (`!`, `\ \`, `&`) and a number goes with a numeric field.

## Other changes for this

- The constant folder and the rewrites of the semantic analyzer
  (`X*2` to `X+X`, `X*1` to `X`, and the others) skip an expression with a
  mismatch. Before, `"a"*2` became `"a"+"a"`, and `"a"*1` became `"a"`.
- The folder gives up on `-"a"`, `NOT "a"`, `ABS("a")` and a FOR with a
  string bound. Before, these stopped the compiler with a Python error.
- `DefFnStatementNode` has a `type_suffix` field, the type of the function.

## Differences that remain

- `DIM B("a")` stops the compile with "Semantic analysis failed". The
  JavaScript backend needs a constant DIM size at compile time (this is true
  for `DIM B(N)` too). The binary gives `Type mismatch` at run time.
- A mismatch that the compiler finds inside an operand of PRINT USING (for
  example `"a"*2`) is raised before the statement prints anything. A value of
  the wrong kind for its field prints the text before it, as the binary does.
- If one expression has both a Type mismatch and another run-time error
  (`"a"*CHR$(-1)`), the JavaScript code reports the Type mismatch after the
  operands, but the binary decides by operator. A program shows the difference only when both
  errors are present.
- `KILL 1` and `NAME 1 AS "b"` stop with "_fkill is not defined" or
  "_fname is not defined". The run-time functions are missing (a separate
  fault), so the argument check is not reached.
- `USR("a")` is `Illegal function call` on the binary. The compiler does not
  check the argument of USR.
- `LSET A$=1` for a variable that `FIELD` did not name stops with
  "_flset is not defined". The missing FIELD is a separate fault.
- `PRINT INPUT$(1)` in a PRINT list writes `await` inside a function that is
  not async, and the program does not load. The INPUT$ code is a separate fault.

## C backend

`SWAP A,A$` is refused too, and `PRINT +"a"` and `A$=+"b"` compile (unary
plus on a string is valid).

The C backend needed only these two changes in this work. It already refuses a program with a
string mixed with a number at compile time. `--compile-c` prints the line and
the words "Type mismatch", writes no C file, and exits with status 1. The
choice is on purpose: the C code has no way to raise a trappable error at
run time. A few messages name the node and not the cause (`PRINT "a"*2`
says `string expression BinaryOpNode`), but the compiler never stops with a
Python error.

## Test

`tests/regression/integration/test_js_type_mismatch.py`. Each expected text is
from the real binary.
