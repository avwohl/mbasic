"""C backend: edges of arithmetic and of the string functions.

Every expected output is what real MBASIC 5.21 printed for the same program
(cpmemu running com/mbasic, see tests/HOW_TO_RUN_REAL_MBASIC.md).  Each program
is "10 <body>" and "20 SYSTEM", except where a case gives its own lines.

What the measurements show:

- -32768 \\ -1 is 32768: no integer holds the quotient, so it is a number of
  single precision (PRINT, a store into a single variable, + 1, * 2 all work);
  a store into an INTEGER variable is Overflow.  -A% for A% = -32768 and
  ABS(A%) are 32768 in the same way.
- CINT, a store into an INTEGER variable and a subscript are Overflow outside
  -32768..32767 (after rounding half away from zero).
- LEFT$, RIGHT$, MID$, STRING$, SPACE$, CHR$ and INSTR give Illegal function
  call for a count or a code outside 0..255 (a start outside 1..255).  ASC("")
  does too.  INSTR with a start beyond the end gives 0, empty strings included.
- VAL reads &H and &O numbers as 16-bit words, and skips blanks inside a
  decimal number (VAL(" 1 2") is 12).  POS is the console column.  RESTORE n
  goes to the first DATA item at or after line n.  HEX$ and OCT$ of a value outside
  -32768..65535 are Overflow.
- SQR of a negative number, LOG of zero or less, and a negative base with a
  fractional exponent give Illegal function call.
- A float division by zero, a float overflow (+, -, *, ^, EXP, a constant above
  the range) and EXP(100) print Division by zero or Overflow on a line of
  their own and go on with the largest float.  EXP gives Overflow from 87.34
  and 0 below -88.72; A^B gives Overflow from 2^126.  A constant above the
  largest float is the largest float, with no message.
- + - * of two integers is a single when it does not fit 16 bits (PRINT, a
  store into a single variable, / and comparisons see 60000); it is Overflow
  in a store into a % variable and as an operand of \\.  Comparisons see the
  single whatever the other operand is (constant, variable, + or *).
- A FOR loop with an INTEGER counter stops with Overflow when NEXT steps it
  past 32767 or -32768.
"""
import sys
from pathlib import Path

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: C backend edge tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_c_backend import NEEDS_TOOLCHAIN, compile_c, run_compiled  # noqa: E402

IFC = "Illegal function call in 10\n"
OVERFLOW = "Overflow in 10\n"

