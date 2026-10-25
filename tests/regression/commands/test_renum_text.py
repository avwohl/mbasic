#!/usr/bin/env python3
"""
RENUM changes only the line numbers, as MBASIC 5.21 does.

The expected listings in BIG_CASES were produced by the real MBASIC 5.21
(com/mbasic.com under cpmemu): type BIG_PROGRAM, then RENUM <args>, then LIST.
Each case holds the arguments, the lines LIST printed afterwards and the
messages RENUM printed ("Undefined line n in m", "Illegal function call").

Before the fix, RENUM rewrote every line from the AST: it dropped PRINT #n and
separators, the $ of INPUT variables and MID$, changed DATA, and failed on
ON GOTO/GOSUB and RESUME n.
"""

import os
import subprocess
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, PROJECT_ROOT)

from src.editing.manager import ProgramManager
from src.renum import (
    RenumError, parse_renum_arguments, renumber_lines, scan_line_references,
)
from src.ui.ui_helpers import renum_program

BIG_PROGRAM = """\
10 REM RENUM regression program
20 DEFINT I-N
30 DIM A(10),B$(5)
40 PRINT ,X
50 PRINT A,B,
60 PRINT "X";
70 PRINT #1, 5
80 LINE INPUT "L";B$
90 INPUT "Name";A$
100 PRINT MID$(A$,1,2);LEFT$(A$,1);RIGHT$(A$,2)
110 DATA 1,"a b",c,GOTO 10, 20
120 READ X,Y$,Z$
130 FOR I=1 TO 10 STEP 2
140 NEXT I
150 IF X>5 THEN 200 ELSE 210
160 IF X=1 THEN PRINT "ONE": GOTO 230
170 ON X GOTO 200,210,220
180 ON X GOSUB 400,410 , 420
190 GOSUB 400
200 PRINT "A"
210 PRINT "B"
220 END
230 ON ERROR GOTO 500
240 ON ERROR GOTO 0
250 IF ERL=500 THEN 510
260 IF ERL<>510 THEN PRINT "NOT"
270 RESUME 520
280 RESUME NEXT
290 RESTORE 110
300 DEF FNA(X)=X*2
310 PRINT FNA(3)
320 WHILE X<10
330 X=X+1
340 WEND
350 PRINT &H1F;1.5#;100000!;.5
360 RESUME
370 A$="GOTO 10"
380 PRINT "THEN 20";
390 REM GOTO 400
400 PRINT "SUB"
410 RETURN
420 RETURN
430 LPRINT "a";
440 OPEN "O",#1,"FILE"
450 FIELD #1, 10 AS A$
460 GET #1,2
470 PUT #1
480 CLOSE #1
490 WRITE #1,A,B$
500 PRINT "ERR": RESUME 200
510 PRINT ERL: GOTO 999
520 X = ERL + 10: Y=ERL
530 GOTO 40 'GOTO 50
540 RUN 10
550 LIST 10-20
560 IF X THEN 170 ELSE IF Y THEN 180 ELSE 190
570 PRINT TAB(5);SPC(3);"X"
580 A(1)=-(2+3)
590 IF A$="x" AND B$<>"y" THEN GOTO 600
600 STOP
"""
# (arguments, listing after RENUM, messages) from the real MBASIC 5.21
BIG_CASES = [
    ('1000,0,10',
     """\
1000 REM RENUM regression program
1010 DEFINT I-N
1020 DIM A(10),B$(5)
1030 PRINT ,X
1040 PRINT A,B,
1050 PRINT "X";
1060 PRINT #1, 5
1070 LINE INPUT "L";B$
1080 INPUT "Name";A$
1090 PRINT MID$(A$,1,2);LEFT$(A$,1);RIGHT$(A$,2)
1100 DATA 1,"a b",c,GOTO 10, 20
1110 READ X,Y$,Z$
1120 FOR I=1 TO 10 STEP 2
1130 NEXT I
1140 IF X>5 THEN 1190 ELSE 1200
1150 IF X=1 THEN PRINT "ONE": GOTO 1220
1160 ON X GOTO 1190,1200,1210
1170 ON X GOSUB 1390,1400 , 1410
1180 GOSUB 1390
1190 PRINT "A"
1200 PRINT "B"
1210 END
1220 ON ERROR GOTO 1490
1230 ON ERROR GOTO 0
1240 IF ERL=1490 THEN 1500
1250 IF ERL<>1500 THEN PRINT "NOT"
1260 RESUME 1510
1270 RESUME NEXT
1280 RESTORE 1100
1290 DEF FNA(X)=X*2
1300 PRINT FNA(3)
1310 WHILE X<10
1320 X=X+1
1330 WEND
1340 PRINT &H1F;1.5#;100000!;.5
1350 RESUME
1360 A$="GOTO 10"
1370 PRINT "THEN 20";
1380 REM GOTO 400
1390 PRINT "SUB"
1400 RETURN
1410 RETURN
1420 LPRINT "a";
1430 OPEN "O",#1,"FILE"
1440 FIELD #1, 10 AS A$
1450 GET #1,2
1460 PUT #1
1470 CLOSE #1
1480 WRITE #1,A,B$
1490 PRINT "ERR": RESUME 1190
1500 PRINT ERL: GOTO 999
1510 X = ERL + 1000: Y=ERL
1520 GOTO 1030 'GOTO 50
1530 RUN 1000
1540 LIST 1000-1010
1550 IF X THEN 1160 ELSE IF Y THEN 1170 ELSE 1180
1560 PRINT TAB(5);SPC(3);"X"
1570 A(1)=-(2+3)
1580 IF A$="x" AND B$<>"y" THEN GOTO 1590
1590 STOP
""",
     ['Undefined line 999 in 510']),
    ('',
     """\
10 REM RENUM regression program
20 DEFINT I-N
30 DIM A(10),B$(5)
40 PRINT ,X
50 PRINT A,B,
60 PRINT "X";
70 PRINT #1, 5
80 LINE INPUT "L";B$
90 INPUT "Name";A$
100 PRINT MID$(A$,1,2);LEFT$(A$,1);RIGHT$(A$,2)
110 DATA 1,"a b",c,GOTO 10, 20
120 READ X,Y$,Z$
130 FOR I=1 TO 10 STEP 2
140 NEXT I
150 IF X>5 THEN 200 ELSE 210
160 IF X=1 THEN PRINT "ONE": GOTO 230
170 ON X GOTO 200,210,220
180 ON X GOSUB 400,410 , 420
190 GOSUB 400
200 PRINT "A"
210 PRINT "B"
220 END
230 ON ERROR GOTO 500
240 ON ERROR GOTO 0
250 IF ERL=500 THEN 510
260 IF ERL<>510 THEN PRINT "NOT"
270 RESUME 520
280 RESUME NEXT
290 RESTORE 110
300 DEF FNA(X)=X*2
310 PRINT FNA(3)
320 WHILE X<10
330 X=X+1
340 WEND
350 PRINT &H1F;1.5#;100000!;.5
360 RESUME
370 A$="GOTO 10"
380 PRINT "THEN 20";
390 REM GOTO 400
400 PRINT "SUB"
410 RETURN
420 RETURN
430 LPRINT "a";
440 OPEN "O",#1,"FILE"
450 FIELD #1, 10 AS A$
460 GET #1,2
470 PUT #1
480 CLOSE #1
490 WRITE #1,A,B$
500 PRINT "ERR": RESUME 200
510 PRINT ERL: GOTO 999
520 X = ERL + 10: Y=ERL
530 GOTO 40 'GOTO 50
540 RUN 10
550 LIST 10-20
560 IF X THEN 170 ELSE IF Y THEN 180 ELSE 190
570 PRINT TAB(5);SPC(3);"X"
580 A(1)=-(2+3)
590 IF A$="x" AND B$<>"y" THEN GOTO 600
600 STOP
""",
     ['Undefined line 999 in 510']),
    ('7,,3',
     """\
7 REM RENUM regression program
10 DEFINT I-N
13 DIM A(10),B$(5)
16 PRINT ,X
19 PRINT A,B,
22 PRINT "X";
25 PRINT #1, 5
28 LINE INPUT "L";B$
31 INPUT "Name";A$
34 PRINT MID$(A$,1,2);LEFT$(A$,1);RIGHT$(A$,2)
37 DATA 1,"a b",c,GOTO 10, 20
40 READ X,Y$,Z$
43 FOR I=1 TO 10 STEP 2
46 NEXT I
49 IF X>5 THEN 64 ELSE 67
52 IF X=1 THEN PRINT "ONE": GOTO 73
55 ON X GOTO 64,67,70
58 ON X GOSUB 124,127 , 130
61 GOSUB 124
64 PRINT "A"
67 PRINT "B"
70 END
73 ON ERROR GOTO 154
76 ON ERROR GOTO 0
79 IF ERL=154 THEN 157
82 IF ERL<>157 THEN PRINT "NOT"
85 RESUME 160
88 RESUME NEXT
91 RESTORE 37
94 DEF FNA(X)=X*2
97 PRINT FNA(3)
100 WHILE X<10
103 X=X+1
106 WEND
109 PRINT &H1F;1.5#;100000!;.5
112 RESUME
115 A$="GOTO 10"
118 PRINT "THEN 20";
121 REM GOTO 400
124 PRINT "SUB"
127 RETURN
130 RETURN
133 LPRINT "a";
136 OPEN "O",#1,"FILE"
139 FIELD #1, 10 AS A$
142 GET #1,2
145 PUT #1
148 CLOSE #1
151 WRITE #1,A,B$
154 PRINT "ERR": RESUME 64
157 PRINT ERL: GOTO 999
160 X = ERL + 7: Y=ERL
163 GOTO 16 'GOTO 50
166 RUN 7
169 LIST 7-10
172 IF X THEN 55 ELSE IF Y THEN 58 ELSE 61
175 PRINT TAB(5);SPC(3);"X"
178 A(1)=-(2+3)
181 IF A$="x" AND B$<>"y" THEN GOTO 184
184 STOP
""",
     ['Undefined line 999 in 510']),
    ('305,300,5',
     """\
10 REM RENUM regression program
20 DEFINT I-N
30 DIM A(10),B$(5)
40 PRINT ,X
50 PRINT A,B,
60 PRINT "X";
70 PRINT #1, 5
80 LINE INPUT "L";B$
90 INPUT "Name";A$
100 PRINT MID$(A$,1,2);LEFT$(A$,1);RIGHT$(A$,2)
110 DATA 1,"a b",c,GOTO 10, 20
120 READ X,Y$,Z$
130 FOR I=1 TO 10 STEP 2
140 NEXT I
150 IF X>5 THEN 200 ELSE 210
160 IF X=1 THEN PRINT "ONE": GOTO 230
170 ON X GOTO 200,210,220
180 ON X GOSUB 355,360 , 365
190 GOSUB 355
200 PRINT "A"
210 PRINT "B"
220 END
230 ON ERROR GOTO 405
240 ON ERROR GOTO 0
250 IF ERL=405 THEN 410
260 IF ERL<>410 THEN PRINT "NOT"
270 RESUME 415
280 RESUME NEXT
290 RESTORE 110
305 DEF FNA(X)=X*2
310 PRINT FNA(3)
315 WHILE X<10
320 X=X+1
325 WEND
330 PRINT &H1F;1.5#;100000!;.5
335 RESUME
340 A$="GOTO 10"
345 PRINT "THEN 20";
350 REM GOTO 400
355 PRINT "SUB"
360 RETURN
365 RETURN
370 LPRINT "a";
375 OPEN "O",#1,"FILE"
380 FIELD #1, 10 AS A$
385 GET #1,2
390 PUT #1
395 CLOSE #1
400 WRITE #1,A,B$
405 PRINT "ERR": RESUME 200
410 PRINT ERL: GOTO 999
415 X = ERL + 10: Y=ERL
420 GOTO 40 'GOTO 50
425 RUN 10
430 LIST 10-20
435 IF X THEN 170 ELSE IF Y THEN 180 ELSE 190
440 PRINT TAB(5);SPC(3);"X"
445 A(1)=-(2+3)
450 IF A$="x" AND B$<>"y" THEN GOTO 455
455 STOP
""",
     ['Undefined line 999 in 510']),
    ('100,200,5',
     """\
10 REM RENUM regression program
20 DEFINT I-N
30 DIM A(10),B$(5)
40 PRINT ,X
50 PRINT A,B,
60 PRINT "X";
70 PRINT #1, 5
80 LINE INPUT "L";B$
90 INPUT "Name";A$
100 PRINT MID$(A$,1,2);LEFT$(A$,1);RIGHT$(A$,2)
110 DATA 1,"a b",c,GOTO 10, 20
120 READ X,Y$,Z$
130 FOR I=1 TO 10 STEP 2
140 NEXT I
150 IF X>5 THEN 200 ELSE 210
160 IF X=1 THEN PRINT "ONE": GOTO 230
170 ON X GOTO 200,210,220
180 ON X GOSUB 400,410 , 420
190 GOSUB 400
200 PRINT "A"
210 PRINT "B"
220 END
230 ON ERROR GOTO 500
240 ON ERROR GOTO 0
250 IF ERL=500 THEN 510
260 IF ERL<>510 THEN PRINT "NOT"
270 RESUME 520
280 RESUME NEXT
290 RESTORE 110
300 DEF FNA(X)=X*2
310 PRINT FNA(3)
320 WHILE X<10
330 X=X+1
340 WEND
350 PRINT &H1F;1.5#;100000!;.5
360 RESUME
370 A$="GOTO 10"
380 PRINT "THEN 20";
390 REM GOTO 400
400 PRINT "SUB"
410 RETURN
420 RETURN
430 LPRINT "a";
440 OPEN "O",#1,"FILE"
450 FIELD #1, 10 AS A$
460 GET #1,2
470 PUT #1
480 CLOSE #1
490 WRITE #1,A,B$
500 PRINT "ERR": RESUME 200
510 PRINT ERL: GOTO 999
520 X = ERL + 10: Y=ERL
530 GOTO 40 'GOTO 50
540 RUN 10
550 LIST 10-20
560 IF X THEN 170 ELSE IF Y THEN 180 ELSE 190
570 PRINT TAB(5);SPC(3);"X"
580 A(1)=-(2+3)
590 IF A$="x" AND B$<>"y" THEN GOTO 600
600 STOP
""",
     ['Illegal function call']),
]


