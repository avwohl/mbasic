"""LOAD and MERGE of a file that MBASIC 5.21 stops reading (issues 34, 35, 36).

Measured on com/mbasic.com under cpmemu (CR LF line ends):

- A file line longer than 255 bytes (not counting the line end): `Line buffer
  overflow in N`, N the leading number of the line, 0 if it has none. 255 bytes
  load; 256 stop.
- A file line with no line number: `Direct statement in file`.
- A bare line number of a line that does not exist: `Undefined line number`.

In all three cases the read stops at the bad line. The lines read before it
stay in memory (LOAD of a file whose first line is bad leaves an empty
program; MERGE keeps the old program and the lines merged before the bad
line). Nothing after the bad line is read. The message is bare: no file name,
no "Loaded from". A bare number typed at the Ok prompt for a missing line
prints `Undefined line number`.
"""
import subprocess
import sys
from pathlib import Path

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: LOAD/MERGE file error tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

ROOT = Path(__file__).resolve().parents[3]
X300 = "X" * 300

# name: (file lines, real message, lines left by LOAD, lines left by MERGE
# into a program holding 5 and 15)
CASES = {
    "long_first": (["10 REM " + X300, '20 PRINT "hi"'],
                   "Line buffer overflow in 10", [], [5, 15]),
    "long_second": (['10 PRINT "A"', "20 REM " + X300, '30 PRINT "C"'],
                    "Line buffer overflow in 20", [10], [5, 10, 15]),
    "long_unnumbered": (['10 PRINT "A"', "REM " + X300, '30 PRINT "C"'],
                        "Line buffer overflow in 0", [10], [5, 10, 15]),
    "direct": (['10 PRINT "A"', 'PRINT "X"', '20 PRINT "B"'],
               "Direct statement in file", [10], [5, 10, 15]),
    "undefined": (['10 PRINT "A"', "20 GOTO 30", "30", '40 PRINT "B"'],
                  "Undefined line number", [10, 20], [5, 10, 15, 20]),
    "undefined_after_delete": (['10 PRINT "A"', "20 PRINT 1", "20", "30",
                                '40 PRINT "B"'],
                               "Undefined line number", [10], [5, 10, 15]),
}


def write(directory, name, lines):
    path = directory / (name + ".bas")
    path.write_bytes("".join(line + "\r\n" for line in lines).encode())
    return path


def run_cli(directory, commands):
    return subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), "--ui", "cli"],
        input=commands, cwd=directory, capture_output=True, text=True, timeout=60)


def listed(output):
    """Line numbers in a LIST output."""
    return [int(row.split()[0]) for row in output.splitlines()
            if row[:1].isdigit()]


@pytest.mark.parametrize("name", sorted(CASES))
def test_load_stops_at_the_bad_line(tmp_path, name):
    lines, message, kept, _ = CASES[name]
    write(tmp_path, name, lines)
    result = run_cli(tmp_path, f'LOAD "{name}.bas"\nLIST\nSYSTEM\n')
    assert message + "\n" in result.stdout, result.stdout + result.stderr
    assert "Loaded from" not in result.stdout
    assert listed(result.stdout) == kept


@pytest.mark.parametrize("name", sorted(CASES))
def test_merge_stops_at_the_bad_line(tmp_path, name):
    lines, message, _, kept = CASES[name]
    write(tmp_path, name, lines)
    result = run_cli(
        tmp_path, f'5 PRINT "Z"\n15 PRINT "Q"\nMERGE "{name}.bas"\nLIST\nSYSTEM\n')
    assert message + "\n" in result.stdout, result.stdout + result.stderr
    assert "Merged from" not in result.stdout
    assert listed(result.stdout) == kept


@pytest.mark.parametrize("length,overflows", [(255, False), (256, True)])
def test_buffer_limit_is_255_bytes(tmp_path, length, overflows):
    text = "20 REM " + "X" * (length - 7)
    assert len(text) == length
    write(tmp_path, "edge", ['10 PRINT "A"', text, '30 PRINT "C"'])
    result = run_cli(tmp_path, 'LOAD "edge.bas"\nLIST 10-30\nSYSTEM\n')
    assert ("Line buffer overflow in 20" in result.stdout) == overflows
    assert listed(result.stdout) == ([10] if overflows else [10, 20, 30])


def test_bare_number_of_missing_line_at_the_prompt(tmp_path):
    result = run_cli(tmp_path, '10 PRINT 1\n30\n10\n10\nSYSTEM\n')
    assert result.stdout.count("Undefined line number\n") == 2


def test_merge_error_in_a_running_program_can_be_trapped(tmp_path):
    # Measured: a program that MERGEs a file whose line 10 is over 255 bytes,
    # under ON ERROR GOTO, prints "ERR 23 ERL 10" (ERL is the file line; ours
    # reports the program line, so only ERR is compared).
    write(tmp_path, "lg", ["10 REM " + X300])
    write(tmp_path, "main", [
        '10 ON ERROR GOTO 100',
        '20 MERGE "lg.bas"',
        '30 PRINT "not reached"',
        '40 SYSTEM',
        '100 PRINT "ERR";ERR',
        '110 SYSTEM'])
    result = run_cli(tmp_path, 'LOAD "main.bas"\nRUN\nSYSTEM\n')
    assert "ERR 23" in result.stdout, result.stdout + result.stderr
    assert "not reached" not in result.stdout
