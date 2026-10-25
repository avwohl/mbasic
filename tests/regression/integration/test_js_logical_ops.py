"""AND, OR, XOR, EQV, IMP and NOT in generated JavaScript are 16-bit integer bitwise operators.

The expected values are the output of real MBASIC 5.21 (cpmemu). Real MBASIC rounds an operand
to the nearest integer (halves away from zero) and stops with Overflow outside -32768..32767.
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


def run_js(tmp_path, source):
    """Return (stdout, exit code) of the compiled program."""
    basic = tmp_path / "prog.bas"
    basic.write_text(source)
    output = tmp_path / "prog.js"
    result = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(basic), "--compile-js", str(output)],
        cwd=ROOT, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    run = subprocess.run([NODE, str(output)], capture_output=True, text=True, timeout=10)
    return run.stdout, run.returncode


VALUES = [
    ("12 AND 10", " 8 "),
    ("12 OR 3", " 15 "),
    ("12 AND 3", " 0 "),
    ("-1 AND 7", " 7 "),
    ("-32768 AND 1", " 0 "),
    ("32767 OR -32768", "-1 "),
    ("5 XOR 3", " 6 "),
    ("3 EQV 5", "-7 "),
    ("3 IMP 5", "-3 "),
    ("-1 EQV 0", " 0 "),
    ("0 IMP 0", "-1 "),
    ("NOT 0", "-1 "),
    ("NOT 5", "-6 "),
    ("NOT 2.7", "-4 "),
    ("NOT -2.7", " 2 "),
    ("2.7 AND 3", " 3 "),
    ("2.5 AND 3", " 3 "),
    ("2.5 OR 0", " 3 "),
    ("3.5 OR 0", " 4 "),
    ("-2.5 OR 0", "-3 "),
    ("(1=1) AND 5", " 5 "),
    ("(1=2) OR (3=3)", "-1 "),
    ("NOT (1=2)", "-1 "),
    ("(5>3) XOR (2>1)", " 0 "),
    ("6 AND 3 OR 8", " 10 "),
    ("NOT 1 AND 3", " 2 "),
    ("1 OR 2 AND 4", " 1 "),
]


@pytest.mark.parametrize("expr,expected", VALUES, ids=[v[0] for v in VALUES])
def test_logical_value(tmp_path, expr, expected):
    out, code = run_js(tmp_path, f"10 PRINT {expr}\n20 SYSTEM\n")
    assert code == 0
    assert out == expected + "\n"


OVERFLOWS = ["40000 AND 1", "32768 AND 1", "65535 AND 255", "-32769 AND 1", "40000 OR 1", "NOT 40000",
             "40000 XOR 1", "1 IMP 40000", "1E10 AND 1"]


@pytest.mark.parametrize("expr", OVERFLOWS)
def test_logical_overflow(tmp_path, expr):
    out, code = run_js(tmp_path, f"10 PRINT {expr}\n20 SYSTEM\n")
    assert code == 1
    assert out.strip() == "?Overflow"


def test_xor_eqv_imp_compile_and_run(tmp_path):
    out, code = run_js(tmp_path, "10 PRINT 5 XOR 3, 3 EQV 5, 3 IMP 5\n20 SYSTEM\n")
    assert code == 0
    assert out.split() == ["6", "-7", "-3"]


def test_if_condition_is_bitwise(tmp_path):
    # JavaScript && gave 3 (true) for 12 AND 3; MBASIC gives 0
    out, code = run_js(tmp_path, '''10 IF 12 AND 3 THEN PRINT "T1" ELSE PRINT "F1"
20 A=6:B=3:PRINT A AND B;A OR B
30 X%=300:PRINT X% AND 255
40 IF A=6 AND B=3 THEN PRINT "both"
50 IF A=1 OR B=3 THEN PRINT "either"
60 IF NOT (A=1) THEN PRINT "not"
70 SYSTEM
''')
    assert code == 0
    assert out == "F1\n 2  7 \n 44 \nboth\neither\nnot\n"


if __name__ == "__main__":
    if NODE is None:
        print("Node.js unavailable: JavaScript execution tests skipped")
        sys.exit(2)
    sys.exit(pytest.main([__file__, "-q", "-p", "no:cacheprovider"]))
