#!/usr/bin/env python3
"""
Test GOSUB inside a THEN/ELSE clause, and NEXT with no variable.

Two interpreter bugs found while making basic/games/startrek.bas run. Both are
in the same handful of lines of that program, and both are silent - the program
keeps going and quietly does less than it was told.

1. A GOSUB inside a THEN clause dropped the rest of the clause.

       30 IF I > 0 THEN GOSUB 100: PRINT "NEVER PRINTED"

   A clause is not addressable by PC - the statement table holds one entry for
   the whole IF - so the GOSUB could only point its return address at the
   statement after the IF, and everything between was lost. Real MBASIC 5.21
   prints it; this is checked against the real binary under cpmemu.

   In startrek that is how the galaxy is filled in:

       380 IF I > 0 THEN GOSUB 540: S(X, Y) = 5: I = I - 1: GOTO 380

   The GOSUB picks an empty sector and the three statements that use it never
   ran, so the map came up with no stars, no Klingons and no starbases - while
   the status panel said CONDITION RED. 180 lines across 35 of the shipped
   programs have this shape.

2. NEXT with no variable searched the source backwards for its FOR, and called
   a StatementTable method that does not exist while doing it. A NEXT reached
   by a jump never found its loop:

       580 FOR I = 0 TO 7: IF K3(I) <= 0 THEN 605
       ...
       605 NEXT: RETURN

   Which FOR a bare NEXT belongs to is a question about what is running, not
   about the text: it is the innermost loop still active.
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
    """Record one check; print pass/fail immediately."""
    results.append(bool(condition))
    print(f"{'PASS' if condition else 'FAIL'}: {label}")


class Capture(IOHandler):
    """Collects output, and answers INPUT from a fixed list."""

    def __init__(self, answers=()):
        self.parts = []
        self.answers = list(answers)

    def output(self, text, end='\n'):
        self.parts.append(str(text) + end)

    def input(self, prompt=''):
        # "" would leave the interpreter asking the same question forever.
        return self.answers.pop(0) if self.answers else "0"

    def input_line(self, prompt=''):
        return self.input(prompt)

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


def run(source, max_statements=20000, answers=()):
    """Run a program to completion and return what it printed."""
    ast = Parser(Lexer(source).tokenize()).parse()
    runtime = Runtime({line.line_number: line for line in ast.lines})
    handler = Capture(answers)
    interpreter = Interpreter(runtime, handler)
    interpreter.start()
    pending = list(answers)
    for _ in range(200):
        state = interpreter.tick(mode='run', max_statements=max_statements)
        if state.input_prompt is not None:
            # The tick model asks for input by setting state.input_prompt and
            # waiting to be given a value - it does not call io.input().
            interpreter.provide_input(pending.pop(0) if pending else "0")
            continue
        if not runtime.pc.is_running() or state.error_info:
            break
    if state.error_info:
        return handler.text() + f"\nERROR: {state.error_info.error_message}"
    return handler.text()


def lines_of(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


def test_statements_after_a_gosub_in_then_still_run():
    """The whole clause belongs to the IF, GOSUB or not."""
    print("\nstatements after a GOSUB inside THEN")
    print("-" * 60)
    got = lines_of(run('10 I = 3\n'
                       '20 IF I > 0 THEN GOSUB 100: PRINT "AFTER"\n'
                       '30 PRINT "NEXT LINE": END\n'
                       '100 PRINT "IN SUB": RETURN\n'))
    check(got == ['IN SUB', 'AFTER', 'NEXT LINE'],
          f"the subroutine runs, then the rest of the clause (got {got})")


def test_a_false_condition_runs_none_of_it():
    """The control that stops the fix from running clauses unconditionally."""
    print("\na false condition still skips the whole clause")
    print("-" * 60)
    got = lines_of(run('10 I = 0\n'
                       '20 IF I > 0 THEN GOSUB 100: PRINT "SHOULD NOT PRINT"\n'
                       '30 PRINT "ONLY THIS": END\n'
                       '100 PRINT "SHOULD NOT PRINT EITHER": RETURN\n'))
    check(got == ['ONLY THIS'], f"nothing in the clause ran (got {got})")


def test_the_startrek_loop_shape():
    """IF cond THEN GOSUB x: <work>: GOTO self - how startrek fills a quadrant.

    The GOTO at the end has to win over the GOSUB's return address, or the loop
    runs once instead of counting down.
    """
    print("\nTHEN GOSUB ... GOTO self loops")
    print("-" * 60)
    got = lines_of(run('10 K = 3\n'
                       '20 IF K > 0 THEN GOSUB 100: K = K - 1: PRINT "K"; K: GOTO 20\n'
                       '30 PRINT "DONE": END\n'
                       '100 S = S + 1: RETURN\n'))
    check(got == ['K 2', 'K 1', 'K 0', 'DONE'],
          f"the loop counted down (got {got})")


def test_gosub_inside_else():
    """ELSE clauses are the same shape and take the same path."""
    print("\nstatements after a GOSUB inside ELSE")
    print("-" * 60)
    got = lines_of(run('10 I = 0\n'
                       '20 IF I > 0 THEN PRINT "THEN" ELSE GOSUB 100: PRINT "AFTER"\n'
                       '30 PRINT "END": END\n'
                       '100 PRINT "IN SUB": RETURN\n'))
    check(got == ['IN SUB', 'AFTER', 'END'],
          f"the ELSE clause finished (got {got})")


def test_nested_gosubs_from_clauses():
    """A clause tail that itself contains another GOSUB."""
    print("\nnested GOSUBs, each from inside a clause")
    print("-" * 60)
    got = lines_of(run('10 I = 1\n'
                       '20 IF I > 0 THEN GOSUB 100: PRINT "BACK IN 20": END\n'
                       '100 PRINT "SUB 1"\n'
                       '110 IF I > 0 THEN GOSUB 200: PRINT "BACK IN 110"\n'
                       '120 RETURN\n'
                       '200 PRINT "SUB 2": RETURN\n'))
    check(got == ['SUB 1', 'SUB 2', 'BACK IN 110', 'BACK IN 20'],
          f"both tails ran, innermost first (got {got})")


def test_two_gosubs_in_one_clause():
    """The tail after the first GOSUB contains the second."""
    print("\ntwo GOSUBs in the same clause")
    print("-" * 60)
    got = lines_of(run('10 I = 1\n'
                       '20 IF I > 0 THEN GOSUB 100: GOSUB 200: PRINT "AFTER BOTH"\n'
                       '30 END\n'
                       '100 PRINT "ONE": RETURN\n'
                       '200 PRINT "TWO": RETURN\n'))
    check(got == ['ONE', 'TWO', 'AFTER BOTH'],
          f"both subroutines ran, then the tail (got {got})")


def test_bare_next_reached_by_a_jump():
    """startrek's line 580/605 shape: the FOR jumps over its body to its NEXT."""
    print("\na bare NEXT that is jumped to")
    print("-" * 60)
    got = lines_of(run('10 FOR I = 0 TO 3\n'
                       '20 IF I = 2 THEN 40\n'
                       '30 PRINT "BODY"; I\n'
                       '40 NEXT\n'
                       '50 PRINT "DONE": END\n'))
    check(got == ['BODY 0', 'BODY 1', 'BODY 3', 'DONE'],
          f"the loop ran to completion (got {got})")


