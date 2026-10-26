"""CLEAR and the DEFtype statements (DEFINT, DEFSNG, DEFDBL, DEFSTR).

Every expected text below was measured on MBASIC 5.21 (com/mbasic.com under
cpmemu, tests/HOW_TO_RUN_REAL_MBASIC.md). The binary:

- runs DEFINT and its kin when the statement runs, not by its place in the
  text: a DEFINT that is jumped over or in an IF that is not taken does nothing,
  and one in a loop types the lines above it on the next pass;
- keeps A, A% and A! apart: after DEFINT A the name A means A%, and A! is the
  single precision variable;
- puts every letter back to single precision at CLEAR (and at RUN);
- types DIM A(3) and ERASE A by the table when they run;
- types FNA by the table when DEF FN runs; FNA before that DEF FN, or after a
  CLEAR, is Undefined user function, and a DEFINT A after the DEF FN makes FNA
  another function;
- rounds the result of an integer function (FNA%(3) with X*1.5 is 5), and a
  function of one kind that gives the other kind is Type mismatch;
- gives Type mismatch for SWAP of two variables of different types.

CLEAR in the JavaScript and C compilers: every variable is 0 or "", every array
is deleted, the FOR and GOSUB stacks are empty (JavaScript), the DATA pointer
goes back, and the DEF FN functions are forgotten (JavaScript). The compilers
fix the DEF types when the program is compiled.
"""
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: CLEAR and DEF type tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))
NODE = shutil.which("node")

