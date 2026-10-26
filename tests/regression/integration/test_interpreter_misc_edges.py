"""Interpreter edges from issue 61: built-in arity, WIDTH n,device, CLEAR, A=ELSE.

Every expected text below was measured on MBASIC 5.21 (com/mbasic.com under
cpmemu, tests/HOW_TO_RUN_REAL_MBASIC.md). The binary:

- reads the arguments of a built-in while the call runs, so a wrong number of
  them is a Syntax error (2) when the line runs, trappable by ON ERROR. The
  arguments up to the first one it cannot use are evaluated first:
  LEFT$(CVI("A")) is Illegal function call (5), LEFT$(A$,1,CVI("A")) is
  Syntax error. RND() and INKEY$() with empty brackets are Syntax error too;
- sets the width for WIDTH 40,1 and then gives Syntax error (WIDTH 30, too);
- forgets ON ERROR GOTO at a CLEAR that succeeds, ends a running handler (the
  RESUME after it is "RESUME without error"), keeps ERR and ERL, empties the
  GOSUB and FOR stacks, goes back to the first DATA item, forgets DEF FN and
  allows OPTION BASE again. A CLEAR that fails (CLEAR ,1) changes nothing;
- A=ELSE is Missing operand (22), and RESUME NEXT then goes on at the NEXT
  LINE: the rest of the line, including ':' parts and an ELSE branch, is skipped.
  A=: and A=1+: are also 22 but RESUME NEXT goes on behind the ':'.

Not covered, and different here: DEFINT and the other DEF types are fixed when the
program is parsed, so CLEAR does not reset them (the binary does).
"""
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: interpreter misc edge tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

ROOT = Path(__file__).resolve().parents[3]
NODE = shutil.which("node")

HANDLER = '900 PRINT "L";ERL;"E";ERR:RESUME NEXT\n'

# statement -> ERR measured on the binary (the handler prints L<line> E<err>)
ARITY = [
    ('A=ABS(1,2)', 2), ('A=POS(1,2)', 2), ('A=USR()', 2), ('A=LPOS(1,2)', 2),
    ('B$=LEFT$(A$)', 2), ('B$=MID$(A$)', 2), ('A=INSTR(1)', 2),
    ('B$=STRING$(5)', 2), ('A=RND()', 2), ('B$=INKEY$()', 2),
    ('A=ABS(1,)', 2), ('A=ASC(A$,1)', 2), ('B$=INPUT$(1,2,3)', 2),
    ('A=EOF(1,2)', 2), ('A=VARPTR(A,1)', 2), ('PRINT TAB(1,2)', 2),
    ('B$=LEFT$(CVI("A"))', 5), ('B$=LEFT$(A$,CVI("A"),2)', 5),
    ('B$=LEFT$(A$,1,CVI("A"))', 2), ('A=INSTR(CVI("A"))', 5),
]
# The JavaScript run-time has no CVI error for "A" (a string of one byte), so
# the cases where the first argument must fail are left out there.
ARITY_JS = [case for case in ARITY if case[1] == 2]
ARITY_SOURCE = ('10 ON ERROR GOTO 900\n20 A$="X"\n'
                + ''.join(f'{100 + 10 * n} {stmt}\n' for n, (stmt, _) in enumerate(ARITY))
                + '800 PRINT "end":END\n' + HANDLER)
ARITY_EXPECTED = ''.join(f'L {100 + 10 * n} E {err} \n' for n, (_, err) in enumerate(ARITY)) + 'end\n'

ARITY_JS_SOURCE = ('10 ON ERROR GOTO 900\n20 A$="X"\n'
                   + ''.join(f'{100 + 10 * n} {stmt}\n' for n, (stmt, _) in enumerate(ARITY_JS))
                   + '800 PRINT "end":END\n' + HANDLER)
ARITY_JS_EXPECTED = ''.join(f'L {100 + 10 * n} E 2 \n' for n in range(len(ARITY_JS))) + 'end\n'

