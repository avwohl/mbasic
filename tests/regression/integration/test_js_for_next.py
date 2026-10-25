"""FOR/NEXT in generated JavaScript: bare NEXT with INTEGER variables, and loops on one line.

The expected output of each program was checked against real MBASIC 5.21 (cpmemu) and the
interpreter.
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
    basic = tmp_path / "prog.bas"
    basic.write_text(source)
    output = tmp_path / "prog.js"
    result = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(basic), "--compile-js", str(output)],
        cwd=ROOT, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    # A loop that never ends makes subprocess.run raise TimeoutExpired: the test fails.
    run = subprocess.run([NODE, str(output)], capture_output=True, text=True, timeout=10)
    assert run.returncode == 0, run.stderr
    return run.stdout


def numbers(*items):
    return "".join(f" {item} \n" for item in items)


# Bare NEXT must find a loop whose variable is INTEGER (issue 14)
BARE_NEXT = [
    ("DEFINT", "10 DEFINT I\n20 FOR I=1 TO 3\n30 PRINT I\n40 NEXT\n50 SYSTEM\n", numbers(1, 2, 3)),
    ("percent", "10 FOR I%=1 TO 3\n30 PRINT I%\n40 NEXT\n50 SYSTEM\n", numbers(1, 2, 3)),
    ("double", "10 FOR D#=1 TO 3\n30 PRINT D#\n40 NEXT\n50 SYSTEM\n", numbers(1, 2, 3)),
    ("plain", "10 FOR I=1 TO 3\n30 PRINT I\n40 NEXT\n50 SYSTEM\n", numbers(1, 2, 3)),
    ("nested", "10 DEFINT I-J\n20 FOR I=1 TO 2\n25 FOR J=1 TO 2\n30 PRINT I;J\n40 NEXT\n45 NEXT\n50 SYSTEM\n",
     " 1  1 \n 1  2 \n 2  1 \n 2  2 \n"),
]


@pytest.mark.parametrize("name,source,expected", BARE_NEXT, ids=[c[0] for c in BARE_NEXT])
def test_bare_next_finds_loop(tmp_path, name, source, expected):
    assert run_js(tmp_path, source) == expected


if __name__ == "__main__":
    if NODE is None:
        print("Node.js unavailable: JavaScript execution tests skipped")
        sys.exit(2)
    sys.exit(pytest.main([__file__, "-q", "-p", "no:cacheprovider"]))
