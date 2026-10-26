"""Errors found when a line is entered or loaded (issues 38, 39, 52 and 53), measured on MBASIC 5.21.

53: a line that does not parse is stored without a message, LIST shows it as
    typed, and Syntax error comes when RUN reaches the bad statement (the
    statements before it on the line run first).  The line editor then opens on
    the line.
52: a reserved word followed by "$", "%", "!" or "#" is the keyword and a stray
    character, so NAME$ is a Syntax error when it runs; TOTAL, NAMES$ and
    NAME.X are plain variables.
38: Overflow is printed for each literal such as 1E39 while LOAD or MERGE or
    the command-line load reads the file.
39: a line with an &H or &O overflow is refused, and LOAD stops reading there.
"""
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: entry-time error tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

ROOT = Path(__file__).resolve().parents[3]
NODE = shutil.which("node")
CPMEMU = shutil.which("cpmemu")
UC80 = shutil.which("uc80")


def run_cli(directory, commands, source=None):
    """Run the CLI on commands (with the program file loaded first when source is given)."""
    argv = [sys.executable, str(ROOT / "mbasic"), "--ui", "cli"]
    if source is not None:
        (directory / "p.bas").write_bytes(source.replace("\n", "\r\n").encode())
        argv.insert(2, str(directory / "p.bas"))
    result = subprocess.run(argv, input=commands, cwd=directory, capture_output=True,
                            text=True, timeout=60)
    return result.stdout.replace("\r", "")


BAD = '10 PRINT "A"\n20 NAME$="B":PRINT "Z"\n30 PRINT "C"\n'


# --- 53 ---------------------------------------------------------------------

def test_typed_bad_line_is_stored_silently_and_fails_at_run(tmp_path):
    # Real MBASIC: no message at entry, LIST shows the three lines, RUN prints
    # A and then "Syntax error in 20"; line 30 does not run.
    out = run_cli(tmp_path, BAD + "LIST\nRUN\n\nLIST\nSYSTEM\n")
    assert "Syntax error:" not in out and "Expected" not in out, out
    listing = '10 PRINT "A"\n20 NAME$="B":PRINT "Z"\n30 PRINT "C"\n'
    assert out.count(listing) == 2, out
    assert 'A\nSyntax error in 20\n' in out, out
    assert "Z" not in out.replace('PRINT "Z"', "")
    assert "\nC\n" not in out


def test_statements_before_the_bad_one_run(tmp_path):
    # Real MBASIC: Z is printed, then "Syntax error in 20"; Y never is.
    out = run_cli(tmp_path, '10 PRINT "A"\n20 PRINT "Z":NAME$="B":PRINT "Y"\nRUN\n\nSYSTEM\n')
    assert 'A\nZ\nSyntax error in 20\n' in out, out
    assert "\nY\n" not in out


def test_bad_statement_inside_if_runs_the_branch_first(tmp_path):
    # Real MBASIC: "10 IF 1 THEN PRINT "T":FORX=1TO3" prints T, then Syntax error in 10.
    out = run_cli(tmp_path, '10 IF 1 THEN PRINT "T":FORX=1TO3\nRUN\n\nSYSTEM\n')
    assert 'T\nSyntax error in 10\n' in out, out


def test_loaded_bad_line_is_kept_without_a_message(tmp_path):
    out = run_cli(tmp_path, "LIST\nRUN\n\nSYSTEM\n", source=BAD)
    assert "Syntax error:" not in out and "Expected" not in out and "rejected" not in out, out
    assert '20 NAME$="B":PRINT "Z"' in out, out
    assert 'A\nSyntax error in 20\n' in out, out


def test_on_error_traps_the_bad_statement(tmp_path):
    # Real MBASIC: Z, " 2  20 ", Y, C.  RESUME NEXT goes on with PRINT "Y".
    program = ('10 ON ERROR GOTO 100\n20 PRINT "Z":NAME$="B":PRINT "Y"\n30 PRINT "C"\n'
               '40 SYSTEM\n100 PRINT ERR;ERL\n110 RESUME NEXT\n')
    out = run_cli(tmp_path, "RUN\nSYSTEM\n", source=program)
    assert "Z\n 2  20 \nY\nC\n" in out, out


def test_renum_keeps_the_bad_line(tmp_path):
    # Real MBASIC: RENUM 100 gives 100 GOTO 110 / 110 NAME$="B":GOTO 120 / 120 PRINT "C".
    out = run_cli(tmp_path, '10 GOTO 20\n20 NAME$="B":GOTO 30\n30 PRINT "C"\nRENUM 100\nLIST\nSYSTEM\n')
    assert '100 GOTO 110\n110 NAME$="B":GOTO 120\n120 PRINT "C"\n' in out, out


