"""PRINT USING of a number with 16 or more digits: the interpreter and compiled JavaScript.

Expected text measured on real MBASIC 5.21 (cpmemu): a fixed field gives up from 1E16 up and
prints '%' and the PRINT form of the number, sign and $ and trailing sign dropped. The
Overflow notice of 10^40 comes first, then '% 1.70141E+38'.
"""
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

ROOT = Path(__file__).resolve().parents[3]
NODE = shutil.which("node")

PROGRAM = '''10 PRINT "a";
20 PRINT USING "##.#";10^40
30 PRINT USING "##.#";1E15;1E16;-1E16;-1D16
40 PRINT USING "##.#-";1E16
50 PRINT USING "#.#^^^^";10^40
60 PRINT "z"
'''
EXPECTED = ("aOverflow\n% 1.70141E+38\n%1000000000000000.0% 1E+16% 1E+16% 1D+16\n"
            "% 1E+16\nOverflow\n0.2E+39\nz\n")


def test_interpreter(tmp_path):
    basic = tmp_path / "prog.bas"
    basic.write_text(PROGRAM)
    result = subprocess.run([sys.executable, str(ROOT / "mbasic"), "--ui", "cli", str(basic)],
                            cwd=ROOT, input="RUN\nSYSTEM\n", capture_output=True, text=True, timeout=60)
    assert EXPECTED in result.stdout, result.stdout


@pytest.mark.skipif(NODE is None, reason="Node.js is needed")
def test_javascript(tmp_path):
    basic = tmp_path / "prog.bas"
    basic.write_text(PROGRAM)
    out = tmp_path / "prog.js"
    result = subprocess.run([sys.executable, str(ROOT / "mbasic"), str(basic), "--compile-js", str(out)],
                            cwd=ROOT, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    run = subprocess.run([NODE, str(out)], capture_output=True, text=True, cwd=tmp_path, timeout=30)
    assert run.stdout == EXPECTED