def load(text):
    program = ProgramManager({})
    for line in text.strip().split('\n'):
        ok, error = program.add_line(int(line.split()[0]), line)
        assert ok, (line, error)
    return program


def listing(program):
    return [program.lines[n] for n in sorted(program.lines)]


def run_cli(program_text, commands):
    """Run the CLI with the program loaded by typing it, return stdout lines."""
    stdin = program_text.strip() + '\n' + commands + 'SYSTEM\n'
    result = subprocess.run(
        [sys.executable, os.path.join(PROJECT_ROOT, 'mbasic'), '--ui', 'cli'],
        input=stdin, capture_output=True, text=True, timeout=60, cwd=PROJECT_ROOT)
    return result.stdout.split('\n')


def numbered(lines):
    return [l for l in lines if l[:1].isdigit()]


def messages(lines):
    return [l for l in lines
            if l.startswith('Undefined line') or l == 'Illegal function call'
            or l == 'Syntax error']


def test_big_program_matches_real_mbasic():
    """RENUM output equals the real MBASIC 5.21 listing, byte for byte."""
    for args, expected, expected_messages in BIG_CASES:
        program = load(BIG_PROGRAM)
        found = []
        try:
            renum_program(program, args, messages=found)
        except RenumError as error:
            found = [str(error)]
        want = expected.strip().split('\n')
        got = listing(program)
        assert got == want, 'RENUM %s: listing differs\n%s' % (
            args, '\n'.join('  got  %s\n  want %s' % (a, b)
                            for a, b in zip(got, want) if a != b))
        assert found == expected_messages, (args, found, expected_messages)
        # every line has an AST with the new line number
        assert sorted(program.line_asts) == sorted(program.lines), args
        for number, node in program.line_asts.items():
            assert node.line_number == number, (args, number)


