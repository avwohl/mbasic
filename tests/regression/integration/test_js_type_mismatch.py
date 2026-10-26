"""Type mismatch (error 13) in generated JavaScript (issue 59).

MBASIC 5.21 finds a string where a number is wanted, or a number where a string
is wanted, when the statement runs. The error is trappable with ON ERROR and
carries the line of the statement. The JavaScript compiler used to fail while
compiling (-"a", NOT "a", ABS("a"), FOR I="a" TO 2), to compute a value
(1+"a" gave 1a, "a"*2 gave aa, "a"<1 gave 0) or to run on without an error
(A$=1, LEN(1)).

Every expected text below was measured on real MBASIC 5.21 (com/mbasic.com
under cpmemu, tests/HOW_TO_RUN_REAL_MBASIC.md): each program was 10 <body> and
20 SYSTEM. The C backend refuses the mixed forms at compile time with a
diagnostic (it has no run-time error to raise at that point); that is checked
here too.
"""
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: JavaScript Type mismatch tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

ROOT = Path(__file__).resolve().parents[3]
NODE = shutil.which("node")

needs_node = pytest.mark.skipif(NODE is None, reason="Node.js is needed to execute generated JavaScript")

MISMATCH = "Type mismatch in 10\n"

# Statements that the binary stops with "Type mismatch in 10".
ERROR_BODIES = [
    # a string and a number under an operator
    'PRINT "a"<1', 'PRINT 1+"a"', 'PRINT "a"*2', 'PRINT "a"+1', 'PRINT 1-"a"',
    'PRINT "a"=1', 'PRINT 1<>"a"', 'PRINT "a"^2', 'PRINT "a"/1',
    'PRINT "a" XOR 1', 'PRINT 1=1 AND "a"', 'PRINT "a" OR 1',
    # a rewrite of X*1, 0*X and X+0 must not hide the error
    'PRINT "a"*1', 'PRINT 0*"a"', 'PRINT "a"+0',
    'A$="x":PRINT A$*2', 'A$="x":B=2:PRINT A$+B', 'A$="a":PRINT LEN(A$)+"b"',
    # two strings under an operator that is not + or a comparison
    'PRINT "a"-"b"', 'PRINT "a"*"b"', 'PRINT "a"/"b"', 'PRINT "a"^"b"',
    'PRINT "a"\\"b"', 'PRINT "a" MOD "b"', 'PRINT "a" AND "b"',
    'PRINT "a" IMP 1',
    # unary - and NOT on a string
    'PRINT -"a"', 'PRINT NOT "a"', 'A$="x":PRINT -A$', 'PRINT -(+"a")',
    'PRINT 1+(+"a")', 'PRINT +"a"+1',
    # assignment of the wrong kind
    'A=1:A$=A', 'A$=1', 'A="x"', 'A$=-1', 'DEFSTR S:S=1', 'DEFINT I:I="a"',
    'DIM A$(2):A$(1)=1', 'DIM A(2):A(1)="x"', 'X=(1+"a")', 'X$=("a"+"b")+1',
    'PRINT ("a"+"b")*2',
    # built-in functions given the wrong kind
    'PRINT LEN(1)', 'PRINT LEFT$(1,1)', 'PRINT RIGHT$(1,1)', 'PRINT LEFT$("a","b")',
    'PRINT CHR$("a")', 'PRINT ABS("a")', 'PRINT VAL(1)', 'PRINT STR$("a")',
    'PRINT SQR("4")', 'PRINT MID$("abc","a")', 'PRINT SPACE$("a")',
    'PRINT ASC(1)', 'PRINT INT("a")', 'PRINT HEX$("a")', 'PRINT OCT$("a")',
    'PRINT CINT("a")', 'PRINT SGN("a")', 'PRINT LOG("a")', 'PRINT FIX("a")',
    'PRINT EXP("a")', 'PRINT CVI(1)', 'PRINT MKI$("a")', 'PRINT PEEK("a")',
    'PRINT RND("a")', 'PRINT STRING$("a",65)', 'PRINT VAL("a")+"b"',
    # statements that need a number or a string
    'IF "a" THEN PRINT 1', 'WHILE "a":WEND', 'FOR I="a" TO 2:NEXT',
    'FOR I=1 TO "a":NEXT', 'FOR I=1 TO 2 STEP "a":NEXT', 'A$="x":FOR A$=1 TO 2:NEXT',
    'ON "a" GOTO 10', 'SWAP A,A$', 'A$="a":MID$(A$,1)=1', 'A$="a":MID$(A$,"a")="b"',
    'RANDOMIZE "a"',
    # DEF FN: the argument and the value
    'DEF FNA(X)=X+1:PRINT FNA("a")', 'DEF FNA$(X$)=X$+"!":PRINT FNA$(2)',
    'DEF FNA(X)=X+1:Y$=FNA(2)',
    # PRINT USING: a string goes with a string field, a number with a numeric field
    'PRINT USING 1;2', 'PRINT USING "#";"a"', 'PRINT USING "#";"1"',
    'PRINT USING "!";1', 'PRINT USING "&";1', 'PRINT USING "\\  \\";1',
]

