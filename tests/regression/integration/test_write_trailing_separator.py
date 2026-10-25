"""WRITE with a trailing ',' or ';' (issue 27), measured on MBASIC 5.21.

The line loads, lists and renumbers as typed. When it runs, the items and a
',' go out with no end of line, then Missing operand (error 22) stops the
statement. WRITE #n, with no items is an empty line; WRITE #n alone is a
Syntax error when it runs.
"""
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: WRITE trailing separator tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

ROOT = Path(__file__).resolve().parents[3]
NODE = shutil.which("node")

PROGRAM = '''10 ON ERROR GOTO 100
20 WRITE 1;
30 PRINT "X"
40 WRITE "a",2,
50 PRINT "Y"
60 WRITE
70 PRINT "Z"
80 OPEN "O",1,"wt.txt"
81 WRITE #1,1,"b";
82 CLOSE
83 OPEN "O",1,"wt2.txt"
84 WRITE #1,
85 CLOSE
86 OPEN "O",1,"wt3.txt"
87 WRITE #1
88 WRITE #1,3
89 CLOSE
90 PRINT "END"
95 SYSTEM
100 PRINT "ERR";ERR;"ERL";ERL
110 RESUME NEXT
'''

EXPECTED = ('1,ERR 22 ERL 20 \nX\n"a",2,ERR 22 ERL 40 \nY\n\nZ\n'
            'ERR 22 ERL 81 \nERR 2 ERL 87 \nEND\n')
FILES = {"wt.txt": '1,"b",', "wt2.txt": "\n", "wt3.txt": "3\n"}


def check_files(directory):
    for name, text in FILES.items():
        assert (directory / name).read_bytes().decode() == text, name


def run_cli(directory, source, commands):
    (directory / "w.bas").write_text(source)
    return subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(directory / "w.bas"), "--ui", "cli"],
        input=commands, cwd=directory, capture_output=True, text=True, timeout=60)


def test_interpreter_runs_the_line(tmp_path):
    result = run_cli(tmp_path, PROGRAM, "RUN\nSYSTEM\n")
    assert EXPECTED in result.stdout, result.stdout + result.stderr
    assert "Syntax error in" not in result.stdout
    check_files(tmp_path)


def test_load_list_renum_keep_the_text(tmp_path):
    result = run_cli(
        tmp_path,
        '10 WRITE 1;\n20 WRITE "a",2,:PRINT "no"\n30 WRITE #1,2,\n40 WRITE #1\n50 GOTO 10\n',
        "LIST\nRENUM 100\nLIST\nSYSTEM\n")
    out = result.stdout
    assert "Syntax error" not in out, out
    for text in ("10 WRITE 1;", "30 WRITE #1,2,", "40 WRITE #1\n", "100 WRITE 1;",
                 "120 WRITE #1,2,", "130 WRITE #1\n", "140 GOTO 100"):
        assert text in out, (text, out)
    assert out.count('WRITE "a",2,:PRINT "no"') == 2, out


def test_uncaught_error_is_missing_operand(tmp_path):
    result = run_cli(tmp_path, '10 PRINT "A"\n20 WRITE 1;\n30 PRINT "C"\n', "RUN\nSYSTEM\n")
    out = result.stdout.replace("\r", "")
    assert "A\n1," in out, out
    assert "Missing operand in 20" in out, out
    assert "\nC\n" not in out


@pytest.mark.skipif(NODE is None, reason="Node.js is needed to execute generated JavaScript")
def test_javascript_compiles_and_raises_at_run_time(tmp_path):
    (tmp_path / "w.bas").write_text(PROGRAM)
    compiled = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(tmp_path / "w.bas"),
         "--compile-js", str(tmp_path / "w.js")],
        cwd=tmp_path, capture_output=True, text=True, timeout=60)
    assert compiled.returncode == 0, compiled.stdout + compiled.stderr
    result = subprocess.run([NODE, str(tmp_path / "w.js")], cwd=tmp_path,
                            capture_output=True, text=True, timeout=60)
    assert result.stdout == EXPECTED, result.stdout + result.stderr
    check_files(tmp_path)


BAD_PROGRAM = '''10 ON ERROR GOTO 100
20 WRITE ,1
30 PRINT "X"
40 WRITE 1,,2
50 PRINT "Y"
60 WRITE ;
70 PRINT "Z"
80 WRITE 1;;2
90 PRINT "END"
95 SYSTEM
100 PRINT "ERR";ERR;"ERL";ERL
110 RESUME NEXT
'''

BAD_EXPECTED = ('ERR 2 ERL 20 \nX\n1,ERR 2 ERL 40 \nY\nERR 2 ERL 60 \nZ\n'
                '1,ERR 2 ERL 80 \nEND\n')


def test_leading_and_doubled_separators_fail_at_run_time(tmp_path):
    result = run_cli(tmp_path, BAD_PROGRAM, "RUN\nSYSTEM\n")
    assert BAD_EXPECTED in result.stdout.replace("\r", ""), result.stdout + result.stderr
    assert "Syntax error in" not in result.stdout


def test_bad_separators_list_as_typed(tmp_path):
    result = run_cli(tmp_path, '10 WRITE ,1\n20 WRITE 1,,2:PRINT "x"\n30 WRITE ;\n',
                     "LIST\nSYSTEM\n")
    for text in ("10 WRITE ,1", '20 WRITE 1,,2:PRINT "x"', "30 WRITE ;"):
        assert text in result.stdout, (text, result.stdout)
    assert "Syntax error" not in result.stdout


@pytest.mark.skipif(NODE is None, reason="Node.js is needed to execute generated JavaScript")
def test_javascript_bad_separators(tmp_path):
    (tmp_path / "w.bas").write_text(BAD_PROGRAM)
    compiled = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(tmp_path / "w.bas"),
         "--compile-js", str(tmp_path / "w.js")],
        cwd=tmp_path, capture_output=True, text=True, timeout=60)
    assert compiled.returncode == 0, compiled.stdout + compiled.stderr
    result = subprocess.run([NODE, str(tmp_path / "w.js")], cwd=tmp_path,
                            capture_output=True, text=True, timeout=60)
    assert result.stdout == BAD_EXPECTED, result.stdout + result.stderr


CPMEMU = shutil.which("cpmemu")
UC80 = shutil.which("uc80")


@pytest.mark.skipif(CPMEMU is None or UC80 is None, reason="uc80 and cpmemu are needed for the C backend")
@pytest.mark.parametrize("line, shown", [
    ('WRITE 5;"a";', '5,"a",?Error 22 in line 20'),
    ('WRITE 1,,2', '1,?Error 2 in line 20'),
    ('WRITE ,1', '?Error 2 in line 20'),
])
def test_c_backend_raises_the_error(tmp_path, line, shown):
    (tmp_path / "w.bas").write_text(f'10 PRINT "A"\n20 {line}\n30 PRINT "no"\n')
    compiled = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(tmp_path / "w.bas"),
         "--compile-c", str(tmp_path / "w")],
        cwd=tmp_path, capture_output=True, text=True, timeout=300)
    assert (tmp_path / "w.com").exists(), compiled.stdout + compiled.stderr
    ran = subprocess.run([CPMEMU, "w.com"], cwd=tmp_path, capture_output=True,
                         text=True, timeout=60)
    out = (ran.stdout + ran.stderr).replace("\r", "")
    assert "A\n" + shown in out, out
    assert "no" not in out.split("Program exit")[0].replace("Loaded", ""), out


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
