"""MID$(A$,n)=X$, CLEAR, USR, DEF USR, LPOS and WIDTH 0 (issue 43), measured on MBASIC 5.21.

MID$(A$,2)=X$ with no length replaces as much as fits. CLEAR, USR and the
others take their arguments as the binary does: CLEAR checks them (and a
successful CLEAR forgets ON ERROR, so the program arms it again); USR[n](x)
evaluates x and then stops with Illegal function call, with or without a DEF
USR (there is no machine code to run); DEF USR[n]=a takes -32768 to 65535;
LPOS(x) takes any argument and is 1 (no printer); WIDTH 0 and WIDTH LPRINT n
take a byte. WIDTH 0 wraps before the first character of a line, and TAB and
SPC divide by the width: Division by zero.
"""
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: MID$/CLEAR/USR/LPOS/WIDTH 0 tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

ROOT = Path(__file__).resolve().parents[3]
NODE = shutil.which("node")

# Measured: each statement on its own line, an ok line after it that prints
# only when no error came (F), the handler on line 900.
STATEMENTS = '1 ON ERROR GOTO 900\n10 A$="HELLO":MID$(A$,2)="XY":PRINT A$\n11 ON ERROR GOTO 900:IF F=0 THEN PRINT 10;"ok" ELSE F=0\n20 A$="HELLO":MID$(A$,2)="XYZABCD":PRINT A$\n21 ON ERROR GOTO 900:IF F=0 THEN PRINT 20;"ok" ELSE F=0\n30 A$="HELLO":MID$(A$,2)=""\n31 ON ERROR GOTO 900:IF F=0 THEN PRINT 30;"ok" ELSE F=0\n40 A$="HELLO":MID$(A$,0)="X"\n41 ON ERROR GOTO 900:IF F=0 THEN PRINT 40;"ok" ELSE F=0\n50 A$="HELLO":MID$(A$,6)="X"\n51 ON ERROR GOTO 900:IF F=0 THEN PRINT 50;"ok" ELSE F=0\n60 A$="HELLO":MID$(A$,2)=5\n61 ON ERROR GOTO 900:IF F=0 THEN PRINT 60;"ok" ELSE F=0\n70 A$="HELLO":MID$(A$,40000)="X"\n71 ON ERROR GOTO 900:IF F=0 THEN PRINT 70;"ok" ELSE F=0\n80 CLEAR 32768\n81 ON ERROR GOTO 900:IF F=0 THEN PRINT 80;"ok" ELSE F=0\n90 CLEAR -1\n91 ON ERROR GOTO 900:IF F=0 THEN PRINT 90;"ok" ELSE F=0\n100 CLEAR 70000\n101 ON ERROR GOTO 900:IF F=0 THEN PRINT 100;"ok" ELSE F=0\n110 CLEAR ,70000\n111 ON ERROR GOTO 900:IF F=0 THEN PRINT 110;"ok" ELSE F=0\n120 CLEAR ,-1\n121 ON ERROR GOTO 900:IF F=0 THEN PRINT 120;"ok" ELSE F=0\n130 CLEAR 0,0\n131 ON ERROR GOTO 900:IF F=0 THEN PRINT 130;"ok" ELSE F=0\n140 CLEAR "A"\n141 ON ERROR GOTO 900:IF F=0 THEN PRINT 140;"ok" ELSE F=0\n150 CLEAR 1.5\n151 ON ERROR GOTO 900:IF F=0 THEN PRINT 150;"ok" ELSE F=0\n160 X=USR(70000)\n161 ON ERROR GOTO 900:IF F=0 THEN PRINT 160;"ok" ELSE F=0\n170 X=USR("A")\n171 ON ERROR GOTO 900:IF F=0 THEN PRINT 170;"ok" ELSE F=0\n180 X=USR5(5)\n181 ON ERROR GOTO 900:IF F=0 THEN PRINT 180;"ok" ELSE F=0\n190 DEF USR=40000\n191 ON ERROR GOTO 900:IF F=0 THEN PRINT 190;"ok" ELSE F=0\n200 DEF USR9=-32768\n201 ON ERROR GOTO 900:IF F=0 THEN PRINT 200;"ok" ELSE F=0\n210 DEF USR=65536\n211 ON ERROR GOTO 900:IF F=0 THEN PRINT 210;"ok" ELSE F=0\n220 DEF USR3="A"\n221 ON ERROR GOTO 900:IF F=0 THEN PRINT 220;"ok" ELSE F=0\n230 DEF USR10=1\n231 ON ERROR GOTO 900:IF F=0 THEN PRINT 230;"ok" ELSE F=0\n240 PRINT LPOS(0);LPOS(1E30);LPOS("A")\n241 ON ERROR GOTO 900:IF F=0 THEN PRINT 240;"ok" ELSE F=0\n250 X=LPOS(300)+LPOS(-1)\n251 ON ERROR GOTO 900:IF F=0 THEN PRINT 250;"ok" ELSE F=0\n260 WIDTH 255\n261 ON ERROR GOTO 900:IF F=0 THEN PRINT 260;"ok" ELSE F=0\n270 WIDTH 256\n271 ON ERROR GOTO 900:IF F=0 THEN PRINT 270;"ok" ELSE F=0\n280 WIDTH 70000\n281 ON ERROR GOTO 900:IF F=0 THEN PRINT 280;"ok" ELSE F=0\n290 WIDTH LPRINT 0\n291 ON ERROR GOTO 900:IF F=0 THEN PRINT 290;"ok" ELSE F=0\n300 WIDTH LPRINT 256\n301 ON ERROR GOTO 900:IF F=0 THEN PRINT 300;"ok" ELSE F=0\n310 WIDTH LPRINT "A"\n311 ON ERROR GOTO 900:IF F=0 THEN PRINT 310;"ok" ELSE F=0\n320 WIDTH LPRINT 40\n321 ON ERROR GOTO 900:IF F=0 THEN PRINT 320;"ok" ELSE F=0\n330 PRINT "end"\n340 SYSTEM\n900 PRINT ERL;"E";ERR:F=1:RESUME NEXT\n'