def test_editor_opens_on_the_bad_line(tmp_path):
    # Real MBASIC: after "Syntax error in 20" the editor starts on line 20; L
    # lists the line, an empty line leaves the editor, the line stays.
    out = run_cli(tmp_path, BAD + "RUN\nL\n\nLIST\nSYSTEM\n")
    assert 'Syntax error in 20\n20 NAME$="B":PRINT "Z"\n20 NAME$="B":PRINT "Z"\n' in out, out
    assert out.rstrip().endswith("Goodbye"), out
    assert '30 PRINT "C"\n' in out.split("Syntax error in 20")[1], out


# --- 52 ---------------------------------------------------------------------

@pytest.mark.parametrize("line", [
    '10 NAME$="A":PRINT NAME$',
    "10 LEN%=3:PRINT LEN%",
    '10 FOR$="A":PRINT FOR$',
    "10 TO%=3:PRINT TO%",
    "10 ERR%=3:PRINT ERR%",
    '10 ERL$="A":PRINT ERL$',
    '10 PRINT LEN("AB")+LEN%',
    "10 ERR=3",
    "10 ERL=3",
    "10 FORX=1TO3",
])
def test_reserved_word_with_suffix_is_a_syntax_error(tmp_path, line):
    # Real MBASIC: "Syntax error in 10" for every one of these lines.
    out = run_cli(tmp_path, "RUN\n\nSYSTEM\n", source=line + "\n")
    assert out.split("Ok\n", 1)[1].startswith("Syntax error in 10\n"), out


@pytest.mark.parametrize("line, shown", [
    ('10 TOTAL=3:NAMES$="X":FORM=2:COST=4:NAME.X=5:PRINT TOTAL;NAMES$;FORM;COST;NAME.X',
     " 3 X 2  4  5 \n"),
    ('10 NAME.X$="A":PRINT NAME.X$', "A\n"),
    ("10 TOTAL%=3:PRINT TOTAL%", " 3 \n"),
    ("10 PRINT ERR;ERL", " 0  0 \n"),
    ('10 TIME$="x":LEFT=1:CHR=2:PRINT TIME$;LEFT;CHR', "x 1  2 \n"),
    ('10 SHOW%=1:HELP$="a":PRINT SHOW%;HELP$', " 1 a\n"),
])
def test_names_that_only_contain_a_reserved_word_still_work(tmp_path, line, shown):
    # Real MBASIC runs all of these.
    out = run_cli(tmp_path, "RUN\nSYSTEM\n", source=line + "\n")
    assert out.split("Ok\n", 1)[1].startswith(shown), out


def test_input_dollar_still_works(tmp_path):
    out = run_cli(tmp_path, "RUN\nxSYSTEM\n", source="10 A$=INPUT$(1):PRINT A$\n")
    assert out.split("Ok\n", 1)[1].startswith("x\n"), out
    assert "Syntax error" not in out, out


def test_file_io_hash_forms_still_work(tmp_path):
    program = '10 OPEN "O",#1,"x.tmp":PRINT#1,1:CLOSE#1:KILL "x.tmp":PRINT "ok"\n'
    out = run_cli(tmp_path, "RUN\nSYSTEM\n", source=program)
    assert out.split("Ok\n", 1)[1].startswith("ok\n"), out


# --- 38 ---------------------------------------------------------------------

def test_load_prints_overflow_for_a_big_literal(tmp_path):
    # Real MBASIC: LOAD "zd.bas" (10 A=1E39 / 20 PRINT A) prints Overflow once, before Ok.
    (tmp_path / "zd.bas").write_bytes(b"10 A=1E39\r\n20 PRINT A\r\n")
    out = run_cli(tmp_path, 'LOAD "zd.bas"\nLIST\nSYSTEM\n')
    assert out.count("Overflow") == 1, out
    assert out.index("Overflow") < out.index("Loaded from"), out
    assert "10 A=" in out and "20 PRINT A" in out, out


def test_load_prints_overflow_for_each_literal(tmp_path):
    # Real MBASIC: MERGE of "20 A=1E39:B=2E39" prints Overflow twice.
    (tmp_path / "zd2.bas").write_bytes(b"10 PRINT 1\r\n20 A=1E39:B=2E39\r\n30 PRINT 2\r\n")
    out = run_cli(tmp_path, 'MERGE "zd2.bas"\nSYSTEM\n')
    assert out.count("Overflow") == 2, out
    out = run_cli(tmp_path, '20 A=1E39:B=2E39\nSYSTEM\n')
    assert out.count("Overflow") == 2, out


def test_command_line_load_prints_overflow(tmp_path):
    out = run_cli(tmp_path, "LIST\nSYSTEM\n", source="10 A=1E39\n20 PRINT A\n")
    assert out.count("Overflow") == 1, out
    assert "10 A=" in out, out


