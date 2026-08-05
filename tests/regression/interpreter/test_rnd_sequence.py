#!/usr/bin/env python3
"""
Test that RND produces MBASIC 5.21's sequence, number for number.

RND used to be Python's `random.random()`, seeded from the clock. That is wrong
twice over: the numbers are not MBASIC's, and they are different every run
where MBASIC's are the same every run. A BASIC game that deals a hand or lays
out a board got a different one here than on the real machine, and a different
one each time from itself.

MBASIC's generator was read out of `com/mbasic.com` - see src/mbasic_rnd.py for
the routine and the addresses. Every expectation below came off the real binary
running under cpmemu:

    PRINT RND;RND;RND        .245121  .305003  .311866      every single time

The values here are printed through a double (A#=RND) wherever the full
mantissa matters, because PRINT on a single shows six figures and would hide a
wrong low byte.

What is checked: the first 200 values in order - which reaches past the
perturbation the routine applies every 171 draws - the three argument forms,
RANDOMIZE, and that RUN starts the sequence again.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

import struct

from src.interpreter import Interpreter
from src.iohandler.base import IOHandler
from src.lexer import Lexer
from src.mbasic_rnd import MbasicRandom, INITIAL_SEED
from src.number_format import format_number, DOUBLE_DIGITS
from src.parser import Parser
from src.runtime import Runtime

results = []


def check(condition, label):
    results.append(bool(condition))
    print(f"{'PASS' if condition else 'FAIL'}: {label}")


class Capture(IOHandler):
    def __init__(self, answers=()):
        self.parts = []
        self.answers = list(answers)

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
    """Run a program and return the lines it printed."""
    ast = Parser(Lexer(source).tokenize()).parse()
    runtime = Runtime({line.line_number: line for line in ast.lines})
    handler = Capture()
    pending = list(answers)
    interpreter = Interpreter(runtime, handler)
    interpreter.start()
    for _ in range(400):
        state = interpreter.tick(mode='run', max_statements=20000)
        if state.input_prompt is not None:
            interpreter.provide_input(pending.pop(0) if pending else "0")
            continue
        if not runtime.pc.is_running() or state.error_info:
            break
    return [p.rstrip('\n') for p in handler.text().split('\n') if p.strip()]


def one(source, answers=()):
    printed = run(source, answers)
    return printed[0] if printed else ''


def same_value(got, printed):
    """Is `got` the number the real binary printed as `printed`?

    Compared as values rather than as sixteen digits: MBASIC's own
    binary-to-decimal conversion rounds the sixteenth digit up where correct
    rounding rounds it down, for about one value in eight - a difference in its
    printing, not in the number. See docs/dev/NUMBER_FORMATTING.md.
    """
    want = float(printed.replace('D', 'E'))
    single = lambda v: struct.unpack('f', struct.pack('f', v))[0]
    return single(got) == single(want) and abs(got - want) < 1e-15


# ---------------------------------------------------------------------------
# The sequence
# ---------------------------------------------------------------------------

#: The first sixteen values, as MBASIC 5.21 printed them from A#=RND.
FIRST_VALUES = [
    ".2451214492321014", ".3050031960010529", ".3118660151958466",
    ".5151634216308594", ".05831358209252358", ".7888908386230469",
    ".4971021711826325", ".3637510240077973", ".9845459461212158",
    ".9015913605690003", ".7273133397102356", "6.834005936980248D-03",
    ".9694297313690186", "1.751398667693138D-03", ".9562250971794129",
    ".04076776653528214",
]

#: Values 168 to 176, which straddle the perturbation applied on the 171st
#: draw. A sequence checked only a few dozen values deep would pass without
#: the perturbation and be wrong from then on.
AROUND_THE_PERTURBATION = 171
LATER_VALUES = {
    168: ".2108281552791595", 169: ".05292222276329994",
    170: ".3010344803333283", 171: ".5494452714920044",
    172: ".06261692196130753", 173: ".4507846534252167",
    174: ".4784656465053559", 175: ".6221193671226501",
    176: ".155074805021286", 200: ".4247079789638519",
}


def test_the_first_values():
    """The sequence starts the same way every run, and it is MBASIC's."""
    print("\nthe first values, against the real binary")
    print("-" * 62)
    rnd = MbasicRandom()
    got = [rnd.next() for _ in range(len(FIRST_VALUES))]
    wrong = [f"[{i}] {g!r} != {w}" for i, (g, w) in enumerate(zip(got, FIRST_VALUES))
             if not same_value(g, w)]
    check(not wrong, f"{len(FIRST_VALUES) - len(wrong)}/{len(FIRST_VALUES)} match"
          + ("" if not wrong else "; " + "; ".join(wrong[:3])))


def test_the_sequence_is_the_same_every_run():
    """MBASIC seeds from a constant, so two runs give the same numbers.

    Python's random.random() reseeded from the clock, which made every run of
    a game different from every other and from the real machine.
    """
    print("\nthe same numbers every run")
    print("-" * 62)
    first = run('10 PRINT RND;RND;RND')
    second = run('10 PRINT RND;RND;RND')
    check(first == second == [' .245121  .305003  .311866 '],
          f"two runs both give ' .245121  .305003  .311866 ' ({first})")


def test_run_starts_the_sequence_again():
    """RUN reloads the seed and zeroes the counters, at 0x4358."""
    print("\nRUN starts over")
    print("-" * 62)
    rnd = MbasicRandom()
    for _ in range(20):
        rnd.next()
    rnd.reset()
    check(rnd.seed == INITIAL_SEED, "the seed is back to the one RUN loads")
    check(same_value(rnd.next(), FIRST_VALUES[0]),
          "and the first value is the first value again")


