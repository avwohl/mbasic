"""Fatal errors in generated JavaScript read '<message> in <line>' with no '?' (issue 41).

Each expected output was measured on MBASIC 5.21 (cpmemu) and is the same in the interpreter.
The line is the BASIC line that ran, also when the error comes after a FOR, GOSUB or NEXT in the
middle of the line (those statements have their own case labels in the generated code).
"""
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: JavaScript execution tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

ROOT = Path(__file__).resolve().parents[3]
NODE = shutil.which("node")

pytestmark = pytest.mark.skipif(NODE is None, reason="Node.js is needed to execute generated JavaScript")

CASES = [
    ("division", '10 PRINT "A"\n20 A=7\\0\n30 PRINT "B"\n', "A\nDivision by zero in 20\n"),
    ("out of data", "10 READ A\n", "Out of DATA in 10\n"),
    ("error 5", "10 ERROR 5\n", "Illegal function call in 10\n"),
    ("error 200", "10 ERROR 200\n", "Unprintable error in 10\n"),
    ("overflow", "10 PRINT CINT(40000)\n", "Overflow in 10\n"),
    ("after a mid-line FOR", '10 FOR I=1 TO 2:PRINT "x";:A=7\\0:NEXT\n', "x\nDivision by zero in 10\n"),
    ("after GOSUB and NEXT",
     '10 GOSUB 20:PRINT "a"\n20 FOR I=1 TO 2:PRINT "x";:NEXT:B=CINT(1E9)\n', "xx\nOverflow in 20\n"),
    ("WHILE without WEND", '10 PRINT "A"\n20 WHILE 0\n30 PRINT "B"\n40 SYSTEM\n', "A\nWHILE without WEND in 20\n"),
    # ON ERROR still traps the error; ERL is the line, not a label
    ("ERL after a mid-line FOR",
     '10 ON ERROR GOTO 100\n20 FOR I=1 TO 2:A=7\\0:NEXT\n30 SYSTEM\n100 PRINT ERR;ERL\n110 SYSTEM\n', " 11  20 \n"),
]


@pytest.mark.parametrize("name,source,expected", CASES, ids=[c[0] for c in CASES])
def test_fatal_error_has_line(tmp_path, name, source, expected):
    basic = tmp_path / "prog.bas"
    basic.write_text(source)
    output = tmp_path / "prog.js"
    result = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(basic), "--compile-js", str(output)],
        cwd=ROOT, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    run = subprocess.run([NODE, str(output)], capture_output=True, text=True, timeout=10)
    assert run.stdout == expected
