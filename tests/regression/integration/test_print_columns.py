"""PRINT wraps at the line width and measures TAB and the comma zones from the real cursor column.

Each program in fixtures/print_columns/ has an .expected file: the output of real
MBASIC 5.21 under cpmemu (tests/HOW_TO_RUN_REAL_MBASIC.md). The interpreter and the
JavaScript that --compile-js writes must print the same bytes. Issues 20 and 23.
The rules are in docs/dev/PRINT_COLUMNS.md.
"""
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: print column tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

NODE = shutil.which("node")
FIXTURES = ROOT / "tests" / "regression" / "integration" / "fixtures" / "print_columns"
PROGRAMS = sorted(FIXTURES.glob("*.bas"))

needs_node = pytest.mark.skipif(NODE is None, reason="Node.js is needed to execute generated JavaScript")


def run_interpreter(directory, source, stdin="RUN\nSYSTEM\n"):
    run = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(source), "--ui", "cli"],
        cwd=directory, input=stdin, capture_output=True, text=True, timeout=120)
    lines = run.stdout.split("\n")
    start = lines.index("Ready") + 1       # skip the banner
    end = max(i for i, line in enumerate(lines) if line == "Goodbye")
    return "\n".join(lines[start:end]) + ("\n" if end > start else "")


def run_js(directory, source):
    output = directory / (source.stem + ".js")
    result = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(source), "--compile-js", str(output)],
        cwd=directory, capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    run = subprocess.run([NODE, str(output)], cwd=directory, capture_output=True, text=True, timeout=120)
    assert run.returncode == 0, run.stderr
    return run.stdout


@pytest.mark.parametrize("program", PROGRAMS, ids=lambda p: p.stem)
def test_interpreter_matches_real_mbasic(tmp_path, program):
    source = tmp_path / program.name
    shutil.copy(program, source)
    assert run_interpreter(tmp_path, source) == program.with_suffix(".expected").read_text()


@needs_node
@pytest.mark.parametrize("program", PROGRAMS, ids=lambda p: p.stem)
def test_js_matches_real_mbasic(tmp_path, program):
    source = tmp_path / program.name
    shutil.copy(program, source)
    assert run_js(tmp_path, source) == program.with_suffix(".expected").read_text()


def test_column_is_zero_after_input(tmp_path):
    """The Enter that ends an INPUT answer puts the cursor at column 0 (real MBASIC: POS is 1)."""
    source = tmp_path / "input_col.bas"
    source.write_text('10 PRINT "abc";\n20 INPUT "x";A$\n30 PRINT TAB(5);POS(0)\n')
    out = run_interpreter(tmp_path, source, stdin="RUN\nzz\nSYSTEM\n")
    assert out == "abcx? " + "    " + " 5 \n"


@pytest.mark.parametrize("statement", ["WIDTH 256", "WIDTH -1"])
def test_width_out_of_range_is_an_error(tmp_path, statement):
    source = tmp_path / "width.bas"
    source.write_text('10 ON ERROR GOTO 100\n20 %s\n30 END\n100 PRINT "E";ERR\n110 RESUME 30\n' % statement)
    assert run_interpreter(tmp_path, source) == "E 5 \n"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
