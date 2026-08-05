# Numbers printed as Python, not as MBASIC

**Created:** 2026-08-05
**Status:** Fixed - `src/number_format.py` (new), `src/interpreter.py`,
`src/basic_builtins.py`
**Regression test:** `tests/regression/interpreter/test_number_format.py`

Noticed while making `basic/games/startrek.bas` run, which reported
`ENERGY = 3934.027898842015` where the real binary says `3934.03`. PRINT was
handing out Python's `repr` for floats and `str` for ints:

	PRINT 1/3           0.3333333333333333      should be   .333333
	PRINT SQR(2)        1.4142135623730951      should be   1.41421
	PRINT 0.1+0.2       0.30000000000000004     should be   .3
	PRINT 1000000!      1000000                 should be   1E+06
	K%=7: PRINT K%      "7", with no spaces      should be  " 7 "

## The rules, from the binary rather than the manual

The manual's account is wrong about the boundaries - it says 10^-7 prints as
`1E-7`, and the binary prints `.0000001` - so every rule here was measured
against `com/mbasic.com` under cpmemu.

* A number is always followed by a space, and preceded by one unless it is
  negative. `PRINT 1;2;-3` gives `" 1  2 -3 "`.
* No leading zero: `.5`, never `0.5`.
* Trailing zeros go, and so does a trailing point.
* Unscaled while it fits, scaled when it does not, and the boundary differs
  above and below 1:

      value >= 1   unscaled while the integer part needs no more than
                   `digits` digits.  999999 prints as itself, 1000000 as 1E+06.
      value < 1    unscaled while the zeros after the point plus the
                   significant digits come to no more than digits + 1.
                   .0000001 fits (6 + 1), 1E-08 does not (7 + 1), and neither
                   does .00012345 (3 + 5 = 8).

* Exponents are signed and at least two digits: `1E+06`, `1E-08`. Double
  precision uses `D`: `1.234567890123457D+16`.

## Precision comes from the type, not the value

	A  = 1/3 : PRINT A       .333333
	A# = 1#/3# : PRINT A#    .3333333333333333

Same arithmetic, different answers, because MBASIC shows six significant
figures for a single-precision value and sixteen for a double. So the formatter
has to be told which, and the answer is a property of the *expression*.

`Interpreter._numeric_digits()` reads it off the tree: a variable's suffix, a
literal's form, the wider of a binary operation's two sides, and a small table
for the functions that are not single precision. Nothing about the evaluator or
the values it computes changes - which is what keeps this from being a rewrite
of the arithmetic.

Literals are typed the way MBASIC types them: more than seven significant
figures makes one double. That is why `PRINT 1234567` gives `1.23457E+06` and
`PRINT 12345678` gives `12345678`.

One wrinkle found on the way: `NumberNode.literal` is documented as "Original
text representation" and actually holds the value, so `1E6` arrives as
`1000000.0`. The significant figures are therefore counted from the value. The
two disagree only for a literal padded with trailing zeros - `1000000.0` is
eight typed digits but one significant one - which is a corner nobody writes.

## Also fixed: PRINT USING lost the minus sign

	PRINT USING "###.##"; -3.14      printed "  3.14"

The sign was worked out and stored in `sign_char`, and then never appended to
the result. Only the `+`-in-format and trailing-sign paths ever emitted one, so
a plain field printed negative numbers as positive - silently, in the statement
whose entire purpose is tidy reports. The overflow path had the same hole:
`%123.46` where the binary says `%-123.46`.

Placement is the binary's: `-$12.50` for `$$###.##`, `**-12.50` for `**###.##`.

## Verifying

	python3 tests/regression/interpreter/test_number_format.py

29 checks. Thirty-three values through the formatter, the spaces around a
printed number, fourteen programs through PRINT where the expression type sets
the precision, the same value at both precisions, STR$, and six PRINT USING
fields with negative numbers. Every expectation is what the real binary
printed.

## Known limitation: single-precision arithmetic

Values are computed and stored as IEEE doubles. MBASIC computes in single
precision unless everything involved is double, so a single-precision result
*widened* into a double shows the difference:

	F# = 1/3      real 5.21 .3333333432674408    here .3333333333333333
	E# = 1/7      real 5.21 .1428571492433548    here .1428571428571429

The division happened in single on the real machine, and the error is preserved
when the result is stored in a double. Printing cannot recover that - it needs
single-precision storage (a float32 round-trip on assignment) and type-directed
arithmetic, which changes every computed value in the interpreter rather than
just its presentation.

Everything that does not cross precisions this way now matches exactly.

A second, smaller gap sits underneath it: MBASIC's double is a 56-bit binary
format, not IEEE 754, so the sixteenth digit can differ - `2#/3#` is
`.6666666666666667` there and `.6666666666666666` here. That one needs the
arithmetic to be emulated, not just the storage.
