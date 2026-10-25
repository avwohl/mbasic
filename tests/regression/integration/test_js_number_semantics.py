"""Overflow, domain errors, VAL, &H/&O constants and HEX$/OCT$ in compiled JavaScript.

The programs in fixtures/number_semantics/ each have a .real file: what MBASIC 5.21
printed for the program under cpmemu. The JavaScript that --compile-js writes must
print the same when Node.js runs it. (tests/regression/interpreter/test_number_semantics.py
holds the interpreter to the same files.)

The programs print only through bare PRINT statements and handle errors with ON ERROR,
so the one thing that differs is left out: the JavaScript backend evaluates a whole PRINT
list before it prints, so a "Overflow" message comes before the "A=" in PRINT "A=";10^40.
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
FIXTURES = ROOT / "tests" / "regression" / "integration" / "fixtures" / "number_semantics"

pytestmark = pytest.mark.skipif(NODE is None, reason="Node.js is needed to execute generated JavaScript")


def compile_and_run(tmp_path, basic_source, name="prog"):
    source = tmp_path / (name + ".bas")
    source.write_text(basic_source)
    output = tmp_path / (name + ".js")
    result = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(source), "--compile-js", str(output)],
        cwd=tmp_path, capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    run = subprocess.run([NODE, str(output)], cwd=tmp_path, capture_output=True, text=True, timeout=60)
    return run.stdout


@pytest.mark.parametrize("program", sorted(FIXTURES.glob("*.bas")), ids=lambda p: p.stem)
def test_js_output_matches_real_mbasic(tmp_path, program):
    expected = (FIXTURES / (program.stem + ".real")).read_text().rstrip("\n")
    got = compile_and_run(tmp_path, program.read_text(), program.stem)
    assert got.rstrip("\n").split("\n") == expected.split("\n")


@pytest.mark.parametrize("statement, message", [
    ("PRINT SQR(-1)", "Illegal function call in 20"),
    ("PRINT LOG(0)", "Illegal function call in 20"),
    ("PRINT LOG(-1)", "Illegal function call in 20"),
    ("PRINT (-8)^(1/3)", "Illegal function call in 20"),
    ("PRINT 5\\X", "Division by zero in 20"),
    ("PRINT 5 MOD X", "Division by zero in 20"),
    ("PRINT CINT(40000)", "Overflow in 20"),
    ("PRINT HEX$(65536)", "Overflow in 20"),
    ("PRINT VAL(\"&HFFFFF\")", "Overflow in 20"),
])
def test_js_fatal_errors_stop_the_program(tmp_path, statement, message):
    """Without ON ERROR these stop the program; nothing prints NaN or Infinity."""
    got = compile_and_run(tmp_path, f'10 X=0\n20 {statement}\n30 PRINT "after"\n')
    assert got.strip() == message


def test_js_never_prints_infinity_or_nan(tmp_path):
    got = compile_and_run(tmp_path, '10 X=0\n20 PRINT 1E39\n30 PRINT 1/X\n40 PRINT 10^40\n50 PRINT 1D300*1D300\n')
    assert "Infinity" not in got and "NaN" not in got
    assert got.count("Overflow") == 2 and got.count("Division by zero") == 1


def test_js_on_error_resume_next_continues_after_the_failing_line(tmp_path):
    got = compile_and_run(tmp_path, '10 ON ERROR GOTO 100\n20 PRINT SQR(-1)\n30 PRINT "after"\n40 GOTO 200\n'
                          '100 PRINT "ERR";ERR;"in";ERL:RESUME NEXT\n200 PRINT "end"\n')
    assert got.split("\n")[:3] == ["ERR 5 in 20 ", "after", "end"]


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
