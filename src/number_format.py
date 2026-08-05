"""How MBASIC 5.21 represents and prints a number.

Derived from the real binary under cpmemu rather than from the manual, which is
wrong about the boundaries: it says 10^-7 prints as 1E-7, and the binary prints
.0000001.

The rules, with the value rounded to `digits` significant figures first (6 for
single precision, 16 for double):

* A number is always followed by a space, and preceded by one if it is not
  negative. PRINT 1;2;-3 gives " 1  2 -3 ".
* There is no leading zero: .5, not 0.5.
* Trailing zeros are dropped, and so is a trailing point.
* Unscaled while it fits, scaled when it does not:

      value >= 1     unscaled while the integer part needs no more than
                     `digits` digits.  999999 prints as 999999 and 1000000
                     as 1E+06.
      value < 1      unscaled while the zeros after the point plus the
                     significant digits come to no more than digits + 1.
                     .0000001 prints unscaled (6 zeros + 1 digit), 1E-08
                     does not (7 + 1), and so does .00012345 (3 + 5 = 8).

* The exponent is at least two digits and always signed: 1E+06, 1E-08.
  Double precision uses D where single uses E: 1.234567890123457D+16.

What decides `digits` is the *type* of the expression, not the value - see
Interpreter._numeric_digits(). A single-precision 1/3 prints as .333333 and a
double-precision one as .3333333333333333.
"""

import struct
from decimal import Decimal, ROUND_HALF_UP, Context

#: Significant figures MBASIC keeps for each precision. None means the
#: value is INTEGER-typed and prints as a plain whole number.
INTEGER_DIGITS = None
SINGLE_DIGITS = 6
DOUBLE_DIGITS = 16


def format_number(value, digits=SINGLE_DIGITS):
    """The characters MBASIC prints for a number, without the padding spaces.

    Args:
        value: an int or float.
        digits: significant figures - SINGLE_DIGITS or DOUBLE_DIGITS, or None
            for an INTEGER-typed value.

    Returns:
        str, e.g. "3934.03", ".333333", "1E+06", "-1.23457E+06".
    """
    if isinstance(value, bool):             # bool is an int; BASIC has neither
        value = int(value)

    if digits is None:
        # An INTEGER-typed value (%), which prints as itself - MBASIC's
        # integers only reach 32767 anyway. Note that a Python int is NOT
        # enough to take this path: a single-precision 1234567 is a whole
        # number and still prints as 1.23457E+06.
        return str(int(value))

    try:
        if value != value or value in (float('inf'), float('-inf')):
            return str(value)               # NaN/Infinity: nothing to imitate
    except (TypeError, ValueError):
        return str(value)

    if value == 0:
        return "0"

    negative = value < 0
    rounded = _round_to_digits(abs(value), digits)
    exponent = rounded.adjusted()           # power of ten of the leading digit
    significant = _significant_digits(rounded)

    if exponent >= 0:
        unscaled = (exponent + 1) <= digits
    else:
        unscaled = (-exponent - 1) + significant <= digits + 1

    text = _unscaled(rounded) if unscaled else _scaled(rounded, digits)
    return "-" + text if negative else text


def format_for_print(value, digits=SINGLE_DIGITS):
    """As printed in a PRINT list: a leading space unless negative, and a
    trailing space always.

        PRINT 1;2;-3      ->  " 1  2 -3 "
    """
    text = format_number(value, digits)
    if not text.startswith("-"):
        text = " " + text
    return text + " "


def _round_to_digits(value, digits):
    """Round a positive value to `digits` significant figures."""
    context = Context(prec=digits, rounding=ROUND_HALF_UP)
    return context.create_decimal(repr(float(value))).normalize(context)


def _significant_digits(rounded):
    """How many significant figures a rounded Decimal actually carries."""
    return len(rounded.as_tuple().digits)


def _unscaled(rounded):
    """Plain decimal notation: no leading zero, no trailing zeros."""
    text = format(rounded, 'f')
    if '.' in text:
        text = text.rstrip('0').rstrip('.')
    if text.startswith('0.'):
        text = text[1:]                     # .5, not 0.5
    return text or "0"


def _scaled(rounded, digits):
    """Exponential notation, MBASIC style: 1E+06, 1.23457E+06, 1.5D-08."""
    exponent = rounded.adjusted()
    mantissa = rounded.scaleb(-exponent)

    text = format(mantissa, 'f')
    if '.' in text:
        text = text.rstrip('0').rstrip('.')

    letter = 'D' if digits > SINGLE_DIGITS else 'E'
    sign = '+' if exponent >= 0 else '-'
    return f"{text}{letter}{sign}{abs(exponent):02d}"


def to_single(value):
    """Round to MBASIC single precision.

    MBASIC stores a single as Microsoft Binary Format: sign, 8-bit exponent,
    24-bit mantissa. The mantissa is the same width as IEEE float32, so a
    round-trip through float32 reproduces it - 1/3 becomes .3333333432674408
    and 1/7 becomes .1428571492433548, which is exactly what the real binary
    prints for a single-precision result stored in a double.

    The two formats are not identical: MBF has no infinities or denormals, and
    its ASCII-to-float routine is a little less accurate than IEEE's correct
    rounding, so a decimal literal at the extremes can land an ulp or two away
    (1E-16 is 9.999998845134855E-17 there and 1.0000000168623835E-16 here).
    Arithmetic on ordinary values agrees.
    """
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return value
    try:
        return struct.unpack('f', struct.pack('f', value))[0]
    except (OverflowError, struct.error, ValueError):
        # Outside float32's range - MBF would say "Overflow"; leaving the value
        # alone keeps the existing behaviour rather than inventing an error.
        return value


def to_integer(value):
    """Round to MBASIC's integer type: nearest, with halves away from zero.

    A% = 3.7 is 4 and A% = -3.7 is -4, measured against the real binary -
    assignment to an integer variable rounds, it does not truncate. A% = 2.5
    is 3, so it is not Python's banker's rounding either.

    The same rule applies everywhere MBASIC wants an integer and is handed a
    fraction: LEFT$("ABCDEF",2.7) is "ABC", CHR$(65.7) is "B", and A(2.7) is
    A(3). INT and FIX are the exceptions - flooring and truncating is their job.
    """
    if isinstance(value, str):
        # Rounding a string is not something to be quiet about, and every
        # caller wants an integer, so this is the error the real binary gives.
        raise TypeError("Type mismatch")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return value
    if isinstance(value, int):
        return value
    try:
        return int(Decimal(repr(value)).quantize(Decimal(1), ROUND_HALF_UP))
    except (ValueError, ArithmeticError):
        return int(value)


def coerce_to_type(value, suffix):
    """Store a value the way a variable of this type would hold it.

    This is what makes a single-precision variable lose the digits it cannot
    hold: F# = 1/3 shows .3333333432674408 because the division happened in
    single precision, not because printing rounded it.
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        if suffix in ('%', '!', '#', None):
            # A% = "X" is a Type mismatch on the real binary. It has to be
            # caught here: rounding a string is not something to be quiet
            # about, and silently storing it would let the wrong type through.
            raise TypeError("Type mismatch")
        return value
    if not isinstance(value, (int, float)):
        return value
    if suffix == '%':
        return to_integer(value)
    if suffix == '#':
        return float(value)
    if suffix in ('!', None):
        return to_single(value)
    return value
