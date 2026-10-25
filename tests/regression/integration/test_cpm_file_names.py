"""File names that CP/M refuses (issue 33), measured on MBASIC 5.21 under cpmemu.

MBASIC turns the name into a CP/M control block. Names it cannot parse are
Bad file name (64): empty, a drive letter that is not a letter, nothing after
the drive colon, nothing before the dot, or a second dot after the type has
begun. A statement that makes the file (OPEN "O", OPEN "R", SAVE) with a name
that has a character the file system refuses (control characters and
% ( ) * , / : ; < = > [ \\ ] ^ |) is Too many files (67); a statement that
reads gives File not found (53). Names too long are cut, not refused.
A name with a slash or backslash is taken as a host path and passes.
"""
import subprocess
import sys
from pathlib import Path

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: CP/M file name tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from src.cpm_names import cpm_name_error  # noqa: E402

# Every row is a name and the result of OPEN "O",1,name on the binary:
# None = opened, else the error number.
OPEN_OUTPUT = [
    ("A:B:C*?.X Y", 67), ("ABCDEFGH.DAT", None), ("ABCDEFGH.DATA", None), ("A.B", None),
    ("A:X.DAT", None), ("AA:X.DAT", 67), ("X*.DAT", 67), ("X?.DAT", None), ("X Y.DAT", None),
    ("X.D Y", None), ("X.D*", 67), ("X.", None), ("X..Y", None), ("X,Y.DAT", 67), ("X;Y", 67),
    ("X=Y", 67), ("X<Y", 67), ("X>Y", 67), ("X[Y", 67), ("X]Y", 67), ("X_Y", None),
    ("X-Y", None), ("X+Y", None), ("x.dat", None), ("X/Y", 67), ("X\\Y", 67), ("X|Y", 67),
    ("X:Y", None), ("X.D:T", 67), ("Z:ABC", None), ("P:X.DAT", None), ("  X.DAT", None),
    ("X.DAT ", None), ("LPT1", None), ("NUL", None), ("LST:", 67), ("CON:", 67),
    ("X.DAT:", None), ("X%Y", 67), ("X(Y", 67), ("X)Y", 67), ("X^Y", 67), ("X\tY", 67),
    ("ABCDEFGHI.DAT", 64), ("1:X.DAT", 64), ("A.B.C", 64), (".DAT", 64), ("", 64),
    ("A:", 64), ("A:.B", 64),
    # eleven characters with no dot are fine; the rest is cut off, a later dot too
    ("ABCDEFGHIJK", None), ("ABCDEFGHIJKLMNOP", None), ("ABCDEFGHIJK.X", None),
    ("X!Y", None), ("X#Y", None), ("X$Y", None), ("X&Y", None), ("X'Y", None),
    ("X@Y", None), ("X~Y", None), ("X`Y", None), ("X{Y", None), ("X}Y", None),
    # a byte of 128 and up is the same byte with bit 7 clear
    ("X\xa5Y", 67), ("X\xaaY", 67), ("X\x85Y", 67),
]


@pytest.mark.parametrize("name, code", OPEN_OUTPUT)
def test_name_rules(name, code):
    assert cpm_name_error(name, creates=True) == code


@pytest.mark.parametrize("name, creates, code", [
    ("X*Y.DAT", False, 53), ("X*Y.DAT", True, 67), ("ABCDEFGHI.DAT", False, 64),
    ("ABCDEFGHI.DAT", True, 64), ("NOSUCH.DAT", False, None),
])
def test_reading_and_making(name, creates, code):
    # binary: OPEN "I", KILL, LOAD, MERGE, CHAIN, RUN and FILES give 53 for X*Y.DAT;
    # OPEN "R" and SAVE give 67; all give 64 for ABCDEFGHI.DAT
    assert cpm_name_error(name, creates) == code


def run_cli(directory, source):
    (directory / "n.bas").write_text(source)
    return subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(directory / "n.bas"), "--ui", "cli"],
        input="RUN\nSYSTEM\n", cwd=directory, capture_output=True, text=True, timeout=60).stdout


def test_issue_recipe_and_no_file_is_made(tmp_path):
    out = run_cli(tmp_path, '10 OPEN "O",1,"A:B:C*?.X Y"\n20 PRINT "ok"\n30 SYSTEM\n')
    assert "Too many files in 10" in out and "ok" not in out.replace("Ready", ""), out
    assert [p.name for p in tmp_path.iterdir()] == ["n.bas"]


def test_names_cut_to_fit_are_not_errors(tmp_path):
    # binary: 11 characters with no dot, and longer, open fine
    out = run_cli(tmp_path, '10 OPEN "O",1,"ABCDEFGHIJK"\n20 CLOSE\n30 PRINT "ok"\n40 SYSTEM\n')
    assert "ok" in out and "Bad file name" not in out, out


@pytest.mark.parametrize("statement, error", [
    ('OPEN "O",1,"ABCDEFGHI.DAT"', 64),
    ('OPEN "R",1,"X*Y.DAT",16', 67),
    ('OPEN "I",1,"X*Y.DAT"', 53),
    ('KILL "ABCDEFGHI.DAT"', 64),
    ('KILL "X*Y.DAT"', 53),
    ('NAME "ABCDEFGHI.DAT" AS "NEWNAME.X"', 64),
    ('SAVE "X*Y"', 67),
    ('LOAD "ABCDEFGHI.BAS"', 64),
    ('MERGE "ABCDEFGHI.BAS"', 64),
])
def test_statements(tmp_path, statement, error):
    source = f'5 ON ERROR GOTO 100\n10 {statement}\n20 PRINT "ok"\n30 SYSTEM\n100 PRINT "err";ERR;ERL:SYSTEM\n'
    out = run_cli(tmp_path, source)
    assert f"err {error}  10" in out, out
    assert sorted(p.name for p in tmp_path.iterdir()) == ["n.bas"]


def test_host_paths_pass(tmp_path):
    (tmp_path / "sub").mkdir()
    path = tmp_path / "sub" / "a_long_host_name.txt"
    out = run_cli(tmp_path, f'10 OPEN "O",1,"{path}"\n20 PRINT #1,"hi"\n30 CLOSE\n40 PRINT "ok"\n50 SYSTEM\n')
    assert "ok" in out and path.read_text() == "hi\n", out
