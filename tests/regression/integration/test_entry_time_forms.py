"""Entry-time behaviour measured on MBASIC 5.21 under cpmemu (issues 39 and 53).

1. RENUM keeps a stored bad line: it still fails with Syntax error when it
   runs.  Measured: 10 PRINT "A" / 20 NAME$="B":PRINT "Z" / 30 PRINT "C" /
   RENUM 100,10,10 / RUN prints A, then "Syntax error in 110".
2. DATA text is not crunched.  DATA &O9, &O8,1 and A,&O19 are stored and
   listed.  Measured: DATA &H12345,&O999,1E39,"A" then READ A$,B$,C$,D$
   gives "&H12345&O9991E39A".  Outside DATA, &O9 refuses the line.
3. A line number stops at 6553: the digits that follow are text.  Measured:
   65529 is a line number; 65530 is line 6553 with "0"; 70000 is line 7000
   with "0"; 99999 is 9999 with "9"; 123456 is 12345 with "6".
4. ON ERROR GOSUB is a Syntax error.  Measured: the stored line lists as
   typed and fails with "Syntax error in 20" when it runs; typed at the
   prompt it prints "Syntax error".
"""
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: entry time tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

ROOT = Path(__file__).resolve().parents[3]
NODE = shutil.which("node")


def run_cli(directory, commands, program=None):
    args = [sys.executable, str(ROOT / "mbasic"), "--ui", "cli"]
    if program is not None:
        (directory / "p.bas").write_text(program)
        args.insert(2, str(directory / "p.bas"))
    return subprocess.run(args, input=commands, cwd=directory,
                          capture_output=True, text=True, timeout=60).stdout


def test_renum_keeps_the_bad_line(tmp_path):
    out = run_cli(tmp_path, '10 PRINT "A"\n20 NAME$="B":PRINT "Z"\n30 PRINT "C"\n'
                            'RENUM 100,10,10\nLIST\nRUN\nSYSTEM\n')
    assert '110 NAME$="B":PRINT "Z"' in out, out
    assert "A\nSyntax error in 110\n" in out, out
    assert "\nC\n" not in out, out


def test_data_keeps_bad_octal_text(tmp_path):
    out = run_cli(tmp_path, '10 DATA &O9\n20 DATA &O8,1\n30 DATA A,&O19\n'
                            '40 DATA &H12345,&O999,1E39,"A"\nLIST\n'
                            '50 RESTORE 40:READ A$,B$,C$,D$:PRINT A$;B$;C$;D$\nRUN 50\nSYSTEM\n')
    for text in ("10 DATA &O9", "20 DATA &O8,1", "30 DATA A,&O19",
                 '40 DATA &H12345,&O999,1E39,"A"', "&H12345&O9991E39A"):
        assert text in out, (text, out)


RAW_ITEMS = ["1 2", "1.5.5", "12abc", "1;2", "&H12G", "&O1E5", "(1)", "X+1",
             "PRINT", "a b", "&OA", "&O1.5", "&HG", "AbC"]


def test_data_items_are_raw_text(tmp_path):
    # Measured on the binary: READ A$ gives each of these as typed (case kept,
    # trailing spaces dropped), and DATA 1 2 etc. are stored without error.
    out = run_cli(tmp_path, "RUN\nSYSTEM\n",
                  program="10 DATA 1 2,1.5.5,12abc,1;2,&H12G,&O1E5,(1),X+1,PRINT,a b ,&OA,&O1.5,&HG,AbC\n"
                          "20 FOR I=1 TO 14:READ A$:PRINT \"[\"A$\"]\":NEXT\n")
    assert out.count("Syntax error") == 0, out
    for item in RAW_ITEMS:
        assert "[" + item + "]\n" in out, (item, out)


