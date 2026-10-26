"""A FOR loop inside a THEN or ELSE clause, and a wrong argument type to a built-in (issue 61).

The expected output of each program is what MBASIC 5.21 printed under cpmemu
(tests/HOW_TO_RUN_REAL_MBASIC.md). A FOR in a clause runs its body to the end of
the line, also after RESUME NEXT or a GOSUB. The interpreter used to stop with
FOR Without NEXT. A string given to a number argument (ABS("a")), or the other
way round (LEFT$(1,2)), is Type mismatch. The interpreter and the JavaScript
backend must print the same.
"""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
NODE = shutil.which("node")

CASES = {
    # the NEXT is in the same THEN or ELSE part
    "loop_in_clause": (
        '10 IF 1 THEN FOR I=1 TO 2:PRINT I:NEXT:PRINT "after"\n'
        '20 IF 0 THEN PRINT "x" ELSE FOR J=1 TO 2:PRINT J:NEXT:PRINT "e"\n'
        '30 PRINT "c"\n40 SYSTEM\n',
        " 1 \n 2 \nafter\n 1 \n 2 \ne\nc\n"),
    # error in the body, RESUME NEXT runs the rest of the loop
    "error_in_body": (
        '10 ON ERROR GOTO 100\n'
        '20 IF 1 THEN FOR I=1 TO 2:PRINT I:X=1/0:PRINT "b":NEXT:PRINT "after"\n'
        '30 PRINT "c"\n40 SYSTEM\n100 PRINT "E";ERR;ERL:RESUME NEXT\n',
        " 1 \nE 11  20 \nb\n 2 \nE 11  20 \nb\nafter\nc\n"),
    # nested loops, a loop not entered, a GOSUB in the body, a NEXT that closes two
    "nested_and_gosub": (
        '10 IF 1 THEN FOR I=1 TO 2:FOR J=1 TO 2:PRINT I;J:NEXT J,I:PRINT "a"\n'
        '20 IF 1 THEN FOR I=5 TO 1:PRINT "no":NEXT:PRINT "b"\n'
        '70 IF 1 THEN FOR I=1 TO 2:PRINT I:GOSUB 800:NEXT:PRINT "f"\n'
        '90 SYSTEM\n800 PRINT "sub":RETURN\n',
        " 1  1 \n 1  2 \n 2  1 \n 2  2 \na\nb\n 1 \nsub\n 2 \nsub\nf\n"),
    # the NEXT is on a later line: the NEXT runs the rest of the part again
    "next_on_later_line": (
        '10 IF 1 THEN FOR I=1 TO 3:PRINT I\n20 NEXT\n30 PRINT "done"\n'
        '40 IF 0 THEN PRINT "x" ELSE FOR J=1 TO 2:PRINT J\n'
        '50 NEXT:PRINT "n"\n'
        '60 IF 1 THEN FOR K=1 TO 2:PRINT K:GOSUB 800\n70 NEXT\n'
        '75 IF 1 THEN FOR L=1 TO 0:PRINT L\n76 NEXT\n'
        '80 PRINT "end"\n90 SYSTEM\n800 PRINT "s":RETURN\n',
        " 1 \n 2 \n 3 \ndone\n 1 \n 2 \nn\n 1 \ns\n 2 \ns\nend\n"),
    # a wrong argument type to a built-in
    "argument_types": (
        '10 ON ERROR GOTO 90\n20 PRINT LEN(1)\n30 PRINT ASC(5)\n40 PRINT VAL(3)\n'
        '50 PRINT CHR$("a")\n60 PRINT MID$(1,1)\n70 PRINT STR$("a")\n'
        '75 PRINT ABS("a")\n76 PRINT LEFT$(1,2)\n80 SYSTEM\n90 PRINT ERR;ERL:RESUME NEXT\n',
        " 13  20 \n 13  30 \n 13  40 \n 13  50 \n 13  60 \n 13  70 \n"
        " 13  75 \n 13  76 \n"),
}


def run_interpreter(tmp_path, source):
    (tmp_path / "e.bas").write_text(source)
    return subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(tmp_path / "e.bas"), "--ui", "cli"],
        input="RUN\nSYSTEM\n", cwd=tmp_path, capture_output=True, text=True, timeout=60)


@pytest.mark.parametrize("name", sorted(CASES))
def test_interpreter(tmp_path, name):
    source, expected = CASES[name]
    result = run_interpreter(tmp_path, source)
    assert expected in result.stdout.replace("\r", ""), result.stdout


@pytest.mark.skipif(NODE is None, reason="Node.js is needed to execute generated JavaScript")
@pytest.mark.parametrize("name", sorted(CASES))
def test_javascript(tmp_path, name):
    source, expected = CASES[name]
    (tmp_path / "e.bas").write_text(source)
    compiled = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), "--compile-js", str(tmp_path / "e.js"),
         str(tmp_path / "e.bas")],
        cwd=tmp_path, capture_output=True, text=True, timeout=60)
    assert compiled.returncode == 0, compiled.stdout + compiled.stderr
    result = subprocess.run([NODE, str(tmp_path / "e.js")], cwd=tmp_path,
                            capture_output=True, text=True, timeout=60)
    assert expected in result.stdout.replace("\r", ""), result.stdout + result.stderr
