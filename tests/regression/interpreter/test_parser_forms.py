#!/usr/bin/env python3
"""
Statement and expression forms that real MBASIC 5.21 accepts and the parser
used to reject (issues 17, 21 and 24).  Every expected value was taken from
the real 5.21 binary under cpmemu.

    PRINT 2^-1              sign after ^            was a syntax error
    LINE INPUT A$(I)        array element target    was a syntax error
    WRITE 1;2               ; between items         was a syntax error

A line that fails to parse is dropped at load time, so each check below also
looks at the program as a whole, not just at the one line.
"""

import os
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.interpreter import Interpreter
from src.iohandler.base import IOHandler
from src.lexer import Lexer
from src.parser import Parser
from src.runtime import Runtime
from src.ui.ui_helpers import serialize_statement, serialize_expression

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
        if prompt:
            self.parts.append(str(prompt))
        return self.answers.pop(0) if self.answers else ""

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


def parse(source):
    return Parser(Lexer(source).tokenize()).parse()


def run(source, answers=()):
    ast = parse(source)
    runtime = Runtime({line.line_number: line for line in ast.lines})
    handler = Capture(answers)
    interpreter = Interpreter(runtime, handler)
    interpreter.start()
    for _ in range(50):
        state = interpreter.tick(mode='run', max_statements=5000)
        if state.error_info:
            break
        if state.input_prompt is not None:
            interpreter.provide_input(handler.answers.pop(0) if handler.answers else "")
            continue
        if not runtime.pc.is_running():
            break
    return handler.text().rstrip('\n')


def lines_of(source):
    """The output as a list of lines with the number padding stripped."""
    return [line.strip() for line in source.splitlines()]


# --- issue 21: a sign after ^ ------------------------------------------------

POWER_PROGRAM = '''10 X=3
20 PRINT 2^-1
30 PRINT 2^-X
40 PRINT -2^2
50 PRINT 2^-1^2
60 PRINT X*-1
70 PRINT X/-2
80 PRINT NOT -1
90 IF 2^-1=.5 THEN PRINT "IFOK"
100 IF X*-1<0 THEN PRINT "IF2"
110 PRINT 2^+1
120 PRINT X^-X^2
130 PRINT 2--1
140 PRINT -X^-2
150 A=2^-1:PRINT A;ABS(2^-1);4^-.5
160 PRINT 2*-3^2;-2^-2;2^-+1;- -2^2
'''
POWER_EXPECTED = ['.5', '.125', '-4', '.5', '-3', '-1.5', '0', 'IFOK', 'IF2',
                  '2', '5.08053E-05', '3', '-.111111', '.5  .5  .5',
                  '-18 -.25  .5  4']
# 3^-9 is 5.08052E-05 in the real binary (its own pow routine); the project
# computes with IEEE arithmetic, see docs/dev/MBASIC_521_DIVERGENCES_TODO.md.

out = lines_of(run(POWER_PROGRAM))
check(out == POWER_EXPECTED, f"sign after ^ prints {out}")
check(len(parse(POWER_PROGRAM).lines) == 16, "no power line is dropped at load")

# The text of each line survives the serializer, and reads back the same.
for text in ["2^-1", "2^-X", "2^-1^2", "X^-X^2", "-X^-2", "2^+1", "-2^2",
             "(-2)^2", "-(2+3)", "2^-(1+X)", "NOT (A AND B)", "(NOT A)=B",
             "NOT A=B"]:
    node = parse("10 Y=" + text).lines[0].statements[0].expression
    again = parse("10 Y=" + serialize_expression(node)).lines[0].statements[0].expression
    check(serialize_expression(again) == serialize_expression(node),
          f"serializer round trip: {text} -> {serialize_expression(node)}")
check(run("10 PRINT (-2)^2;-(2+3);-2^2\n") == " 4 -5 -4 ",
      "evaluation of (-2)^2, -(2+3), -2^2")
node = parse("10 Y=(-2)^2").lines[0].statements[0].expression
check(run("10 PRINT " + serialize_expression(node)).strip() == "4",
      "serializer keeps the brackets in (-2)^2")

# --- issue 24: LINE INPUT into an array element ---------------------------------

source = '''10 DIM A$(3),B$(2,2)
20 LINE INPUT A$(1)
30 PRINT "[";A$(1);"]"
40 I=2
50 LINE INPUT "P";A$(I)
60 PRINT "[";A$(2);"]"
70 LINE INPUT B$(1,I)
80 PRINT "[";B$(1,2);"]"
'''
out = run(source, ["first", "second", "third, x"])
check(out.splitlines() == ["[first]", "P[second]", "[third, x]"],
      f"LINE INPUT into array elements: {out.splitlines()}")

workdir = tempfile.mkdtemp()
old = os.getcwd()
os.chdir(workdir)
try:
    source = '''10 DIM A$(3)
20 OPEN "O",#1,"T.DAT"
30 PRINT #1,"hello, x"
40 PRINT #1,"world"
50 CLOSE #1
60 OPEN "I",#1,"T.DAT"
70 FOR I=1 TO 2
80 LINE INPUT #1,A$(I)
90 PRINT "[";A$(I);"]"
100 NEXT
110 CLOSE
'''
    out = run(source)
    check(out.splitlines() == ["[hello, x]", "[world]"],
          f"LINE INPUT #1 into array elements: {out.splitlines()}")

    # --- issue 17: WRITE with ; between items ------------------------------
    source = '''10 WRITE 1;2
20 WRITE "a";"b";3
30 A=0:B$="":WRITE A;B$
40 WRITE 1,2
50 OPEN "O",#1,"W.DAT":WRITE #1,3;4:WRITE #1,"x";5,"y":CLOSE
60 OPEN "I",#1,"W.DAT":LINE INPUT #1,C$:LINE INPUT #1,D$:PRINT C$:PRINT D$:CLOSE
'''
    out = run(source)
    check(out.splitlines() == ['1,2', '"a","b",3', '0,""', '1,2', '3,4', '"x",5,"y"'],
          f"WRITE with ; separators: {out.splitlines()}")
finally:
    os.chdir(old)

# Forms that real MBASIC rejects stay rejected.
for bad in ["10 WRITE #1;3", "10 WRITE ;1", "10 WRITE 1;;2"]:
    try:
        parse(bad)
        rejected = False
    except Exception:
        rejected = True
    check(rejected, f"still a syntax error: {bad}")

# LIST keeps the text the user typed.
ast = parse('10 LINE INPUT "P";A$(I+1):WRITE 1;2\n')
check(ast.lines[0].statements[0].variable.subscripts is not None,
      "LINE INPUT keeps its subscripts in the tree")
check(serialize_statement(ast.lines[0].statements[0]) == 'LINE INPUT "P"; A$(I + 1)',
      "LINE INPUT array element serializes")

if all(results):
    print(f"\nAll {len(results)} checks passed")
    sys.exit(0)
print(f"\n{results.count(False)} of {len(results)} checks FAILED")
sys.exit(1)