# Output of the real binary for STATEMENTS.
STATEMENTS_EXPECTED = 'HXYLO\n 10 ok\nHXYZA\n 20 ok\n 30 ok\n 40 E 5 \n 50 E 5 \n 60 E 13 \n 70 E 6 \n 80 E 6 \n 90 E 5 \n 100 E 6 \n 110 E 6 \n 120 ok\n 130 E 5 \n 140 E 13 \n 150 ok\n 160 E 5 \n 170 E 5 \n 180 E 5 \n 190 ok\n 200 ok\n 210 E 6 \n 220 E 13 \n 230 E 2 \n 1  1  1 \n 240 ok\n 250 ok\n 260 ok\n 270 E 5 \n 280 E 6 \n 290 ok\n 300 E 5 \n 310 E 13 \n 320 ok\nend\n'

# Measured on the binary: a name that starts with the reserved word USR is a
# Syntax error (USRX, USR1X, USR10), DEF USR 4=100 with a space is fine, a
# missing right-hand side is Missing operand (22) at the end of a statement
# and before ':' or ELSE but a Syntax error before ',' or ')', MID$ of a
# number is Type mismatch, and MID$(A$,n)=A$ copies byte by byte inside the
# one string (HEHEH) where a copy of A$ (LEFT$, another variable) does not.
FORMS = '1 ON ERROR GOTO 900\n10 USR0=5\n11 ON ERROR GOTO 900:IF F=0 THEN PRINT 10;"ok" ELSE F=0\n20 USRX=5:PRINT USRX\n21 ON ERROR GOTO 900:IF F=0 THEN PRINT 20;"ok" ELSE F=0\n30 USR1X=5\n31 ON ERROR GOTO 900:IF F=0 THEN PRINT 30;"ok" ELSE F=0\n40 USR10=3\n41 ON ERROR GOTO 900:IF F=0 THEN PRINT 40;"ok" ELSE F=0\n50 DEF USR 4=100\n51 ON ERROR GOTO 900:IF F=0 THEN PRINT 50;"ok" ELSE F=0\n60 DEF USR9=5\n61 ON ERROR GOTO 900:IF F=0 THEN PRINT 60;"ok" ELSE F=0\n70 DEF USR=\n71 ON ERROR GOTO 900:IF F=0 THEN PRINT 70;"ok" ELSE F=0\n80 WIDTH LPRINT\n81 ON ERROR GOTO 900:IF F=0 THEN PRINT 80;"ok" ELSE F=0\n90 A$="HELLO":MID$(A$,2)=\n91 ON ERROR GOTO 900:IF F=0 THEN PRINT 90;"ok" ELSE F=0\n100 A=\n101 ON ERROR GOTO 900:IF F=0 THEN PRINT 100;"ok" ELSE F=0\n110 PRINT 1+:PRINT 2\n111 ON ERROR GOTO 900:IF F=0 THEN PRINT 110;"ok" ELSE F=0\n120 PRINT 1+)\n121 ON ERROR GOTO 900:IF F=0 THEN PRINT 120;"ok" ELSE F=0\n130 A=,\n131 ON ERROR GOTO 900:IF F=0 THEN PRINT 130;"ok" ELSE F=0\n140 A$="HELLO":MID$(A,2)="X"\n141 ON ERROR GOTO 900:IF F=0 THEN PRINT 140;"ok" ELSE F=0\n150 A$="HELLO":MID$(A$,3)=A$:PRINT A$\n151 ON ERROR GOTO 900:IF F=0 THEN PRINT 150;"ok" ELSE F=0\n160 A$="HELLO":MID$(A$,2,3)=A$:PRINT A$\n161 ON ERROR GOTO 900:IF F=0 THEN PRINT 160;"ok" ELSE F=0\n170 A$="HELLO":MID$(A$,3)=(A$):PRINT A$\n171 ON ERROR GOTO 900:IF F=0 THEN PRINT 170;"ok" ELSE F=0\n180 A$="HELLO":MID$(A$,3)=LEFT$(A$,5):PRINT A$\n181 ON ERROR GOTO 900:IF F=0 THEN PRINT 180;"ok" ELSE F=0\n190 DIM B$(2):B$(1)="HELLO":MID$(B$(1),3)=B$(1):PRINT B$(1)\n191 ON ERROR GOTO 900:IF F=0 THEN PRINT 190;"ok" ELSE F=0\n200 B$(1)="HELLO":B$(2)=B$(1):MID$(B$(1),3)=B$(2):PRINT B$(1);B$(2)\n201 ON ERROR GOTO 900:IF F=0 THEN PRINT 200;"ok" ELSE F=0\n210 PRINT "end"\n220 SYSTEM\n900 PRINT ERL;"E";ERR:F=1:RESUME NEXT\n'

