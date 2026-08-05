# Arithmetic was done in double, and MBASIC does it in single

**Created:** 2026-08-05
**Status:** Fixed - `src/number_format.py`, `src/runtime.py`, `src/interpreter.py`,
`src/basic_builtins.py`, `src/lexer.py`, `src/parser.py`, `src/tokens.py`,
`src/ast_nodes.py`
**Regression test:** `tests/regression/interpreter/test_single_precision.py`
**Follows:** `NUMBER_FORMATTING.md`, whose "Known limitation" section this closes

Printing numbers correctly left one hole open, and it showed the moment a
single-precision result was widened into a double:

	F# = 1/3      real 5.21 .3333333432674408      here .3333333333333333
	B# = .1       real 5.21 .1000000014901161      here .1
	D# = SQR(2)   real 5.21 1.414213538169861      here 1.414213562373095

Every value was computed and stored as a Python float - an IEEE double. MBASIC
works in single precision unless everything involved is double, so the real
machine's answer carries an error that ours did not have. PRINT could hide it
at six significant figures; a double could not.

## The model

MBASIC stores a single in Microsoft Binary Format: sign, 8-bit exponent, 24-bit
mantissa. The mantissa is the same width as IEEE float32, so rounding through
float32 reproduces MBF exactly for values in range - measured, not assumed, and
every expectation in the test file came off the real binary under cpmemu.

`src/number_format.py` gained three functions: `to_single()`, `to_integer()`,
and `coerce_to_type(value, suffix)` which dispatches on a variable's type. The
rounding happens in three places, and all three are needed:

* **Storing.** `Runtime.set_variable()` and `set_array_element()` coerce to the
  resolved type, so `DEFSNG S: S = 1#/3#` loses the digits a single cannot hold
  the moment it lands.
* **Arithmetic.** `Interpreter.evaluate_binaryop()` rounds a float result when
  the expression's type is single. Rounding only at assignment is not the same
  thing - double rounding gives a different answer as soon as an expression has
  more than one operation in it.
* **Reading.** A literal is single before it is used at all (`B# = .1` is
  `.1000000014901161`), and so is a function result: `SQR(2#)` is
  `1.414213538169861` on the real binary, the same as `SQR(2)`. MBASIC's maths
  functions work in single whatever they are handed.

Exact integer results are deliberately left as Python ints. Rounding them would
turn subscripts and string lengths into floats for nothing - MBASIC's integers
are 16-bit, far inside what a single holds exactly.

The type still comes from the expression, via `_numeric_digits()` - see
`NUMBER_FORMATTING.md`. It is now asked on every operation rather than once per
PRINT, so the answer is cached on the node (`_mb_digits`); it is a static
property of the tree and cannot change.

## Two things had to survive parsing

Neither of these was decidable before, because the information was thrown away:

* **A literal's type suffix.** The lexer parsed `1#` and dropped the `#`, so the
  parser saw the same `1.0` for `1` and `1#` and `1#/3#` could not be typed as
  double. `Token.literal_text` now carries the number as written, and the parser
  puts it in `NumberNode.literal` - which was always *documented* as the original
  text and had been holding the value instead. A `&HFF` keeps its own spelling
  too, which the serializer can use.
* **A DEF FN call's suffix.** `FNB#(1#)` is double and `FNA(1)` is single, but
  the parser strips the suffix from the name for lookup, so both arrived as
  `fnb`/`fna`. `FunctionCallNode.type_suffix` now records what the call was
  written with. The lookup key is unchanged, so the existing deviation - `DEF
  FNA` and `DEF FNA$` are one function here and two on the real machine - is
  still there, untouched and separate.

## What else was found while measuring

**Every float-to-integer conversion truncated instead of rounding.** MBASIC
rounds to nearest, halves away from zero, wherever it wants an integer and is
handed a fraction. Python's `int()` truncates and Python's `round()` is
banker's rounding, so both were wrong, in opposite directions:

	A% = 3.7                     real 4        was 3
	A% = -3.7                    real -4       was -3
	CINT(2.5)                    real 3        was 2
	LEFT$("ABCDEF",2.7)          real ABC      was AB
	RIGHT$("ABCDEF",2.7)         real DEF      was EF
	MID$("ABCDEF",2.7,1.6)       real CD       was B
	STRING$(2.7,"X")             real XXX      was XX
	CHR$(65.7)                   real B        was A
	TAB(4.7)                     real col 5    was col 4
	A(2.7)  with A(3)=33         real 33       was 22
	DIM B(2.7)                   real B(3) ok  was subscript out of range
	ON 1.7 GOTO 30,40            real 40       was 30

The subscript one is the worst of them: it silently read and wrote the wrong
array element. All of these now go through `to_integer()`, which is the one
place the rule lives. `INT` and `FIX` are deliberately left alone - flooring
and truncating is what they are for.

**Assigning a string to a numeric variable stopped erroring.** Rounding cannot
be applied to a string, and passing it through would have stored the wrong
type, so `coerce_to_type()` raises `TypeError("Type mismatch")` - which the
interpreter already maps to error 13, the code the real binary reports.

