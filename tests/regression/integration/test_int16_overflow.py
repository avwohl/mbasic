"""FRCINT and CONINT argument checks (issue 43), measured on MBASIC 5.21.

An integer argument is rounded to the nearest integer and must fit -32768..32767, or
the binary stops with Overflow. A byte argument (LEFT$, SPACE$, CHR$, STRING$ and so on) is then
tested against 0..255, which is Illegal function call. An array subscript or DIM bound that is
negative is Illegal function call. PEEK and POKE take an address of -32768..65535.
Each case is one program line. The program prints "<n>|" first, then the statement
runs, and ON ERROR GOTO prints "ERR <code> ERL <line>" on the same line. The expected
text is what real MBASIC 5.21 printed for the same program (cpmemu, tests/HOW_TO_RUN_REAL_MBASIC.md).
Error 6 is Overflow, 5 is Illegal function call, 9 is Subscript out of range, 13 is Type mismatch.
"""
import re
import subprocess
import sys
from pathlib import Path

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: int16 overflow tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

ROOT = Path(__file__).resolve().parents[3]

PRELUDE = ["DIM A(100)", "DIM M(2,2)", "ON ERROR GOTO 60000"]
HANDLER = 'PRINT "ERR";ERR;"ERL";ERL:RESUME NEXT'

