# AND, OR, XOR, EQV, IMP and NOT in the generated JavaScript

**Status:** Done (GitHub issue 15)
**Test:** `tests/regression/integration/test_js_logical_ops.py`

## Problem

The JavaScript that `--compile-js` makes did not follow MBASIC for the
logical operators:

* AND and OR became `&&` and `||`. These return one operand, not a bitwise
  result. `12 AND 3` was 3 (true) and not 0.
* XOR, EQV and IMP made invalid JavaScript. Node stopped with a
  `SyntaxError`.
* NOT did not round its operand.

## What the compiler does now

The compiler writes a call to a runtime function for each operator: `_and`,
`_or`, `_xor`, `_eqv`, `_imp` and `_not`. Each function converts its
operands with `_ci`:

* The function rounds an operand to the nearest integer. A half goes away from zero:
  `NOT 2.7` is -4, `2.5 AND 3` is 3, `-2.5 OR 0` is -3.
* An operand outside -32768 to 32767 gives `Overflow`.
* A comparison gives -1 or 0, so `(A=1) AND (B=2)` works as before.

`IF 12 AND 3` uses the plain JavaScript truth test of the result. The
test is correct because the result is a number.

## Check against real MBASIC 5.21

The range of an operand is -32768 to 32767. Real MBASIC 5.21 gives
`Overflow` for `32768 AND 1`, `65535 AND 255` and `40000 OR 1`. The test
compares 27 values and 9 overflow cases with real MBASIC.

The interpreter follows real MBASIC too (issue 56): `PRINT NOT 2.7` gives -4
and `PRINT 40000 OR 1` gives `Overflow`.

## Differences that remain

* The JavaScript backend does not pass an Overflow from these operators to
  `ON ERROR`. Real MBASIC gives ERR=6 and the line number in ERL. The
  JavaScript prints `?Overflow` and stops. Other runtime errors (for example
  `CHR$(300)`) have the same limit.

## Hex and octal masks

The generator writes `&HFFFF` as -1 and `&H8000` as -32768, as real MBASIC
does, so `&HFFFF AND 1` is 1 and not an Overflow.
