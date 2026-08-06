#!/usr/bin/env python3
"""FOR loop entry, and the two integer operators, as MBASIC 5.21 does them.

Every expectation here was read off the real 5.21 binary running under cpmemu,
and each one was wrong before. They were found by cross-checking
basic/dev/tests_with_results/ against the binary - see
docs/dev/TESTS_VERIFIED_AGAINST_BINARY.md.

What was wrong:

    FOR I = 10 TO 1 ... NEXT     ran the body once and left I at 11
    -10 MOD 3                    2, Python's remainder, instead of -1
    -10 \\ 3                      -4, Python's floor, instead of -3
    7.6 MOD 3                    1.6 - the operands were never made integers
    12 \\ 2 * 3                   18 - \\ was sharing a precedence level with *

The FOR one is the interesting one. MBASIC never falls into the body: FOR
scans forward for its matching NEXT (NXTSCN in bintrp.mac) and jumps *to* it
with the increment suppressed, so the ordinary termination test in NEXT is what
ends the loop. Entering through the NEXT rather than skipping past it is why

    10 FOR I=10 TO 1 / 20 PRINT "BODY" / 30 NEXT J

reports "NEXT without FOR" at line 30 without ever printing BODY - the NEXT
still runs, and still checks the name it was given.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.interpreter import Interpreter
from src.iohandler.base import IOHandler
from src.lexer import Lexer
from src.parser import Parser
from src.runtime import Runtime

results = []


def check(condition, label):
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
    """Run a program and return what it printed, or 'ERROR: ...' if it died."""
    ast = Parser(Lexer(source).tokenize()).parse()
    runtime = Runtime({line.line_number: line for line in ast.lines})
    handler = Capture()
    interpreter = Interpreter(runtime, handler)
    interpreter.start()
    try:
        for _ in range(200):
            state = interpreter.tick(mode='run', max_statements=5000)
            if not runtime.pc.is_running() or state.error_info:
                break
    except Exception as error:                  # the message is the assertion
        return f"ERROR: {error}"
    return handler.text().rstrip('\n')


def test_a_loop_that_should_not_run():
    """The body runs no times, and the control variable keeps its start value."""
    print("\nZero-trip FOR")
    print("-" * 60)
    for source, expected in [
        # N counts the iterations, I is read after the loop.
        ('10 N=0\n20 FOR I=10 TO 1\n30 N=N+1\n40 NEXT I\n50 PRINT N;I', ' 0  10 '),
        ('10 N=0\n20 FOR I=1 TO 1\n30 N=N+1\n40 NEXT I\n50 PRINT N;I', ' 1  2 '),
        ('10 N=0\n20 FOR I=10 TO 1 STEP -1\n30 N=N+1\n40 NEXT I\n50 PRINT N;I', ' 10  0 '),
        ('10 N=0\n20 FOR I=1 TO 10 STEP -1\n30 N=N+1\n40 NEXT I\n50 PRINT N;I', ' 0  1 '),
        ('10 N=0\n20 FOR I=10 TO 1 STEP 2\n30 N=N+1\n40 NEXT I\n50 PRINT N;I', ' 0  10 '),
        # STEP 0 ends only on landing exactly on the limit - the termination
        # test is sign(current - end) == sign(step), and sign(0) is 0.
        ('10 N=0\n20 FOR I=5 TO 5 STEP 0\n30 N=N+1\n40 NEXT I\n50 PRINT N;I', ' 0  5 '),
        # A blank INPUT gives N=0, which is how this reaches real programs:
        # FOR I=1 TO 0 must not ask for player 1's name.
        ('10 N=0\n20 FOR I=1 TO 0\n30 PRINT "BODY"\n40 NEXT I\n50 PRINT "AFTER";I', 'AFTER 1 '),
    ]:
        got = run(source)
        label = source.split('\n')[1][3:]
        check(got == expected, f"{label:34} -> {got!r}"
              + ("" if got == expected else f"   (want {expected!r})"))


def test_where_a_zero_trip_loop_lands():
    """It lands on the NEXT, not past it - which is what the names see."""
    print("\nZero-trip FOR: the NEXT still runs")
    print("-" * 60)

    # Mid-line: the statement after the NEXT is still reached.
    got = run('10 FOR A=10 TO 1: PRINT "BODY": NEXT A: PRINT "SAMELINE"\n20 PRINT A')
    check(got == 'SAMELINE\n 10 ', f"NEXT mid-line          -> {got!r}")

    # A whole inner loop inside a zero-trip outer one is skipped, and the inner
    # control variable is never touched.
    got = run('10 N=0\n20 FOR I=10 TO 1\n30 FOR J=1 TO 3\n40 N=N+1\n50 NEXT J\n'
              '60 NEXT I\n70 PRINT N;I;J')
    check(got == ' 0  10  0 ', f"nested, outer zero-trip -> {got!r}")

    # A bare NEXT closes it just the same.
    got = run('10 N=0\n20 FOR K=10 TO 1\n30 N=N+1\n40 NEXT\n50 PRINT N;K')
    check(got == ' 0  10 ', f"bare NEXT               -> {got!r}")

    # NEXT J,I closes two loops, so the scan stops on the I - and J, whose loop
    # was never entered, is left alone.
    got = run('10 N=0\n20 FOR I=10 TO 1\n30 FOR J=1 TO 3\n40 N=N+1\n50 NEXT J,I\n'
              '60 PRINT N;I;J')
    check(got == ' 0  10  0 ', f"NEXT J,I                -> {got!r}")

    # The NEXT is entered, so the name it carries is still checked. The body
    # must not run, and the error must come from the NEXT.
    got = run('10 FOR I=10 TO 1\n20 PRINT "BODY"\n30 NEXT J\n40 PRINT "HERE"')
    check(got.startswith('ERROR: NEXT without FOR'),
          f"NEXT with a wrong name  -> {got!r}")

    # Same for the second name of a NEXT that closes more loops than exist.
    got = run('10 FOR I=10 TO 1\n20 PRINT "BODY"\n30 NEXT I,J\n40 PRINT "HERE"')
    check(got.startswith('ERROR: NEXT without FOR'),
          f"NEXT I,J, only I open   -> {got!r}")


def test_mod_and_integer_division():
    """Truncation toward zero, the dividend's sign, and CINT'd operands."""
    print("\nMOD and \\")
    print("-" * 60)
    for source, expected in [
        # The remainder takes the sign of the dividend, as in C - Python gives
        # 2 and -2 here, taking the sign of the divisor.
        ('10 PRINT -10 MOD 3;10 MOD -3;-10 MOD -3;10 MOD 3', '-1  1 -1  1 '),
        # The quotient truncates toward zero; Python floors.
        ('10 PRINT -10 \\ 3;10 \\ -3;-10 \\ -3;10 \\ 3', '-3 -3  3  3 '),
        # Operands are rounded to integers first, halves away from zero.
        ('10 PRINT 7.6 MOD 3;-7.6 MOD 3;7.6 \\ 3;-7.6 \\ 3', ' 2 -2  2 -2 '),
        ('10 PRINT 10.5 \\ 3;2.5 \\ 1;-2.5 \\ 1', ' 3  3 -3 '),
        # -32768 \ -1 is 32768: the one quotient the binary floats rather than
        # wrapping.
        ('10 PRINT -32768 \\ -1;32767 \\ 1', ' 32768  32767 '),
    ]:
        got = run(source)
        check(got == expected, f"{source[9:46]:38} -> {got!r}"
              + ("" if got == expected else f"   (want {expected!r})"))

    # An operand that will not fit 16 bits is Overflow, before any check of the
    # divisor for zero.
    got = run('10 PRINT 40000 \\ 2')
    check(got.startswith('ERROR: Overflow'), f"40000 \\ 2 overflows       -> {got!r}")
    got = run('10 PRINT 100000 MOD 7')
    check(got.startswith('ERROR: Overflow'), f"100000 MOD 7 overflows    -> {got!r}")
    got = run('10 PRINT 5 \\ 0')
    check(got.startswith('ERROR: Division by zero'), f"5 \\ 0                     -> {got!r}")
    got = run('10 PRINT 5 MOD 0')
    check(got.startswith('ERROR: Division by zero'), f"5 MOD 0                   -> {got!r}")


def test_the_four_precedence_levels():
    """* and / , then \\ , then MOD, then + and - . Four levels, not three."""
    print("\nPrecedence of \\ and MOD")
    print("-" * 60)
    for source, expected in [
        # 12 \ (2*3), not (12\2)*3.
        ('10 PRINT 12 \\ 2 * 3;12 MOD 5 * 2;2 * 6 \\ 4;1 + 12 \\ 4', ' 2  2  3  4 '),
        ('10 PRINT 20 \\ 3 \\ 2;20 MOD 7 MOD 3;100 \\ 3 MOD 4;100 MOD 30 \\ 4', ' 3  0  1  2 '),
        ('10 PRINT 10 - 8 / 2;2 * 3 ^ 2;10 \\ 3 + 1;10 MOD 3 + 1', ' 6  18  4  2 '),
        ('10 PRINT -2 ^ 2;7 \\ 2 * 2 + 1;1 + 2 MOD 3 * 4', '-4  2  3 '),
    ]:
        got = run(source)
        check(got == expected, f"{source[9:52]:44} -> {got!r}"
              + ("" if got == expected else f"   (want {expected!r})"))


if __name__ == "__main__":
    print("MBASIC 5.21 FOR entry and integer operators")
    print("=" * 60)

    test_a_loop_that_should_not_run()
    test_where_a_zero_trip_loop_lands()
    test_mod_and_integer_division()
    test_the_four_precedence_levels()

    failed = results.count(False)
    print("\n" + "=" * 60)
    print(f"Results: {results.count(True)} passed, {failed} failed")

    if failed:
        print("❌ Some tests failed")
        sys.exit(1)
    print("✅ All tests passed!")
    sys.exit(0)
