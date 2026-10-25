"""PRINT, STR$, WRITE and PRINT USING in compiled JavaScript print numbers the MBASIC way.

The programs in fixtures/js_print_format/ are compiled with --compile-js, run
under Node.js, and their output is compared byte for byte with what the Python
interpreter prints. EXPECTED_ISSUE_9 comes from real MBASIC 5.21 under cpmemu.
Programs leave out the few things where the interpreter and real MBASIC still
differ (see docs/dev/JS_PRINT_FORMAT.md).
"""
import json
import random
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
sys.path.insert(0, str(ROOT))

from src.codegen_js_backend import JS_NUMBER_RUNTIME  # noqa: E402
from src.number_format import format_for_print, to_single  # noqa: E402

NODE = shutil.which("node")
PROGRAMS = ROOT / "tests" / "regression" / "integration" / "fixtures" / "js_print_format"

pytestmark = pytest.mark.skipif(NODE is None, reason="Node.js is needed to execute generated JavaScript")

ISSUE_9_SOURCE = '''10 PRINT 42
20 PRINT -3
30 PRINT 1;2;-3
40 X!=8.7:PRINT X!
50 PRINT 1/3
60 D#=1/3#:PRINT D#
70 PRINT 1E+20
80 PRINT "[";5;"]"
90 PRINT "[";STR$(-3);"][";STR$(5);"][";STR$(1/3);"]"
100 SYSTEM
'''

# Printed by real MBASIC 5.21 (cpmemu) for ISSUE_9_SOURCE.
EXPECTED_ISSUE_9 = "\n".join([
    " 42 ",
    "-3 ",
    " 1  2 -3 ",
    " 8.7 ",
    " .333333 ",
    " .3333333333333333 ",
    " 1E+20 ",
    "[ 5 ]",
    "[-3][ 5][ .333333]",
]) + "\n"


def run_js(directory, basic_path):
    output = directory / (basic_path.stem + ".js")
    result = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(basic_path), "--compile-js", str(output)],
        cwd=directory, capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    run = subprocess.run([NODE, str(output)], cwd=directory, capture_output=True, text=True, timeout=60)
    assert run.returncode == 0, run.stderr
    return run.stdout


def run_interpreter(directory, basic_path):
    run = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(basic_path), "--ui", "cli"],
        cwd=directory, input="RUN\nSYSTEM\n", capture_output=True, text=True, timeout=60)
    lines = run.stdout.split("\n")
    start = lines.index("Ok") + 1       # skip the banner
    end = max(i for i, line in enumerate(lines) if line == "Goodbye")
    if lines[end - 1] == "Ok":             # the Ok that follows RUN
        end -= 1
    return "\n".join(lines[start:end]) + ("\n" if end > start else "")


def test_issue_9_example_matches_real_mbasic(tmp_path):
    source = tmp_path / "issue9.bas"
    source.write_text(ISSUE_9_SOURCE)
    assert run_js(tmp_path, source) == EXPECTED_ISSUE_9


@pytest.mark.parametrize("program", sorted(PROGRAMS.glob("*.bas")), ids=lambda p: p.stem)
def test_js_output_matches_interpreter(tmp_path, program):
    source = tmp_path / program.name
    shutil.copy(program, source)
    expected = run_interpreter(tmp_path, source)
    assert expected, "the interpreter printed nothing"
    assert run_js(tmp_path, source) == expected


def test_number_formatter_matches_python_for_random_values(tmp_path):
    """_fmt_print in the JS runtime agrees with number_format.format_for_print."""
    rng = random.Random(9)
    cases = []
    for _ in range(3000):
        kind = rng.random()
        if kind < 0.35:
            value = rng.uniform(-1, 1) * 10 ** rng.randint(-12, 12)
        elif kind < 0.55:
            value = float(rng.randint(-10 ** 15, 10 ** 15))
        elif kind < 0.75:
            value = round(rng.uniform(-1000, 1000), rng.randint(0, 8))
        else:
            value = rng.choice([9.99999, 99999.95, 999999.5, 0.999999, 0.9999995,
                                1e-7, 1e-8, 123456.5, 1234567.5, 0.1, 0.5, 0.0, 1e16])
        digits = rng.choice([6, 6, 16, 0])
        if digits == 6:
            value = to_single(value)
        elif digits == 0:
            value = float(int(value) % 40000)
        cases.append((value, digits))

    script = tmp_path / "format.js"
    script.write_text(JS_NUMBER_RUNTIME + "\nconst cases = " + json.dumps(cases) +
                      ";\nfor (const [v, d] of cases) console.log(JSON.stringify(_fmt_print(v, d)));\n")
    run = subprocess.run([NODE, str(script)], capture_output=True, text=True, timeout=60)
    assert run.returncode == 0, run.stderr
    got = [json.loads(line) for line in run.stdout.splitlines()]
    want = [format_for_print(int(v) if d == 0 else v, None if d == 0 else d) for v, d in cases]
    mismatches = [(c, g, w) for c, g, w in zip(cases, got, want) if g != w]
    assert len(got) == len(want)
    assert mismatches == []


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
