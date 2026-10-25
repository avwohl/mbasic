#!/usr/bin/env python3
"""
The ELSE clause of a one-line IF runs to the end of the line, as in MBASIC 5.21.

    IF 0 THEN PRINT "t" ELSE PRINT "e1":PRINT "e2"

prints e1 and e2 when the condition is false and only t when the condition is true.
Checked against real MBASIC 5.21 (cpmemu). The parser used to end the ELSE clause after one
statement, so the rest of the line ran in both cases, and a FOR in an ELSE clause lost its NEXT
(semantic analysis: NEXT without FOR).
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


def lines_of(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


def test_else_runs_to_end_of_line():
    print("\nELSE clause with several statements")
    got = lines_of(run('10 IF 1=1 THEN PRINT "t" ELSE PRINT "e1":PRINT "e2"\n'
                       '20 X=0:IF X THEN PRINT "t" ELSE PRINT "e1":PRINT "e2"\n'))
    check(got == ["t", "e1", "e2"], f"got {got}")


def test_analyzer_accepts_the_two_lines():
    from src.semantic_analyzer import SemanticAnalyzer
    ast = Parser(Lexer('10 X=1:IF X=1 THEN FOR I=1 TO 3:PRINT I;:NEXT I:PRINT "a"\n'
                       '20 X=0:IF X=1 THEN PRINT "no" ELSE FOR J=1 TO 2:PRINT J;:NEXT:PRINT "b"\n'
                       '30 SYSTEM\n').tokenize()).parse()
    analyzer = SemanticAnalyzer()
    check(analyzer.analyze(ast), f"analysis errors: {analyzer.errors}")


if __name__ == "__main__":
    test_else_runs_to_end_of_line()
    test_analyzer_accepts_the_two_lines()
    failed = results.count(False)
    print(f"Results: {results.count(True)} passed, {failed} failed")
    sys.exit(1 if failed else 0)