def test_big_program_through_the_cli():
    """The CLI prints what real MBASIC prints."""
    for args, expected, expected_messages in BIG_CASES:
        lines = run_cli(BIG_PROGRAM, 'RENUM %s\nLIST\n' % args)
        assert numbered(lines) == expected.strip().split('\n'), args
        assert messages(lines) == expected_messages, (args, messages(lines))


def test_issue_examples():
    """The examples of issue #12."""
    program = load('10 PRINT "X";\n20 PRINT #1, 5\n30 PRINT "Y"')
    renum_program(program, '')
    assert listing(program) == ['10 PRINT "X";', '20 PRINT #1, 5', '30 PRINT "Y"']

    program = load('10 INPUT "Name";A$\n20 PRINT "Hi ";A$;\n'
                   '30 PRINT "there"\n40 PRINT MID$(A$,1,2)')
    renum_program(program, '100')
    assert listing(program) == [
        '100 INPUT "Name";A$', '110 PRINT "Hi ";A$;',
        '120 PRINT "there"', '130 PRINT MID$(A$,1,2)']

    program = load('10 ON A GOTO 10,20\n20 ON A GOSUB 10,20')
    renum_program(program, '100')
    assert listing(program) == ['100 ON A GOTO 100,110', '110 ON A GOSUB 100,110']
    node = program.line_asts[100].statements[0]
    assert node.line_numbers == [100, 110], node.line_numbers