def test_bare_next_picks_the_innermost_loop():
    """Two bare NEXTs close the inner loop then the outer one."""
    print("\nbare NEXT with nested loops")
    print("-" * 60)
    got = lines_of(run('10 FOR A = 1 TO 2\n'
                       '20 FOR B = 1 TO 2\n'
                       '30 PRINT "A"; A; "B"; B\n'
                       '40 NEXT\n'
                       '50 NEXT\n'
                       '60 PRINT "DONE": END\n'))
    check(got == ['A 1 B 1', 'A 1 B 2', 'A 2 B 1', 'A 2 B 2', 'DONE'],
          f"inner then outer (got {got})")


def test_startrek_fills_its_galaxy():
    """The program this was all found in: its map must not be empty.

    Lines 350-380 place Klingons, starbases and stars with
    'IF ... THEN GOSUB 540: S(X,Y) = n: ...'. With the clause tail dropped the
    quadrant display came up as nothing but dots and the Enterprise, while the
    status panel reported Klingons present.
    """
    print("\nstartrek.bas places something in its quadrant")
    print("-" * 60)
    program = PROJECT_ROOT / 'basic' / 'games' / 'startrek.bas'
    if not program.exists():
        check(False, f"{program} is missing")
        return

    source = program.read_text()
    # Stop after the first quadrant is drawn: the game is interactive, and
    # what is being checked is what the map contains.
    source = source.replace('730 INPUT "COMMAND"; A', '730 END')
    # 'N' to the instructions prompt, then the random number it asks for.
    text = run(source, answers=['N', '42'])
    grid = [line for line in text.splitlines() if ' . ' in line or '. .' in line]

    check(len(grid) >= 8, f"a quadrant was drawn ({len(grid)} rows)")
    contents = ''.join(grid)
    check(any(symbol in contents for symbol in ('K', 'B', '*')),
          f"and it contains Klingons, a starbase or stars, not just dots "
          f"({contents[:60]!r})")


if __name__ == "__main__":
    print("GOSUB inside THEN/ELSE, and bare NEXT")
    print("=" * 60)

    test_statements_after_a_gosub_in_then_still_run()
    test_a_false_condition_runs_none_of_it()
    test_the_startrek_loop_shape()
    test_gosub_inside_else()
    test_nested_gosubs_from_clauses()
    test_two_gosubs_in_one_clause()
    test_bare_next_reached_by_a_jump()
    test_bare_next_picks_the_innermost_loop()
    test_startrek_fills_its_galaxy()

    failed = results.count(False)
    print("\n" + "=" * 60)
    print(f"Results: {results.count(True)} passed, {failed} failed")

    if failed:
        print("❌ Some tests failed")
        sys.exit(1)
    print("✅ All tests passed!")
    sys.exit(0)