def test_the_perturbation_at_171():
    """Every 171 draws the routine nudges three bytes of the result.

    A sequence that is only checked for a few dozen values would never notice,
    and it would then diverge from the real machine forever after.
    """
    print("\nthe perturbation on the 171st draw")
    print("-" * 62)
    rnd = MbasicRandom()
    wrong = []
    for n in range(1, 201):
        value = rnd.next()
        if n in LATER_VALUES and not same_value(value, LATER_VALUES[n]):
            wrong.append(f"[{n}] {value!r} != {LATER_VALUES[n]}")
    check(not wrong,
          f"values 168-176 and 200 all match" + ("" if not wrong else "; " + "; ".join(wrong[:3])))
    check(rnd.count == 200 - AROUND_THE_PERTURBATION,
          f"and the counter wrapped at 171 (now {rnd.count})")


# ---------------------------------------------------------------------------
# The argument forms, and RANDOMIZE
# ---------------------------------------------------------------------------

def test_the_argument_forms():
    """RND(0) repeats, RND(x>0) advances, RND(x<0) restarts.

    RND(-1) and RND(-2) give the same number because only the argument's
    mantissa is used and -1 and -2 differ only in exponent. That is the detail
    that says the argument itself is being scrambled, not a seed derived from
    its value.
    """
    print("\nRND(0), RND(x>0), RND(x<0)")
    print("-" * 62)
    rnd = MbasicRandom()
    for source, expected in [
        (lambda: rnd.next(), ".2451214492321014"),
        (lambda: rnd.next(0), ".2451214492321014"),      # repeats, draws nothing
        (lambda: rnd.next(0), ".2451214492321014"),
        (lambda: rnd.next(1), ".3050031960010529"),      # advances
        (lambda: rnd.next(5), ".3118660151958466"),      # any positive is the same
        (lambda: rnd.next(-1), ".3086014091968536"),
        (lambda: rnd.next(-1), ".3086014091968536"),     # deterministic
        (lambda: rnd.next(), ".498870462179184"),
        (lambda: rnd.next(-2), ".3086014091968536"),     # same mantissa as -1
        (lambda: rnd.next(), ".498870462179184"),
        (lambda: rnd.next(-1000), ".3086086809635162"),  # different mantissa
    ]:
        value = source()
        ok = same_value(value, expected)
        check(ok, f"{format_number(value, DOUBLE_DIGITS):22}"
              + ("" if ok else f" want {expected}")) 


def test_randomize():
    """RANDOMIZE n puts n into the middle two bytes of the seed and draws once.

    It does not reset the generator, which is why RANDOMIZE 1 twice in one run
    gives two different numbers - the bytes it left alone had moved on.
    """
    print("\nRANDOMIZE")
    print("-" * 62)
    rnd = MbasicRandom()
    rnd.randomize(1)
    first, second = rnd.next(), rnd.next()
    check(same_value(first, ".5804103016853333"), f"RANDOMIZE 1 then RND -> {first!r}")
    check(same_value(second, ".1289277374744415"), f"and the next -> {second!r}")
    rnd.randomize(2)
    check(same_value(rnd.next(), ".9715879559516907"), "RANDOMIZE 2")
    rnd.randomize(3)
    check(same_value(rnd.next(), ".9104958772659302"), "RANDOMIZE 3")
    rnd.randomize(1)
    again = rnd.next()
    check(same_value(again, ".4762487709522247"),
          f"RANDOMIZE 1 a second time gives something else ({again!r})")


def test_randomize_through_the_interpreter():
    print("\nRANDOMIZE in a program")
    print("-" * 62)
    got = one('10 RANDOMIZE 1: PRINT RND')
    check(got == ' .58041 ', f"RANDOMIZE 1: PRINT RND -> {got!r}")
    # With no argument the real binary asks for a seed rather than using the
    # clock, so the run stays repeatable.
    printed = run('10 RANDOMIZE\n20 A#=RND: PRINT A#', answers=['7'])
    check(printed and printed[0].endswith(' .04349604621529579 '),
          f"RANDOMIZE with no argument prompts and takes the answer ({printed})")


def test_rnd_through_print():
    print("\nRND in a program")
    print("-" * 62)
    for source, expected in [
        ('10 PRINT RND;RND;RND', ' .245121  .305003  .311866 '),
        ('10 A#=RND: PRINT A#', ' .2451214492321014 '),
        ('10 X=RND: PRINT RND(0)', ' .245121 '),
        ('10 PRINT INT(RND*100)', ' 24 '),
    ]:
        got = one(source)
        check(got == expected, f"{source[3:34]:32} -> {got!r}"
              + ("" if got == expected else f"   (want {expected!r})"))


if __name__ == "__main__":
    print("MBASIC 5.21's RND")
    print("=" * 62)

    test_the_first_values()
    test_the_sequence_is_the_same_every_run()
    test_run_starts_the_sequence_again()
    test_the_perturbation_at_171()
    test_the_argument_forms()
    test_randomize()
    test_randomize_through_the_interpreter()
    test_rnd_through_print()

    failed = results.count(False)
    print("\n" + "=" * 62)
    print(f"Results: {results.count(True)} passed, {failed} failed")

    if failed:
        print("❌ Some tests failed")
        sys.exit(1)
    print("✅ All tests passed!")
    sys.exit(0)
