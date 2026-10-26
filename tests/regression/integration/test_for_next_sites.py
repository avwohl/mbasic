"""FOR and NEXT sites, loops spoilt by an error, DEF FN types at the call, FIELD with a reserved word.

Every expected output is what MBASIC 5.21 printed after RUN (cpmemu, default 3 files). Each program
runs in the interpreter and in the JavaScript backend.

The scan a FOR makes for its NEXT (NXTSCN) counts FORs and names on NEXTs. The loop is valid only
at the NEXT (and the name in its list) the scan ended at. Any other NEXT that finds the loop by its
name, or a NEXT with no name that finds it on top, is NEXT without FOR, and the entry on the stack is
spoilt: the next NEXT does not find it, nor any loop below it (the loops entered later stay). An error
in the step of NEXT (Overflow of an integer variable) spoils the entry the same way. A NEXT whose
name has no loop changes nothing. A NEXT that finds a loop takes the loops entered after it off the
stack. A subroutine sees its own loops, not the loops of the caller, and RETURN drops the loops it
opened. A DEF FN is its name and its type (FNA$ is not FNA: Undefined user function), and a
parameter without a suffix has the type the DEF types give when the call runs. FIELD NAME$ is a
Syntax error (NAME is a reserved word) and binds nothing.
"""
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: JavaScript execution tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

ROOT = Path(__file__).resolve().parents[3]
NODE = shutil.which("node")

PROGRAMS = [
    ('overflow_spoils_loop',
     '10 ON ERROR GOTO 900\n20 FOR I%=32767 TO 32767:NEXT:PRINT "after"\n25 NEXT:PRINT "x"\n85 SYSTEM\n900 PRINT "E";ERR;ERL:RESUME NEXT\n',
     'E 6  20 \nafter\nE 1  25 \nx\n'),
    ('failed_for_then_bare_next',
     '10 ON ERROR GOTO 900\n20 FOR I=1 TO 3:FOR J=1 TO 1/0:NEXT:PRINT "p";I:NEXT I:PRINT "y"\n50 FOR I=1 TO 2:FOR J="a" TO 2:PRINT "j":NEXT:PRINT "k";I:NEXT:PRINT "z"\n85 SYSTEM\n900 PRINT "E";ERR;ERL:RESUME NEXT\n',
     'E 11  20 \nE 1  20 \np 1 \nE 1  20 \ny\nE 13  50 \nj\nE 1  50 \nk 1 \nE 1  50 \nz\n'),
    ('named_next_keeps_outer_loop',
     '10 ON ERROR GOTO 900\n20 FOR I=1 TO 3:FOR J=1 TO 1/0:NEXT:PRINT "p";I:NEXT I:PRINT "y"\n30 PRINT "--"\n40 FOR I=1 TO 2:FOR J=1 TO 1/0:NEXT J:PRINT "p";I:NEXT I:PRINT "y"\n85 SYSTEM\n900 PRINT "E";ERR;ERL:RESUME NEXT\n',
     'E 11  20 \nE 1  20 \np 1 \nE 1  20 \ny\n--\nE 11  40 \nE 1  40 \np 1 \nE 11  40 \nE 1  40 \np 2 \ny\n'),
    ('nesting_and_missing_next',
     '10 ON ERROR GOTO 900\n20 FOR I=1 TO 2:FOR J=1 TO 2:NEXT:PRINT "p";I:NEXT I:PRINT "y"\n30 PRINT "--"\n40 FOR I=1 TO 2:X=1/0:NEXT:PRINT "p";I:NEXT I:PRINT "y"\n50 PRINT "--"\n60 FOR I=1 TO 2:FOR J=1 TO 1/0:NEXT J:PRINT "p";I:NEXT:PRINT "y"\n70 PRINT "--"\n80 FOR I=1 TO 2:FOR J=1 TO 1/0:PRINT "q":NEXT I:PRINT "y"\n85 SYSTEM\n900 PRINT "E";ERR;ERL:RESUME NEXT\n',
     'p 1 \np 2 \ny\n--\nE 11  40 \nE 11  40 \np 3 \nE 1  40 \ny\n--\nE 11  60 \nE 1  60 \np 1 \nE 11  60 \nE 1  60 \np 2 \ny\n--\nE 26  80 \nE 11  80 \nq\nE 1  80 \ny\n'),
    ('loops_and_subroutines',
     '10 ON ERROR GOTO 900\n20 FOR I=1 TO 3\n30 GOSUB 100\n40 NEXT I\n50 PRINT "done";I\n60 PRINT "--"\n70 FOR J=1 TO 2:GOSUB 300:NEXT:PRINT "ok";J\n95 SYSTEM\n100 PRINT "sub";I\n110 NEXT I\n120 RETURN\n300 FOR K=1 TO 5:IF K=2 THEN RETURN\n310 NEXT K:RETURN\n900 PRINT "E";ERR;ERL:RESUME NEXT\n',
     'sub 1 \nE 1  110 \nsub 2 \nE 1  110 \nsub 3 \nE 1  110 \ndone 4 \n--\nok 3 \n'),
    ('def_fn_name_is_name_and_type',
     '10 ON ERROR GOTO 900\n20 DEF FNA$(X)="a":PRINT FNA(1)\n30 DEF FNB%(X)=X*2:PRINT FNB(1.6)\n40 DEF FNC(X)=X*2:PRINT FNC%(1.6)\n50 DEF FND(X)=X*2:PRINT FND!(1.6)\n70 DEFINT G:DEF FNG(X)=X*2:PRINT FNG(1.6):PRINT FNG%(1.6)\n80 DEFSTR H:DEF FNH(X)="q":PRINT FNH(1)\n85 SYSTEM\n900 PRINT "E";ERR;ERL:RESUME NEXT\n',
     'E 18  20 \nE 18  30 \nE 18  40 \n 3.2 \n 3 \n 3 \nq\n'),
    ('def_fn_parameter_type_at_call',
     '10 ON ERROR GOTO 900\n20 DEF FNA(X)=X*2:DEFINT X:PRINT FNA(1.6)\n30 DEF FNB(X)=X*2:PRINT X;:DEFINT X:PRINT FNB(1.6);X\n40 DEFSNG X:DEF FNC(X)=X*2:DEFINT X:X=2.7:PRINT FNC(1.6);X\n50 DEFINT X:DEF FND(X)=X*2:DEFSNG X:PRINT FND(1.6)\n85 SYSTEM\n900 PRINT "E";ERR;ERL:RESUME NEXT\n',
     ' 4 \n 0  4  0 \n 4  3 \n 3.2 \n'),
    ('field_reserved_word',
     '10 ON ERROR GOTO 900\n20 OPEN "R",1,"ZN.DAT",20\n40 FIELD 1, 20 AS NAME$, 5 AS B$\n50 PRINT "ok"\n60 CLOSE:KILL "ZN.DAT":SYSTEM\n900 PRINT "E";ERR;ERL:RESUME NEXT\n',
     'E 2  40 \nok\n'),
]