# --- 39 ---------------------------------------------------------------------

OVERFLOW_PROGRAM = "10 PRINT 1\n20 A=&H12345\n30 PRINT 2\n40 B=&O200000\n50 PRINT 3\n"


def test_typed_radix_overflow_is_refused(tmp_path):
    # Real MBASIC: Overflow after line 20 and after line 40; LIST shows 10, 30
    # and 50; RUN prints 1, 2, 3.
    out = run_cli(tmp_path, OVERFLOW_PROGRAM + "LIST\nRUN\nSYSTEM\n")
    assert out.count("Overflow") == 2, out
    assert "20 A=" not in out and "40 B=" not in out, out
    assert "10 PRINT 1\n30 PRINT 2\n50 PRINT 3\n" in out, out
    assert " 1 \n 2 \n 3 \n" in out, out


def test_refused_line_leaves_the_old_line(tmp_path):
    out = run_cli(tmp_path, "20 PRINT 7\n20 A=&H12345\nLIST\nRUN\nSYSTEM\n")
    assert "20 PRINT 7" in out and " 7 \n" in out, out


def test_load_stops_at_a_radix_overflow(tmp_path):
    # Real MBASIC: LOAD prints Overflow and the lines after the bad one are not
    # loaded (LIST shows line 10 only).
    (tmp_path / "zh.bas").write_bytes(OVERFLOW_PROGRAM.replace("\n", "\r\n").encode())
    out = run_cli(tmp_path, 'LOAD "zh.bas"\nLIST\nRUN\nSYSTEM\n')
    assert "Overflow" in out, out
    assert "10 PRINT 1\n" in out and "30 PRINT 2" not in out and "50 PRINT 3" not in out, out


# --- compilers: the bad statement is a run-time error -------------------------

COMPILE_PROGRAM = '10 PRINT "A"\n20 PRINT "Z":NAME$="B":PRINT "Y"\n30 PRINT "no"\n'


@pytest.mark.skipif(NODE is None, reason="Node.js is needed to execute generated JavaScript")
def test_javascript_raises_syntax_error_at_run_time(tmp_path):
    (tmp_path / "w.bas").write_text(COMPILE_PROGRAM)
    compiled = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(tmp_path / "w.bas"),
         "--compile-js", str(tmp_path / "w.js")],
        cwd=tmp_path, capture_output=True, text=True, timeout=60)
    assert compiled.returncode == 0, compiled.stdout + compiled.stderr
    result = subprocess.run([NODE, str(tmp_path / "w.js")], cwd=tmp_path,
                            capture_output=True, text=True, timeout=60)
    out = (result.stdout + result.stderr).replace("\r", "")
    assert out.startswith("A\nZ\n") and "Syntax error" in out, out
    assert "Y" not in out and "no" not in out, out


@pytest.mark.skipif(CPMEMU is None or UC80 is None, reason="uc80 and cpmemu are needed for the C backend")
def test_c_backend_raises_syntax_error_at_run_time(tmp_path):
    (tmp_path / "w.bas").write_text(COMPILE_PROGRAM)
    compiled = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(tmp_path / "w.bas"),
         "--compile-c", str(tmp_path / "w")],
        cwd=tmp_path, capture_output=True, text=True, timeout=300)
    assert (tmp_path / "w.com").exists(), compiled.stdout + compiled.stderr
    ran = subprocess.run([CPMEMU, "w.com"], cwd=tmp_path, capture_output=True,
                         text=True, timeout=60)
    out = (ran.stdout + ran.stderr).replace("\r", "")
    assert "A\nZ\nSyntax error" in out, out
    assert "no" not in out.split("Program exit")[0].replace("Loaded", ""), out


# --- review round: measured on MBASIC 5.21 with ON ERROR GOTO and RESUME NEXT ---

TRAP = '5 ON ERROR GOTO 1000\n%s\n900 PRINT "end":SYSTEM\n1000 PRINT "E";ERR;ERL:RESUME NEXT\n'


def trapped(tmp_path, line):
    return run_cli(tmp_path, "RUN\nSYSTEM\n", source=TRAP % line)


def test_data_text_is_kept_raw(tmp_path):
    # Real MBASIC (re-measured): DATA text is raw, so NAME$ and LEN% keep their case.
    out = run_cli(tmp_path, "RUN\nSYSTEM\n",
                  source='20 DATA NAME$,LEN%,XYZ$\n40 READ A$,B$,C$:PRINT A$;B$;C$\n')
    assert "NAME$LEN%XYZ$" in out, out