# (statement, output on real MBASIC 5.21)
CASES = [
    ('PRINT A(40000)', 'ERR 6 ERL 100'),
    ('PRINT A(32768)', 'ERR 6 ERL 110'),
    ('PRINT A(32767)', 'ERR 9 ERL 120'),
    ('PRINT A(-32768)', 'ERR 5 ERL 130'),
    ('PRINT A(-32769)', 'ERR 6 ERL 140'),
    ('PRINT A(32767.4)', 'ERR 9 ERL 150'),
    ('PRINT A(32767.5)', 'ERR 6 ERL 160'),
    ('PRINT A(-32768.5)', 'ERR 6 ERL 170'),
    ('PRINT A(-1)', 'ERR 5 ERL 180'),
    ('PRINT M(1,40000)', 'ERR 6 ERL 190'),
    ('PRINT M(40000,1)', 'ERR 6 ERL 200'),
    ('A(40000)=1', 'ERR 6 ERL 210'),
    ('A(-1)=1', 'ERR 5 ERL 220'),
    ('A(-32769)=1', 'ERR 6 ERL 230'),
    ('DIM B(1E38)', 'ERR 6 ERL 240'),
    ('DIM C(40000)', 'ERR 6 ERL 250'),
    ('DIM D(-1)', 'ERR 5 ERL 260'),
    ('DIM E(-32769)', 'ERR 6 ERL 270'),
    ('PRINT "A";TAB(1E38);"B"', 'AERR 6 ERL 280'),
    ('PRINT "A";TAB(32768);"B"', 'AERR 6 ERL 290'),
    ('PRINT "A";TAB(32767.5);"B"', 'AERR 6 ERL 300'),
    ('PRINT "A";TAB(-32769);"B"', 'AERR 6 ERL 310'),
    ('PRINT "A";SPC(1E38);"B"', 'AERR 6 ERL 320'),
    ('PRINT "A";SPC(32768);"B"', 'AERR 6 ERL 330'),
    ('PRINT "A";SPC(-32769);"B"', 'AERR 6 ERL 340'),
    ('PRINT LEN(STRING$(40000,65))', 'ERR 6 ERL 350'),
    ('PRINT LEN(STRING$(32768,65))', 'ERR 6 ERL 360'),
    ('PRINT LEN(STRING$(-32769,65))', 'ERR 6 ERL 370'),
    ('PRINT LEN(STRING$(-1,65))', 'ERR 5 ERL 380'),
    ('PRINT LEN(STRING$(256,65))', 'ERR 5 ERL 390'),
    ('PRINT LEN(STRING$(255,65))', ' 255'),
    ('PRINT LEN(STRING$(3,40000))', 'ERR 6 ERL 410'),
    ('PRINT LEN(STRING$(3,-32769))', 'ERR 6 ERL 420'),
    ('PRINT LEN(STRING$(3,256))', 'ERR 5 ERL 430'),
    ('PRINT LEN(STRING$(3,-1))', 'ERR 5 ERL 440'),
    ('PRINT LEN(STRING$(3,""))', 'ERR 5 ERL 450'),
    ('PRINT LEFT$("AB",1E38)', 'ERR 6 ERL 460'),
    ('PRINT LEFT$("AB",32768)', 'ERR 6 ERL 470'),
    ('PRINT LEFT$("AB",32767.5)', 'ERR 6 ERL 480'),
    ('PRINT LEFT$("AB",-32769)', 'ERR 6 ERL 490'),
    ('PRINT LEFT$("AB",-32768)', 'ERR 5 ERL 500'),
    ('PRINT LEFT$("AB",256)', 'ERR 5 ERL 510'),
    ('PRINT LEFT$("AB",-1)', 'ERR 5 ERL 520'),
    ('PRINT LEFT$("AB",255)', 'AB'),
    ('PRINT RIGHT$("AB",1E38)', 'ERR 6 ERL 540'),
    ('PRINT RIGHT$("AB",32768)', 'ERR 6 ERL 550'),
    ('PRINT RIGHT$("AB",-32769)', 'ERR 6 ERL 560'),
    ('PRINT RIGHT$("AB",256)', 'ERR 5 ERL 570'),
    ('PRINT RIGHT$("AB",-1)', 'ERR 5 ERL 580'),
    ('PRINT MID$("ABC",1E38)', 'ERR 6 ERL 590'),
    ('PRINT MID$("ABC",32768)', 'ERR 6 ERL 600'),
    ('PRINT MID$("ABC",-32769)', 'ERR 6 ERL 610'),
    ('PRINT MID$("ABC",0)', 'ERR 5 ERL 620'),
    ('PRINT MID$("ABC",256)', 'ERR 5 ERL 630'),
    ('PRINT MID$("ABC",1,40000)', 'ERR 6 ERL 640'),
    ('PRINT MID$("ABC",1,32768)', 'ERR 6 ERL 650'),
    ('PRINT MID$("ABC",1,-32769)', 'ERR 6 ERL 660'),
    ('PRINT MID$("ABC",1,-1)', 'ERR 5 ERL 670'),
    ('PRINT MID$("ABC",1,256)', 'ERR 5 ERL 680'),
    ('PRINT LEN(SPACE$(40000))', 'ERR 6 ERL 690'),
    ('PRINT LEN(SPACE$(32768))', 'ERR 6 ERL 700'),
    ('PRINT LEN(SPACE$(-32769))', 'ERR 6 ERL 710'),
    ('PRINT LEN(SPACE$(-1))', 'ERR 5 ERL 720'),
    ('PRINT LEN(SPACE$(256))', 'ERR 5 ERL 730'),
    ('PRINT LEN(SPACE$(255))', ' 255'),
    ('PRINT CHR$(40000)', 'ERR 6 ERL 750'),
    ('PRINT CHR$(32768)', 'ERR 6 ERL 760'),
    ('PRINT CHR$(-32769)', 'ERR 6 ERL 770'),
    ('PRINT CHR$(-1)', 'ERR 5 ERL 780'),
    ('PRINT CHR$(256)', 'ERR 5 ERL 790'),
    ('PRINT ASC(CHR$(255))', ' 255'),
    ('PRINT PEEK(70000)>=0', 'ERR 6 ERL 810'),
    ('PRINT PEEK(65536)>=0', 'ERR 6 ERL 820'),
    ('PRINT PEEK(-32769)>=0', 'ERR 6 ERL 830'),
    ('PRINT PEEK(-32768.5)>=0', 'ERR 6 ERL 840'),
    ('PRINT PEEK(65535)>=0', '-1'),
    ('PRINT PEEK(65535.5)>=0', '-1'),
    ('PRINT PEEK(-32768)>=0', '-1'),
    ('PRINT PEEK(-1)>=0', '-1'),
    ('PRINT LEN(MKI$(40000))', 'ERR 6 ERL 890'),
    ('PRINT LEN(MKI$(32768))', 'ERR 6 ERL 900'),
    ('PRINT LEN(MKI$(32767))', ' 2'),
    ('PRINT LEN(MKI$(32767.5))', 'ERR 6 ERL 920'),
    ('PRINT LEN(MKI$(-32769))', 'ERR 6 ERL 930'),
    ('PRINT LEN(MKI$(-32768))', ' 2'),
    ('PRINT LEN(MKI$(-32768.5))', 'ERR 6 ERL 950'),
    ('PRINT INSTR(40000,"ABC","B")', 'ERR 6 ERL 960'),
    ('PRINT INSTR(0,"ABC","B")', 'ERR 5 ERL 970'),
    ('PRINT INSTR(256,"ABC","B")', 'ERR 5 ERL 980'),
    ('PRINT INSTR(255,"ABC","B")', ' 0'),
    ('PRINT INSTR(2,"ABC","B")', ' 2'),
    ('PRINT INP(40000)', 'ERR 6 ERL 1010'),
    ('PRINT INP(256)', 'ERR 5 ERL 1020'),
    ('PRINT INP(-1)', 'ERR 5 ERL 1030'),
    ('OUT 70000,1', 'ERR 6 ERL 1040'),
    ('OUT 1,256', 'ERR 5 ERL 1050'),
    ('OUT 1,-1', 'ERR 5 ERL 1060'),
    ('POKE 65536,1', 'ERR 6 ERL 1070'),
    ('POKE -32769,1', 'ERR 6 ERL 1080'),
    ('POKE 40000,1', ''),
    ('POKE -1,1', ''),
    ('POKE 1,256', 'ERR 5 ERL 1110'),
    ('POKE 1,40000', 'ERR 6 ERL 1120'),
    ('POKE 1,-1', 'ERR 5 ERL 1130'),
    ('ON 40000 GOTO 100', 'ERR 6 ERL 1140'),
    ('ON 32768 GOTO 100', 'ERR 6 ERL 1150'),
    ('ON -32769 GOTO 100', 'ERR 6 ERL 1160'),
    ('ON 256 GOTO 100', 'ERR 5 ERL 1170'),
    ('ON -1 GOTO 100', 'ERR 5 ERL 1180'),
    ('ON 1E38 GOSUB 100', 'ERR 6 ERL 1190'),
    ('ON 0 GOTO 100', ''),
    ('RANDOMIZE 40000', 'ERR 6 ERL 1210'),
    ('RANDOMIZE -32769', 'ERR 6 ERL 1220'),
    ('RANDOMIZE 1E38', 'ERR 6 ERL 1230'),
    ('PRINT EOF(40000)', 'ERR 6 ERL 1240'),
    ('PRINT EOF(256)', 'ERR 5 ERL 1250'),
    ('PRINT EOF(-1)', 'ERR 5 ERL 1260'),
    ('PRINT LOC(40000)', 'ERR 6 ERL 1270'),
    ('PRINT LOF(256)', 'ERR 5 ERL 1280'),
    ('CLOSE 40000', 'ERR 6 ERL 1290'),
    ('CLOSE 256', 'ERR 5 ERL 1300'),
    ('CLOSE -1', 'ERR 5 ERL 1310'),
    ('PRINT INPUT$(40000)', 'ERR 6 ERL 1320'),
    ('PRINT INPUT$(0)', 'ERR 5 ERL 1330'),
    ('PRINT INPUT$(256)', 'ERR 5 ERL 1340'),
    ('PRINT INPUT$(1,40000)', 'ERR 6 ERL 1350'),
    ('PRINT INPUT$(1,256)', 'ERR 5 ERL 1360'),
    ('WIDTH 40000', 'ERR 6 ERL 1370'),
    ('WIDTH 32768', 'ERR 6 ERL 1380'),
    ('WIDTH 256', 'ERR 5 ERL 1390'),
    ('WIDTH -1', 'ERR 5 ERL 1400'),
]