# (body of line 10, output of real MBASIC 5.21)
CASES = [
    # \ with a quotient of 32768
    ("PRINT -32768\\-1", " 32768 \n"),
    ("A%=-32768:B%=-1:C=A%\\B%:PRINT C", " 32768 \n"),
    ("A%=-32768:B%=-1:PRINT A%\\B%+1", " 32769 \n"),
    ("A%=-32768:B%=-1:PRINT (A%\\B%)*2", " 65536 \n"),
    ("A%=-32768:B%=-1:C%=A%\\B%", OVERFLOW),
    ("A%=-32768:PRINT -A%;ABS(A%)", " 32768  32768 \n"),
    ("A%=7:B%=-2:PRINT A%\\B%;-7\\2;A% MOD B%", "-3 -3  1 \n"),
    # integer conversions
    ("A=40000:PRINT CINT(A)", OVERFLOW),
    ("A%=40000", OVERFLOW),
    ("A%=32767.6", OVERFLOW),
    ("A%(40000)=1", OVERFLOW),
    ("A%=3.5:B%=-3.5:PRINT A%;B%", " 4 -4 \n"),
    # string functions
    ('PRINT LEFT$("HELLO",256)', IFC),
    ('PRINT LEFT$("HELLO",300)', IFC),
    ('PRINT RIGHT$("HELLO",-1)', IFC),
    ('PRINT MID$("HELLO",0)', IFC),
    ('PRINT MID$("HELLO",256)', IFC),
    ('PRINT MID$("HELLO",2,-1)', IFC),
    ('PRINT MID$("HELLO",2,256)', IFC),
    ('PRINT MID$("HELLO",0,2)', IFC),
    ("PRINT CHR$(256)", IFC),
    ("PRINT CHR$(-1)", IFC),
    ("PRINT SPACE$(256)", IFC),
    ("PRINT SPACE$(-1)", IFC),
    ('PRINT STRING$(256,"A")', IFC),
    ('PRINT STRING$(3,256)', IFC),
    ('PRINT STRING$(3,-1)', IFC),
    ('PRINT INSTR(0,"ABC","A")', IFC),
    ('PRINT INSTR(256,"ABC","A")', IFC),
    ('PRINT ASC("")', IFC),
    ('PRINT INSTR("","");INSTR("","A");INSTR(1,"","");INSTR(2,"A","");INSTR(3,"ABC","")',
     " 0  0  0  0  3 \n"),
    ('PRINT INSTR(4,"ABC","")', " 0 \n"),
    ('PRINT VAL("&H1F");VAL("&O17");VAL("&HFFFF");VAL("-&H10")', " 31  15 -1  0 \n"),
    ("PRINT HEX$(70000)", OVERFLOW),
    ("PRINT HEX$(-32769)", OVERFLOW),
    ("PRINT HEX$(65535);HEX$(-1);OCT$(8)", "FFFFFFFF10\n"),
    # math functions
    ("PRINT SQR(-8)", IFC),
    ("PRINT LOG(0)", IFC),
    ("PRINT LOG(-1)", IFC),
    ("PRINT (-8)^(1/3)", IFC),
    ("PRINT 2^0.5;(-2)^2;(-2)^3;(-2)^-1", " 1.41421  4 -8 -.5 \n"),
    # float errors that go on
    ("PRINT 1/0", "Division by zero\n 1.70141E+38 \n"),
    ("A=0:PRINT 5/A;-5/A",
     "Division by zero\n 1.70141E+38 Division by zero\n-1.70141E+38 \n"),
    ("PRINT 0^-1", "Division by zero\n 1.70141E+38 \n"),
    ("PRINT 3.5E37*10", "Overflow\n 1.70141E+38 \n"),
    ("PRINT -3.5E37*10", "Overflow\n-1.70141E+38 \n"),
    ("A=1E20:PRINT A*A", "Overflow\n 1.70141E+38 \n"),
    ("PRINT EXP(100)", "Overflow\n 1.70141E+38 \n"),
    # float and integer overflow (measured)
    ('A=1.5E38:B=1.5E38:PRINT A+B', 'Overflow\n 1.70141E+38 \n'),
    ('A=1.5E38:PRINT A*2', 'Overflow\n 1.70141E+38 \n'),
    ('A=1.5E38:B=-1.5E38:PRINT B-A', 'Overflow\n-1.70141E+38 \n'),
    ('PRINT 1.7E38+1.7E38', 'Overflow\n 1.70141E+38 \n'),
    ('A=3E38:PRINT A', ' 1.70141E+38 \n'),
    ('A=1.5E38:PRINT A+A:PRINT -A-A:PRINT A-(-A):B=A+1:PRINT B', 'Overflow\n 1.70141E+38 \nOverflow\n-1.70141E+38 \nOverflow\n 1.70141E+38 \n 1.5E+38 \n'),
    ('A=-100:PRINT EXP(A)', ' 0 \n'),
    ('PRINT EXP(88)', 'Overflow\n 1.70141E+38 \n'),
    ('PRINT EXP(-89)', ' 0 \n'),
    ('PRINT EXP(87.4)', 'Overflow\n 1.70141E+38 \n'),
    ('A%=32767:A%=A%+1', 'Overflow in 10\n'),
    ('A%=200:A%=A%*200', 'Overflow in 10\n'),
    ('A%=300:B%=200:C%=A%*B%', 'Overflow in 10\n'),
    ('A%=-32768:A%=A%-1', 'Overflow in 10\n'),
    ('A%=300:B%=200:PRINT A%*B%;A%+B%', ' 60000  500 \n'),
    ('A%=300:B%=200:C=A%*B%:PRINT C:PRINT A%*B%/3', ' 60000 \n 20000 \n'),
    ('A%=300:B%=200:C%=A%*B%-50000:PRINT C%', ' 10000 \n'),
    ('A%=300:B%=200:PRINT A%*B%\\7', 'Overflow in 10\n'),
    ('A%=300:B%=200:C%=(A%*B%-50000)*2:PRINT C%', ' 20000 \n'),
    ('A%=32767:B%=1:PRINT (A%+B%)*2:IF A%+B%>A% THEN PRINT "gt"', ' 65536 \ngt\n'),
    ('A%=5:B%=7:C%=A%+B%:D%=A%-B%:E%=A%*B%:PRINT C%;D%;E%', ' 12 -2  35 \n'),
    ('A%=-32768:B%=-1:PRINT STR$(A%\\B%)', ' 32768\n'),
    ('A=2:PRINT A^126', 'Overflow\n 1.70141E+38 \n'),
    ('A=3:PRINT A^80', 'Overflow\n 1.70141E+38 \n'),
    # comparison with an integer + - * result, FOR past 32767, nested integer store (measured)
    ('A%=30000:B%=30000:PRINT A%+B%>40000', '-1 \n'),
    ('A%=30000:B%=30000:PRINT A%+B%=60000;A%+B%<>60000;A%+B%>=60000;60000=A%+B%', '-1  0 -1 -1 \n'),
    ('A%=30000:B%=30000:C=60000:PRINT A%+B%=C', '-1 \n'),
    ('A%=300:B%=200:IF A%*B%=60000 THEN PRINT "y" ELSE PRINT "n"', 'y\n'),
    ('A%=300:B%=200:C=60000:PRINT 60000=A%*B%;A%*B%>59999;A%*B%=C', '-1 -1 -1 \n'),
    ('FOR I%=32766 TO 32767:PRINT I%:NEXT', ' 32766 \n 32767 \nOverflow in 10\n'),
    ('FOR I%=32766 TO 32767 STEP 2:PRINT I%:NEXT', ' 32766 \nOverflow in 10\n'),
    ('FOR I%=-32767 TO -32768 STEP -1:PRINT I%:NEXT', '-32767 \n-32768 \nOverflow in 10\n'),
    ('S%=2:FOR I%=32766 TO 32767 STEP S%:PRINT I%:NEXT', ' 32766 \nOverflow in 10\n'),
    ('A%=300:B%=200:C%=A%*B%-50000:PRINT C%', ' 10000 \n'),
    ('A%=32767:B%=32767:C%=A%*B%*A%', 'Overflow in 10\n'),
    ('A%=-30000:B%=-30000:C%=A%+B%+A%+B%', 'Overflow in 10\n'),
    # VAL skips blanks inside a decimal number; POS; RESTORE to a line
    ('PRINT VAL(" 1 2");VAL("3 E 2");VAL("1 2.5 x")', ' 12  300  12.5 \n'),
    ('PRINT "abc";POS(1);"x";POS("a")', 'abc 4 x 8 \n'),
    ('DATA 1,2:READ A,B:RESTORE 10:READ C:PRINT A;B;C', ' 1  2  1 \n'),
    # an integer FOR rounds its limit and step like FRCINT (STEP .5 is STEP 1)
    ('FOR I%=0.1 TO 1 STEP 0.5:PRINT I%;:NEXT:PRINT "/";I%', ' 0  1 / 2 \n'),
    ('S=0.5:E=2.6:FOR J%=0 TO E STEP S:PRINT J%;:NEXT:PRINT "/";J%', ' 0  1  2  3 / 4 \n'),
    ('FOR K%=5 TO 0.4 STEP -1.5:PRINT K%;:NEXT:PRINT "/";K%', ' 5  3  1 /-1 \n'),
    # a signed DATA number; READ into a string takes the item as it was typed
    ('DATA +7,-2,1E3:READ A$,B$,C$:RESTORE:READ D:PRINT A$;B$;C$;D', '+7-21E3 7 \n'),
]


@NEEDS_TOOLCHAIN
@pytest.mark.parametrize("body,expected", CASES)
def test_edge(tmp_path, body, expected):
    result = compile_c(tmp_path, f"10 {body}\n20 SYSTEM\n")
    assert result.returncode == 0, result.stdout + result.stderr
    assert run_compiled(tmp_path, "") == expected