**FOR left the loop variable one step short.** `FOR I=1 TO 3: NEXT I: PRINT I`
printed 3 here and prints 4 on the real binary. The increment was only stored on
the branch that continues the loop, so a program reading the variable afterwards
got the last value that still fit rather than the value that ended the loop.
Programs do read it, and with a fractional STEP the difference is bigger than
one step:

	FOR L=1 TO 2 STEP .1: NEXT L      real 2.000000238418579     was 1.9

## The arithmetic is native, and deliberately so

Single is IEEE binary32 and double is IEEE binary64 - a C++ `float` and a C++
`double`. Nothing here emulates Microsoft Binary Format arithmetic. `to_single`
is a `struct` round-trip because MBF and binary32 carry the same 24 mantissa
bits, not because MBF is being reproduced, and the maths functions call libm.

That is a decision, not an accident: MBASIC's arithmetic was poor, and
reproducing its errors would mean writing worse code to get worse answers. The
only place in the interpreter that touches MBF byte layout is
`src/mbasic_rnd.py`, and that is an algorithm being reproduced rather than an
arithmetic - even there the multiply and add are done in binary32.

### The one thing this leaves crooked: the maths functions are single

MBASIC's library functions are single-precision *by signature*, the way C's
`sqrtf` is. `_FUNCTION_PRECISION` in `src/interpreter.py` reproduces that: SQR,
SIN, COS, TAN, ATN, LOG, EXP, CSNG and the rest return a single whatever they
are given, and only CDBL, CVD and VAL return a double.

So a double argument still comes back with binary32 accuracy:

	A# = SQR(2#)     1.414213538169861    here, and on the real machine
	                 1.4142135623730951   what binary64 would give

This is a typing rule rather than emulated arithmetic - the value is computed
by libm in double and *then* rounded to binary32, so it is the correctly
rounded single, not MBASIC's answer. It is worth knowing that the two are
usually the same thing: measured against the binary, SQR, LOG, EXP, COS and `^`
agree exactly once rounded to single.

Where they do not agree is SIN, TAN and ATN, by about one ulp - `SIN(1)` is
`.841471016407013` there and `.8414709568023682` here. That is not a gap on our
side. MBASIC evaluated its own polynomial and got the last bit wrong; we call
libm and get it right. The difference grows where cancellation magnifies it -
`SIN(3.14159)` is `2.8088E-06` there and `2.53518E-06` here - and it is the
real machine that is wrong in that pair.

To make the functions follow their argument's type instead, `_numeric_digits`
would return the argument's precision for them rather than consulting
`_FUNCTION_PRECISION`. That is a few lines, and it would make `A# = SQR(2#)`
more accurate and no longer what MBASIC printed. It has not been done, because
the type of an expression is language semantics and the accuracy of the
arithmetic is not.

## What still differs
* **SIN, TAN and ATN**, by about one ulp, because we are right and MBASIC was
  not - see above. Listed here only so nobody re-measures it and files it as a
  bug.
* **Double literals at extreme exponents.** `1D-16` is `9.999998845134855D-17`
  there and `1.000000016862384D-16` here: MBASIC's ASCII-to-float routine is
  less accurate than IEEE's correctly-rounded conversion. Arithmetic on ordinary
  values agrees.
* **The sixteenth digit of a double.** `2#/3#` is `.6666666666666667` there and
  `.6666666666666666` here, because MBASIC's double is a 56-bit binary format
  rather than IEEE 754. Carried over from `NUMBER_FORMATTING.md`; it needs the
  arithmetic emulated, not just the storage.

## Effect on the 200 programs in basic/

All of them were run before and after, and 35 printed something different.

Twenty-seven of those use RND, which was seeded per run here, so they differed
between two runs of the *same* build - noise, not a change. (That gap is now
closed: RND reproduces the real binary's sequence, `.245121 .305003 .311866`
and on. See `RND_ALGORITHM.md`.) Two more, `ykw1` and `ykw2`, are long enough
to hit the sweep's timeout at a different point each run.

The six that genuinely changed all changed the way they should, and where the
program is self-running it was checked against the real binary:

	education/mathtest    26 lines differed from the real binary, now 21;
	                      what is left is the SIN/TAN/ATN gap above
	business/log10k       error term .5457254793072934 -> .546215616443078,
	                      against .5461504873501326 on the real binary
	incompatible/fprod1   a cancellation residue of 7.10543E-15 is now 0,
	                      which is what single precision does to it
	games/rocket, incompatible/fprod   a TAB column moved, because TAB now
	                      rounds its argument
	games/lunar           a fuel figure of 5016 is now 5015

## Cost

About 5% on a loop of 40,000 iterations doing three arithmetic operations each
(12.35s to 13.15s, and 14.10s to 14.58s on a second run) - the extra work is a
`struct` round-trip per single-precision float result, and a cached lookup of
the node's type.

## Verifying

	python3 tests/regression/interpreter/test_single_precision.py

84 checks: the coercions on their own, 41 whole programs whose output is what
MBASIC 5.21 printed for them, twelve fractions where an integer is wanted, a
Type mismatch, INPUT, where FOR leaves the loop variable, and that the literal
suffix reaches the tree.

The four `numfmt` matrices from `NUMBER_FORMATTING.md` were re-run against the
real binary: the one that tested widening across precisions is now identical,
and what remains is the three items above.
