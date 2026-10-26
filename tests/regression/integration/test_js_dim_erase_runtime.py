"""DIM and ERASE errors in the JavaScript backend are found when the program runs.

The expected output of each program is what MBASIC 5.21 printed under cpmemu
(tests/HOW_TO_RUN_REAL_MBASIC.md). Measured on the binary:
  ERASE of an array that does not exist: Illegal function call (5); the arrays
    named before it in the same ERASE are erased, the ones after it are not.
  DIM of an array that exists, also an array made by a use: Duplicate
    Definition (10), and the array keeps its old size.
  DIM A(-1), also with a variable bound: Illegal function call (5).
  DIM B("a"): Type mismatch (13). DIM A(40000): Overflow (6).
  OPTION BASE 1 with DIM A(0): Subscript out of range (9).
  A DIM that fails leaves the arrays of its later declarations unmade.
  A DIM that a GOTO runs again is Duplicate Definition; a DIM that a GOTO skips
    leaves the array to the first use, and a later DIM is Duplicate Definition.
  A bound can be any expression, so DIM A(N*2) in a loop with ERASE works.
  CLEAR deletes every array, so a DIM after CLEAR is not a duplicate.
The interpreter and the JavaScript backend must print the same.
"""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
NODE = shutil.which("node")

CASES = {
    # ERASE of an array never made, a second DIM, a use and then DIM, -1, a variable -2, a string bound
    "erase_dim_errors": (
        '10 ON ERROR GOTO 100\n20 PRINT "a":ERASE Q\n30 PRINT "b"\n40 DIM A(3):PRINT "c"\n'
        '50 DIM A(3):PRINT "d"\n60 A(1)=1:B(1)=2:DIM B(5):PRINT "e"\n70 DIM C(-1):PRINT "f"\n'
        '80 N=-2:DIM D(N):PRINT "g"\n90 DIM E("a"):PRINT "h":SYSTEM\n100 PRINT ERR;ERL:RESUME NEXT\n',
        "a\n 5  20 \nb\nc\n 10  50 \nd\n 10  60 \ne\n 5  70 \nf\n 5  80 \ng\n 13  90 \nh\n"),
    # a DIM that fails: the arrays before it are made, the ones after it are not
    "partial_dim_and_erase": (
        '10 ON ERROR GOTO 100\n20 DIM A(2),B(-1),C(2)\n30 PRINT "p1"\n40 A(1)=7:PRINT A(1)\n'
        '50 C(1)=5:PRINT C(1)\n60 DIM D(2),A(4),E(2)\n70 E(2)=3:PRINT E(2);A(4)\n'
        '80 DIM F(2),G("x"),H(2)\n90 H(1)=1:PRINT H(1)\n95 ERASE D,Q,F\n'
        '96 D(1)=1:F(1)=2:PRINT D(1);F(1);"er"\n97 ERASE A,A\n98 A(3)=1:PRINT A(3);"z":SYSTEM\n'
        '100 PRINT ERR;ERL:RESUME NEXT\n',
        " 5  20 \np1\n 7 \n 5 \n 10  60 \n 3  9  70 \n 13  80 \n 1 \n 5  95 \n 1  2 er\n"
        " 5  97 \n 1 z\n"),
    # OPTION BASE 1, bounds that are expressions, string arrays, rounding, Overflow, a GOSUB with DIM
    "runtime_bounds_option_base": (
        '5 OPTION BASE 1\n10 ON ERROR GOTO 100\n20 FOR N=2 TO 4\n30 DIM A(N*2),S$(N,2)\n'
        '40 A(N*2)=N:S$(N,2)="s"+STR$(N)\n50 PRINT A(N*2);S$(N,2);\n55 ON ERROR GOTO 100\n'
        '60 PRINT A(N*2+1)\n70 ERASE A,S$\n80 NEXT N\n90 DIM Z(0):PRINT "z0"\n'
        '91 DIM Y(2.5):Y(3)=1:PRINT Y(3)\n92 DIM W(40000):PRINT "w"\n93 DIM V(2,"a"):PRINT "v"\n'
        '94 GOSUB 200:GOSUB 200\n95 PRINT Q(1,1),FRE(0)>0\n96 DIM Q(2,2)\n97 PRINT "ZZ":SYSTEM\n'
        '100 PRINT ERR;ERL:RESUME NEXT\n200 DIM G(3):RETURN\n',
        " 2 s 2 9  60 \n 3 s 3 9  60 \n 4 s 4 9  60 \n 9  90 \nz0\n 1 \n 6  92 \nw\n"
        " 13  93 \nv\n 10  200 \n 0            -1 \n 10  96 \nZZ\n"),
    # a DIM that a GOTO runs again, and a DIM that a GOTO skips
    "dim_run_twice_or_skipped": (
        '10 DIM A(3):A(2)=5\n20 ON ERROR GOTO 100\n30 I=I+1:IF I<3 THEN GOTO 10\n'
        '40 PRINT A(2);"ok"\n50 GOTO 70\n60 DIM B(4)\n70 B(1)=1:PRINT B(1)\n'
        '80 DIM B(4):PRINT "bb"\n90 SYSTEM\n100 PRINT ERR;ERL:RESUME NEXT\n',
        " 10  10 \n 10  10 \n 5 ok\n 1 \n 10  80 \nbb\n"),
    # CLEAR deletes every array: the old one is gone, and a DIM after CLEAR is not a duplicate
    "dim_after_clear": (
        '10 DIM A(3):A(1)=9\n20 CLEAR\n30 ON ERROR GOTO 100\n40 PRINT A(1);A(10)\n'
        '50 DIM A(2,2):A(1,1)=4:PRINT A(1,1)\n60 CLEAR:DIM A(5):PRINT A(5)\n70 SYSTEM\n'
        '100 PRINT ERR;ERL:RESUME NEXT\n',
        " 0  0 \n 10  50 \n 9  50 \n 9  50 \n 0 \n"),
    # arrays named B and N: the JS parameters of the run-time DIM must not hide the array (measured on the binary)
    "arrays_named_b_and_n": (
        '10 N=3:DIM B(N)\n20 B(1)=4:PRINT B(1)\n30 DIM B$(N):B$(2)="x":PRINT B$(2)\n'
        '40 ERASE B:DIM B(2):PRINT B(1)\n50 M=3:DIM N(M):N(2)=7:PRINT N(2)\n'
        '60 ERASE N:DIM N(M):N(1)=2:PRINT N(1);N(2)\n70 IF 1 THEN DIM Z(2)\n'
        '80 Z(1)=1:PRINT Z(1):SYSTEM\n',
        " 4 \nx\n 0 \n 7 \n 2  0 \n 1 \n"),
}


@pytest.mark.parametrize("name", sorted(CASES))
def test_interpreter(tmp_path, name):
    source, expected = CASES[name]
    (tmp_path / "e.bas").write_text(source)
    result = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(tmp_path / "e.bas"), "--ui", "cli"],
        input="RUN\nSYSTEM\n", cwd=tmp_path, capture_output=True, text=True, timeout=60)
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


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