RULER = "A234567890B234567890C234567890D234567890E234567890"
# name: (program, expected text after RUN)
CASES = {
    "builtin_arity": (ARITY_SOURCE, ARITY_EXPECTED),
    "builtin_arity_js": (ARITY_JS_SOURCE, ARITY_JS_EXPECTED),
    # WIDTH 40,1 and WIDTH 30, set the width, then are Syntax error (2)
    "width_device": (
        '10 ON ERROR GOTO 900\n20 WIDTH 40,1\n30 PRINT "' + RULER + '"\n'
        '40 WIDTH 80\n50 WIDTH 30,\n60 PRINT "' + RULER + '"\n'
        '70 WIDTH 80:WIDTH 20,$\n80 PRINT "' + RULER + '"\n'
        '90 WIDTH 300,1\n100 WIDTH "A",1\n110 END\n' + HANDLER,
        'L 20 E 2 \n' + RULER[:40] + '\n' + RULER[40:] + '\n'
        'L 50 E 2 \n' + RULER[:30] + '\n' + RULER[30:] + '\n'
        'L 70 E 2 \n' + RULER[:20] + '\n' + RULER[20:40] + '\n' + RULER[40:] + '\n'
        'L 90 E 5 \nL 100 E 13 \n'),
    # CLEAR forgets the handler: the second error is fatal. ERR and ERL stay.
    "clear_forgets_handler": (
        '10 ON ERROR GOTO 900\n20 ERROR 5\n30 PRINT "back"\n40 CLEAR\n'
        '50 PRINT "cleared";ERR;ERL\n60 ERROR 6\n70 PRINT "not reached"\n80 END\n'
        '900 PRINT "H";ERR;ERL\n910 RESUME NEXT\n',
        'H 5  20 \nback\ncleared 0  20 \nOverflow in 60\n'),
    # CLEAR: variables, DEF FN (18), DATA pointer, FOR stack (NEXT without FOR, 1),
    # OPTION BASE (allowed again, the base is 0) and GOSUB stack (RETURN without GOSUB, 3)
    "clear_state": (
        '10 OPTION BASE 1\n20 DEF FNA(X)=X*2\n30 DATA 1,2,3\n40 READ A\n50 FOR K=1 TO 2\n'
        '60 CLEAR\n70 ON ERROR GOTO 900\n80 PRINT "A";A\n90 PRINT FNA(2)\n'
        '100 READ B:PRINT "B";B\n110 NEXT K\n120 OPTION BASE 0\n'
        '130 DIM Q(1):PRINT "ok":Q(0)=1\n140 GOSUB 200\n150 END\n200 CLEAR\n'
        '210 ON ERROR GOTO 900\n220 RETURN\n230 END\n900 PRINT "H";ERR;ERL:RESUME NEXT\n',
        'A 0 \nH 18  90 \nB 1 \nH 1  110 \nok\nH 3  220 \n'),
    # CLEAR inside a handler ends the handler: RESUME is RESUME without error
    "clear_in_handler": (
        '10 ON ERROR GOTO 900\n20 ERROR 5\n30 PRINT "after handler"\n60 END\n'
        '900 PRINT "H";ERR;ERL\n910 CLEAR\n920 PRINT "cleared";ERR;ERL\n930 RESUME NEXT\n',
        'H 5  20 \ncleared 5  20 \nRESUME without error in 930\n'),
    # a CLEAR that fails (Out of memory) keeps the handler
    "clear_failing_keeps_handler": (
        '10 ON ERROR GOTO 900\n20 CLEAR ,1\n30 PRINT "after bad clear"\n40 ERROR 5\n'
        '50 PRINT "handler still on"\n60 END\n900 PRINT "H";ERR;ERL\n910 RESUME NEXT\n',
        'H 7  20 \nafter bad clear\nH 5  40 \nhandler still on\n'),
    # A=ELSE: RESUME NEXT goes on at the next line
    "else_operand": (
        '10 ON ERROR GOTO 900\n20 A=ELSE:PRINT "same line"\n30 PRINT "next"\n'
        '40 IF 1 THEN A=ELSE\n50 PRINT "after if"\n60 A=ELSE PRINT "x"\n70 PRINT "n70"\n'
        '80 IF 1 THEN A=ELSE PRINT "e80" ELSE PRINT "e80b"\n90 PRINT "n90"\n'
        '100 IF 0 THEN PRINT "t" ELSE A=ELSE:PRINT "same100"\n110 PRINT "n110"\n'
        '120 A=1+ELSE:PRINT "same120"\n130 PRINT "n130"\n'
        '140 PRINT 1+ELSE:PRINT "same140"\n150 PRINT "n150"\n160 END\n' + HANDLER,
        'L 20 E 22 \nnext\nL 40 E 22 \nafter if\nL 60 E 22 \nn70\nL 80 E 22 \nn90\n'
        'L 100 E 22 \nn110\nL 120 E 22 \nn130\nL 140 E 22 \nn150\n'),
    # an argument of the wrong type is Type mismatch (13) before the count is
    # Syntax error (2); single-argument built-ins and too few arguments are 2
    "arity_types": (
        '10 ON ERROR GOTO 900\n20 A$=LEFT$(1,2,3)\n70 A$=LEFT$("A","B",1)\n100 X=INSTR(1,2,3,4)\n110 A$=STRING$("A")\n120 A$=STRING$("A","B","C")\n130 X=ABS("x",1)\n140 A$=LEFT$(1)\n150 A$=INPUT$("A",2,3)\n160 A$=STRING$(1,2,3)\n170 A$=RIGHT$("A",1,"x")\n800 PRINT "end":END\n900 PRINT "L";ERL;"E";ERR:RESUME NEXT\n',
        'L 20 E 13 \nL 70 E 13 \nL 100 E 13 \nL 110 E 13 \nL 120 E 13 \nL 130 E 2 \nL 140 E 2 \nL 150 E 13 \nL 160 E 2 \nL 170 E 2 \nend\n'),
    # WIDTH n,x outside an IF takes the rest of the line, ELSE part included
    "width_else": (
        '20 ON ERROR GOTO 900\n50 WIDTH 80:WIDTH 50,1 ELSE PRINT "e"\n'
        '60 PRINT STRING$(60,"c")\n70 WIDTH 80:WIDTH 50,1:PRINT "colon"\n'
        '80 PRINT "n80"\n90 IF 0 THEN WIDTH 20,1 ELSE PRINT "else ran"\n95 WIDTH 80\n'
        '96 SYSTEM\n' + HANDLER,
        'L 50 E 2 \n' + 'c' * 50 + '\n' + 'c' * 10 + '\nL 70 E 2 \ncolon\nn80\nelse ran\n'),
    # CLEAR with no argument ends at ELSE: the CLEAR runs and the handler goes
    "clear_else": (
        '10 ON ERROR GOTO 100\n60 IF 1 THEN CLEAR ELSE PRINT "no"\n65 PRINT "after if"\n70 X=1/0\n80 SYSTEM\n100 PRINT "H";ERR;ERL:RESUME NEXT\n',
        'after if\nDivision by zero\n'),
    # CLEAR with bad arguments fails (6, 7, 5) and keeps the handler
    "clear_bad_arguments": (
        '10 ON ERROR GOTO 100\n20 CLEAR 1000000\n30 PRINT "a"\n40 CLEAR ,200\n50 PRINT "b"\n60 CLEAR ,,5\n70 PRINT "c"\n80 CLEAR 0,0\n85 PRINT "d"\n90 X=1/0\n95 PRINT "after"\n99 SYSTEM\n100 PRINT "H";ERR;ERL:RESUME NEXT\n',
        'H 6  20 \na\nH 7  40 \nb\nH 7  60 \nc\nH 5  80 \nd\nH 11  90 \nafter\n'),
    # INSTR: the error depends on the types as well as the count (all 30
    # combinations of 1 and "A", one to four arguments, measured on 5.21)
    "instr_shapes": (
        '10 ON ERROR GOTO 900\n15 E=0\n20 X=INSTR(1)\n21 PRINT 20;E:E=0\n22 X=INSTR("A")\n23 PRINT 22;E:E=0\n24 X=INSTR(1,1)\n25 PRINT 24;E:E=0\n26 X=INSTR(1,"A")\n27 PRINT 26;E:E=0\n28 X=INSTR("A",1)\n29 PRINT 28;E:E=0\n30 X=INSTR("A","A")\n31 PRINT 30;E:E=0\n32 X=INSTR(1,1,1)\n33 PRINT 32;E:E=0\n34 X=INSTR(1,1,"A")\n35 PRINT 34;E:E=0\n36 X=INSTR(1,"A",1)\n37 PRINT 36;E:E=0\n38 X=INSTR(1,"A","A")\n39 PRINT 38;E:E=0\n40 X=INSTR("A",1,1)\n41 PRINT 40;E:E=0\n42 X=INSTR("A",1,"A")\n43 PRINT 42;E:E=0\n44 X=INSTR("A","A",1)\n45 PRINT 44;E:E=0\n46 X=INSTR("A","A","A")\n47 PRINT 46;E:E=0\n48 X=INSTR(1,1,1,1)\n49 PRINT 48;E:E=0\n50 X=INSTR(1,1,1,"A")\n51 PRINT 50;E:E=0\n52 X=INSTR(1,1,"A",1)\n53 PRINT 52;E:E=0\n54 X=INSTR(1,1,"A","A")\n55 PRINT 54;E:E=0\n56 X=INSTR(1,"A",1,1)\n57 PRINT 56;E:E=0\n58 X=INSTR(1,"A",1,"A")\n59 PRINT 58;E:E=0\n60 X=INSTR(1,"A","A",1)\n61 PRINT 60;E:E=0\n62 X=INSTR(1,"A","A","A")\n63 PRINT 62;E:E=0\n64 X=INSTR("A",1,1,1)\n65 PRINT 64;E:E=0\n66 X=INSTR("A",1,1,"A")\n67 PRINT 66;E:E=0\n68 X=INSTR("A",1,"A",1)\n69 PRINT 68;E:E=0\n70 X=INSTR("A",1,"A","A")\n71 PRINT 70;E:E=0\n72 X=INSTR("A","A",1,1)\n73 PRINT 72;E:E=0\n74 X=INSTR("A","A",1,"A")\n75 PRINT 74;E:E=0\n76 X=INSTR("A","A","A",1)\n77 PRINT 76;E:E=0\n78 X=INSTR("A","A","A","A")\n79 PRINT 78;E:E=0\n890 SYSTEM\n900 E=ERR:RESUME NEXT\n',
        ' 20  2 \n 22  2 \n 24  13 \n 26  2 \n 28  13 \n 30  0 \n 32  13 \n 34  13 \n 36  13 \n 38  0 \n 40  2 \n 42  2 \n 44  2 \n 46  2 \n 48  13 \n 50  13 \n 52  13 \n 54  13 \n 56  2 \n 58  2 \n 60  2 \n 62  2 \n 64  2 \n 66  2 \n 68  2 \n 70  2 \n 72  2 \n 74  2 \n 76  2 \n 78  2 \n'),
    # RESUME NEXT after an error in a THEN clause goes on with the next ':'
    # statement of the clause; in the first statement of an ELSE clause it goes
    # on at the next line (measured on 5.21)
    "clause_resume_next": (
        '10 ON ERROR GOTO 100\n20 IF 0 THEN PRINT "t" ELSE PRINT "e1":X=1/0:PRINT "s2"\n25 IF 0 THEN PRINT "t" ELSE X=1/0:PRINT "s3":PRINT "s4"\n30 IF 1 THEN PRINT "a":X=1/0:PRINT "s5" ELSE PRINT "b"\n32 IF 1 THEN X=1/0\n34 PRINT "x":IF 1 THEN X=1/0:PRINT "s6"\n40 PRINT "next"\n50 SYSTEM\n100 PRINT ERR;ERL:RESUME NEXT\n',
        'e1\n 11  20 \ns2\n 11  25 \na\n 11  30 \ns5\n 11  32 \nx\n 11  34 \ns6\nnext\n'),
    # WIDTH n,x in a clause ends only the WIDTH statement; in an ELSE clause it
    # also takes a second ELSE (measured on 5.21)
    "width_clause": (
        '10 ON ERROR GOTO 100\n20 IF 1 THEN WIDTH 40,1:PRINT "same"\n30 IF 0 THEN PRINT "t" ELSE WIDTH 40,1 ELSE PRINT "e"\n35 PRINT "n35"\n40 IF 0 THEN PRINT "t" ELSE PRINT "x":WIDTH 40,1:PRINT "tail"\n50 WIDTH 80:SYSTEM\n100 PRINT ERR;ERL:RESUME NEXT\n',
        ' 2  20 \nsame\n 2  30 \nn35\nx\n 2  40 \ntail\n'),
}


