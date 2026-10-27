"""C backend: ON ERROR GOTO, RESUME, ERROR, ERR, ERL and PRINT USING.

Every expected output is what real MBASIC 5.21 printed for the same program
(cpmemu running com/mbasic, see tests/HOW_TO_RUN_REAL_MBASIC.md).

What the measurements show:

- An error with ON ERROR GOTO armed goes to the handler with ERR and ERL set;
  so do Division by zero and Overflow, which without a handler only print a
  message. RESUME runs the statement again, RESUME NEXT runs the one after
  it, RESUME n goes to line n; each sets ERR to 0 and keeps ERL.
- After an error in the condition of an IF, RESUME NEXT goes on at the
  second statement of the THEN part (MBASIC looks for the next ':').
- An error inside the handler stops the program, in the handler's line.
  ON ERROR GOTO 0 inside the handler stops it with the error being handled,
  in ERL. RESUME with no error is RESUME without error (20), which a handler
  can trap. ON ERROR GOTO a missing line is Undefined line number. A handler
  that runs off the end of the program is No RESUME.
- ERROR 0 and ERROR 256 are Illegal function call; a code with no message
  prints Unprintable error.
- The MID$ statement: a start of 0 or beyond the end of the string, or a
  count outside 0..255, is Illegal function call; a count of 0 does nothing.
- READ into a number of a quoted item, or of text that is no number, is a
  Syntax error at the DATA line, after the number the text starts with is
  stored (12x gives 12); &O8 is one at the READ line, with nothing stored;
  1E50 is Overflow. A quoted item with text after it ("a"b) is the error for
  a string too. The next READ starts again at the first item of the failed
  statement.
- A FOR with a double variable is Type mismatch, after the start is worked
  out (the variable keeps its value). A FOR that fails starts no loop, so
  its NEXT is NEXT without FOR. An integer FOR with a limit or step outside
  16 bits is Overflow before the variable is set.
- PRINT USING: numeric fields with + - $$ ** , and ^^^^, the string fields
  ! \\  \\ and &, _ before a literal character, a format used again for more
  values, and a value too big for its field (%).
"""
import sys
from pathlib import Path

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: C backend ON ERROR tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_c_backend import NEEDS_TOOLCHAIN, compile_c, run_compiled  # noqa: E402