def test_data_numbers_read_into_strings_as_typed(tmp_path):
    # Measured: &O9|&O8|1|1.50|.5|&HFF|1E5|007|-3|abc
    out = run_cli(tmp_path, "RUN\nSYSTEM\n",
                  program="10 DATA &O9,&O8,1,1.50,.5,&HFF,1E5,007,-3,abc\n"
                          "20 READ A$,B$,C$,D$,E$,F$,G$,H$,I$,J$\n"
                          "30 PRINT A$;\"|\";B$;\"|\";C$;\"|\";D$;\"|\";E$;\"|\";F$;\"|\";G$;\"|\";H$;\"|\";I$;\"|\";J$\n")
    assert "&O9|&O8|1|1.50|.5|&HFF|1E5|007|-3|abc\n" in out, out


@pytest.mark.skipif(NODE is None, reason="node not installed")
def test_js_data_numbers_read_into_strings_as_typed(tmp_path):
    (tmp_path / "g.bas").write_text(
        "10 DATA &O9,&O8,1,1.50,.5,&HFF,1E5,007,-3,abc\n"
        "20 READ A$,B$,C$,D$,E$,F$,G$,H$,I$,J$\n"
        "30 PRINT A$;\"|\";B$;\"|\";C$;\"|\";D$;\"|\";E$;\"|\";F$;\"|\";G$;\"|\";H$;\"|\";I$;\"|\";J$\n")
    subprocess.run([sys.executable, str(ROOT / "mbasic"), str(tmp_path / "g.bas"),
                    "--compile-js", str(tmp_path / "g.js")],
                   check=True, capture_output=True, text=True, timeout=60)
    result = subprocess.run([NODE, str(tmp_path / "g.js")], capture_output=True,
                            text=True, timeout=60)
    assert "&O9|&O8|1|1.50|.5|&HFF|1E5|007|-3|abc" in result.stdout, result.stdout + result.stderr


def test_data_in_a_loaded_file(tmp_path):
    out = run_cli(tmp_path, "LIST\nSYSTEM\n", program="10 DATA &O9\n20 DATA A,&O19\n")
    assert "10 DATA &O9" in out and "20 DATA A,&O19" in out, out


def test_octal_89_outside_data_is_refused(tmp_path):
    out = run_cli(tmp_path, "10 PRINT &O9\nLIST\nSYSTEM\n")
    assert "Syntax error" in out and "10 PRINT" not in out, out


def test_line_number_stops_at_6553(tmp_path):
    out = run_cli(tmp_path, '65529 PRINT 2\n70000 PRINT 1\n65530 PRINT 3\n'
                            '99999 PRINT 4\n123456\nLIST\nSYSTEM\n')
    assert ("6553 0 PRINT 3\n7000 0 PRINT 1\n9999 9 PRINT 4\n12345 6\n"
            "65529 PRINT 2\n") in out, out


def test_bare_number_above_65529_is_a_line(tmp_path):
    out = run_cli(tmp_path, "65529\n70000\nLIST\nSYSTEM\n")
    assert "Undefined line number" in out, out
    assert "7000 0\n" in out, out


def test_line_number_in_a_loaded_file(tmp_path):
    out = run_cli(tmp_path, "LIST\nSYSTEM\n", program="70000 PRINT 1\n65529 PRINT 2\n")
    assert "7000 0 PRINT 1\n65529 PRINT 2\n" in out, out


def test_on_error_gosub_is_a_syntax_error(tmp_path):
    out = run_cli(tmp_path, 'LIST\nRUN\nSYSTEM\n',
                  program='10 PRINT "A"\n20 ON ERROR GOSUB 100\n30 PRINT "B"\n100 RETURN\n')
    assert "20 ON ERROR GOSUB 100" in out, out
    assert "A\nSyntax error in 20\n" in out, out
    assert "\nB\n" not in out, out


def test_on_error_gosub_at_the_prompt(tmp_path):
    out = run_cli(tmp_path, "ON ERROR GOSUB 100\nSYSTEM\n")
    assert "Syntax error" in out, out


