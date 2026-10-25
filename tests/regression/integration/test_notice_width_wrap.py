"""The Overflow and Division by zero messages that do not stop the program follow WIDTH (issue 40).

MBASIC 5.21 sends these messages through the same width logic as PRINT, one character at a time,
so a word next to the right edge is split. A full line wraps lazily, before the next character.
Each expected output was measured on MBASIC 5.21 (cpmemu). The interpreter and the JavaScript
backend (under node) must give the same text.
"""
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: notice width tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

ROOT = Path(__file__).resolve().parents[3]
NODE = shutil.which("node")

CASES = [
    # The program of issue 40
    ("issue", '10 WIDTH 40\n20 PRINT "123456789012345678901234567890123";\n30 A=1D39\n40 PRINT 1/0\n50 PRINT "X"\n',
     "123456789012345678901234567890123Overflo\nw\nDivision by zero\n 1.70141E+38 \nX\n"),
    ("split at 40 then column", '10 WIDTH 40\n20 PRINT "12345678901234567890123456789012345678";\n30 A=1D39\n'
     '40 PRINT "Y";\n50 PRINT 1/0\n60 PRINT "Y";\n70 A=1D39\n80 PRINT "X"\n',
     "12345678901234567890123456789012345678Ov\nerflow\nYDivision by zero\n 1.70141E+38 \nYOverflow\nX\n"),
    ("full line wraps lazily", '10 WIDTH 40\n20 PRINT "1234567890123456789012345678901234567890";\n30 A=1D39\n'
     '40 PRINT POS(0)\n50 PRINT "1234567890123456789012345678";\n60 B=1/0\n70 PRINT POS(0);"X"\n',
     "1234567890123456789012345678901234567890\nOverflow\n 1 \n1234567890123456789012345678Division by \nzero\n 1 X\n"),
    ("inside a PRINT list", '10 WIDTH 40\n20 PRINT "12345678901234567890123456789012345";\n30 PRINT "ab";1/0;"cd"\n40 PRINT "X"\n',
     "12345678901234567890123456789012345abDiv\nision by zero\n 1.70141E+38 cd\nX\n"),
]
IDS = [c[0] for c in CASES]


@pytest.mark.parametrize("name,source,expected", CASES, ids=IDS)
def test_interpreter(tmp_path, name, source, expected):
    (tmp_path / "p.bas").write_text(source)
    result = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(tmp_path / "p.bas"), "--ui", "cli"],
        input="RUN\nSYSTEM\n", cwd=tmp_path, capture_output=True, text=True, timeout=60)
    assert expected in result.stdout, result.stdout + result.stderr


@pytest.mark.skipif(NODE is None, reason="Node.js is needed to execute generated JavaScript")
@pytest.mark.parametrize("name,source,expected", CASES, ids=IDS)
def test_javascript(tmp_path, name, source, expected):
    (tmp_path / "p.bas").write_text(source)
    result = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(tmp_path / "p.bas"), "--compile-js", str(tmp_path / "p.js")],
        cwd=ROOT, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
    run = subprocess.run([NODE, str(tmp_path / "p.js")], capture_output=True, text=True, timeout=10)
    assert run.stdout == expected
