"""The CLI prints Ok as MBASIC 5.21 does (issue 49).

Measured on the binary (tests/HOW_TO_RUN_REAL_MBASIC.md): Ok once at start-up,
then Ok after every direct statement, after every error message and after a
program stops (Break in 20 for STOP). No Ok follows a numbered line. CLI output
used to be "Ready" at start-up and nothing after that.

Binary, input RETURN / PRINT 5 / 10 PRINT 1 / 20 STOP / RUN:
    Ok
    RETURN without GOSUB
    Ok
     5
    Ok
     1
    Break in 20
    Ok
"""
import subprocess
import sys
from pathlib import Path

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: CLI Ok prompt tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

ROOT = Path(__file__).resolve().parents[3]

EXPECTED = ["Ok", "RETURN without GOSUB", "Ok", " 5 ", "Ok", " 1 ", "Break in 20", "Ok", "Goodbye"]


def run_cli(tmp_path, stdin, args=()):
    run = subprocess.run([sys.executable, str(ROOT / "mbasic"), "--ui", "cli", *args],
                         cwd=tmp_path, input=stdin, capture_output=True, text=True, timeout=60)
    lines = run.stdout.split("\n")
    # The first two lines are the banner and the key tip.
    return [line.rstrip("\r") for line in lines[2:] if line != ""]


def test_ok_after_each_direct_command_error_and_stop(tmp_path):
    out = run_cli(tmp_path, "RETURN\nPRINT 5\n10 PRINT 1\n20 STOP\nRUN\nSYSTEM\n")
    assert out == EXPECTED


def test_ok_replaces_ready_at_start_up(tmp_path):
    out = run_cli(tmp_path, "SYSTEM\n")
    assert out == ["Ok", "Goodbye"]


def test_ok_after_new_load_and_merge(tmp_path):
    (tmp_path / "p.bas").write_text("10 PRINT 1\n")
    out = run_cli(tmp_path, 'LOAD "p"\nMERGE "p"\nNEW\nSYSTEM\n')
    assert "Ready" not in out
    assert out.count("Ok") == 4          # start-up, LOAD, MERGE, NEW


def test_ok_starts_a_new_line_after_unfinished_output(tmp_path):
    # PRINT "A"; leaves the cursor in column 1; Ok goes on the next line.
    out = run_cli(tmp_path, 'PRINT "A";\nSYSTEM\n')
    assert out == ["Ok", "A", "Ok", "Goodbye"]


def test_blank_line_prints_no_ok(tmp_path):
    out = run_cli(tmp_path, "\nSYSTEM\n")
    assert out == ["Ok", "Goodbye"]


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
