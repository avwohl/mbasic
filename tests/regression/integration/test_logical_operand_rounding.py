"""AND, OR, XOR, EQV, IMP and NOT round a fractional operand and check 16 bits (issue 56).

MBASIC converts each operand like CINT: halves round away from zero, and a value outside
-32768..32767 is Overflow. The generated JavaScript already does this (test_js_logical_ops.py).
Each case is one program line. The program prints "<n>|" first, then the statement
runs, and ON ERROR GOTO prints "ERR <code> ERL <line>" on the same line. The expected
text is what real MBASIC 5.21 printed for the same program (cpmemu, tests/HOW_TO_RUN_REAL_MBASIC.md).
Error 6 is Overflow, 5 is Illegal function call, 9 is Subscript out of range, 13 is Type mismatch.
"""
import re
import subprocess
import sys
from pathlib import Path

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: logical operand rounding tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

ROOT = Path(__file__).resolve().parents[3]

PRELUDE = ["DIM A(100)", "DIM M(2,2)", "ON ERROR GOTO 60000"]
HANDLER = 'PRINT "ERR";ERR;"ERL";ERL:RESUME NEXT'

# (statement, output on real MBASIC 5.21)
CASES = [
    ('PRINT NOT 2.7;NOT -2.7;NOT 2.5;NOT 2.4;NOT 3.5', '-4  2 -4 -3 -5'),
    ('PRINT 2.5 AND 3;-2.5 OR 0;2.6 XOR 0;2.5 EQV 0;2.5 IMP 0', ' 3 -3  3 -4 -4'),
    ('PRINT -1.5 AND -1', '-2'),
    ('PRINT 40000 OR 1', 'ERR 6 ERL 130'),
    ('PRINT 65535 AND 1', 'ERR 6 ERL 140'),
    ('PRINT 32767.5 OR 0', 'ERR 6 ERL 150'),
    ('PRINT -32768.5 OR 0', 'ERR 6 ERL 160'),
    ('PRINT -32769 OR 0', 'ERR 6 ERL 170'),
    ('PRINT NOT 40000', 'ERR 6 ERL 180'),
    ('PRINT 1 XOR 70000', 'ERR 6 ERL 190'),
    ('PRINT 1 EQV 40000', 'ERR 6 ERL 200'),
    ('PRINT 1 IMP 40000', 'ERR 6 ERL 210'),
    ('PRINT 1 AND 40000', 'ERR 6 ERL 220'),
    ('PRINT 32767.4 OR 0', ' 32767'),
    ('PRINT -32768.4 OR 0', '-32768'),
    ('PRINT 32767 AND -32768', ' 0'),
    ('PRINT NOT -32768', ' 32767'),
    ('PRINT NOT 32768', 'ERR 6 ERL 270'),
    ('PRINT (1=1) AND (2=2)', '-1'),
    ('PRINT (1=2) OR (3=3)', '-1'),
    ('PRINT NOT (1=2)', '-1'),
    ('PRINT 6 AND 3;6 OR 3;6 XOR 3;6 EQV 3;6 IMP 3', ' 2  7  5 -6 -5'),
    ('PRINT "A" AND 1', 'ERR 13 ERL 320'),
    ('PRINT 1 OR "A"', 'ERR 13 ERL 330'),
    ('PRINT NOT "A"', 'ERR 13 ERL 340'),
    ('IF 2.5 AND 1 THEN PRINT "yes" ELSE PRINT "no"', 'yes'),
    ('IF 0.4 THEN PRINT "yes" ELSE PRINT "no"', 'yes'),
    ('IF 1E10 THEN PRINT "yes" ELSE PRINT "no"', 'yes'),
    ('X=40000:PRINT X AND 1', 'ERR 6 ERL 380'),
    ('X#=2.5:PRINT X# AND 3', ' 3'),
]


def program():
    lines = ["%d %s" % (n, text) for n, text in enumerate(PRELUDE, 1)]
    for i, (statement, _) in enumerate(CASES):
        lines.append('%d PRINT "%d|";:%s:PRINT' % (100 + i * 10, i, statement))
    lines.append("%d SYSTEM" % (100 + len(CASES) * 10))
    lines.append("60000 " + HANDLER)
    return "\n".join(lines) + "\n"


def run_interpreter(tmp_path):
    (tmp_path / "cases.bas").write_text(program())
    result = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(tmp_path / "cases.bas"), "--ui", "cli"],
        input="RUN\nSYSTEM\n", cwd=tmp_path, capture_output=True, text=True, timeout=120)
    text = result.stdout.replace("\r", "").split("Goodbye")[0]   # SYSTEM ends our run with Goodbye
    got = {}
    for piece in re.split(r"(?:^|\n)(?=\d+\|)", text):
        found = re.match(r"(\d+)\|(.*)", piece, re.S)
        if found:
            got[int(found.group(1))] = found.group(2).strip("\n")
    return got, result


def test_every_case_matches_real_mbasic(tmp_path):
    got, result = run_interpreter(tmp_path)
    wrong = []
    for i, (statement, expected) in enumerate(CASES):
        if got.get(i, "<missing>").rstrip() != expected.rstrip():
            wrong.append("%s: real %r, ours %r" % (statement, expected, got.get(i, "<missing>")))
    assert not wrong, "\n".join(wrong) + "\n" + result.stderr

