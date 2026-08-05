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
    """A negative number must not print as positive.

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
    ]:
        got = run(source)
        check(got == expected,
              f"{source[3:36]:34} -> {got!r}"
              + ("" if got == expected else f"   (want {expected!r})"))


if __name__ == "__main__":
    print("MBASIC 5.21 number formatting")
    print("=" * 60)

    test_the_formatter_matches_the_real_binary()
    test_the_spaces_around_a_printed_number()
    test_print_uses_the_expression_type()
    test_the_same_value_at_two_precisions()
    test_str_dollar_matches_print()
    test_print_using_keeps_the_sign()

    failed = results.count(False)
    print("\n" + "=" * 60)
    print(f"Results: {results.count(True)} passed, {failed} failed")

    if failed:
        print("❌ Some tests failed")
        sys.exit(1)
    print("✅ All tests passed!")
    sys.exit(0)
