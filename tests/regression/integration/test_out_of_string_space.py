"""Out of string space (issue 31), and CLEAR ,n / FRE, measured on MBASIC 5.21.

The binary keeps string data in the free memory that FRE reports (39168 bytes
at start-up under cpmemu). When the strings do not fit, even after garbage
collection, it stops with "Out of string space". The interpreter counts the
bytes of the live string variables and array elements against the same figure.
That is an estimate: the binary also spends memory on the program text and on
the variables and arrays, so it runs out a little sooner (190 strings of 200
bytes fit in the issue's DIM A$(300) recipe there; 195 fit here). The tests use
amounts far from that edge.

CLEAR ,n moves the top of memory and CLEAR ,,n the stack space; FRE follows.
The FRE figures below are the binary's, and the estimate is within 20 of them.
"""
import subprocess
import sys
from pathlib import Path

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: string space tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

ROOT = Path(__file__).resolve().parents[3]


def run_cli(directory, source):
    (directory / "s.bas").write_text(source)
    return subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(directory / "s.bas"), "--ui", "cli"],
        input="RUN\nSYSTEM\n", cwd=directory, capture_output=True, text=True, timeout=60).stdout


def fill(count, dim="DIM A$(300)"):
    return (f"10 {dim}\n20 FOR I=0 TO {count}\n30 A$(I)=STRING$(200,65)\n40 NEXT\n"
            '50 PRINT "done"\n60 SYSTEM\n')


def test_issue_recipe(tmp_path):
    # binary: 301 strings of 203 bytes -> "Out of string space in 30"
    source = ("10 DIM A$(300)\n20 FOR I=0 TO 300\n30 A$(I)=STRING$(200,65)+STR$(I)\n"
              '40 NEXT\n50 PRINT "done"\n60 SYSTEM\n')
    out = run_cli(tmp_path, source)
    assert "Out of string space in 30" in out and "done" not in out, out


def test_error_is_trappable_as_error_14(tmp_path):
    # binary: ERR 14, ERL 30, and FRE is nearly nothing
    source = ("5 ON ERROR GOTO 100\n10 DIM A$(300)\n20 FOR I=0 TO 300\n30 A$(I)=STRING$(200,65)\n"
              '40 NEXT\n50 SYSTEM\n100 PRINT "ERR";ERR;"ERL";ERL;FRE(0)<300:SYSTEM\n')
    out = run_cli(tmp_path, source)
    assert "ERR 14 ERL 30 -1" in out, out


def test_a_string_that_fits_is_not_an_error(tmp_path):
    # binary: 100 strings of 200 bytes fit
    out = run_cli(tmp_path, fill(100, "DIM A$(100)"))
    assert "done" in out and "string space" not in out, out


def test_replaced_strings_are_given_back(tmp_path):
    # binary: 400 passes of A$=STRING$(200,65) print done 401
    source = '10 FOR I=1 TO 400\n20 A$=STRING$(200,65)\n30 NEXT\n40 PRINT "done";I\n50 SYSTEM\n'
    assert "done 401" in run_cli(tmp_path, source)


def test_erase_gives_the_strings_back(tmp_path):
    # binary: 151 strings of 200 bytes, ERASE, and another 151 -> done
    source = ("10 DIM A$(150)\n20 FOR I=0 TO 150\n30 A$(I)=STRING$(200,65)\n40 NEXT\n50 ERASE A$\n"
              '60 DIM B$(150)\n70 FOR I=0 TO 150\n80 B$(I)=STRING$(200,66)\n90 NEXT\n'
              '100 PRINT "done"\n110 SYSTEM\n')
    out = run_cli(tmp_path, source)
    assert "done" in out and "string space" not in out, out


def test_clear_memory_top_shrinks_the_string_space(tmp_path):
    # binary: after CLEAR ,30000 the 31 strings of 200 bytes do not fit -> error in 40
    source = ("10 CLEAR ,30000\n20 DIM A$(30)\n30 FOR I=0 TO 30\n40 A$(I)=STRING$(200,65)\n"
              '50 NEXT\n60 PRINT "done"\n70 SYSTEM\n')
    out = run_cli(tmp_path, source)
    assert "Out of string space in 40" in out and "done" not in out, out


