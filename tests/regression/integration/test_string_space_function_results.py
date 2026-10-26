"""Out of string space (issue 31): a string that a function or operator makes counts.

Measured on MBASIC 5.21 under cpmemu with a 100-character literal L:
  10 DIM A$(600) / 20 ON ERROR GOTO 100 / 30 FOR I=0 TO 600 / 40 A$(I)=<expr>
  50 NEXT / 70 PRINT "done";I / 100 PRINT "err";ERR;"at I=";I
  <expr> = LEFT$(L,100), RIGHT$(L,100), MID$(L,1), MID$(L,1,255), L+"" or ""+L:
      err 14 at I= 371
  <expr> = LEFT$(L,LEN(L)):  err 14 at I= 370
  B$=LEFT$(L,100) then A$(I)=B$:  err 14 at I= 370
  <expr> = L (the literal itself):  no error, it points into the program text.
The interpreter counts the budget about 20 strings later than the binary (see
STRING_SPACE_AND_FILE_ERRORS.md), so the tests check the error and a range of I.
A result that equals the whole literal used to be the same Python object as the
literal and cost nothing.
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
LITERAL = '"' + "X" * 100 + '"'


def run_cli(directory, source):
    (directory / "s.bas").write_text(source)
    return subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(directory / "s.bas"), "--ui", "cli"],
        input="RUN\nSYSTEM\n", cwd=directory, capture_output=True, text=True, timeout=60).stdout


def loop(expr, before=""):
    return (before + "10 DIM A$(600)\n20 ON ERROR GOTO 100\n30 FOR I=0 TO 600\n40 A$(I)=%s\n50 NEXT\n"
            '70 PRINT "done";I\n80 SYSTEM\n100 PRINT "err";ERR;"at I=";I\n110 SYSTEM\n'
            % expr.replace("@", LITERAL))


@pytest.mark.parametrize("expr", [
    "LEFT$(@,100)", "RIGHT$(@,100)", "MID$(@,1)", "MID$(@,1,255)",
    '@+""', '""+@', "LEFT$(@,LEN(@))"])
def test_full_length_result_counts(tmp_path, expr):
    out = run_cli(tmp_path, loop(expr))
    assert "err 14 at I=" in out and "done" not in out, out
    i = int(out.split("at I=")[1].split()[0])
    assert 340 <= i <= 400, out


def test_result_kept_in_a_variable_counts(tmp_path):
    out = run_cli(tmp_path, loop("B$", "5 B$=LEFT$(%s,100)\n" % LITERAL))
    assert "err 14 at I=" in out, out


def test_the_literal_itself_is_free(tmp_path):
    out = run_cli(tmp_path, loop("@"))
    assert "done 601" in out and "err" not in out.replace("error", ""), out


def test_def_fn_passing_a_string_through_counts(tmp_path):
    # Measured on the binary: DEF FNA$(X)=L$ with A$(I)=FNA$(0), and
    # DEF FNA$(X$)=X$ with A$(I)=FNA$(L$): both err 14 at I= 371.
    for define, call in (("DEF FNA$(X)=L$", "FNA$(0)"), ("DEF FNA$(X$)=X$", "FNA$(L$)")):
        out = run_cli(tmp_path, loop(call, "5 L$=%s\n6 %s\n" % (LITERAL, define)))
        assert "err 14 at I=" in out and "done" not in out, out


def test_def_fn_with_a_literal_body_is_free(tmp_path):
    # Measured on the binary: DEF FNA$(X)="xxx..." gives done 601.
    out = run_cli(tmp_path, loop("FNA$(0)", "6 DEF FNA$(X)=%s\n" % LITERAL))
    assert "done 601" in out, out


def test_data_strings_are_free(tmp_path):
    # Measured on the binary: READ D$ from DATA text, then A$(I)=D$: done 601.
    for data in ("X" * 100, LITERAL):
        out = run_cli(tmp_path, loop("D$", "6 READ D$:DATA %s\n" % data))
        assert "done 601" in out, out


def test_def_fn_calling_a_literal_def_fn_is_free(tmp_path):
    # Measured on the binary: DEF FNB$(X)=<literal>, DEF FND$(X)=FNB$(X) and
    # DEF FNH$(X$)=FNB$(X), then A$(I)=FND$(1) or FNH$(L$): done 601.
    for define, call in (("DEF FND$(X)=FNB$(X)", "FND$(1)"), ("DEF FNH$(X$)=FNB$(X)", "FNH$(L$)")):
        before = "5 L$=%s\n6 DEF FNB$(X)=%s\n9 %s\n" % (LITERAL, LITERAL, define)
        out = run_cli(tmp_path, loop(call, before))
        assert "done 601" in out, out