@pytest.mark.skipif(NODE is None, reason="node not installed")
def test_js_on_error_gosub_is_a_syntax_error(tmp_path):
    (tmp_path / "g.bas").write_text(
        '10 PRINT "A"\n20 ON ERROR GOSUB 100\n30 PRINT "B"\n100 RETURN\n')
    subprocess.run([sys.executable, str(ROOT / "mbasic"), str(tmp_path / "g.bas"),
                    "--compile-js", str(tmp_path / "g.js")],
                   check=True, capture_output=True, text=True, timeout=60)
    result = subprocess.run([NODE, str(tmp_path / "g.js")], capture_output=True,
                            text=True, timeout=60)
    assert result.stdout.startswith("A\nSyntax error in 20"), result.stdout + result.stderr


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))


# READ into a number variable parses the text of an unquoted DATA item.
# Each row was measured on the binary: 10 DATA <item> / 20 READ A or A% /
# 30 PRINT "A=";A.  The value is what PRINT shows, or the error text.
READ_NUMBER_CASES = [
    ("A", "abc", "Syntax error in 10"),
    ("A", "12abc", "Syntax error in 10"),
    ("A", "1 2", "A= 12"),
    ("A", "3 4 5", "A= 345"),
    ("A", "1 .5", "A= 1.5"),
    ("A", "1.5.5", "Syntax error in 10"),
    ("A", "&HG", "Syntax error in 10"),
    ("A", "&O8", "Syntax error in 20"),
    ("A", "&O19", "Syntax error in 20"),
    ("A", "&9", "Syntax error in 20"),
    ("A", "&O1A", "Syntax error in 10"),
    ("A", "&O 7", "A= 7"),
    ("A", "& 7", "A= 7"),
    ("A", "&H 1F", "Syntax error in 10"),
    ("A", "&H1F%", "Syntax error in 10"),
    ("A", "-&O7", "Syntax error in 10"),
    ("A", "&H12345", "Overflow in 20"),
    ("A", "&O1777777", "Overflow in 20"),
    ("A", "1E", "A= 1"),
    ("A", "1E+", "A= 1"),
    ("A", "5E 3", "A= 5000"),
    ("A", "5 %", "A= 5"),
    ("A", "5%%", "Syntax error in 10"),
    ("A", "- 5", "A=-5"),
    ("A", "+-5", "Syntax error in 10"),
    ("A", '"7"', "Syntax error in 10"),
    ("A", ",1", "A= 0"),
    ("A%", "12.7", "A= 13"),
    ("A%", "70000", "Overflow in 20"),
    ("A%", "5 5", "A= 55"),
    ("A%", "abc", "Syntax error in 10"),
]


def first_result(text):
    for line in text.splitlines():
        if line.startswith(("A=", "Syntax error", "Overflow")):
            return line.rstrip()
    return None


@pytest.mark.parametrize("var,item,expected", READ_NUMBER_CASES)
def test_read_number_from_data_text(tmp_path, var, item, expected):
    prog = f'10 DATA {item}\n20 READ {var}\n30 PRINT "A=";{var}\n'
    assert first_result(run_cli(tmp_path, "RUN\nSYSTEM\n", prog)) == expected


@pytest.mark.skipif(NODE is None, reason="node not installed")
@pytest.mark.parametrize("var,item,expected", READ_NUMBER_CASES)
def test_js_read_number_from_data_text(tmp_path, var, item, expected):
    (tmp_path / "p.bas").write_text(f'10 DATA {item}\n20 READ {var}\n30 PRINT "A=";{var}\n')
    subprocess.run([sys.executable, str(ROOT / "mbasic"), str(tmp_path / "p.bas"),
                    "--compile-js", str(tmp_path / "p.js")], check=True, capture_output=True)
    run = subprocess.run([NODE, str(tmp_path / "p.js")], capture_output=True, text=True, timeout=60)
    assert first_result(run.stdout + run.stderr) == expected