def program():
    lines = ["%d %s" % (n, text) for n, text in enumerate(PRELUDE, 1)]
    for i, (statement, _) in enumerate(CASES):
        lines.append('%d PRINT "%d|";:%s:PRINT' % (100 + i * 10, i, statement))
    lines.append("%d SYSTEM" % (100 + len(CASES) * 10))
    lines.append("60000 " + HANDLER)
    return "\n".join(lines) + "\n"


def run_interpreter(tmp_path):
    (tmp_path / "cases.bas").write_text(program())
    result = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(tmp_path / "cases.bas"), "--ui", "cli"],
        input="RUN\nSYSTEM\n", cwd=tmp_path, capture_output=True, text=True, timeout=120)
    text = result.stdout.replace("\r", "").split("Goodbye")[0]   # SYSTEM ends our run with Goodbye
    got = {}
    for piece in re.split(r"(?:^|\n)(?=\d+\|)", text):
        found = re.match(r"(\d+)\|(.*)", piece, re.S)
        if found:
            got[int(found.group(1))] = found.group(2).strip("\n")
    return got, result


def test_every_case_matches_real_mbasic(tmp_path):
    got, result = run_interpreter(tmp_path)
    wrong = []
    for i, (statement, expected) in enumerate(CASES):
        if got.get(i, "<missing>").rstrip() != expected.rstrip():
            wrong.append("%s: real %r, ours %r" % (statement, expected, got.get(i, "<missing>")))
    assert not wrong, "\n".join(wrong) + "\n" + result.stderr

