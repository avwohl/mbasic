"""FIELD overflow and the OPEN record length (issue 32), measured on MBASIC 5.21.

The widths of one FIELD statement must fit in the record length of the OPEN
(128 when none is given). The record length is 0 to 128: 129 and up, and a
negative number, are Illegal function call, and 65536 is Overflow. GET and PUT
use the record length as the record size, so a FIELD that covers part of the
record leaves the rest as it was. Each FIELD statement starts again at the first
byte of the record.
"""
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: FIELD record length tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

ROOT = Path(__file__).resolve().parents[3]
CLOSE = '40 CLOSE:KILL "ZZ.DAT":SYSTEM\n'


def run_cli(directory, source):
    (directory / "f.bas").write_text(source)
    return subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(directory / "f.bas"), "--ui", "cli"],
        input="RUN\nSYSTEM\n", cwd=directory, capture_output=True, text=True, timeout=60).stdout


@pytest.mark.parametrize("open_args, fields, expected", [
    ('"ZZ.DAT",16', "16 AS A$", "ok"),
    ('"ZZ.DAT",16', "17 AS A$", "FIELD overflow in 20"),
    ('"ZZ.DAT",16', "8 AS A$,8 AS B$,1 AS C$", "FIELD overflow in 20"),
    ('"ZZ.DAT"', "128 AS A$", "ok"),
    ('"ZZ.DAT"', "129 AS A$", "FIELD overflow in 20"),
    ('"ZZ.DAT"', "200 AS A$", "FIELD overflow in 20"),
    ('"ZZ.DAT",0', "1 AS A$", "FIELD overflow in 20"),
    ('"ZZ.DAT",0', "128 AS A$", "FIELD overflow in 20"),
    ('"ZZ.DAT",16', "0 AS A$", "ok"),
    ('"ZZ.DAT",16', "-1 AS A$", "Illegal function call in 20"),
])
def test_field_against_record_length(tmp_path, open_args, fields, expected):
    out = run_cli(tmp_path, f'10 OPEN "R",1,{open_args}\n20 FIELD 1,{fields}\n30 PRINT "ok"\n{CLOSE}')
    assert expected in out, out
    if expected != "ok":
        assert "ok\n" not in out.replace("Ready", "").replace("Goodbye", ""), out


@pytest.mark.parametrize("length, expected", [
    ("127", "ok"), ("128", "ok"), ("0", "ok"),
    ("129", "Illegal function call in 10"), ("256", "Illegal function call in 10"),
    ("1000", "Illegal function call in 10"), ("-1", "Illegal function call in 10"),
    ("32767", "Illegal function call in 10"), ("65536", "Overflow in 10"),
])
def test_record_length_range(tmp_path, length, expected):
    out = run_cli(tmp_path, f'10 OPEN "R",1,"ZZ.DAT",{length}\n20 PRINT "ok"\n{CLOSE}')
    assert expected in out, out


def test_second_field_starts_at_the_first_byte(tmp_path):
    # binary: two FIELD statements of 10 and 10+6 on a 16 byte record are fine
    source = ('10 OPEN "R",1,"ZZ.DAT",16\n20 FIELD 1,10 AS A$\n25 FIELD 1,10 AS B$,6 AS C$\n'
              f'30 PRINT "ok"\n{CLOSE}')
    assert "ok" in run_cli(tmp_path, source)


def test_a_failed_field_binds_nothing(tmp_path):
    # the binary binds A$ before it stops at B$; here nothing changes (see docs)
    source = ('10 OPEN "R",1,"ZZ.DAT",16\n15 A$="keep":B$="keepb"\n20 ON ERROR GOTO 100\n'
              '21 FIELD 1,8 AS A$,9 AS B$\n30 PRINT "ok"\n' + CLOSE +
              '100 PRINT ERR;A$;B$:RESUME 40\n')
    out = run_cli(tmp_path, source)
    assert " 50 keepkeepb" in out, out


def test_a_field_covering_part_of_the_record_keeps_the_rest(tmp_path):
    # binary: C$ overlays the first 4 bytes of the 16 byte record; B$ still reads BBBBBBBB
    source = '''10 OPEN "R",1,"ZZ.DAT",16
20 FIELD 1,8 AS A$,8 AS B$
30 LSET A$="AAAAAAAA":LSET B$="BBBBBBBB":PUT 1,1
40 FIELD 1,4 AS C$
50 LSET C$="CCCC":PUT 1,2
60 LSET C$="DDDD":PUT 1,3
70 GET 1,1:PRINT C$;"/";A$;"/";B$
80 GET 1,2:PRINT C$;"/";LEN(A$);"/";B$
90 GET 1,3:PRINT C$
95 CLOSE:KILL "ZZ.DAT"
100 SYSTEM
'''
    out = run_cli(tmp_path, source)
    assert "AAAA/AAAAAAAA/BBBBBBBB\nCCCC/ 8 /BBBBBBBB\nDDDD\n" in out, out


def test_sequential_file_has_no_fields(tmp_path):
    # binary: FIELD on an OPEN "O" file is Bad file mode
    out = run_cli(tmp_path, f'10 OPEN "O",1,"ZZ.DAT"\n20 FIELD 1,5 AS A$\n30 PRINT "ok"\n{CLOSE}')
    assert "Bad file mode in 20" in out, out


NODE = shutil.which("node")


def run_js(directory, source):
    (directory / "f.bas").write_text(source)
    compiled = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(directory / "f.bas"),
         "--compile-js", str(directory / "f.js")],
        cwd=directory, capture_output=True, text=True, timeout=60)
    assert compiled.returncode == 0, compiled.stdout + compiled.stderr
    result = subprocess.run([NODE, str(directory / "f.js")], cwd=directory,
                            capture_output=True, text=True, timeout=60)
    return result.stdout + result.stderr


@pytest.mark.skipif(NODE is None, reason="Node.js is needed to execute generated JavaScript")
@pytest.mark.parametrize("open_args, fields, expected", [
    ('"ZZ.DAT",16', "16 AS A$", "ok"),
    ('"ZZ.DAT",16', "17 AS A$", "FIELD overflow"),
    ('"ZZ.DAT"', "128 AS A$", "ok"),
    ('"ZZ.DAT"', "129 AS A$", "FIELD overflow"),
    ('"ZZ.DAT",0', "1 AS A$", "FIELD overflow"),
])
def test_javascript_field_against_record_length(tmp_path, open_args, fields, expected):
    out = run_js(tmp_path, f'10 OPEN "R",1,{open_args}\n20 FIELD 1,{fields}\n30 PRINT "ok"\n{CLOSE}')
    assert expected in out, out


@pytest.mark.skipif(NODE is None, reason="Node.js is needed to execute generated JavaScript")
@pytest.mark.parametrize("length", ["129", "256", "-1"])
def test_javascript_record_length_range(tmp_path, length):
    out = run_js(tmp_path, f'10 OPEN "R",1,"ZZ.DAT",{length}\n20 PRINT "ok"\n{CLOSE}')
    assert "Illegal function call" in out and "ok" not in out, out
