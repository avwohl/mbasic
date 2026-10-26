"""An array that ERASE deletes can be made again with another number of subscripts (issue 60).

ERASE deletes the array. A DIM, or the next use, makes it again, and the number
of subscripts is the one of the DIM or of the use. The expected output of each
program is what MBASIC 5.21 printed under cpmemu (tests/HOW_TO_RUN_REAL_MBASIC.md).
A use with another number of subscripts than the array has is Subscript out of
range. The interpreter and the JavaScript backend must print the same.
"""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
NODE = shutil.which("node")

CASES = {
    # DIM again with more subscripts, then ERASE and a use with two subscripts
    "dim_rank_change": (
        "10 DIM A(3)\n20 A(1)=1\n30 ERASE A\n40 DIM A(3,3)\n60 A(2,2)=5:PRINT A(2,2)\n"
        "70 ERASE A\n80 A(5,5)=2:PRINT A(5,5)\n90 SYSTEM\n",
        " 5 \n 2 \n"),
    # a string array, three subscripts, and the old rank after ERASE is wrong
    "string_array": (
        '10 DIM A$(3)\n20 A$(1)="x"\n30 ERASE A$\n40 DIM A$(2,2,2)\n'
        '50 A$(2,2,2)="deep":PRINT A$(2,2,2)\n60 ERASE A$\n70 PRINT A$(1):PRINT "after"\n'
        '80 PRINT A$(1,1)\n90 SYSTEM\n',
        "deep\n\nafter\nSubscript out of range in 80\n"),
    # a use with the wrong number of subscripts is error 9, and RESUME NEXT goes on
    "wrong_count": (
        '10 ON ERROR GOTO 100\n20 DIM A(3)\n30 ERASE A\n40 DIM A(3,3)\n50 PRINT A(1)\n'
        '60 PRINT "n"\n70 A(4,4)=1\n80 PRINT "m"\n90 SYSTEM\n100 PRINT ERR;ERL:RESUME NEXT\n',
        " 9  50 \nn\n 9  70 \nm\n"),
    # the first use makes the array, ERASE deletes it, and the next use sets the rank again
    "implicit_arrays": (
        "10 A(1,2)=7\n20 PRINT A(1,2)\n30 ERASE A\n40 A(3)=1:PRINT A(3)\n50 ERASE A\n"
        "60 DIM A(2,2,2):A(2,2,2)=4:PRINT A(2,2,2)\n70 SYSTEM\n",
        " 7 \n 1 \n 4 \n"),
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
