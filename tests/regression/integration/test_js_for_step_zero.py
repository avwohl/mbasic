"""FOR ... STEP 0 in generated JavaScript (issue 55, JavaScript part).

MBASIC 5.21 ends a loop when the sign of (variable - limit) equals the sign of the step. With
STEP 0 the loop ends only when the variable equals the limit, at FOR and at NEXT. Each expected
output was measured on MBASIC 5.21 (cpmemu). A counter stops the loops that never end.
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

BODY = ('30 N=N+1\n40 PRINT I;N\n50 IF N>=4 THEN PRINT "STOP":SYSTEM\n60 NEXT I\n70 PRINT "DONE"\n80 SYSTEM\n')
FOUR = "".join(f" {{i}}  {n} \n" for n in range(1, 5)) + "STOP\n"

CASES = [
    ("up", "1", "3", FOUR.replace("{i}", "1")),
    ("down", "3", "1", FOUR.replace("{i}", "3")),
    ("equal", "2", "2", "DONE\n"),
]


@pytest.mark.parametrize("name,first,last,expected", CASES, ids=[c[0] for c in CASES])
def test_step_zero(tmp_path, name, first, last, expected):
    basic = tmp_path / "prog.bas"
    basic.write_text(f"10 N=0\n20 FOR I={first} TO {last} STEP 0\n{BODY}")
    output = tmp_path / "prog.js"
    result = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(basic), "--compile-js", str(output)],
        cwd=ROOT, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    run = subprocess.run([NODE, str(output)], capture_output=True, text=True, timeout=10)
    assert run.stdout == expected