def test_ast_is_rebuilt_for_resume_and_if():
    program = load('10 RESUME 20\n20 IF A THEN 10 ELSE 20\n30 RESTORE 10')
    renum_program(program, '100,0,5')
    assert listing(program) == [
        '100 RESUME 105', '105 IF A THEN 100 ELSE 105', '110 RESTORE 100']
    assert program.line_asts[100].statements[0].line_number == 105
    if_node = program.line_asts[105].statements[0]
    assert (if_node.then_line_number, if_node.else_line_number) == (100, 105)


def test_renumbered_program_still_runs():
    program = '10 GOTO 30\n20 PRINT "BAD"\n30 GOSUB 50\n40 END\n50 PRINT "OK"\n60 RETURN'
    lines = run_cli(program, 'RENUM 100\nRUN\n')
    assert 'OK' in lines and 'BAD' not in lines, lines


def test_text_is_kept_byte_for_byte():
    source = {
        10: '10 print #1,a$;"GOTO 20";   : goto 20',
        20: "20 data 1 ,\"x\",GOTO 10: x=1e5 'goto 10",
        30: '30 If a$<>"" Then 10 Else 20',
        40: '40 PRINT MID$(A$,1,2);:INPUT A$',
    }
    new, mapping, found = renumber_lines(dict(source), 100, 0, 10)
    assert found == []
    assert new == {
        100: '100 print #1,a$;"GOTO 20";   : goto 110',
        110: "110 data 1 ,\"x\",GOTO 10: x=1e5 'goto 10",
        120: '120 If a$<>"" Then 100 Else 110',
        130: '130 PRINT MID$(A$,1,2);:INPUT A$',
    }