FORMS_EXPECTED = ' 10 E 2 \n 20 E 2 \n 20 E 2 \n 30 E 2 \n 40 E 2 \n 50 ok\n 60 ok\n 70 E 22 \n 80 E 22 \n 90 E 22 \n 100 E 22 \n 110 E 22 \n 2 \n 120 E 2 \n 130 E 2 \n 140 E 13 \nHEHEH\n 150 ok\nHHHHO\n 160 ok\nHEHEH\n 170 ok\nHEHEL\n 180 ok\nHEHEH\n 190 ok\nHEHELHELLO\n 200 ok\nend\n'


# Measured: WIDTH 0 prints a line break before the first character of a line
# and never wraps again; TAB and SPC are Division by zero (error 11).
WIDTH0 = '5 ON ERROR GOTO 100\n10 WIDTH 0\n20 PRINT "ab";TAB(5);"c";\n30 PRINT "d";SPC(3);"e";POS(0)\n40 PRINT "k";TAB(1);"z"\n50 PRINT\n60 PRINT "q";:PRINT\n70 PRINT "wxyz"\n75 PRINT 1,2;POS(0)\n80 WIDTH 0.4:PRINT "A";POS(0)\n85 WIDTH 255:PRINT "B"\n90 WIDTH 80\n95 PRINT "end"\n99 SYSTEM\n100 PRINT "ERR";ERR;ERL:RESUME NEXT\n'