# name: (program, output on the binary and in the interpreter)
CASES = {
    # DEFINT A, then CLEAR: A is single again
    "clear_resets_defint_defstr": (
        '10 DEFINT A:A=1.5:PRINT A:CLEAR:A=1.5:PRINT A\n'
        '20 DEFSTR S:S="x":PRINT S:CLEAR:S=1:PRINT S\n30 SYSTEM\n',
        ' 2 \n 1.5 \nx\n 1 \n'),
    # the DEFINT in line 20 never runs; A and A% are two variables after line 60
    "defint_jumped_over": (
        '10 GOTO 40\n20 DEFINT A\n40 A=1.5:PRINT A\n50 A%=7:PRINT A, A%\n'
        '60 DEFINT A:PRINT A,A%\n70 PRINT A!\n80 A!=2.5:PRINT A,A!\n'
        '90 DEFSNG A: PRINT A\n100 SYSTEM\n',
        ' 1.5 \n 1.5           7 \n 7             7 \n 1.5 \n 7             2.5 \n 2.5 \n'),
    # the DEFINT below the assignment types it on the second pass
    "defint_in_loop": (
        '10 FOR K=1 TO 2\n20 A=1.5: PRINT A\n30 DEFINT A\n40 NEXT\n50 SYSTEM\n',
        ' 1.5 \n 2 \n'),
    # DIM A(3) under DEFINT is A%(3); CLEAR deletes it and A(1) is a single array
    "dim_and_clear": (
        '10 DEFINT A: DIM A(3): A(1)=2.7: PRINT A(1)\n20 CLEAR\n'
        '30 A(1)=2.7: PRINT A(1)\n40 DIM A(3): PRINT A(1)\n'
        '50 ERASE A: DIM A(4): A(1)=2.7: PRINT A(1)\n60 SYSTEM\n',
        ' 3 \n 2.7 \nDuplicate Definition in 40'),
    # a DEFINT in a subroutine that runs
    "defint_in_gosub": (
        '10 GOSUB 100\n20 A=1.5:PRINT A\n30 GOSUB 100\n40 A=1.5:PRINT A,A!,A%\n'
        '50 SYSTEM\n100 DEFINT A: RETURN\n',
        ' 2 \n 2             0             2 \n'),
    # FNA is typed by A when DEF FN runs; a later DEFINT A makes FNA another function
    "def_fn_type": (
        '10 DEFINT X: DEF FNA(X)=X*2.5: PRINT FNA(1.5)\n20 DEFSNG X: PRINT FNA(1.5)\n'
        '30 DEFINT A:PRINT FNA(1.5)\n40 DEFSNG A:DEFINT F: PRINT FNA(1.5)\n'
        '50 PRINT FN A(1.5)\n60 SYSTEM\n',
        ' 5 \n 3.75 \nUndefined user function in 30'),
    # DEFSTR S in line 10 runs, the DEFINT S behind IF 0 does not
    "defstr_and_untaken_if": (
        '10 DEFSTR S: S="x": IF 0 THEN DEFINT S\n20 PRINT S\n'
        '30 DEFINT S:PRINT S;S$;S%\n40 S=3.5: PRINT S\n50 SYSTEM\n',
        'x\n 0 x 0 \n 4 \n'),
    # CLEAR in an error handler: ERR and ERL stay, the handler is gone
    "clear_in_handler": (
        '10 DEFINT A-Z\n20 READ X: PRINT X\n30 DATA 2.7,2.7,abc\n40 CLEAR\n'
        '50 RESTORE: READ X: PRINT X\n60 DEFINT X\n70 READ X: PRINT X\n'
        '90 Y=3.5:PRINT Y\n100 ON ERROR GOTO 200\n110 ERROR 5\n120 SYSTEM\n'
        '200 PRINT ERR;ERL:DEFSTR E: PRINT ERR;ERL;E:CLEAR: DEFSTR E:PRINT ERR;ERL;E: RESUME NEXT\n',
        ' 3 \n 2.7 \n 3 \n 3.5 \n 5  110 \n 5  110 \n 5  110 \nRESUME without error in 200'),
    # the result of a function has the type of the function
    "def_fn_result_type": (
        '10 DEF FNA%(X)=X*1.5\n20 PRINT FNA%(3);FNA%(5);FNA%(-3):B=FNA%(3):PRINT B\n'
        '30 PRINT FNA%(3)/2\n40 DEF FNB#(X)=X/3\n50 PRINT FNB#(1)\n60 DEF FNC!(X)=X/3\n'
        '70 PRINT FNC!(1)\n80 DEFDBL D:DEF FND(X)=X/3:PRINT FND(1)\n'
        '90 DEFSTR S:DEF FNS(X)=STR$(X):PRINT FNS(1)\n100 DEF FNE$(X)=X\n'
        '110 PRINT FNE$(1)\n120 SYSTEM\n',
        ' 5  8 -5 \n 5 \n 2.5 \n .3333333432674408 \n .333333 \n .3333333432674408 \n'
        ' 1\nType mismatch in 110'),
    # CLEAR: variables, arrays, DATA pointer, FOR and GOSUB stacks
    "clear_everything": (
        '10 A=5:B$="x":C%=7:D#=1.5\n20 DIM M(3,3),N$(4)\n30 M(1,1)=9:N$(2)="q"\n'
        '40 READ Q:PRINT "Q";Q\n50 FOR I=1 TO 3\n60 GOSUB 200\n70 NEXT\n80 PRINT "bad"\n'
        '200 PRINT "sub";I\n210 CLEAR\n220 PRINT A;B$;C%;D#;M(1,1);N$(2);I\n'
        '230 READ Q:PRINT "Q";Q\n240 ERASE M\n250 DIM M(5):M(4)=3:PRINT M(4)\n'
        '260 ON ERROR GOTO 300\n270 RETURN\n300 PRINT "H";ERR;ERL\n310 SYSTEM\n500 DATA 11,22\n',
        'Q 11 \nsub 1 \n 0  0  0  0  0 \nQ 11 \n 3 \nH 3  270 \n'),
    # SWAP of two different types
    "swap_type_mismatch": (
        '10 ON ERROR GOTO 100\n20 X%=1:Y=2:SWAP X%,Y:PRINT X%;Y\n30 Z#=1:SWAP Z#,Y:PRINT Z#;Y\n'
        '40 A$="a":SWAP A$,Y\n50 B=3:SWAP B,Y:PRINT B;Y\n60 SYSTEM\n100 PRINT ERR;ERL:RESUME NEXT\n',
        ' 13  20 \n 1  2 \n 13  30 \n 1  2 \n 13  40 \n 2  3 \n'),
    # DEF FN is known only when its statement has run; CLEAR forgets it
    "def_fn_before_def_and_clear": (
        '10 ON ERROR GOTO 100\n15 GOTO 30\n20 DEF FNB(X)=X+9\n30 DEF FNA(X)=X+1\n'
        '40 PRINT FNA(1)\n45 PRINT FNB(1)\n50 CLEAR\n60 PRINT FNA(1)\n90 SYSTEM\n'
        '100 PRINT ERR;ERL:RESUME NEXT\n',
        ' 2 \n 18  45 \nUndefined user function in 60'),
    "def_fn_redefined_after_clear": (
        '10 ON ERROR GOTO 100\n20 DEF FNA(X)=X+1\n30 PRINT FNA(1)\n40 CLEAR\n'
        '50 ON ERROR GOTO 100\n60 PRINT FNA(1)\n70 DEF FNA(X)=X+2\n80 PRINT FNA(1)\n'
        '90 SYSTEM\n100 PRINT ERR;ERL:RESUME NEXT\n',
        ' 2 \n 18  60 \n 3 \n'),
    # CLEAR deletes the array: DIM again gives a new one (measured: 9 and 0)
    "dim_again_after_clear": (
        '10 DIM Z(3):Z(1)=4:CLEAR:DIM Z(2):Z(2)=9:PRINT Z(2);Z(1)\n20 SYSTEM\n',
        ' 9  0 \n'),
    # the idiom CLEAR before DIM: CLEAR never fails (measured: ' 5 x')
    "clear_before_dim": (
        '10 CLEAR 500\n20 DIM A(10),B$(3)\n30 A(1)=5:B$(1)="x"\n40 PRINT A(1);B$(1)\n50 SYSTEM\n',
        ' 5 x'),
    "clear_then_dim_late": (
        '10 CLEAR\n20 DIM Q(3)\n30 PRINT 1\n40 CLEAR\n50 CLEAR\n60 SYSTEM\n', ' 1 \n'),
    # a DIM after CLEAR, or after a use, is Duplicate Definition (measured)
    "duplicate_dim_after_clear": (
        '10 DIM X(3)\n20 CLEAR\n30 DIM X(4)\n40 DIM X(5)\n50 PRINT "no"\n60 SYSTEM\n',
        'Duplicate Definition in 40'),
    "duplicate_dim_after_use": (
        '80 DIM Q(3):Q(2)=1\n90 CLEAR\n100 PRINT Q(2)\n110 DIM Q(5)\n120 SYSTEM\n',
        ' 0 \nDuplicate Definition in 110'),
    "duplicate_dim_after_erase": (
        '10 DIM X(3)\n20 ERASE X\n30 DIM X(4)\n40 DIM X(5)\n50 PRINT "no"\n60 SYSTEM\n',
        'Duplicate Definition in 40'),
    # CLEAR inside a FOR loop ends the loop: the NEXT has no FOR (measured)
    "for_ended_by_clear": (
        '10 FOR I=1 TO 3\n20 PRINT I\n30 CLEAR\n40 NEXT\n50 PRINT "end";I\n',
        ' 1 \nNEXT without FOR in 40'),
    # the second variable of SWAP must exist already (measured on the binary)
    "swap_unused_variable": (
        '5 ON ERROR GOTO 200\n10 SWAP Y,Y2:PRINT Y;Y2\n20 Y3=1:SWAP Y3,Y4:PRINT Y3;Y4\n'
        '30 SWAP Y5,Y3:PRINT Y5;Y3\n60 SWAP S$,T$:PRINT "x";S$;T$\n'
        '70 SWAP Y9,Y9:PRINT "same"\n100 SWAP A(1),B(1):PRINT "arr"\n'
        '110 SWAP Q%,R%\n120 SYSTEM\n200 PRINT ERR;ERL:RESUME NEXT\n',
        ' 5  10 \n 0  0 \n 5  20 \n 1  0 \n 1  0 \n 5  60 \nx\nsame\narr\n 5  110 \n'),
    # an integer loop variable rounds the limit (measured)
    "for_integer_limit_rounded": (
        '10 FOR F%=1 TO 2.6:PRINT F%;:NEXT:PRINT\n20 FOR F%=1 TO 2.4:PRINT F%;:NEXT:PRINT\n'
        '30 FOR F%=1 TO 2.5:PRINT F%;:NEXT:PRINT\n40 FOR F%=1 TO -0.6 STEP -1:PRINT F%;:NEXT:PRINT\n'
        '50 DEFINT G:FOR G=1 TO 2.6:PRINT G;:NEXT:PRINT\n60 FOR F=1 TO 2.6:PRINT F;:NEXT:PRINT\n'
        '70 SYSTEM\n',
        ' 1  2  3 \n 1  2 \n 1  2  3 \n 1  0 -1 \n 1  2  3 \n 1  2 \n'),
}