# Forms that are fine: unary + passes a string, + and a comparison take two strings,
# a comparison is a number whatever it compares.
OK_CASES = [
    ('PRINT +"a"', "a\n"),
    ('PRINT +"a"+"b"', "ab\n"),
    ('PRINT "a"+"b"', "ab\n"),
    ('PRINT "a"<"b"', "-1 \n"),
    ('PRINT "a"+"b"="ab"', "-1 \n"),
    ('PRINT 1+("a"="a")', " 0 \n"),
    ('PRINT ("a"<"b")*2', "-2 \n"),
    ('PRINT STRING$(2,"a")', "aa\n"),
    ('PRINT CHR$(65)+CHR$(66)', "AB\n"),
    ('DEFSTR S:S="q":PRINT S', "q\n"),
    ('DEF FNA$(X$)=X$+"!":PRINT FNA$("a")', "a!\n"),
    ('DEF FNA(X)=X+1:PRINT 1+FNA(2)', " 4 \n"),
    ('PRINT USING "#";1', "1\n"),
    ('PRINT USING "!";"abc"', "a\n"),
    ('IF "a"="a" THEN PRINT 7', " 7 \n"),
]


def compile_js(tmp_path, source):
    basic = tmp_path / "prog.bas"
    basic.write_text(source)
    output = tmp_path / "prog.js"
    result = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(basic), "--compile-js", str(output)],
        cwd=ROOT, capture_output=True, text=True, timeout=60)
    return result, output


def run_js(tmp_path, source):
    result, output = compile_js(tmp_path, source)
    assert result.returncode == 0, result.stdout + result.stderr
    run = subprocess.run([NODE, str(output)], capture_output=True, text=True, timeout=10)
    return run.stdout


@needs_node
@pytest.mark.parametrize("body", ERROR_BODIES)
def test_type_mismatch_at_run_time(tmp_path, body):
    assert run_js(tmp_path, f"10 {body}\n20 SYSTEM\n") == MISMATCH


@needs_node
@pytest.mark.parametrize("body,expected", OK_CASES, ids=[c[0] for c in OK_CASES])
def test_well_typed_forms_still_work(tmp_path, body, expected):
    assert run_js(tmp_path, f"10 {body}\n20 SYSTEM\n") == expected


@needs_node
def test_error_is_trappable_and_names_the_line(tmp_path):
    # Measured: the binary prints x, then the handler prints ERR and ERL (13 and 20); the
    # second error, in 205, is untrapped after ON ERROR GOTO 0.
    source = ('10 ON ERROR GOTO 100\n20 PRINT "x";"a"*2\n30 PRINT "no"\n40 END\n'
              '100 PRINT ERR;ERL\n110 RESUME 200\n200 ON ERROR GOTO 0\n205 A=1:A$=A\n'
              '210 PRINT "no2"\n')
    assert run_js(tmp_path, source) == "x 13  20 \nType mismatch in 205\n"


@needs_node
def test_error_comes_when_the_statement_runs_not_when_compiled(tmp_path):
    # The statement is never reached, so the program runs to its end (as on the binary).
    source = '10 PRINT "start"\n20 GOTO 40\n30 A$=1\n40 PRINT "end"\n'
    assert run_js(tmp_path, source) == "start\nend\n"


@needs_node
def test_well_typed_code_gets_no_check(tmp_path):
    source = ('10 A$="x":B$=A$+"y":C=2*3+LEN(B$):D=C<7\n20 PRINT B$;C;D\n'
              '30 FOR I=1 TO 2:E=E+I:NEXT:IF E THEN PRINT E\n')
    result, output = compile_js(tmp_path, source)
    assert result.returncode == 0, result.stdout + result.stderr
    # a check is written into the statement that has the mismatch, so none is written here
    assert ', _error("Type mismatch"))' not in output.read_text()
    run = subprocess.run([NODE, str(output)], capture_output=True, text=True, timeout=10)
    assert run.stdout == "xy 8  0 \n 3 \n"


C_DIAGNOSED = ['PRINT "a"<1', 'PRINT 1+"a"', 'PRINT "a"*2', 'PRINT -"a"', 'A=1:A$=A',
               'A$=1', 'PRINT CHR$("a")', 'PRINT ABS("a")', 'PRINT NOT "a"',
               'FOR I="a" TO 2:NEXT', 'IF "a" THEN PRINT 1']


@pytest.mark.parametrize("body", C_DIAGNOSED)
def test_c_backend_refuses_with_a_diagnostic(tmp_path, body):
    basic = tmp_path / "prog.bas"
    basic.write_text(f"10 {body}\n20 SYSTEM\n")
    result = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(basic), "--compile-c", str(tmp_path / "prog")],
        cwd=ROOT, capture_output=True, text=True, timeout=60)
    text = result.stdout + result.stderr
    assert result.returncode != 0, text
    assert "Traceback" not in text and "Compilation error" not in text, text
    assert "does not support" in text, text


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
