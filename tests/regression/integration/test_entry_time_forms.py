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