def compile_js(tmp_path, source):
    basic = tmp_path / "prog.bas"
    basic.write_text(source)
    output = tmp_path / "prog.js"
    result = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(basic), "--compile-js", str(output)],
        cwd=ROOT, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return output


def run_js(tmp_path, source):
    output = compile_js(tmp_path, source)
    result = subprocess.run([NODE, str(output)], cwd=tmp_path, capture_output=True, text=True, timeout=20)
    return result.stdout.rstrip("\n") + "\n"


def run_interpreter(tmp_path, source):
    basic = tmp_path / "prog.bas"
    basic.write_text(source)
    result = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(basic), "--ui", "cli"],
        input="RUN\nSYSTEM\n", cwd=tmp_path, capture_output=True, text=True, timeout=30)
    text = result.stdout.replace("\r", "")
    return text.split("\nOk\n", 1)[1].split("\nOk\n")[0].replace("Goodbye", "").rstrip("\n") + "\n"


@pytest.mark.skipif(NODE is None, reason="Node.js is needed to execute generated JavaScript")
@pytest.mark.parametrize("name,source,expected", PROGRAMS, ids=[p[0] for p in PROGRAMS])
def test_program_js(tmp_path, name, source, expected):
    assert run_js(tmp_path, source) == expected


@pytest.mark.parametrize("name,source,expected", PROGRAMS, ids=[p[0] for p in PROGRAMS])
def test_program_interpreter(tmp_path, name, source, expected):
    assert run_interpreter(tmp_path, source) == expected


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
