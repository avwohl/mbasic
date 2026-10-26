"""OPEN modes and lengths, integer FOR loops, DEF FN result types, PRINT INPUT$, LOF, FIELD views.

Every expected output is what MBASIC 5.21 printed after RUN (cpmemu, default 3 files). The programs
run in the JavaScript backend and, where the interpreter agrees with the binary, in the interpreter.

OPEN: the mode is read first (a number is Type mismatch, an empty or unknown mode is Bad file mode,
M$ may hold the mode and only its first letter counts), then the file number, then LEN, then the name
(a number is Type mismatch, an empty name is Bad file name). An I or O file takes no length: the
file is opened and the statement ends with Syntax error. FOR with an integer variable takes the start,
the limit and the step through FRCINT (Overflow over 32767 at the FOR). A DEF FN result takes the
type of the function. LOF is the size at OPEN in sectors of 128 bytes. A FIELD variable that was
given another string is no longer in the record.
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
    ('for_integer',
     '10 ON ERROR GOTO 900\n20 PRINT "A":FOR I%=1 TO 2.5:PRINT "a";I%;:NEXT:PRINT\n30 PRINT "B":FOR I%=1.5 TO 3.4999999:PRINT "d";I%;:NEXT:PRINT\n40 PRINT "C":FOR I%=1 TO 40000:PRINT "c";I%;:NEXT:PRINT\n50 PRINT "D":FOR I%=1 TO 3 STEP 40000:PRINT "in";I%;:NEXT:PRINT\n60 PRINT "E":FOR I%=1 TO 3 STEP .5:PRINT "e";I%;:NEXT:PRINT\n65 PRINT "E2":FOR I%=1 TO 3 STEP -.5:PRINT "e";I%;:NEXT:PRINT\n70 PRINT "F":FOR I%=40000 TO 1:PRINT "f";I%;:NEXT:PRINT\n80 PRINT "G":FOR I%=1 TO 3 STEP 1.5:PRINT "g";I%;:NEXT:PRINT\n90 PRINT "H":FOR I%=3 TO 1 STEP -1.5:PRINT "h";I%;:NEXT:PRINT\n95 PRINT "I":FOR I%=32765 TO 32767:PRINT "i";I%;:NEXT:PRINT\n96 PRINT "J":FOR I%=-1.5 TO -4.6:PRINT "j";I%;:NEXT:PRINT\n97 PRINT "K":FOR I%=1 TO -2.5 STEP -1:PRINT "k";I%;:NEXT:PRINT\n98 PRINT "L":DEFINT J:FOR J=1 TO 2.5:PRINT "l";J;:NEXT:PRINT\n99 SYSTEM\n900 PRINT "E";ERR;ERL:RESUME NEXT\n',
     'A\na 1 a 2 a 3 \nB\nd 2 d 3 d 4 \nC\nE 6  40 \nc 5 E 1  40 \n\nD\nE 6  50 \nin 5 E 1  50 \n\nE\ne 1 e 2 e 3 \nE2\n\nF\nE 6  70 \nf 1 E 1  70 \n\nG\ng 1 g 3 \nH\nh 3 h 1 \nI\ni 32765 i 32766 i 32767 E 6  95 \n\nJ\n\nK\nk 1 k 0 k-1 k-2 k-3 \nL\nl 1 l 2 l 3 \n',
     True),
    ('def_fn_type',
     '10 ON ERROR GOTO 900\n20 DEF FNA%(X)=X:PRINT FNA%(2.5);FNA%(2.4);FNA%(-2.5)\n30 PRINT FNA%(40000)\n40 DEF FND%(A%,B)=A%+B:PRINT FND%(2.5,2.5)\n50 DEFSTR S:DEF FNR(S)=S+"x":PRINT FNR("a")\n60 DEF FNS(X)="a":PRINT FNS(1)\n70 DEF FNT$(X)=X:PRINT FNT$(1)\n80 DEF FNU$(X)=STR$(X)+"z":PRINT FNU$(1)\n90 DEFINT K:DEF FNK(X)=X*1.5:PRINT FNK(3)\n100 DEF FNL#(X)=X/3:PRINT FNL#(1)\n110 DEF FNM!(X#)=X#/3:PRINT FNM!(1)\n120 DEF FNN%(X)=X/3:PRINT FNN%(10)\n125 DEF FNP(X)=X*1.5:PRINT FNP(3)\n130 PRINT FNA%("a")\n140 DEF FNQ%=2.5:PRINT FNQ%\n150 SYSTEM\n900 PRINT "E";ERR;ERL:RESUME NEXT\n',
     ' 3  2 -3 \nE 6  30 \n 6 \nE 13  50 \na\nE 13  70 \n 1z\n 5 \n .3333333432674408 \n .333333 \n 3 \n 4.5 \nE 13  130 \n 3 \n',
     True),
    ('open_modes',
     '5 OPEN "O",1,"ZA.DAT":PRINT #1,"hello":CLOSE 1\n10 ON ERROR GOTO 900\n30 PRINT 30:OPEN 5,1,"ZA.DAT":CLOSE\n31 PRINT 31:OPEN "",1,"ZA.DAT":CLOSE\n32 PRINT 32:OPEN "X",1,"ZA.DAT":CLOSE\n33 PRINT 33:OPEN 5,99,"":CLOSE\n34 PRINT 34:OPEN "Q",99,"":CLOSE\n35 PRINT 35:OPEN "Q",1,"":CLOSE\n36 PRINT 36:OPEN "I",99,"":CLOSE\n37 PRINT 37:OPEN "I",1,5:CLOSE\n38 PRINT 38:OPEN "Q",1,5:CLOSE\n39 PRINT 39:OPEN "I","a","ZA.DAT":CLOSE\n40 PRINT 40:OPEN "Q","a","ZA.DAT":CLOSE\n41 PRINT 41:OPEN "Q",1,"ZNONE.DAT":CLOSE\n42 PRINT 42:OPEN 5,"a",5:CLOSE\n43 PRINT 43:OPEN "I",1,"":CLOSE\n44 PRINT 44:OPEN "I",99,"ZNONE.DAT":CLOSE\n45 PRINT 45:OPEN "Q",1,"ZA.DAT",300:CLOSE\n46 PRINT 46:OPEN "R",1,"ZA.DAT","a":CLOSE\n47 PRINT 47:OPEN "I",1,"ZA.DAT",5:CLOSE\n48 PRINT 48:M$="O":OPEN M$,1,"ZB.DAT":PRINT #1,"zz":CLOSE 1\n49 PRINT 49:M$="i"+"x":OPEN M$,1,"ZA.DAT":LINE INPUT #1,A$:PRINT A$:CLOSE 1\n50 PRINT 50:OPEN "Input",1,"ZA.DAT":LINE INPUT #1,A$:PRINT A$:CLOSE 1\n51 PRINT 51:OPEN "R",1,"ZA.DAT",300:CLOSE\n52 PRINT 52:OPEN "R",1,"ZA.DAT",0:CLOSE\n55 SYSTEM\n900 PRINT "E";ERR;ERL:RESUME NEXT\n',
     ' 30 \nE 13  30 \n 31 \nE 54  31 \n 32 \nE 54  32 \n 33 \nE 13  33 \n 34 \nE 54  34 \n 35 \nE 54  35 \n 36 \nE 52  36 \n 37 \nE 13  37 \n 38 \nE 54  38 \n 39 \nE 13  39 \n 40 \nE 54  40 \n 41 \nE 54  41 \n 42 \nE 13  42 \n 43 \nE 64  43 \n 44 \nE 52  44 \n 45 \nE 54  45 \n 46 \nE 13  46 \n 47 \nE 2  47 \n 48 \n 49 \nhello\n 50 \nhello\n 51 \nE 5  51 \n 52 \n',
     True),
    ('open_length',
     '5 OPEN "O",1,"ZA.DAT":PRINT #1,"hello":CLOSE 1\n10 ON ERROR GOTO 900\n30 PRINT 30:OPEN "I",1,"ZNONE.DAT",5:CLOSE\n31 PRINT 31:OPEN "I",1,"ZA.DAT",5:PRINT EOF(1):CLOSE\n32 PRINT 32:OPEN "O",1,"ZB.DAT",5:PRINT LOF(1):CLOSE\n33 PRINT 33:OPEN "I",99,"ZA.DAT",5:CLOSE\n34 PRINT 34:OPEN "I",1,"ZA.DAT",300:CLOSE\n35 PRINT 35:OPEN "I",1,"ZA.DAT":OPEN "I",1,"ZA.DAT",5:CLOSE\n36 PRINT 36:OPEN "I",1,"ZA.DAT","a":CLOSE\n55 SYSTEM\n900 PRINT "E";ERR;ERL:RESUME NEXT\n',
     ' 30 \nE 53  30 \n 31 \nE 2  31 \n 0 \n 32 \nE 2  32 \n 0 \n 33 \nE 52  33 \n 34 \nE 2  34 \n 35 \nE 55  35 \n 36 \nE 2  36 \n',
     True),
    ('lof',
     '10 OPEN "R",1,"ZF.DAT",16:FIELD 1,16 AS A$\n20 PRINT LOF(1)\n30 FOR I=1 TO 9:LSET A$="x":PUT 1,I:PRINT LOF(1);:NEXT:PRINT\n40 CLOSE:OPEN "R",1,"ZF.DAT",16:PRINT LOF(1):CLOSE\n50 OPEN "R",1,"ZF.DAT":FIELD 1,128 AS B$:FOR I=1 TO 3:LSET B$="y":PUT 1,I:PRINT LOF(1);:NEXT:PRINT\n60 CLOSE:OPEN "O",1,"ZF.DAT":PRINT #1,"abc":PRINT LOF(1):CLOSE\n70 OPEN "I",1,"ZF.DAT":PRINT LOF(1):CLOSE\n80 KILL "ZF.DAT":SYSTEM\n',
     ' 0 \n 0  0  0  0  0  0  0  0  0 \n 2 \n 2  2  2 \n 0 \n 1 \n',
     True),
    ('print_input_dollar',
     '10 OPEN "O",1,"ZA.DAT":PRINT #1,"abc":CLOSE 1\n20 OPEN "I",1,"ZA.DAT"\n30 PRINT INPUT$(2,#1)\n40 PRINT "x";INPUT$(1,#1);"y"\n50 CLOSE\n60 SYSTEM\n',
     'ab\nxcy\n',
     True),
    ('next_runtime_errors',
     '10 ON ERROR GOTO 900\n20 PRINT "a":NEXT I:PRINT "b"\n30 PRINT "c":NEXT:PRINT "d"\n40 PRINT "e":FOR I=1 TO 2:FOR J=1 TO 2:NEXT J,I:PRINT "f";I;J\n50 PRINT "g":FOR I=1 TO 2:NEXT I,I:PRINT "h"\n60 PRINT "i":WHILE 0:WEND:NEXT K:PRINT "j"\n70 SYSTEM\n900 PRINT "E";ERR;ERL:RESUME NEXT\n',
     'a\nE 1  20 \nb\nc\nE 1  30 \nd\ne\nf 3  3 \ng\nE 1  50 \nh\ni\nE 1  60 \nj\n',
     True),
    ('field_views',
     '10 ON ERROR GOTO 900\n20 OPEN "R",1,"ZF.DAT",16\n30 FIELD 1, 4 AS A$, 4 AS B$\n40 FIELD 1, 8 AS C$, 8 AS D$\n50 LSET A$="ab":RSET B$="cd"\n60 PRINT "[";A$;"][";B$;"][";C$;"]"\n70 PUT 1,1\n80 LSET A$="zzzzzzzzzz":PRINT "[";A$;"]"\n90 GET 1,1:PRINT "[";A$;"][";B$;"][";C$;"]"\n100 A$="plain":PRINT LEN(A$):LSET A$="x":PRINT "[";A$;"]":GET 1,1:PRINT "[";A$;"]"\n110 LSET E$="abc":PRINT "[";E$;"]"\n120 E$="abcdef":LSET E$="xy":PRINT "[";E$;"]":RSET E$="xy":PRINT "[";E$;"]"\n130 MID$(C$,1,2)="QQ":PRINT "[";C$;"]"\n140 PUT 1,2:GET 1,2:PRINT "[";A$;"]"\n150 CLOSE:OPEN "R",1,"ZF.DAT",16:FIELD 1,4 AS A$:GET 1,1:PRINT "[";A$;"]":GET 1,2:PRINT "[";A$;"]"\n160 PRINT LOF(1);LOC(1);EOF(1)\n170 CLOSE:KILL "ZF.DAT"\n180 PRINT "end"\n190 SYSTEM\n900 PRINT "E";ERR;ERL:RESUME NEXT\n',
     '[ab  ][  cd][ab    cd]\n[zzzz]\n[ab  ][  cd][ab    cd]\n 5 \n[x    ]\n[x    ]\n[]\n[xy    ]\n[    xy]\n[QQ    cd]\n[x    ]\n[ab  ]\n[QQ  ]\n 1  2  0 \nend\n',
     True),
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
@pytest.mark.parametrize("name,source,expected,both", PROGRAMS, ids=[p[0] for p in PROGRAMS])
def test_program_js(tmp_path, name, source, expected, both):
    assert run_js(tmp_path, source) == expected


@pytest.mark.parametrize("name,source,expected,both", [p for p in PROGRAMS if p[3]], ids=[p[0] for p in PROGRAMS if p[3]])
def test_program_interpreter(tmp_path, name, source, expected, both):
    assert run_interpreter(tmp_path, source) == expected


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