def references(text):
    return [(r.value, r.skip) for r in scan_line_references(text, 0)]


def test_scanner_follows_the_tokeniser():
    # GOTO10 is a variable name for MBASIC, not a statement with a line number
    assert references('GOTO10') == []
    assert references('GOTO 10') == [(10, False)]
    assert references('GO TO 10') == [(10, False)]
    assert references('ON A GOTO 10 , 20,30') == [(10, False), (20, False), (30, False)]
    # ON ERROR GOTO 0 is left alone, GOTO 0 is not
    assert references('ON ERROR GOTO 0') == [(0, True)]
    assert references('GOTO 0') == [(0, False)]
    # any operator after ERL, strings, REM, DATA and ' hide numbers
    assert references('IF ERL=10 THEN 20') == [(10, False), (20, False)]
    assert references('X=ERL+10') == [(10, False)]
    assert references('IF 10=ERL THEN 20') == [(20, False)]
    assert references('PRINT "GOTO 10"') == []
    assert references('REM GOTO 10') == []
    assert references('DATA GOTO 10') == []
    assert references("X=1 'GOTO 10") == []
    assert references('IF A THEN PRINT 10') == []
    assert references('CHAIN "A",10') == []
    assert references('LIST 10-20') == [(10, False), (20, False)]
    # a number above 65529 is two constants, as in MBASIC
    assert references('GOTO 70000') == [(7000, False), (0, False)]


