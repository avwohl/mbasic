"""ERROR 24, 25, 68 to 72, 75 and 76 are "Unprintable error" (issue 42), measured on MBASIC 5.21.

The manual lists device and disk errors under these numbers, but the binary has no message for
them: ERROR n prints "Unprintable error in 10" for each, the same as ERROR 73, 74 and 255.
ERR keeps the number given to ERROR. The two-letter table and the message table lose the names.
"""
import subprocess
import sys
from pathlib import Path

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: unprintable error tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from src.error_codes import ERROR_CODES, get_error_message  # noqa: E402

NINE = [24, 25, 68, 69, 70, 71, 72, 75, 76]
OTHERS = [73, 74, 255]


def run_cli(tmp_path, source):
    (tmp_path / "e.bas").write_text(source)
    return subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(tmp_path / "e.bas"), "--ui", "cli"],
        input="RUN\nSYSTEM\n", cwd=tmp_path, capture_output=True, text=True, timeout=60)


@pytest.mark.parametrize("code", NINE + OTHERS)
def test_error_n_is_unprintable(tmp_path, code):
    result = run_cli(tmp_path, "10 ERROR %d\n" % code)
    assert "Unprintable error in 10" in result.stdout, result.stdout + result.stderr


def test_err_keeps_the_number(tmp_path):
    # real MBASIC: ERR is 24, 75 and 76; ERL is 20
    source = ("10 ON ERROR GOTO 50\n20 ERROR 24\n30 ERROR 75\n40 ERROR 76\n45 SYSTEM\n"
              '50 PRINT ERR;ERL:RESUME NEXT\n')
    result = run_cli(tmp_path, source)
    assert " 24  20 \n" in result.stdout, result.stdout
    assert " 75  30 \n" in result.stdout, result.stdout
    assert " 76  40 \n" in result.stdout, result.stdout


@pytest.mark.parametrize("code", NINE)
def test_table_has_no_entry(code):
    assert code not in ERROR_CODES
    assert get_error_message(code) == ("UE", "Unprintable error")