WIDTH0_EXPECTED = '\nab\n\nERR\n\n 11 \n\n 20 \n\nd\n\nERR\n\n 11 \n\n 30 \n\nk\n\nERR\n\n 11 \n\n 40 \n\n\nq\n\nwxyz\n\n 1            \n\n 2 \n\n 4 \n\nA\n\n 2 \nB\nend\n'

MID_PROGRAM = '''10 A$="HELLO":MID$(A$,2)="XY":PRINT A$
20 A$="HELLO":MID$(A$,2)="XYZABCD":PRINT A$
30 DIM B$(2):B$(1)="ABCDEF":MID$(B$(1),3)="12":PRINT B$(1)
40 MID$(A$,5)="Q":PRINT A$
50 SYSTEM
'''
MID_EXPECTED = "HXYLO\nHXYZA\nAB12EF\nHXYZQ\n"


def run_cli(directory, source, commands="RUN\nSYSTEM\n"):
    (directory / "w.bas").write_text(source)
    return subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(directory / "w.bas"), "--ui", "cli"],
        input=commands, cwd=directory, capture_output=True, text=True, timeout=60)


def test_statement_arguments(tmp_path):
    result = run_cli(tmp_path, STATEMENTS)
    assert STATEMENTS_EXPECTED in result.stdout, result.stdout + result.stderr


def test_width_zero(tmp_path):
    result = run_cli(tmp_path, WIDTH0)
    assert WIDTH0_EXPECTED in result.stdout, result.stdout + result.stderr


def test_mid_statement_without_length(tmp_path):
    result = run_cli(tmp_path, MID_PROGRAM)
    assert MID_EXPECTED in result.stdout, result.stdout + result.stderr


def test_forms_after_syntax_edge_cases(tmp_path):
    result = run_cli(tmp_path, FORMS)
    assert FORMS_EXPECTED in result.stdout, result.stdout + result.stderr


def test_load_list_renum_keep_the_forms(tmp_path):
    # The forms must survive LIST and RENUM and still run afterwards. (The
    # loader keeps a line it cannot parse as text, so LIST alone would not
    # show a parser that rejects the forms; running the lines does.)
    result = run_cli(
        tmp_path,
        '10 A$="HELLO":MID$(A$,2)="X":PRINT A$\n20 DEF USR3=100\n30 DEF USR 4=5\n'
        '40 PRINT LPOS(0)\n50 WIDTH LPRINT 40\n60 SYSTEM\n',
        "LIST\nRENUM 100\nLIST\nRUN\nSYSTEM\n")
    assert "Syntax error" not in result.stdout, result.stdout
    for text in ('10 A$="HELLO":MID$(A$,2)="X":PRINT A$', "20 DEF USR3=100",
                 "30 DEF USR 4=5", "40 PRINT LPOS(0)", "50 WIDTH LPRINT 40",
                 '100 A$="HELLO":MID$(A$,2)="X":PRINT A$', "130 PRINT LPOS(0)"):
        assert text in result.stdout, (text, result.stdout)
    assert "HXLLO\n 1 \n" in result.stdout, result.stdout


@pytest.mark.skipif(NODE is None, reason="node not installed")
def test_js_mid_statement_without_length(tmp_path):
    (tmp_path / "m.bas").write_text(MID_PROGRAM)
    out = tmp_path / "m.js"
    done = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(tmp_path / "m.bas"), "--compile-js", str(out)],
        capture_output=True, text=True, timeout=60)
    assert out.exists(), done.stdout + done.stderr
    run = subprocess.run([NODE, str(out)], capture_output=True, text=True, timeout=10)
    assert run.stdout == MID_EXPECTED, run.stdout + run.stderr


@pytest.mark.skipif(NODE is None, reason="node not installed")
def test_js_lpos(tmp_path):
    (tmp_path / "l.bas").write_text('10 PRINT LPOS(0);LPOS("A")\n20 SYSTEM\n')
    out = tmp_path / "l.js"
    subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(tmp_path / "l.bas"), "--compile-js", str(out)],
        capture_output=True, text=True, timeout=60)
    run = subprocess.run([NODE, str(out)], capture_output=True, text=True, timeout=10)
    assert run.stdout == " 1  1 \n", run.stdout + run.stderr   # real 5.21: LPOS(x) is 1 with no printer


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