def run_cli(directory, source):
    (directory / "e.bas").write_text(source)
    result = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(directory / "e.bas"), "--ui", "cli"],
        input="RUN\nSYSTEM\n", cwd=directory, capture_output=True, text=True, timeout=60)
    return result.stdout.replace("\r", "")


@pytest.mark.parametrize("name", sorted(CASES))
def test_interpreter(tmp_path, name):
    source, expected = CASES[name]
    out = run_cli(tmp_path, source)
    assert expected in out, out
    assert "Traceback" not in out, out


# the JavaScript compiler: arity (this branch), the Missing operand rule, and
# the handler part of CLEAR. WIDTH 40,1 is a Syntax error there too.
JS_CASES = ["builtin_arity_js", "width_device", "clear_forgets_handler", "else_operand",
            "arity_types", "clear_bad_arguments", "instr_shapes"]


@pytest.mark.skipif(NODE is None, reason="Node.js is needed to execute generated JavaScript")
@pytest.mark.parametrize("name", JS_CASES)
def test_javascript(tmp_path, name):
    source, expected = CASES[name]
    (tmp_path / "e.bas").write_text(source)
    compiled = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), "--compile-js", str(tmp_path / "e.js"),
         str(tmp_path / "e.bas")],
        cwd=tmp_path, capture_output=True, text=True, timeout=60)
    assert compiled.returncode == 0, compiled.stdout + compiled.stderr
    result = subprocess.run([NODE, str(tmp_path / "e.js")], cwd=tmp_path,
                            capture_output=True, text=True, timeout=60)
    assert expected in result.stdout, result.stdout + result.stderr


def test_c_backend_refuses_wrong_arity(tmp_path):
    """--compile-c has no run-time errors to give, so it stops at compile time."""
    (tmp_path / "e.bas").write_text("10 A=ABS(1,2)\n20 PRINT A\n")
    result = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), "--compile-c", str(tmp_path / "e.c"),
         str(tmp_path / "e.bas")],
        cwd=tmp_path, capture_output=True, text=True, timeout=60)
    assert result.returncode != 0
    assert "ABS requires 1 argument" in result.stdout + result.stderr
    assert not (tmp_path / "e.c").exists()


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