def argument_error(args):
    try:
        parse_renum_arguments(args)
    except RenumError as error:
        return str(error)
    return None


def test_argument_forms():
    assert parse_renum_arguments('') == (10, 0, 10)
    assert parse_renum_arguments('100') == (100, 0, 10)
    assert parse_renum_arguments('100,50') == (100, 50, 10)
    assert parse_renum_arguments('100,50,20') == (100, 50, 20)
    assert parse_renum_arguments(',50,20') == (10, 50, 20)
    assert parse_renum_arguments('100,,20') == (100, 0, 20)
    assert parse_renum_arguments('100,') == (100, 0, 10)
    assert parse_renum_arguments('0') == (0, 0, 10)
    assert argument_error('100,,0') == 'Illegal function call'
    assert argument_error('100,,') == 'Illegal function call'
    assert argument_error('1,2,3,4') == 'Syntax error'
    assert argument_error('A') == 'Syntax error'
    assert argument_error('65530') == 'Syntax error'
    assert argument_error('70000') == 'Syntax error'


def renum_error(text, args):
    program = load(text)
    try:
        renum_program(program, args)
    except RenumError as error:
        assert listing(program) == [l for l in text.strip().split('\n')]
        return str(error)
    return None


def test_illegal_function_call_cases():
    five = '10 PRINT 1\n20 PRINT 2\n30 GOTO 10\n40 PRINT 4\n50 PRINT 5'
    assert renum_error(five, '5,20') == 'Illegal function call'
    assert renum_error(five, '6,30') == 'Illegal function call'
    assert renum_error(five, '65529') == 'Illegal function call'
    assert renum_error(five, '100,,20000') == 'Illegal function call'
    assert renum_error(five, '15,20') is None
    assert renum_error(five, '20,20') is None
    assert renum_error(five, '100,60') is None
    assert renum_error(five, '65525,,1') is None


def test_no_program():
    program = ProgramManager({})
    assert renum_program(program, '') == ([], {})


TESTS = [
    test_big_program_matches_real_mbasic,
    test_big_program_through_the_cli,
    test_issue_examples,
    test_ast_is_rebuilt_for_resume_and_if,
    test_renumbered_program_still_runs,
    test_text_is_kept_byte_for_byte,
    test_scanner_follows_the_tokeniser,
    test_argument_forms,
    test_illegal_function_call_cases,
    test_no_program,
]

if __name__ == '__main__':
    failed = 0
    for test in TESTS:
        try:
            test()
            print('PASS', test.__name__)
        except Exception as error:
            failed += 1
            print('FAIL', test.__name__)
            print(error)
    sys.exit(1 if failed else 0)