def run_cli(directory, source, stdin="RUN\nSYSTEM\n"):
    (directory / "e.bas").write_text(source)
    result = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(directory / "e.bas"), "--ui", "cli"],
        input=stdin, cwd=directory, capture_output=True, text=True, timeout=60)
    return result.stdout.replace("\r", ""), result.stderr


@pytest.mark.parametrize("name", sorted(CASES))
def test_interpreter(tmp_path, name):
    source, expected = CASES[name]
    out, err = run_cli(tmp_path, source)
    assert "Traceback" not in err, err
    assert expected in out, out


def test_deftype_at_the_ok_prompt_does_not_reach_run(tmp_path):
    # Measured: DEFINT A typed at Ok, then RUN of a program with no DEFtype: A is
    # single (RUN puts every letter back). PRINT A afterwards shows 1.5.
    out, err = run_cli(tmp_path, "10 A=1.5:PRINT A\n", "DEFINT A\nRUN\nSYSTEM\n")
    assert " 1.5 \n" in out and "Traceback" not in err, out + err


def test_deftype_of_the_program_reaches_the_ok_prompt(tmp_path):
    # Measured: after RUN of 10 DEFINT A:A=1.5:PRINT A the prompt shows PRINT A as
    # 2 (A% of the program) and PRINT A! as 0 (another variable)
    out, err = run_cli(tmp_path, "10 DEFINT A:A=1.5:PRINT A\n",
                       "RUN\nPRINT A\nPRINT A!\nSYSTEM\n")
    assert " 2 \nOk\n 2 \nOk\n 0 \nOk\n" in out and "Traceback" not in err, out + err