# name: (program, output of real MBASIC 5.21)
CASES = {
    'trap_resume_forms': (
        ('10 ON ERROR GOTO 100\n'
         '20 X=1/0:PRINT "back"\n'
         '30 PRINT "A":ERROR 200:PRINT "B"\n'
         '50 FOR I=1 TO 2:PRINT I;LOG(-I):NEXT\n'
         '60 RESUME\n'
         '65 B=-1\n'
         '70 A=SQR(B):PRINT "retry ok";A\n'
         '75 GOSUB 200:PRINT "after gosub"\n'
         '76 W=0:WHILE W<3:W=W+1:PRINT "w";W;:X=1/0:PRINT "w2":WEND:PRINT\n'
         '77 OPEN "O",1,"T1.TXT":PRINT #1,"abc";1/0;"def":CLOSE 1:PRINT "closed"\n'
         '78 X=1/0:Y=2:PRINT "sticky":ERROR 7\n'
         '79 ON ERROR GOTO 300:ERROR 12\n'
         '80 PRINT "end";ERR;ERL\n'
         '90 END\n'
         '100 PRINT "h";ERR;ERL\n'
         '110 IF ERL=70 THEN B=4:RESUME\n'
         '120 RESUME NEXT\n'
         '200 PRINT "sub":X=1/0:PRINT "sub2":RETURN\n'
         '300 PRINT "h300";ERR;ERL:RESUME 80\n'),
        ('h 11  20 \n'
         'back\n'
         'A\n'
         'h 200  30 \n'
         'B\n'
         ' 1 h 5  50 \n'
         ' 2 h 5  50 \n'
         'h 20  60 \n'
         'h 5  70 \n'
         'retry ok 2 \n'
         'sub\n'
         'h 11  200 \n'
         'sub2\n'
         'after gosub\n'
         'w 1 h 11  76 \n'
         'w2\n'
         'w 2 h 11  76 \n'
         'w2\n'
         'w 3 h 11  76 \n'
         'w2\n'
         '\n'
         'h 11  77 \n'
         'closed\n'
         'h 11  78 \n'
         'sticky\n'
         'h 7  78 \n'
         'h300 12  79 \n'
         'end 0  79 \n')),
    'resume_next_in_if': (
        ('10 ON ERROR GOTO 100\n'
         '40 IF 1/0 THEN PRINT "t1":PRINT "t2" ELSE PRINT "e"\n'
         '45 IF 1 THEN PRINT "t3":X=1/0:PRINT "t4" ELSE PRINT "e2"\n'
         '46 IF 1/0 THEN PRINT "t5" ELSE PRINT "e3"\n'
         '47 IF 1/0 THEN 48 ELSE PRINT "e4"\n'
         '48 PRINT "l48":IF 0 THEN PRINT "x" ELSE PRINT "e5":X=1/0:PRINT "e6"\n'
         '49 IF 1/0 THEN PRINT "t7":PRINT "t8":PRINT "t9"\n'
         '50 PRINT "end":END\n'
         '100 PRINT "h";ERR;ERL:RESUME NEXT\n'),
        ('h 11  40 \n'
         't2\n'
         't3\n'
         'h 11  45 \n'
         't4\n'
         'h 11  46 \n'
         'h 11  47 \n'
         'l48\n'
         'e5\n'
         'h 11  48 \n'
         'e6\n'
         'h 11  49 \n'
         't8\n'
         't9\n'
         'end\n')),
    'error_in_handler': (
        ('10 ON ERROR GOTO 100\n'
         '20 X=1/0:PRINT "back"\n'
         '30 SYSTEM\n'
         '100 PRINT "h";ERR;ERL:Y=SQR(-1)\n'
         '110 RESUME NEXT\n'),
        ('h 11  20 \n'
         'Illegal function call in 100\n')),
    'on_error_goto_0_in_handler': (
        ('10 ON ERROR GOTO 100\n'
         '20 X=1/0:PRINT "back"\n'
         '30 SYSTEM\n'
         '100 PRINT "h";ERR;ERL\n'
         '110 ON ERROR GOTO 0\n'
         '120 PRINT "after"\n'),
        ('h 11  20 \n'
         'Division by zero in 20\n')),
    'resume_without_error_is_trapped': (
        ('10 ON ERROR GOTO 100\n'
         '20 RESUME\n'
         '30 SYSTEM\n'
         '100 PRINT "h";ERR;ERL:RESUME NEXT\n'),
        ('h 20  20 \n')),
    'unprintable_error': (
        ('10 ERROR 200\n'
         '20 SYSTEM\n'),
        ('Unprintable error in 10\n')),
    'error_message_starts_a_line': (
        ('10 PRINT "x";:ERROR 11\n'
         '20 SYSTEM\n'),
        ('x\n'
         'Division by zero in 10\n')),
    'error_code_range': (
        ('10 ON ERROR GOTO 100\n'
         '20 ERROR 0\n'
         '25 ERROR 256\n'
         '30 PRINT 1/0;"z"\n'
         '35 SYSTEM\n'
         '100 PRINT "h";ERR;ERL:RESUME NEXT\n'),
        ('h 5  20 \n'
         'h 5  25 \n'
         'h 11  30 \n')),
    'on_error_goto_missing_line': (
        ('10 ON ERROR GOTO 500\n'
         '20 PRINT "a"\n'
         '30 SYSTEM\n'),
        ('Undefined line number in 10\n')),
    'untrapped_warnings_and_resume': (
        ('10 PRINT 1/0;"z"\n'
         '20 X=1E30*1E30:PRINT X\n'
         '25 RESUME\n'
         '30 SYSTEM\n'),
        ('Division by zero\n'
         ' 1.70141E+38 z\n'
         'Overflow\n'
         ' 1.70141E+38 \n'
         'RESUME without error in 25\n')),
    'handler_above_32767': (
        ('10 ON ERROR GOTO 40000\n'
         '20 ERROR 5\n'
         '30 SYSTEM\n'
         '40000 PRINT ERR;ERL:RESUME NEXT\n'),
        (' 5  20 \n')),
    'handler_runs_off_the_end': (
        ('10 ON ERROR GOTO 100\n'
         '20 X=1/0:PRINT "back"\n'
         '30 END\n'
         '100 PRINT "h";ERR;ERL\n'
         '110 PRINT "fell"\n'),
        ('h 11  20 \n'
         'fell\n'
         'No RESUME in 110\n')),
    'mid_statement_checks': (
        ('10 ON ERROR GOTO 100\n'
         '20 Z$="abcdef":MID$(Z$,255,255)=CHR$(97):PRINT Z$\n'
         '30 Z$="abcdef":MID$(Z$,2,256)=" x ":PRINT Z$\n'
         '40 Z$="abcdef":MID$(Z$,10,10)=CHR$(32):PRINT Z$\n'
         '50 Z$="abcdef":MID$(Z$,6,-1)=STR$(255):PRINT Z$\n'
         '60 Z$="abcdef":MID$(Z$,10,0)="x":PRINT Z$\n'
         '70 Z$="abcdef":MID$(Z$,0)="x":PRINT Z$\n'
         '80 Z$="abcdef":MID$(Z$,5)="xyz":PRINT Z$\n'
         '90 SYSTEM\n'
         '100 PRINT "E";ERR;ERL:RESUME NEXT\n'),
        ('E 5  20 \n'
         'abcdef\n'
         'E 5  30 \n'
         'abcdef\n'
         'E 5  40 \n'
         'abcdef\n'
         'E 5  50 \n'
         'abcdef\n'
         'abcdef\n'
         'E 5  70 \n'
         'abcdef\n'
         'abcdxy\n')),
    'read_bad_data_quoted': (
        ('10 ON ERROR GOTO 100\n'
         '20 R$="":R=0:READ R,R$,R:PRINT "[";R$;"]";R\n'
         '25 PRINT "next"\n'
         '30 DATA "a"b,",A$\n'
         '40 READ R$:PRINT R$:READ R:PRINT R\n'
         '50 DATA 12x,7\n'
         '90 SYSTEM\n'
         '100 PRINT "E";ERR;ERL:RESUME NEXT\n'),
        ('E 2  30 \n'
         '[] 0 \n'
         'next\n'
         'E 2  30 \n'
         'a\n'
         'E 2  30 \n'
         ' 0 \n')),
    'read_bad_data_text': (
        ('10 ON ERROR GOTO 100\n'
         '20 READ A:PRINT A\n'
         '30 READ B%:PRINT B%\n'
         '40 READ C:PRINT C\n'
         '45 READ D$,E:PRINT D$;E\n'
         '50 DATA 12x,7.6y,&O8,1 2,&H10,1E50\n'
         '60 READ F:PRINT F\n'
         '90 SYSTEM\n'
         '100 PRINT "E";ERR;ERL:READ X$:PRINT "skip ";X$:RESUME NEXT\n'),
        ('E 2  50 \n'
         'skip 12x\n'
         ' 12 \n'
         'E 2  50 \n'
         'skip 7.6y\n'
         ' 8 \n'
         'E 2  40 \n'
         'skip &O8\n'
         ' 0 \n'
         '1 2 16 \n'
         'E 6  60 \n'
         'skip 1E50\n'
         ' 0 \n')),
    'for_that_fails': (
        ('10 ON ERROR GOTO 100\n'
         '20 I#=5:FOR I#=1 TO 3:PRINT "b";I#;\n'
         '30 NEXT:PRINT "/";I#\n'
         '40 FOR I%=1E10 TO 3:PRINT "c";I%;\n'
         '50 NEXT:PRINT "/";I%\n'
         '60 FOR J=1 TO 2:PRINT J;:NEXT:PRINT\n'
         '90 SYSTEM\n'
         '100 PRINT "E";ERR;ERL:RESUME NEXT\n'),
        ('E 13  20 \n'
         'b 5 E 1  30 \n'
         '/ 5 \n'
         'E 6  40 \n'
         'c 0 E 1  50 \n'
         '/ 0 \n'
         ' 1  2 \n')),
    'for_double_variable': (
        ('10 FOR I#=1 TO 3:PRINT I#:NEXT\n'
         '20 SYSTEM\n'),
        ('Type mismatch in 10\n')),
    'for_integer_limit_overflow': (
        ('10 ON ERROR GOTO 100\n'
         '20 FOR I%=2.5 TO 1E10 STEP -1:PRINT "c";I%;\n'
         '30 NEXT:PRINT "/";I%\n'
         '40 FOR I%=1 TO 2 STEP 40000:PRINT "d";I%;:NEXT\n'
         '50 PRINT\n'
         '90 SYSTEM\n'
         '100 PRINT "E";ERR;ERL:RESUME NEXT\n'),
        ('E 6  20 \n'
         'c 0 E 1  30 \n'
         '/ 0 \n'
         'E 6  40 \n'
         'd 0 E 1  40 \n'
         '\n')),
    'print_using': (
        ('10 PRINT USING "##.##";3.14159;-2.5;100.123\n'
         '20 PRINT USING "+###";5;-5\n'
         '30 PRINT USING "###-";5;-5\n'
         '40 PRINT USING "$$###.##";12.5\n'
         '50 PRINT USING "**$##.##";1.5\n'
         '60 PRINT USING "#,###.##";12345.67;-1234.5\n'
         '70 PRINT USING "##.##^^^^";12345.6;-0.000123\n'
         '80 PRINT USING "!";"hello"\n'
         '90 PRINT USING "\\  \\";"abcdefg";"ab"\n'
         '100 PRINT USING "&";"full"\n'
         '110 PRINT USING "X=## Y=##";1;2;3\n'
         '120 PRINT USING "_##_#";5\n'
         '130 F$="[###]":PRINT USING F$;7;8;\n'
         '140 PRINT "after"\n'
         '150 A%=123:PRINT USING "#####";A%;32767\n'
         '160 PRINT USING "#.#";-0.01;999.99\n'
         '170 PRINT USING "##";1E20\n'
         '180 PRINT USING "##.##^^^^-";-12.5\n'
         '200 PRINT USING "ab ##, ";1,2\n'
         '210 SYSTEM\n'),
        (' 3.14-2.50%100.12\n'
         '  +5  -5\n'
         '  5   5-\n'
         '  $12.50\n'
         '***$1.50\n'
         '%12,345.70%-1,234.50\n'
         ' 1.23E+04-1.23E-04\n'
         'h\n'
         'abcdab  \n'
         'full\n'
         'X= 1 Y= 2X= 3 Y=\n'
         '#5#\n'
         '[  7][  8]after\n'
         '  12332767\n'
         '-.0%1000.0\n'
         '% 1E+20\n'
         '12.50E+00-\n'
         'ab   1 ab   2 \n')),
}


@NEEDS_TOOLCHAIN
@pytest.mark.parametrize("name", sorted(CASES))
def test_c_backend_matches_mbasic(tmp_path, name):
    source, expected = CASES[name]
    result = compile_c(tmp_path, source)
    assert result.returncode == 0, result.stdout + result.stderr
    assert run_compiled(tmp_path, "") == expected


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
