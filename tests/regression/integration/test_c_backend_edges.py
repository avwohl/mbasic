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
- VAL reads &H and &O numbers as 16-bit words.  HEX$ and OCT$ of a value outside
  -32768..65535 are Overflow.
- SQR of a negative number, LOG of zero or less, and a negative base with a
  fractional exponent give Illegal function call.
- A float division by zero, a float overflow and EXP(100) print Division by zero
  or Overflow on a line of their own and go on with the largest float.
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
]


@NEEDS_TOOLCHAIN
@pytest.mark.parametrize("body,expected", CASES)
def test_edge(tmp_path, body, expected):
    result = compile_c(tmp_path, f"10 {body}\n20 SYSTEM\n")
    assert result.returncode == 0, result.stdout + result.stderr
    assert run_compiled(tmp_path, "") == expected