# JavaScript: CLEAR deletes the variables, as the interpreter does
JS_CASES = {
    "clear_everything": CASES["clear_everything"],
    "def_fn_before_def_and_clear": CASES["def_fn_before_def_and_clear"],
    "dim_again_after_clear": CASES["dim_again_after_clear"],
    "for_ended_by_clear": CASES["for_ended_by_clear"],
    "duplicate_dim_after_clear": CASES["duplicate_dim_after_clear"],
    "duplicate_dim_after_use": CASES["duplicate_dim_after_use"],
    "duplicate_dim_after_erase": CASES["duplicate_dim_after_erase"],
    "clear_before_dim": CASES["clear_before_dim"],
}


@pytest.mark.skipif(NODE is None, reason="node is needed to run the compiled JavaScript")
@pytest.mark.parametrize("name", sorted(JS_CASES))
def test_javascript(tmp_path, name):
    source, expected = JS_CASES[name]
    (tmp_path / "e.bas").write_text(source)
    compiled = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(tmp_path / "e.bas"),
         "--compile-js", str(tmp_path / "e.js")],
        cwd=tmp_path, capture_output=True, text=True, timeout=60)
    assert compiled.returncode == 0, compiled.stdout + compiled.stderr
    result = subprocess.run([NODE, str(tmp_path / "e.js")], cwd=tmp_path,
                            capture_output=True, text=True, timeout=60)
    assert expected in result.stdout.replace("\r", ""), result.stdout + result.stderr


# C: CLEAR sets the variables to 0 and "", deletes the arrays, sends the DATA pointer back
C_PROGRAM = (
    '10 A=5:B$="x":C%=7\n20 DIM M(3,3),N$(4)\n30 M(1,1)=9:N$(2)="q"\n'
    '40 READ Q:PRINT "Q";Q\n50 GOSUB 200\n60 PRINT "back"\n70 CLEAR\n'
    '80 PRINT A;B$;C%;M(1,1);N$(2)\n90 READ Q:PRINT "Q";Q\n100 ERASE M\n'
    '110 DIM M(5):M(4)=3:PRINT M(4)\n120 SYSTEM\n200 PRINT "sub":RETURN\n500 DATA 11,22\n')
C_EXPECTED = 'Q 11 \nsub\nback\n 0  0  0 \nQ 11 \n 3 \n'


def test_c_dim_again_after_clear(tmp_path):
    from test_c_backend import toolchain_missing, compile_c, run_compiled
    why = toolchain_missing()
    if why:
        pytest.skip(why)
    compiled = compile_c(tmp_path, CASES["dim_again_after_clear"][0])
    assert compiled.returncode == 0, compiled.stdout + compiled.stderr
    assert run_compiled(tmp_path, "") == CASES["dim_again_after_clear"][1]


@pytest.mark.parametrize("name", ["clear_before_dim", "clear_then_dim_late",
                                  "duplicate_dim_after_clear", "duplicate_dim_after_use"])
def test_c_clear_edges(tmp_path, name):
    from test_c_backend import toolchain_missing, compile_c, run_compiled
    why = toolchain_missing()
    if why:
        pytest.skip(why)
    compiled = compile_c(tmp_path, CASES[name][0])
    assert compiled.returncode == 0, compiled.stdout + compiled.stderr
    assert CASES[name][1] in run_compiled(tmp_path, "")


def test_c_clear(tmp_path):
    from test_c_backend import toolchain_missing, compile_c, run_compiled, run_interpreted
    why = toolchain_missing()
    if why:
        pytest.skip(why)
    compiled = compile_c(tmp_path, C_PROGRAM)
    assert compiled.returncode == 0, compiled.stdout + compiled.stderr
    assert run_compiled(tmp_path, "") == C_EXPECTED
    assert run_interpreted(tmp_path, "") == C_EXPECTED


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