@pytest.mark.parametrize("clear, binary_free", [
    ("CLEAR", 39182),
    ("CLEAR ,40000", 14409),
    ("CLEAR ,&HC000", 23563),
    ("CLEAR ,60000", 34409),
    ("CLEAR ,65535", 39944),
    ("CLEAR ,-1", 39947),
    ("CLEAR ,,1000", 38688),
    ("CLEAR ,,100", 39589),
    ("CLEAR ,&HC000,1000", 23071),
    ("CLEAR 500", 39178),
    ("CLEAR 500,32768", 7174),
    ("CLEAR ,40000:CLEAR", 14407),
])
def test_clear_moves_fre(tmp_path, clear, binary_free):
    out = run_cli(tmp_path, f"10 {clear}\n20 PRINT FRE(0)\n30 SYSTEM\n")
    free = int(out.split("Ready")[1].split()[0])
    assert abs(free - binary_free) <= 20, (free, binary_free, out)


@pytest.mark.parametrize("clear, message", [
    ("CLEAR ,,0", "Illegal function call in 20"),
    ("CLEAR ,0", "Illegal function call in 20"),
    ("CLEAR ,1000", "Out of memory in 20"),
    ("CLEAR ,25000", "Out of memory in 20"),
    ("CLEAR ,,60000", "Out of memory in 20"),
    ("CLEAR ,,-1", "Out of memory in 20"),
    ("CLEAR ,,50", "Out of memory in 20"),
    ("CLEAR ,65536", "Overflow in 20"),
])
def test_clear_errors(tmp_path, clear, message):
    # all measured on the binary
    out = run_cli(tmp_path, f"10 PRINT 1\n20 {clear}\n30 PRINT 2\n40 SYSTEM\n")
    assert message in out and " 2 " not in out, out


def test_clear_arguments_survive_list_and_renum(tmp_path):
    source = "10 CLEAR ,40000,1000\n20 CLEAR ,,1000\n30 CLEAR 500,32768\n40 CLEAR\n"
    (tmp_path / "l.bas").write_text(source)
    result = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(tmp_path / "l.bas"), "--ui", "cli"],
        input="LIST\nRENUM 100\nLIST\nSYSTEM\n", cwd=tmp_path, capture_output=True, text=True, timeout=60).stdout
    for text in ("10 CLEAR ,40000,1000", "20 CLEAR ,,1000", "30 CLEAR 500,32768", "40 CLEAR\n",
                 "100 CLEAR ,40000,1000", "110 CLEAR ,,1000"):
        assert text in result, (text, result)


def test_program_strings_take_no_string_space(tmp_path):
    # binary: 401 elements of 150 characters assigned from a literal fit (okA 37751);
    # the same made by STRING$ run out at element 251 or 252
    literal = "X" * 150
    source = (f'5 ON ERROR GOTO 900\n10 DIM A$(400)\n20 FOR I=0 TO 400:A$(I)="{literal}":NEXT\n'
              '30 PRINT "okA"\n40 SYSTEM\n900 PRINT "E";ERR:SYSTEM\n')
    out = run_cli(tmp_path, source)
    assert "okA" in out and "E 14" not in out, out
    source = source.replace(f'"{literal}"', "STRING$(150,65)")
    assert "E 14" in run_cli(tmp_path, source)


@pytest.mark.parametrize("clear, expected", [
    # binary: the number before the first comma is read as an integer
    ("CLEAR 32767", "ok"), ("CLEAR 32768", "Overflow in 10"), ("CLEAR 70000", "Overflow in 10"),
    ("CLEAR -1", "Illegal function call in 10"), ("CLEAR -32768", "Illegal function call in 10"),
    ("CLEAR -32769", "Overflow in 10"), ("CLEAR -5,60000", "Illegal function call in 10"),
])
def test_clear_first_number(tmp_path, clear, expected):
    out = run_cli(tmp_path, f'10 {clear}\n20 PRINT "ok"\n30 SYSTEM\n')
    assert expected in out, out