TRAPPED_READ = ('10 DATA abc,5\n20 ON ERROR GOTO 100\n30 READ A\n35 PRINT A\n40 END\n'
                '100 PRINT ERR;ERL:RESUME NEXT\n')


def test_read_number_error_is_trapped_with_the_data_line(tmp_path):
    # Measured: ERR is 2 and ERL is the DATA line (10); RESUME NEXT goes on
    # after the READ, so PRINT A shows 0.
    out = run_cli(tmp_path, "RUN\nSYSTEM\n", TRAPPED_READ)
    assert " 2  10 \n 0 \n" in out, out


@pytest.mark.skipif(NODE is None, reason="node not installed")
def test_js_read_number_error_is_trapped_with_the_data_line(tmp_path):
    (tmp_path / "p.bas").write_text(TRAPPED_READ)
    subprocess.run([sys.executable, str(ROOT / "mbasic"), str(tmp_path / "p.bas"),
                    "--compile-js", str(tmp_path / "p.js")], check=True, capture_output=True)
    run = subprocess.run([NODE, str(tmp_path / "p.js")], capture_output=True, text=True, timeout=60)
    assert run.stdout.splitlines()[:2] == [" 2  10 ", " 0 "], run.stdout + run.stderr


# A bad item is not consumed: the next READ gets the same item again
# (measured on the binary for abc, &O8, &O19 and &HFFFFF).
BAD_ITEM_THEN_STRING = ('10 DATA {item},5\n20 ON ERROR GOTO 100\n30 READ A\n35 READ B$\n'
                        '36 PRINT "B=";B$\n40 SYSTEM\n100 PRINT ERR;ERL:RESUME NEXT\n')


@pytest.mark.parametrize("item", ["abc", "&O8", "&O19", "&HFFFFF"])
def test_bad_data_item_is_read_again(tmp_path, item):
    out = run_cli(tmp_path, "RUN\nSYSTEM\n", BAD_ITEM_THEN_STRING.format(item=item))
    assert f"B={item}\n" in out, out


@pytest.mark.skipif(NODE is None, reason="node not installed")
@pytest.mark.parametrize("item", ["abc", "&O8", "&O19", "&HFFFFF"])
def test_js_bad_data_item_is_read_again(tmp_path, item):
    (tmp_path / "p.bas").write_text(BAD_ITEM_THEN_STRING.format(item=item))
    subprocess.run([sys.executable, str(ROOT / "mbasic"), str(tmp_path / "p.bas"),
                    "--compile-js", str(tmp_path / "p.js")], check=True, capture_output=True)
    run = subprocess.run([NODE, str(tmp_path / "p.js")], capture_output=True, text=True, timeout=60)
    assert f"B={item}\n" in run.stdout, run.stdout + run.stderr


# A failing item rewinds the whole READ statement, not only the failing item
# (measured on the binary).
MULTI_READ = ('10 DATA 1,2,x,4\n20 ON ERROR GOTO 100\n30 READ A,B,C\n40 READ D\n'
              '45 PRINT A;B;C;D\n50 SYSTEM\n100 PRINT ERR;ERL:RESUME NEXT\n')


def test_failed_read_rewinds_the_whole_statement(tmp_path):
    out = run_cli(tmp_path, "RUN\nSYSTEM\n", MULTI_READ)
    assert " 2  10 \n 1  2  0  1 \n" in out, out


@pytest.mark.skipif(NODE is None, reason="node not installed")
def test_js_failed_read_rewinds_the_whole_statement(tmp_path):
    (tmp_path / "p.bas").write_text(MULTI_READ)
    subprocess.run([sys.executable, str(ROOT / "mbasic"), str(tmp_path / "p.bas"),
                    "--compile-js", str(tmp_path / "p.js")], check=True, capture_output=True)
    run = subprocess.run([NODE, str(tmp_path / "p.js")], capture_output=True, text=True, timeout=60)
    assert " 2  10 \n 1  2  0  1 \n" in run.stdout, run.stdout + run.stderr
