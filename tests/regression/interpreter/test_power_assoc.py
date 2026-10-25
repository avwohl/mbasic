#!/usr/bin/env python3
"""
^ is left associative in MBASIC 5.21 (issue 26): 2^3^2 is (2^3)^2 = 64, not 512.
A minus or NOT after ^ takes the rest of the chain (2^-3^2 = 2^-(3^2)), and a
plus after ^ is ignored (2^+3^2 = 64).  Every expected value was printed by the
real 5.21 binary under cpmemu (A=2, B=3, C=2).
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
from src.ui.ui_helpers import serialize_expression

CASES = [
    ("2^3^2", "64"),
    ("2^-3^2", "1.95313E-03"),
    ("-2^2^3", "-64"),
    ("2^3^-1", ".125"),
    ("2^-2^-1", ".707107"),
    ("A^B^C", "64"),
    ("2*-3^2", "-18"),
    ("-A^B*C", "-16"),
    ("NOT 2^2", "-5"),
    ("2^2=4", "-1"),
    ("4^.5^2", "4"),
    ("2^-1^2", ".5"),
    ("2^3^2^2", "4096"),
    ("2^-2^3^2", "5.42101E-20"),
    ("2^+3^2", "64"),
    ("2^-3*2", ".25"),
    ("2^-3+2", "2.125"),
    ("2^3^-1^2", ".125"),
    ("2^NOT 1^2", ".25"),
    ("2^(3)^2", "64"),
    ("2^-2^3^-1", ".917004"),
    ("2^--2^2", "16"),
    ("2^-2^-2^2", ".957603"),
    ("2^+2^3", "64"),
    ("2^+-2^2", ".0625"),
    ("2^-+2^2", ".0625"),
    ("2^+2^-1^2", ".25"),
    ("3^+2^2^2", "6561"),
    ("2^NOT 2^2", ".03125"),
    ("2^NOT 3^2", "9.76563E-04"),
    ("2^-NOT 0^2", "2"),
    ("2^NOT 0=0", "1"),
    ("2^NOT 0+1", ".25"),
    ("2^NOT 1 AND 1", "0"),
    ("2^NOT 0*3", ".5"),
    ("2^-1+1", "1.5"),
    ("2^NOT 0^2^2", ".5"),
    ("2^NOT NOT 0^2", "1"),
    ("2^NOT 1 OR 1", "1"),
    ("2^(3^2)", "512"),
    ("(2^3)^2", "64"),
    ("(2^-3)^2", ".015625"),
    ("-2^-2^3", "-3.90625E-03"),
]


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
        return ""

    def input_line(self, prompt=''):
        return ""

    def input_char(self, blocking=True):
        return ""

    def clear_screen(self):
        pass

    def error(self, message):
        self.parts.append(f"Error: {message}\n")

    def debug(self, message):
        pass


def parse(source):
    return Parser(Lexer(source).tokenize()).parse()


def run(source):
    ast = parse(source)
    runtime = Runtime({line.line_number: line for line in ast.lines})
    handler = Capture()
    interpreter = Interpreter(runtime, handler)
    interpreter.start()
    for _ in range(50):
        state = interpreter.tick(mode='run', max_statements=5000)
        if state.error_info or not runtime.pc.is_running():
            break
    return ''.join(handler.parts)


source = "10 A=2:B=3:C=2\n" + "".join(
    f"{20 + 10 * i} PRINT {expr}\n" for i, (expr, _) in enumerate(CASES))
check(len(parse(source).lines) == len(CASES) + 1, "no power line is dropped at load")
out = [line.strip() for line in run(source).splitlines()]
for (expr, want), got in zip(CASES, out):
    check(got == want, f"{expr} prints {got}, real MBASIC prints {want}")
check(len(out) == len(CASES), f"{len(out)} lines printed")

# The expression text survives the serializer (LIST and RENUM use it) and reads back as the
# same tree, so the same number.
for expr, _ in CASES:
    node = parse("10 Y=" + expr).lines[0].statements[0].expression
    text = serialize_expression(node)
    again = parse("10 Y=" + text).lines[0].statements[0].expression
    check(serialize_expression(again) == text, f"serializer round trip: {expr} -> {text}")
    check(run(f"10 A=2:B=3:C=2:PRINT {text}").strip() == run(f"10 A=2:B=3:C=2:PRINT {expr}").strip(),
          f"serialized {text} has the value of {expr}")

if all(results):
    print(f"\nAll {len(results)} checks passed")
    sys.exit(0)
print(f"\n{results.count(False)} of {len(results)} checks FAILED")
sys.exit(1)
