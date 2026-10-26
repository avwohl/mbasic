"""The JavaScript backend checks 16-bit and byte arguments as MBASIC 5.21 does (issue 43), and
reports STOP, RETURN and the errors around a handler as the binary does (issue 41).

Every expected output was measured on MBASIC 5.21 (cpmemu): FRCINT rounds an integer argument
to 16 bits or says Overflow; CONINT adds a test for 0..255 and says Illegal function call. The
interpreter gives the same output for all of the range cases.
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

pytestmark = pytest.mark.skipif(NODE is None, reason="Node.js is needed to execute generated JavaScript")

# (program, output of the real binary after RUN)
RANGE_CASES = [
    ('10 PRINT "[";STRING$(300,"A");"]"\n',
     '[\nIllegal function call in 10\n'),
    ('10 PRINT "[";STRING$(2.7,65);"]"\n',
     '[AAA]\n'),
    ('10 PRINT "[";STRING$(3,300);"]"\n',
     '[\nIllegal function call in 10\n'),
    ('10 PRINT "[";STRING$(3,-1);"]"\n',
     '[\nIllegal function call in 10\n'),
    ('10 PRINT "[";STRING$(40000,"A");"]"\n',
     '[\nOverflow in 10\n'),
    ('10 PRINT "[";STRING$(3,"");"]"\n',
     '[\nIllegal function call in 10\n'),
    ('10 PRINT "[";STRING$(-1,"A");"]"\n',
     '[\nIllegal function call in 10\n'),
    ('10 PRINT "[";STRING$(3,65.7);"]"\n',
     '[BBB]\n'),
    ('10 PRINT "[";SPACE$(256);"]"\n',
     '[\nIllegal function call in 10\n'),
    ('10 PRINT "[";SPACE$(-1);"]"\n',
     '[\nIllegal function call in 10\n'),
    ('10 PRINT "[";SPACE$(2.5);"]"\n',
     '[   ]\n'),
    ('10 PRINT "[";SPACE$(40000);"]"\n',
     '[\nOverflow in 10\n'),
    ('10 PRINT "[";LEFT$("ABC",300);"]"\n',
     '[\nIllegal function call in 10\n'),
    ('10 PRINT "[";LEFT$("ABC",-1);"]"\n',
     '[\nIllegal function call in 10\n'),
    ('10 PRINT "[";LEFT$("ABC",2.5);"]"\n',
     '[ABC]\n'),
    ('10 PRINT "[";LEFT$("ABC",40000);"]"\n',
     '[\nOverflow in 10\n'),
    ('10 PRINT "[";RIGHT$("ABC",-1);"]"\n',
     '[\nIllegal function call in 10\n'),
    ('10 PRINT "[";RIGHT$("ABC",256);"]"\n',
     '[\nIllegal function call in 10\n'),
    ('10 PRINT "[";RIGHT$("ABC",1.5);"]"\n',
     '[BC]\n'),
    ('10 PRINT "[";MID$("ABC",0);"]"\n',
     '[\nIllegal function call in 10\n'),
    ('10 PRINT "[";MID$("ABC",2,300);"]"\n',
     '[\nIllegal function call in 10\n'),
    ('10 PRINT "[";MID$("ABC",256);"]"\n',
     '[\nIllegal function call in 10\n'),
    ('10 PRINT "[";MID$("ABC",2,-1);"]"\n',
     '[\nIllegal function call in 10\n'),
    ('10 PRINT "[";MID$("ABC",1.5);"]"\n',
     '[BC]\n'),
    ('10 PRINT "[";MID$("ABC",2,1.5);"]"\n',
     '[BC]\n'),
    ('10 PRINT "[";MID$("ABC",40000);"]"\n',
     '[\nOverflow in 10\n'),
    ('10 PRINT "[";CHR$(256);"]"\n',
     '[\nIllegal function call in 10\n'),
    ('10 PRINT "[";CHR$(-1);"]"\n',
     '[\nIllegal function call in 10\n'),
    ('10 PRINT "[";CHR$(65.5);"]"\n',
     '[B]\n'),
    ('10 PRINT "[";CHR$(40000);"]"\n',
     '[\nOverflow in 10\n'),
    ('10 PRINT "[";ASC(CHR$(66.5));"]"\n',
     '[ 67 ]\n'),
    ('10 PRINT "[";INSTR(0,"ABC","B");"]"\n',
     '[\nIllegal function call in 10\n'),
    ('10 PRINT "[";INSTR(256,"ABC","B");"]"\n',
     '[\nIllegal function call in 10\n'),
    ('10 PRINT "[";INSTR(2.5,"ABCB","B");"]"\n',
     '[ 4 ]\n'),
    ('10 PRINT "[";INSTR(-1,"ABC","B");"]"\n',
     '[\nIllegal function call in 10\n'),
    ('10 PRINT "[";INSTR(40000,"ABC","B");"]"\n',
     '[\nOverflow in 10\n'),
    ('10 X=PEEK(70000)\n20 PRINT "ok"\n',
     'Overflow in 10\n'),
    ('10 X=PEEK(-32769)\n20 PRINT "ok"\n',
     'Overflow in 10\n'),
    ('10 X=PEEK(65536)\n20 PRINT "ok"\n',
     'Overflow in 10\n'),
    ('10 PRINT "A";TAB(40000);"B"\n',
     'A\nOverflow in 10\n'),
    ('10 PRINT "A";TAB(3.7);"B"\n',
     'A  B\n'),
    ('10 PRINT "A";SPC(-1);"B"\n',
     'AB\n'),
    ('10 PRINT "A";SPC(40000);"B"\n',
     'A\nOverflow in 10\n'),
    ('10 PRINT "A";SPC(3.7);"B"\n',
     'A    B\n'),
    ('10 DIM A(10)\n20 PRINT A(-1)\n',
     'Illegal function call in 20\n'),
    ('10 DIM A(10)\n20 PRINT A(40000)\n',
     'Overflow in 20\n'),
    ('10 DIM A(10)\n20 A(1.5)=7:PRINT A(2)\n',
     ' 7 \n'),
    ('10 DIM A(10)\n20 A(-1)=7\n',
     'Illegal function call in 20\n'),
    ('10 DIM A(10)\n20 A(40000)=7\n',
     'Overflow in 20\n'),
    ('10 DIM A(10)\n20 A(11)=7\n',
     'Subscript out of range in 20\n'),
    ('10 DIM A(10)\n20 PRINT A(10.5)\n',
     'Subscript out of range in 20\n'),
    ('10 DIM B(40000)\n',
     'Overflow in 10\n'),
    ('10 DIM B(2.5)\n20 PRINT B(3)\n',
     ' 0 \n'),
    ('10 A(-1)=3\n',
     'Illegal function call in 10\n'),
    ('10 PRINT A(40000)\n',
     'Overflow in 10\n'),
    ('10 DIM A(3,3)\n20 PRINT A(1,-1)\n',
     'Illegal function call in 20\n'),
    ('10 DIM A(3,3)\n20 PRINT A(40000,1)\n',
     'Overflow in 20\n'),
    ('10 ON 256 GOTO 30,40\n20 PRINT "fall":END\n30 PRINT "t1":END\n40 PRINT "t2"\n',
     'Illegal function call in 10\n'),
    ('10 ON -1 GOTO 30,40\n20 PRINT "fall":END\n30 PRINT "t1":END\n40 PRINT "t2"\n',
     'Illegal function call in 10\n'),
    ('10 ON 40000 GOTO 30,40\n20 PRINT "fall":END\n30 PRINT "t1":END\n40 PRINT "t2"\n',
     'Overflow in 10\n'),
    ('10 ON 2.5 GOTO 30,40\n20 PRINT "fall":END\n30 PRINT "t1":END\n40 PRINT "t2"\n',
     'fall\n'),
    ('10 ON 1.5 GOTO 30,40\n20 PRINT "fall":END\n30 PRINT "t1":END\n40 PRINT "t2"\n',
     't2\n'),
    ('10 X=INP(256)\n20 PRINT "ok"\n',
     'Illegal function call in 10\n'),
    ('10 RANDOMIZE 40000\n20 PRINT "ok"\n',
     'Overflow in 10\n'),
    ('10 WIDTH 300\n20 PRINT "ok"\n',
     'Illegal function call in 10\n'),
    ('10 WIDTH 40000\n20 PRINT "ok"\n',
     'Overflow in 10\n'),
    ('10 POKE 100,256\n20 PRINT "ok"\n',
     'Illegal function call in 10\n'),
    ('10 POKE 100,-1\n20 PRINT "ok"\n',
     'Illegal function call in 10\n'),
    ('10 OUT 256,1\n20 PRINT "ok"\n',
     'Illegal function call in 10\n'),
    ('10 ERROR 256\n20 PRINT "ok"\n',
     'Illegal function call in 10\n'),
    ('10 ERROR 0\n20 PRINT "ok"\n',
     'Illegal function call in 10\n'),
    ('10 ERROR 5.6\n20 PRINT "ok"\n',
     'Overflow in 10\n'),
    ('10 A$="ABCDE":MID$(A$,2,3)="X":PRINT A$\n',
     'AXCDE\n'),
    ('10 A$="ABCDE":MID$(A$,2,2)="XYZ":PRINT A$\n',
     'AXYDE\n'),
    ('10 A$="ABCDE":MID$(A$,0,1)="X":PRINT A$\n',
     'Illegal function call in 10\n'),
    ('10 A$="ABCDE":MID$(A$,6,1)="X":PRINT A$\n',
     'Illegal function call in 10\n'),
    ('10 A$="ABCDE":MID$(A$,2,300)="X":PRINT A$\n',
     'Illegal function call in 10\n'),
    ('10 A$="ABCDE":MID$(A$,2,0)="X":PRINT A$\n',
     'ABCDE\n'),
    ('10 A$="ABCDE":MID$(A$,5,3)="XYZ":PRINT A$\n',
     'ABCDX\n'),
    ('10 A$="ABCDE":MID$(A$,6,0)="X":PRINT A$\n',
     'ABCDE\n'),
    ('10 A$="ABCDE":MID$(A$,1,2)="":PRINT A$\n',
     'ABCDE\n'),
    ('10 A$="ABCDE":MID$(A$,7,1)="":PRINT A$\n',
     'Illegal function call in 10\n'),
    ('10 A$="ABCDE":MID$(A$,2,1)=5:PRINT A$\n',
     'Type mismatch in 10\n'),
    ('10 A$="ABCDE":MID$(A$,40000,1)="X":PRINT A$\n',
     'Overflow in 10\n'),
    ('10 A$="ABCDE":MID$(A$,2.5,1.5)="XY":PRINT A$\n',
     'ABXYE\n'),
    ('10 DIM A$(2):A$(1)="ABCDE":MID$(A$(1),2,2)="XY":PRINT A$(1)\n',
     'AXYDE\n'),
]

# Measured on the binary: STOP names its line also inside a handler, and starts a new line when the
# cursor is not in column 0; a RETURN in a program with no GOSUB is an error; an error in a handler
# is reported with its own message and line; RESUME to a line that does not exist is error 8 at the
# RESUME, so a handler that is still armed catches it again and again.
HANDLER_CASES = [
    ("return without gosub", '10 PRINT "A"\n20 RETURN\n', "A\nRETURN without GOSUB in 20\n"),
    ("stop in a handler", "10 ON ERROR GOTO 100\n20 ERROR 11\n40 END\n100 STOP\n", "Break in 100\n"),
    ("stop after print", '10 PRINT "x";\n20 STOP\n', "x\nBreak in 20\n"),
    ("error in a handler", "10 ON ERROR GOTO 100\n20 X=5\n30 ERROR 11\n40 END\n100 PRINT ERR;ERL\n110 ERROR 9\n",
     " 11  30 \nSubscript out of range in 110\n"),
    ("resume to a missing line",
     "10 ON ERROR GOTO 100\n20 ERROR 11\n40 END\n100 N=N+1:PRINT ERR;ERL;N:IF N>4 THEN SYSTEM\n110 RESUME 55\n",
     " 11  20  1 \n 8  110  2 \n 8  110  3 \n 8  110  4 \n 8  110  5 \n"),
]

# Round 2, all measured on the binary and run on the interpreter and in JavaScript: READ and SWAP
# with array elements, OPTION BASE 1, the wrong number of subscripts, a second dimension above its
# own bound, RESUME with no error, ON ERROR GOTO 0 in a handler (the original line is reported),
# ERASE, INSTR with a start beyond the string, MID$ with the target as the value.
BOTH_CASES = [
    ("swap elements",
     "10 DIM A(2,3)\n80 A(1,1)=4:A(2,2)=8:SWAP A(1,1),A(2,2):PRINT A(1,1);A(2,2)\n110 ON ERROR GOTO 200\n"
     "120 SWAP A(1,1),A(5,5)\n130 SYSTEM\n200 PRINT ERR;ERL:SYSTEM\n",
     " 8  4 \n 9  120 \n"),
    ("read elements",
     "10 DIM A(2,3)\n30 DATA 1,2,3,4,5,6\n40 FOR I=1 TO 2:FOR J=1 TO 3:READ A(I,J):NEXT:NEXT\n"
     "50 PRINT A(2,3);A(1,1)\n60 DATA 9\n70 DIM B(3)\n80 READ B(4)\n",
     " 6  1 \nSubscript out of range in 80\n"),
    ("option base 1",
     "10 OPTION BASE 1\n20 DIM A(2,3)\n30 A(2,3)=5\n40 PRINT A(2,3)\n50 ON ERROR GOTO 100\n"
     "60 PRINT A(0,1)\n70 SYSTEM\n100 PRINT ERR;ERL:RESUME NEXT\n",
     " 5 \n 9  60 \n"),
    ("too many subscripts", "10 DIM A(3)\n20 PRINT A(1,1)\n", "Subscript out of range in 20\n"),
    ("too few subscripts", "10 DIM A(3,3)\n20 PRINT A(1)\n", "Subscript out of range in 20\n"),
    ("second dimension above its bound",
     "10 DIM A(5,5)\n20 A(2,3)=7\n30 PRINT A(2,3);A(3,2)\n40 A(2,6)=1\n",
     " 7  0 \nSubscript out of range in 40\n"),
    ("second dimension smaller than the first", "10 DIM A(3,2)\n20 PRINT A(2,3)\n",
     "Subscript out of range in 20\n"),
    ("resume without error", "10 RESUME\n", "RESUME without error in 10\n"),
    ("resume in a handler that falls off the end", '10 ON ERROR GOTO 100\n20 RESUME\n100 PRINT "q"\n',
     "q\nNo RESUME in 100\n"),
    ("on error goto 0 in a handler",
     "10 ON ERROR GOTO 100\n20 X=1/0\n30 END\n100 PRINT ERR;ERL\n110 ON ERROR GOTO 0\n120 X=1/0\n",
     " 11  20 \nDivision by zero in 20\n"),
    ("erase empties the array", "10 DIM A(3)\n20 A(1)=1\n30 ERASE A\n40 PRINT A(1)\n", " 0 \n"),
    ("instr start beyond the string",
     '10 PRINT INSTR(3,"abc","");INSTR(4,"abc","");INSTR(1,"","");INSTR(2,"","");INSTR("","");'
     'INSTR(4,"abc","c");INSTR("abc","")\n',
     " 3  0  0  0  0  0  1 \n"),
    ("mid assignment from itself", '10 A$="hello"\n20 MID$(A$,2,3)=A$\n30 PRINT A$\n40 B$="abcdef"\n'
     '50 MID$(B$,2,3)=B$\n60 PRINT B$\n', "hhhho\naaaaef\n"),
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
    return subprocess.run([NODE, str(output)], capture_output=True, text=True, timeout=10).stdout


def run_interpreter(tmp_path, source):
    basic = tmp_path / "prog.bas"
    basic.write_text(source)
    result = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(basic), "--ui", "cli"],
        input="RUN\nSYSTEM\n", cwd=tmp_path, capture_output=True, text=True, timeout=30)
    text = result.stdout.replace("\r", "")
    return text.split("\nOk\n", 1)[1].split("\nOk\n")[0].replace("Goodbye", "").rstrip("\n") + "\n"


@pytest.mark.parametrize("source,expected", RANGE_CASES, ids=[c[0].replace("\n", " / ")[:60] for c in RANGE_CASES])
def test_range_checks(tmp_path, source, expected):
    assert run_js(tmp_path, source) == expected


@pytest.mark.parametrize("name,source,expected", HANDLER_CASES, ids=[c[0] for c in HANDLER_CASES])
def test_handler_cases_js(tmp_path, name, source, expected):
    assert run_js(tmp_path, source) == expected


@pytest.mark.parametrize("name,source,expected", HANDLER_CASES, ids=[c[0] for c in HANDLER_CASES])
def test_handler_cases_interpreter(tmp_path, name, source, expected):
    assert run_interpreter(tmp_path, source) == expected


@pytest.mark.parametrize("name,source,expected", BOTH_CASES, ids=[c[0] for c in BOTH_CASES])
def test_round2_cases_js(tmp_path, name, source, expected):
    assert run_js(tmp_path, source) == expected


@pytest.mark.parametrize("name,source,expected", BOTH_CASES, ids=[c[0] for c in BOTH_CASES])
def test_round2_cases_interpreter(tmp_path, name, source, expected):
    assert run_interpreter(tmp_path, source) == expected


def test_compiled_arrays_keep_each_subscript(tmp_path):
    # A two-dimensional array is indexed per dimension, also when it is not DIMed (measured: 5 7 0 / x)
    source = ('10 DIM A(3,3)\n20 A(1,2)=5:A(2,1)=7:PRINT A(1,2);A(2,1);A(0,0)\n'
              '30 DIM B$(2,2):B$(1,1)="x":PRINT B$(1,1);B$(2,2)\n40 C(1,2)=4:PRINT C(1,2)\n')
    assert run_js(tmp_path, source) == " 5  7  0 \nx\n 4 \n"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
