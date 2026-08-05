#!/usr/bin/env python3
"""
Test that arithmetic happens in the precision MBASIC 5.21 would use.

Formatting was fixed first, and it left a visible hole: a single-precision
result *widened* into a double showed digits the real machine never had.

    F# = 1/3      real 5.21 .3333333432674408    here .3333333333333333
    B# = .1       real 5.21 .1000000014901161    here .1

MBASIC works in single precision unless everything involved is double, and a
single holds 24 bits of mantissa - the same width as IEEE float32, so a
round-trip through float32 reproduces it exactly. The error is real, it is
kept, and printing cannot recover it afterwards. Three places had to round:

* storing into a variable or array element (src/runtime.py)
* every arithmetic operation (Interpreter.evaluate_binaryop)
* literals and function results, which are single before they are used at all

Two things had to survive parsing for any of that to be decidable: the type
suffix on a numeric literal, which the lexer used to discard (1# and 1 both
arrived as 1.0), and the suffix on a DEF FN call, which the parser strips from
the name for lookup.

Every expectation here was read off `com/mbasic.com` under cpmemu, with one
marked exception: the maths functions follow their argument's type here and are
single by signature there, so `SQR(2#)` is deliberately more accurate than the
real machine. Those cases carry the binary's value beside them.

The values are printed through a double so the digits a single cannot hold are
visible - PRINT on a single would round them away again and prove nothing.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.interpreter import Interpreter
from src.iohandler.base import IOHandler
from src.lexer import Lexer
from src.number_format import coerce_to_type, to_integer, to_single
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


def run(source, answers=()):
    """Run a program and return what it printed, one line per PRINT.

    INPUT does not call back into the IO handler - the interpreter pauses with
    state.input_prompt set and waits to be given an answer, so the harness has
    to answer it the way a UI would.
    """
    ast = Parser(Lexer(source).tokenize()).parse()
    runtime = Runtime({line.line_number: line for line in ast.lines})
    handler = Capture()
    pending = list(answers)
    interpreter = Interpreter(runtime, handler)
    interpreter.start()
    for _ in range(200):
        state = interpreter.tick(mode='run', max_statements=20000)
        if state.input_prompt is not None:
            interpreter.provide_input(pending.pop(0) if pending else "0")
            continue
        if not runtime.pc.is_running() or state.error_info:
            break
    return [part.rstrip('\n') for part in handler.text().split('\n') if part.strip()]


def one(source, answers=()):
    """Run a program that prints exactly once."""
    printed = run(source, answers)
    return printed[0] if printed else ''


# ---------------------------------------------------------------------------
# The coercions on their own
# ---------------------------------------------------------------------------

def test_the_float32_round_trip():
    print("\nsingle precision is 24 bits of mantissa")
    print("-" * 62)
    check(repr(to_single(1 / 3)) == '0.3333333432674408', "1/3 loses its tail")
    check(repr(to_single(1 / 7)) == '0.1428571492433548', "1/7 too")
    check(to_single(0.5) == 0.5, "a value a single can hold is untouched")
    check(to_single(1e300) == 1e300,
          "out of float32 range is left alone rather than made infinite")
    check(to_single("x") == "x" and to_single(True) is True,
          "non-numbers pass through")


def test_integer_assignment_rounds():
    """A% = 3.7 is 4 on the real binary. It was 3 here: int() truncates."""
    print("\nassigning to an integer rounds, it does not truncate")
    print("-" * 62)
    for value, expected in [(3.7, 4), (-3.7, -4), (3.2, 3), (-3.2, -3),
                            (2.5, 3), (-2.5, -3), (3.0, 3)]:
        got = to_integer(value)
        check(got == expected, f"to_integer({value}) = {got}"
              + ("" if got == expected else f"   (want {expected})"))


def test_coerce_by_suffix():
    print("\ncoerce_to_type dispatches on the suffix")
    print("-" * 62)
    check(coerce_to_type(3.7, '%') == 4, "% rounds to an integer")
    check(repr(coerce_to_type(1 / 3, '!')) == '0.3333333432674408', "! is single")
    check(repr(coerce_to_type(1 / 3, None)) == '0.3333333432674408',
          "no suffix is single")
    check(coerce_to_type(1 / 3, '#') == 1 / 3, "# keeps every digit")
    check(coerce_to_type("hi", '$') == "hi", "$ passes strings through")


# ---------------------------------------------------------------------------
# Through the interpreter, against the real binary
# ---------------------------------------------------------------------------

#: (program, what MBASIC 5.21 printed). Each stores into a double so the
#: single-precision error is visible instead of being rounded away by PRINT.
PROGRAMS = [
    # Storage: the division is single, and widening keeps its error.
    ('10 F# = 1/3: PRINT F#', ' .3333333432674408 '),
    ('10 E# = 1/7: PRINT E#', ' .1428571492433548 '),
    # ... unless everything in it is double.
    ('10 A# = 1#/3#: PRINT A#', ' .3333333333333333 '),
    # A literal is single before it is used at all.
    ('10 B# = .1: PRINT B#', ' .1000000014901161 '),
    ('10 C# = .1#: PRINT C#', ' .1 '),
    ('10 I# = 3.7: PRINT I#', ' 3.700000047683716 '),
    ('10 N# = 1E6/3: PRINT N#', ' 333333.34375 '),
    ('10 J# = 1.5D2/7: PRINT J#', ' 21.42857142857143 '),
    # Every operation rounds, not just the assignment.
    ('10 F# = 1/3+1/3: PRINT F#', ' .6666666865348816 '),
    ('10 G# = 2*(1/3): PRINT G#', ' .6666666865348816 '),
    ('10 I# = .1+.2: PRINT I#', ' .300000011920929 '),
    ('10 C# = 100!/7!: PRINT C#', ' 14.2857141494751 '),
    ('10 B# = 1/3*3: PRINT B#', ' 1 '),
    ('10 F# = -(1/3): PRINT F#', '-.3333333432674408 '),
    # A function of a single is single, and matches the real binary exactly.
    ('10 D# = SQR(2): PRINT D#', ' 1.414213538169861 '),
    ('10 K# = EXP(1): PRINT K#', ' 2.718281745910645 '),
    ('10 L# = 10^0.5: PRINT L#', ' 3.162277698516846 '),
    ('10 A# = LOG(2): PRINT A#', ' .6931471824645996 '),
    ('10 A# = COS(1): PRINT A#', ' .5403022766113281 '),
    ('10 A# = SQR(3): PRINT A#', ' 1.732050776481628 '),
    ('10 A# = 2^10: PRINT A#', ' 1024 '),
    # ... and the conversions say what they say.
    ('10 H# = CDBL(1/3): PRINT H#', ' .3333333432674408 '),
    ('10 C# = CSNG(1#/3#): PRINT C#', ' .3333333432674408 '),
    ('10 D# = ABS(-1/3): PRINT D#', ' .3333333432674408 '),
    ('10 E# = INT(100/3): PRINT E#', ' 33 '),
    # VAL is double on the real binary - .1 through it stays .1.
    ('10 G# = VAL(".1"): PRINT G#', ' .1 '),
    # CINT rounds halves away from zero. Python's round() is banker's
    # rounding, which sent 2.5 to 2.
    ('10 PRINT CINT(2.5);CINT(3.5);CINT(-2.5);CINT(3.7);CINT(-3.7)',
     ' 3  4 -3  4 -4 '),
    ('10 PRINT INT(2.5);INT(-2.5);FIX(-2.7)', ' 2 -3 -2 '),
    ('10 A# = CSNG(1.23456789#): PRINT A#', ' 1.234567880630493 '),
    # Integer arithmetic stays exact.
    ('10 E% = 32767: F# = E%+0: PRINT F#', ' 32767 '),
    ('10 H% = 1/3*30: PRINT H%', ' 10 '),
    # Assigning to an integer rounds.
    ('10 A% = 3.7: PRINT A%', ' 4 '),
    ('10 B% = -3.7: PRINT B%', '-4 '),
    ('10 D% = 2.5: PRINT D%', ' 3 '),
    ('10 C% = 3.2: PRINT C%', ' 3 '),
    # An array element holds its type the same way a scalar does.
    ('10 DIM Z(3)\n20 Z(1) = 1/7: G# = Z(1): PRINT G#', ' .1428571492433548 '),
    # DEFDBL/DEFSNG set the type, and the type decides.
    ('10 DEFDBL D\n20 D1 = 1/3: PRINT D1', ' .3333333432674408 '),
    ('10 DEFDBL D\n20 D2 = 1#/3#: PRINT D2', ' .3333333333333333 '),
    ('10 DEFSNG S\n20 S1 = 1#/3#: S2# = S1: PRINT S2#',
     ' .3333333432674408 '),
    # A DEF FN is typed by its name, like a variable.
    ('10 DEF FNA(X) = X/3\n20 A# = FNA(1): PRINT A#', ' .3333333432674408 '),
    ('10 DEF FNB#(X#) = X#/3#\n20 B# = FNB#(1#): PRINT B#',
     ' .3333333333333333 '),
]


def test_programs_match_the_real_binary():
    print("\nwhole programs, against MBASIC 5.21 under cpmemu")
    print("-" * 62)
    for source, expected in PROGRAMS:
        got = one(source)
        label = source.replace('\n', ' | ')[3:]
        check(got == expected, f"{label:44} -> {got!r}"
              + ("" if got == expected else f"   (want {expected!r})"))


#: MBASIC rounds wherever it wants an integer and is handed a fraction, not
#: just on assignment. Every one of these was truncating.
FRACTIONAL_ARGUMENTS = [
    ('10 PRINT "[";LEFT$("ABCDEF",2.7);"]"', '[ABC]'),
    ('10 PRINT "[";RIGHT$("ABCDEF",2.7);"]"', '[DEF]'),
    ('10 PRINT "[";MID$("ABCDEF",2.7,1.6);"]"', '[CD]'),
    ('10 PRINT "[";STRING$(2.7,"X");"]"', '[XXX]'),
    ('10 PRINT "[";STRING$(3,65.7);"]"', '[BBB]'),
    ('10 PRINT "[";SPACE$(2.7);"]"', '[   ]'),
    ('10 PRINT "[";CHR$(65.7);"]"', '[B]'),
    ('10 PRINT "[";TAB(4.7);"X";"]"', '[   X]'),
    ('10 PRINT "[";SPC(3.7);"Y";"]"', '[    Y]'),
    # A subscript too - truncating read the wrong element.
    ('10 DIM A(10)\n20 A(3)=33: A(2)=22\n30 PRINT A(2.7);A(2.4)', ' 33  22 '),
    # ... and a dimension: DIM B(2.7) has to leave B(3) in range.
    ('10 DIM B(2.7)\n20 B(3)=99: PRINT B(3)', ' 99 '),
    # ... and the index of an ON GOTO.
    ('10 ON 1.7 GOTO 30,40\n30 PRINT "ONE": END\n40 PRINT "TWO"', 'TWO'),
]


def test_fractional_arguments_round():
    """LEFT$("ABCDEF",2.7) is "ABC" on the real binary, and A(2.7) is A(3).

    Everywhere MBASIC wants an integer and is given a fraction it rounds, the
    same way an assignment to an integer variable does.
    """
    print("\nfractions where an integer is wanted")
    print("-" * 62)
    for source, expected in FRACTIONAL_ARGUMENTS:
        got = one(source)
        label = source.replace('\n', ' | ')[3:]
        check(got == expected, f"{label:44} -> {got!r}"
              + ("" if got == expected else f"   (want {expected!r})"))


def test_a_string_in_a_number_is_a_type_mismatch():
    """A% = "X" must not quietly store the string.

    Rounding cannot be applied to a string, and passing it through would put
    the wrong type in the variable. The real binary says Type mismatch, which
    is error 13.
    """
    print("\nType mismatch")
    print("-" * 62)
    got = one('10 ON ERROR GOTO 100\n20 A% = "X"\n30 END\n'
              '100 PRINT "ERR=";ERR: RESUME 30')
    check(got == 'ERR= 13 ', f"A% = \"X\" raises error 13 ({got!r})")


#: The maths functions follow their argument's type here, where MBASIC's are
#: single by signature. A deliberate divergence: these are the only
#: expectations in this file that are NOT what the real binary printed, and
#: what it printed is given alongside.
ARGUMENT_TYPED_FUNCTIONS = [
    ('10 E# = SQR(2#): PRINT E#', ' 1.414213562373095 ', '1.414213538169861'),
    ('10 C# = SIN(1#): PRINT C#', ' .8414709848078965 ', '.841471016407013'),
    ('10 E# = LOG(2#): PRINT E#', ' .6931471805599453 ', '.6931471824645996'),
    ('10 F# = EXP(1#): PRINT F#', ' 2.718281828459045 ', '2.718281745910645'),
    ('10 I# = ATN(1#)*4: PRINT I#', ' 3.141592653589793 ', '3.141592979431152'),
]


def test_maths_functions_follow_their_argument():
    """SQR(2#) is computed in double here, and in single on the real machine.

    MBASIC's library functions are single by signature, the way C's sqrtf is,
    so a double argument came back with 24 bits of mantissa. This interpreter
    uses native binary32 and binary64 and does not reproduce MBASIC's
    arithmetic, so a double argument is computed in double - which is more
    accurate and no longer bit-identical to 1981. See
    docs/dev/SINGLE_PRECISION.md.
    """
    print("\nthe maths functions take their precision from their argument")
    print("-" * 62)
    for source, expected, real in ARGUMENT_TYPED_FUNCTIONS:
        got = one(source)
        check(got == expected, f"{source[3:30]:30} -> {got!r}"
              + ("" if got == expected else f"   (want {expected!r})")
              + f"   [real 5.21: {real}]")


def test_a_single_argument_still_gives_a_single():
    """The divergence is only for double arguments; everything else still
    matches the binary exactly."""
    print("\nand a single argument is still single")
    print("-" * 62)
    for source, expected in [
        ('10 PRINT SQR(2)', ' 1.41421 '),
        ('10 D# = SQR(2): PRINT D#', ' 1.414213538169861 '),
        ('10 H# = SQR(4%): PRINT H#', ' 2 '),          # never narrower than single
        ('10 D# = SIN(1): PRINT D#', ' .8414709568023682 '),
    ]:
        got = one(source)
        check(got == expected, f"{source[3:30]:30} -> {got!r}"
              + ("" if got == expected else f"   (want {expected!r})"))


def test_input_stores_a_single():
    """INPUT into a single-precision variable loses what a single cannot hold."""
    print("\nINPUT")
    print("-" * 62)
    # The prompt lands on the same captured line as the value, so compare the
    # tail rather than the whole line.
    got = one('10 INPUT "X"; X\n20 Y# = X: PRINT Y#', answers=['.1'])
    check(got.endswith(' .1000000014901161 '),
          f"INPUT .1 into X -> {got!r}")


def test_the_loop_variable_after_the_loop():
    """MBASIC leaves it at the value that ended the loop, not the last one
    that fit - FOR I=1 TO 3: NEXT: PRINT I prints 4 there, and printed 3 here.

    With a fractional STEP the loop variable also carries the accumulated
    single-precision error, which is what makes the last case a test of both.
    """
    print("\nwhere FOR leaves the loop variable")
    print("-" * 62)
    for source, expected in [
        ('10 FOR I=1 TO 3: NEXT I: PRINT I', ' 4 '),
        ('10 FOR J=1 TO 2 STEP .5: NEXT J: PRINT J', ' 2.5 '),
        ('10 FOR K=1 TO 2 STEP .1: NEXT K: PRINT K', ' 2 '),
        ('10 FOR L=1 TO 2 STEP .1: NEXT L: M# = L: PRINT M#',
         ' 2.000000238418579 '),
        ('10 FOR I=5 TO 1 STEP -2: NEXT I: PRINT I', '-1 '),
    ]:
        got = one(source)
        check(got == expected, f"{source[3:44]:44} -> {got!r}"
              + ("" if got == expected else f"   (want {expected!r})"))


def test_the_literal_suffix_survives_parsing():
    """1# and 1 have the same value and different precision, and the lexer
    used to throw the suffix away."""
    print("\nthe type suffix on a literal reaches the tree")
    print("-" * 62)
    for source, expected in [('1#', '1#'), ('1', '1'), ('1.5D2', '1.5D2'),
                             ('&HFF', '&HFF'), ('1234567.8!', '1234567.8!')]:
        node = Parser(Lexer(f'10 PRINT {source}').tokenize()).parse() \
            .lines[0].statements[0].expressions[0]
        check(node.literal == expected,
              f"{source:12} -> literal {node.literal!r}"
              + ("" if node.literal == expected else f"   (want {expected!r})"))


def test_the_precision_is_worked_out_once():
    """Every operation asks for the type, so the answer is cached on the node
    rather than re-walking the subtree once per pass through a loop."""
    print("\nthe type of a node is computed once")
    print("-" * 62)
    ast = Parser(Lexer('10 FOR I=1 TO 3: X = I/3: NEXT I').tokenize()).parse()
    runtime = Runtime({line.line_number: line for line in ast.lines})
    interpreter = Interpreter(runtime, Capture())
    interpreter.start()
    for _ in range(50):
        interpreter.tick(mode='run', max_statements=5000)
        if not runtime.pc.is_running():
            break
    divide = ast.lines[0].statements[1].expression
    check(getattr(divide, '_mb_digits', None) == 6,
          f"the division kept its answer ({getattr(divide, '_mb_digits', None)})")


if __name__ == "__main__":
    print("MBASIC 5.21 single-precision arithmetic")
    print("=" * 62)

    test_the_float32_round_trip()
    test_integer_assignment_rounds()
    test_coerce_by_suffix()
    test_programs_match_the_real_binary()
    test_maths_functions_follow_their_argument()
    test_a_single_argument_still_gives_a_single()
    test_fractional_arguments_round()
    test_a_string_in_a_number_is_a_type_mismatch()
    test_input_stores_a_single()
    test_the_loop_variable_after_the_loop()
    test_the_literal_suffix_survives_parsing()
    test_the_precision_is_worked_out_once()

    failed = results.count(False)
    print("\n" + "=" * 62)
    print(f"Results: {results.count(True)} passed, {failed} failed")

    if failed:
        print("❌ Some tests failed")
        sys.exit(1)
    print("✅ All tests passed!")
    sys.exit(0)