@pytest.mark.parametrize("line", ['10 NEXT%=1', '10 USR%=1', '10 A=LPOS%', '10 LET%=1',
                                  '10 WEND%=1', '10 RETURN%', '10 END%'])
def test_keyword_plus_stray_character_is_only_a_syntax_error(tmp_path, line):
    # Real MBASIC: "E 2  10" and nothing else (no NEXT without FOR, no END).
    out = trapped(tmp_path, line)
    assert "E 2  10" in out and "E 1 " not in out and "E 30" not in out and "E 3 " not in out, out
    assert "\nend\n" in out, out


def test_resume_with_stray_text_gives_only_error_20(tmp_path):
    out = trapped(tmp_path, '10 RESUME$=1')
    assert "E 20  10" in out and "E 2  10" not in out, out


def test_restore_with_stray_text_gives_error_8(tmp_path):
    assert "E 8  10" in trapped(tmp_path, '10 RESTORE%')


def test_print_runs_before_the_stray_text(tmp_path):
    # Real MBASIC: PRINT "a";$ prints a, then Syntax error.
    out = trapped(tmp_path, '10 PRINT "a";$')
    assert "aE 2  10" in out, out


def test_immediate_mode_reports_syntax_error(tmp_path):
    out = run_cli(tmp_path, 'LEN%=1\nNAME$="x"\nPRINT 1 @\nSYSTEM\n')
    assert out.count("Syntax error") == 3 and "Illegal function call" not in out, out


@pytest.mark.parametrize("text", ["&O9", "&O19", "&O78", "&19"])
def test_typed_octal_with_8_or_9_is_refused(tmp_path, text):
    # Real MBASIC: "10 X=&O9" gives Syntax error and the line is not stored.
    out = run_cli(tmp_path, "10 X=%s\nLIST\nSYSTEM\n" % text)
    assert "Syntax error" in out and "10 X=" not in out, out


def test_load_stops_at_an_octal_with_9_and_prints_bare_messages(tmp_path):
    # Real MBASIC: LOAD prints Syntax error and stops; lines after are not loaded.
    (tmp_path / "o.bas").write_bytes(b"10 A=1\r\n20 X=&O9\r\n30 PRINT 3\r\n")
    out = run_cli(tmp_path, 'LOAD "o.bas"\nLIST\nSYSTEM\n')
    assert "Syntax error\n" in out and "file line" not in out, out
    assert "10 A=1" in out and "30 PRINT 3" not in out, out


def test_load_overflow_prints_no_file_diagnostic(tmp_path):
    (tmp_path / "h.bas").write_bytes(b"10 A=1\r\n20 A=&H12345\r\n30 PRINT 3\r\n")
    out = run_cli(tmp_path, 'LOAD "h.bas"\nSYSTEM\n')
    assert "Overflow\n" in out and "file line" not in out, out


def test_data_text_gets_no_overflow_and_is_stored(tmp_path):
    # Real MBASIC: DATA text is raw. "10 DATA 1E39,&HFFFFF" gives no Overflow and is listed;
    # only the PRINT 1E39 on line 40 gives one.
    out = run_cli(tmp_path, "LIST\nSYSTEM\n", source="10 DATA 1E39,&HFFFFF\n40 PRINT 1\n")
    assert "Overflow" not in out and "10 DATA 1E39,&HFFFFF" in out, out
    out = run_cli(tmp_path, "10 DATA 1E39,&HFFFFF\n40 PRINT 1E39\nLIST\nSYSTEM\n")
    assert out.count("Overflow") == 1 and "10 DATA 1E39,&HFFFFF" in out, out


@pytest.mark.parametrize("word", ["STOP", "SYSTEM", "NEW"])
def test_stop_system_new_with_stray_text_do_not_run(tmp_path, word):
    # Real MBASIC: "20 STOP@" gives "Syntax error in 20" (not Break), SYSTEM@ does not exit
    # and NEW@ does not wipe the program.
    out = run_cli(tmp_path, "RUN\nSYSTEM\n", source="10 PRINT 1\n20 %s@\n30 PRINT 2\n" % word)
    assert "Syntax error in 20" in out and "Break" not in out, out


def test_unterminated_string_at_end_of_line_is_valid(tmp_path):
    # Real MBASIC 5.21: '10 PRINT "abc' and '20 PRINT "z' run and print abc and z.
    out = run_cli(tmp_path, "RUN\nSYSTEM\n", source='10 PRINT "abc\n20 PRINT "z\n')
    assert "abc\nz\n" in out and "Syntax error" not in out, out


def test_null_with_type_character_is_a_syntax_error(tmp_path):
    # Real MBASIC: NULL is reserved, so NULL%=1 is a Syntax error (E 2).
    assert "E 2  10" in trapped(tmp_path, '10 NULL%=1')


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
