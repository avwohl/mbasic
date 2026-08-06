#!/usr/bin/env python3
"""
Test that numbers print the way MBASIC 5.21 prints them.

Every expectation here was taken from the real 5.21 binary running under
cpmemu, not from the manual - the manual is wrong about the boundaries, saying
10^-7 prints as 1E-7 where the binary prints .0000001.

What was wrong before:

    PRINT 1/3           0.3333333333333333      should be  .333333
    PRINT SQR(2)        1.4142135623730951      should be  1.41421
    PRINT 0.1+0.2       0.30000000000000004     should be  .3
    PRINT 1000000!      1000000                 should be  1E+06
    K%=7: PRINT K%      "7" with no spaces      should be  " 7 "

Python's repr was being printed for floats, and Python's str for ints - which
also lost the leading and trailing spaces that MBASIC puts around every number.

Two things decide the answer, and only one of them is the value:

* Precision comes from the *type* of the expression. A single-precision 1/3
  shows six significant figures and a double-precision one sixteen, from the
  same underlying float. Interpreter._numeric_digits() reads that off the
  expression tree, so the evaluator and every value it computes are untouched.
* Scaled or unscaled comes from the magnitude - see src/number_format.py.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.interpreter import Interpreter
from src.iohandler.base import IOHandler
from src.lexer import Lexer
from src.number_format import (format_number, format_for_print,
                               INTEGER_DIGITS, SINGLE_DIGITS, DOUBLE_DIGITS)
from src.parser import Parser
from src.runtime import Runtime

results = []


def check(condition, label):
    """Record one check; print pass/fail immediately."""
    results.append(bool(condition))
    print(f"{'PASS' if condition else 'FAIL'}: {label}")


class Capture(IOHandler):
    def __init__(self):
        self.parts = []

    def output(self, text, end='\n'):
        self.parts.append(str(text) + end)

    def input(self, prompt=''):
        return "0"

    def input_line(self, prompt=''):
        return "0"

    def input_char(self, blocking=True):
        return ""

    def clear_screen(self):
        pass

    def error(self, message):
        self.parts.append(f"Error: {message}\n")

    def debug(self, message):
        pass

    def text(self):
        return ''.join(self.parts)


def run(source):
    """Run a one-line program and return exactly what it printed."""
    ast = Parser(Lexer(source).tokenize()).parse()
    runtime = Runtime({line.line_number: line for line in ast.lines})
    handler = Capture()
    interpreter = Interpreter(runtime, handler)
    interpreter.start()
    for _ in range(50):
        state = interpreter.tick(mode='run', max_statements=5000)
        if not runtime.pc.is_running() or state.error_info:
            break
    return handler.text().rstrip('\n')


# ---------------------------------------------------------------------------
# The formatter on its own
# ---------------------------------------------------------------------------

#: (value, digits, expected) - every one of these is what the real binary
#: printed for the same number.
FORMATTER_CASES = [
    (0, SINGLE_DIGITS, "0"),
    (1, SINGLE_DIGITS, "1"),
    (-1, SINGLE_DIGITS, "-1"),
    (100, SINGLE_DIGITS, "100"),
    (3.14, SINGLE_DIGITS, "3.14"),
    (0.5, SINGLE_DIGITS, ".5"),                 # no leading zero
    (-0.5, SINGLE_DIGITS, "-.5"),
    (1 / 3, SINGLE_DIGITS, ".333333"),          # six significant figures
    (2 / 3, SINGLE_DIGITS, ".666667"),          # rounded, not truncated
    (10 / 3, SINGLE_DIGITS, "3.33333"),
    (2 ** 0.5, SINGLE_DIGITS, "1.41421"),
    (3934.027898842015, SINGLE_DIGITS, "3934.03"),
    (123456, SINGLE_DIGITS, "123456"),          # six digits fit
    (1234567, SINGLE_DIGITS, "1.23457E+06"),    # seven do not
    (999999, SINGLE_DIGITS, "999999"),
    (1000000, SINGLE_DIGITS, "1E+06"),
    (123456.7, SINGLE_DIGITS, "123457"),
    (1e30, SINGLE_DIGITS, "1E+30"),
    (-1234567, SINGLE_DIGITS, "-1.23457E+06"),
    (0.1, SINGLE_DIGITS, ".1"),
    (0.0001, SINGLE_DIGITS, ".0001"),
    (1e-6, SINGLE_DIGITS, ".000001"),
    (1e-7, SINGLE_DIGITS, ".0000001"),          # the manual says 1E-7; it lies
    (1e-8, SINGLE_DIGITS, "1E-08"),             # two-digit exponent, signed
    (1e-30, SINGLE_DIGITS, "1E-30"),
    (0.00012345, SINGLE_DIGITS, "1.2345E-04"),  # zeros + digits > 7
    (2 / 3, DOUBLE_DIGITS, ".6666666666666666"),
    (12345678, DOUBLE_DIGITS, "12345678"),
    (1234567890123456, DOUBLE_DIGITS, "1234567890123456"),
    (1e10, DOUBLE_DIGITS, "10000000000"),       # 11 digits fit in a double
    (1e10, SINGLE_DIGITS, "1E+10"),             # but not in a single
    (7, INTEGER_DIGITS, "7"),
    (32767, INTEGER_DIGITS, "32767"),
]


def test_the_formatter_matches_the_real_binary():
    print("\nthe formatter, value by value")
    print("-" * 60)
    wrong = []
    for value, digits, expected in FORMATTER_CASES:
        got = format_number(value, digits)
        if got != expected:
            wrong.append(f"{value!r} d={digits}: got {got!r}, want {expected!r}")
    check(not wrong,
          f"{len(FORMATTER_CASES) - len(wrong)}/{len(FORMATTER_CASES)} match"
          + ("" if not wrong else "; wrong: " + "; ".join(wrong[:4])))


def test_the_spaces_around_a_printed_number():
    """Always a trailing space, and a leading one unless it is negative."""
    print("\nthe spaces MBASIC puts around a number")
    print("-" * 60)
    check(format_for_print(1, SINGLE_DIGITS) == " 1 ", "positive gets both")
    check(format_for_print(-1, SINGLE_DIGITS) == "-1 ", "negative gets one")
    check(format_for_print(7, INTEGER_DIGITS) == " 7 ", "integers too")


# ---------------------------------------------------------------------------
# Through PRINT, where the type decides the precision
# ---------------------------------------------------------------------------

#: (program, expected output) - again, all from the real binary.
PRINT_CASES = [
    ('10 PRINT 1;2;-3', ' 1  2 -3 '),
    ('10 PRINT 1/3', ' .333333 '),
    ('10 PRINT SQR(2)', ' 1.41421 '),
    ('10 PRINT 0.1+0.2', ' .3 '),
    ('10 PRINT 1000000!', ' 1E+06 '),
    ('10 PRINT 1234567', ' 1.23457E+06 '),
    # More than seven significant figures makes a literal double precision,
    # which is why this one prints in full and the line above does not.
    ('10 PRINT 12345678', ' 12345678 '),
    ('10 A = 4000 - 65.972101158: PRINT A', ' 3934.03 '),
    ('10 A# = 4000 - 65.972101158: PRINT A#', ' 3934.027898842 '),
    ('10 A% = 7: PRINT A%', ' 7 '),
    ('10 A% = 7: PRINT A%*2', ' 14 '),
    ('10 A = 2: PRINT A/7', ' .285714 '),
    ('10 PRINT -0.5', '-.5 '),
    ('10 PRINT 100000!;999999!;1000000!', ' 100000  999999  1E+06 '),
]


def test_print_uses_the_expression_type():
    print("\nPRINT, where the expression's type sets the precision")
    print("-" * 60)
    for source, expected in PRINT_CASES:
        got = run(source)
        check(got == expected,
              f"{source[3:]:38} -> {got!r}"
              + ("" if got == expected else f"   (want {expected!r})"))


def test_the_same_value_at_two_precisions():
    """The point of reading the type off the tree rather than the value."""
    print("\none value, two precisions")
    print("-" * 60)
    single = run('10 A = 1/3: PRINT A')
    double = run('10 A# = 1#/3#: PRINT A#')
    check(single == ' .333333 ', f"single shows six figures ({single!r})")
    check(double == ' .3333333333333333 ',
          f"double shows sixteen ({double!r})")


def test_str_dollar_matches_print():
    """STR$ produces what PRINT would, minus the trailing space."""
    print("\nSTR$")
    print("-" * 60)
    for source, expected in [
        ('10 PRINT "[";STR$(3.14);"]"', '[ 3.14]'),
        ('10 PRINT "[";STR$(-2);"]"', '[-2]'),
        ('10 PRINT "[";STR$(1/3);"]"', '[ .333333]'),
    ]:
        got = run(source)
        check(got == expected,
              f"{source[9:40]:34} -> {got!r}"
              + ("" if got == expected else f"   (want {expected!r})"))


def test_print_using_keeps_the_sign():
    """A negative number must not print as positive, and a positive one must
    not print its sign twice.

    The sign was worked out and then never written, so PRINT USING "###.##"
    turned -3.14 into "  3.14" - silently, in a statement whose whole purpose
    is producing tidy reports.
    """
    print("\nPRINT USING and negative numbers")
    print("-" * 60)
    for source, expected in [
        ('10 PRINT USING "###.##"; -3.14159', ' -3.14'),
        ('10 PRINT USING "$$###.##"; -12.5', ' -$12.50'),
        ('10 PRINT USING "**###.##"; -12.5', '**-12.50'),
        ('10 PRINT USING "#####"; -42', '  -42'),
        ('10 PRINT USING "##.##"; -123.456', '%-123.46'),
        ('10 PRINT USING "###.##"; 3.14159', '  3.14'),
        # A '+' format emits its own sign. Appending sign_char as well printed
        # ++42 and --42 - the fix for the missing minus, overshooting.
        ('10 PRINT USING "+###"; 42', ' +42'),
        ('10 PRINT USING "+###"; -42', ' -42'),
        ('10 PRINT USING "+##.##"; 3.5', ' +3.50'),
        ('10 PRINT USING "+##.##"; -3.5', ' -3.50'),
        ('10 PRINT USING "+#####"; 12345', '+12345'),
        ('10 PRINT USING "###+"; 42', ' 42+'),
        ('10 PRINT USING "###+"; -42', ' 42-'),
        ('10 PRINT USING "###-"; 42', ' 42 '),
        ('10 PRINT USING "###-"; -42', ' 42-'),
    ]:
        got = run(source)
        check(got == expected,
              f"{source[3:36]:34} -> {got!r}"
              + ("" if got == expected else f"   (want {expected!r})"))


def test_print_using_matches_the_real_binary():
    """PRINT USING as PUFOUT does it.

    Every line below was read off the real 5.21 binary. Four rules were being
    broken, and the assembler in f4.mac agrees with the binary on all four:

    * The value is converted by the same routine PRINT uses, so a single is
      six significant figures here too: "##,###.##" of 12345.67 is 12,345.70.
      This was the one the cross-check caught - the field was reading the
      stored float straight off and printing 12,345.67.
    * The field's own rounding is half away from zero, not Python's half to
      even. 1.005 in "##.##" is 1.01, and -0.005 is -0.01.
    * A minus sign, or the plus of a "+" field, uses up one of the positions
      to the left of the point. "####" holds 1234 but overflows on -1234.
    * The zero in front of the point is only printed when there is room left
      for it, so "#.###" of -0.5 is -.500 while "##.###" of -0.5 is -0.500.

    A ^^^^ mantissa takes its integer-digit count from the field rather than
    normalising to one digit, which is why "#.#^^^^" of 1.5 is 0.2E+01.
    """
    print("\nPRINT USING against the binary")
    print("-" * 60)
    for source, expected in [
        # Six significant figures for a single, sixteen for a double.
        ('10 PRINT USING "##,###.##"; 12345.67', '12,345.70'),
        ('10 PRINT USING "######.##"; 12345.67', ' 12345.70'),
        ('10 PRINT USING "#######.##"; 12345.67#', '  12345.67'),
        ('10 PRINT USING "#######.#"; 123456.7', ' 123457.0'),
        ('10 PRINT USING "#,###,###"; 1234567', '1,234,570'),
        # Half away from zero, on the six-digit value not the stored float.
        ('10 PRINT USING "##.##"; 1.005', ' 1.01'),
        ('10 PRINT USING "##.##"; 2.675', ' 2.68'),
        ('10 PRINT USING "##.##"; 1.005#', ' 1.01'),
        ('10 PRINT USING "#.#"; .45', '0.5'),
        ('10 PRINT USING "##.##"; -0.005', '-0.01'),
        ('10 PRINT USING "#.##"; -0.005', '-.01'),
        ('10 PRINT USING "#.##"; 0.005', '0.01'),
        ('10 PRINT USING "#####"; -1234.5', '-1235'),
        ('10 PRINT USING "#"; 0.5', '1'),
        # The sign takes a digit position - unless it is trailing, or the
        # space in front of a positive number.
        ('10 PRINT USING "####"; 1234', '1234'),
        ('10 PRINT USING "####"; -1234', '%-1234'),
        ('10 PRINT USING "###.##"; -123.45', '%-123.45'),
        ('10 PRINT USING "###.##"; -12.34', '-12.34'),
        ('10 PRINT USING "+###"; 1234', '%+1234'),
        ('10 PRINT USING "+####"; 1234', '+1234'),
        ('10 PRINT USING "###-"; 1234', '%1234 '),
        ('10 PRINT USING "#,###"; -1234', '%-1,234'),
        ('10 PRINT USING "$$##.##"; 1234.5', '%$1234.50'),
        # The leading zero, only while it fits.
        ('10 PRINT USING "#.###"; -0.5', '-.500'),
        ('10 PRINT USING "##.###"; -0.5', '-0.500'),
        ('10 PRINT USING ".##"; 0.5', '.50'),
        ('10 PRINT USING ".##"; -0.5', '%-.50'),
        ('10 PRINT USING "#####.##"; 0', '    0.00'),
        # A value that is negative but rounds to zero keeps its sign; IEEE's
        # negative zero does not have one to keep. MBF has no signed zero, so
        # 0 * (-1) is plain zero - basic/business/budget.bas reaches every
        # total that way and had a minus in front of each one.
        ('10 PRINT USING "###.##"; -0.001', ' -0.00'),
        ('10 PRINT USING "###.##"; 0*(-1)', '  0.00'),
        ('10 PRINT USING "$$#####.##"; 0*(-1)', '     $0.00'),
        # ^^^^ takes its mantissa width from the field, and a double prints D.
        ('10 PRINT USING "#.#^^^^"; 1.5', '0.2E+01'),
        ('10 PRINT USING "#.#^^^^"; -1.5', '-.2E+01'),
        ('10 PRINT USING "##.#^^^^"; 1.5', ' 1.5E+00'),
        ('10 PRINT USING "###.#^^^^"; 1.5', ' 15.0E-01'),
        ('10 PRINT USING "#^^^^"; 1234.5', '0E+04'),
        ('10 PRINT USING "##^^^^"; 1234.5', ' 1E+03'),
        ('10 PRINT USING "+#.#^^^^"; 1.5', '+1.5E+00'),
        ('10 PRINT USING "#.#^^^^-"; -1.5', '1.5E+00-'),
        ('10 PRINT USING "##.##^^^^"; 3.14159#', ' 3.14D+00'),
        ('10 PRINT USING "#.#^^^^"; 0', '0.0E+00'),
    ]:
        got = run(source)
        check(got == expected,
              f"{source[3:40]:39} -> {got!r}"
              + ("" if got == expected else f"   (want {expected!r})"))


def test_the_using_string_is_reused():
    """The format string runs again until the value list is exhausted.

    This was missing altogether: PRINT USING "###"; 1; 2; 3 printed "  1" and
    dropped the rest. MBASIC scans the string, and when it reaches the end with
    values still in hand it starts the string over (PRINUS -> REUSIN).

    Scanning stops the moment a *field* finds no value left - the literal text
    passed on the way out has already been printed by then, which is why
    "### ###" with three values ends in a trailing space rather than stopping
    cleanly after the third.
    """
    print("\nThe USING string is reused")
    print("-" * 60)
    for source, expected in [
        ('10 PRINT USING "###"; 1; 2; 3', '  1  2  3'),
        ('10 PRINT USING "## ##"; 1; 2; 3; 4', ' 1  2 3  4'),
        ('10 PRINT USING "[#]"; 7; 8', '[7][8]'),
        ('10 PRINT USING "!"; "AB"; "CD"', 'AC'),
        ('10 PRINT USING "### ###"; 10; 20; 30', ' 10  20 30 '),
        # A comma delimits the value list just as a semicolon does, and does
        # not tab to a print zone. This was a syntax error.
        ('10 PRINT USING "###"; 1, 2', '  1  2'),
        ('10 PRINT USING "## ##"; 1; 2, 3; 4', ' 1  2 3  4'),
    ]:
        got = run(source)
        check(got == expected, f"{source[3:40]:39} -> {got!r}"
              + ("" if got == expected else f"   (want {expected!r})"))

    # A trailing ';' or ',' suppresses the newline, as on a plain PRINT.
    got = run('10 PRINT USING "###"; 1;\n20 PRINT "X"')
    check(got == '  1X', f"{'trailing ; joins the next PRINT':39} -> {got!r}")
    got = run('10 PRINT USING "###"; 1,\n20 PRINT "Y"')
    check(got == '  1Y', f"{'trailing , does the same':39} -> {got!r}")
    got = run('10 PRINT USING "###"; 1\n20 PRINT "Z"')
    check(got == '  1\nZ', f"{'without one, the newline stays':39} -> {got!r}")


def test_punctuation_that_is_not_a_field():
    """A '+', '-' or '.' with no digit positions after it is a literal.

    MBASIC only commits to a numeric field once it has seen a digit position,
    and prints the character otherwise - PLSPRT exists precisely to flush a '+'
    that turned out not to begin one. We were building a zero-width field out
    of it and formatting the value into nothing.
    """
    print("\nPunctuation that is not a field")
    print("-" * 60)
    for source, expected in [
        # "+###" already emits its own sign, so the '+' after it is not a
        # trailing sign - it is an ordinary character.
        ('10 PRINT USING "+###+"; 42', ' +42+'),
        ('10 PRINT USING "+###+"; -42', ' -42+'),
        ('10 PRINT USING "+###-"; -42', ' -42-'),
        # A leading '-' never starts a field, so this prints a minus and then
        # formats 5 into "#".
        ('10 PRINT USING "-#"; 5', '-5'),
        ('10 PRINT USING "-.##"; 0.5', '-.50'),
    ]:
        got = run(source)
        check(got == expected, f"{source[3:40]:39} -> {got!r}"
              + ("" if got == expected else f"   (want {expected!r})"))

    # With no field anywhere, MBASIC prints the literal text - a '.' with no
    # '#' after it is a literal too - and only then complains that it never
    # found somewhere to put the value.
    for source, text in [('10 PRINT USING "A.B"; 5', 'A.B'),
                         ('10 PRINT USING "+X"; 5', '+X')]:
        try:
            got, raised = run(source), None
        except RuntimeError as error:
            got, raised = text, str(error)
        check(got == text and raised == 'Illegal function call',
              f"{source[3:40]:39} -> {got!r} then {raised!r}")


if __name__ == "__main__":
    print("MBASIC 5.21 number formatting")
    print("=" * 60)

    test_the_formatter_matches_the_real_binary()
    test_the_spaces_around_a_printed_number()
    test_print_uses_the_expression_type()
    test_the_same_value_at_two_precisions()
    test_str_dollar_matches_print()
    test_print_using_keeps_the_sign()
    test_print_using_matches_the_real_binary()
    test_the_using_string_is_reused()
    test_punctuation_that_is_not_a_field()

    failed = results.count(False)
    print("\n" + "=" * 60)
    print(f"Results: {results.count(True)} passed, {failed} failed")

    if failed:
        print("❌ Some tests failed")
        sys.exit(1)
    print("✅ All tests passed!")
    sys.exit(0)
