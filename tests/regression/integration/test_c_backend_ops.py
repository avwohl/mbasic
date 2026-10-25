"""C backend: integer operators and FOR with STEP 0 (issues 54 and 55).

Expected output is what real MBASIC 5.21 printed for the same program.

Issue 54: the operands of \\, MOD, AND, OR, XOR, EQV, IMP and NOT are rounded
half away from zero; a value outside -32768..32767 after rounding is Overflow
(32767.4 is allowed, 32767.5 and -32768.5 are not).  The operands are checked
before the divisor, so 40000\\0 is Overflow and 5\\0 is Division by zero.

Issue 55: a FOR loop with STEP 0 ends only when the variable equals the limit,
at FOR and at NEXT.  (1,3) and (3,1) loop forever, (2,2) never runs the body.
"""
import sys
from pathlib import Path

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: C backend operator tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_c_backend import NEEDS_TOOLCHAIN, compile_c, run_compiled  # noqa: E402


def run_c(tmp_path, source):
    result = compile_c(tmp_path, source)
    assert result.returncode == 0, result.stdout + result.stderr
    return run_compiled(tmp_path, "")


# Measured on real MBASIC 5.21: (program, output).  Each program stops at its
# first error, so each error case is a program of its own.
OVERFLOW_CASES = [
    ("A=40000:PRINT A MOD 3", "Overflow in 10\n"),
    ("A=40000:PRINT A\\3", "Overflow in 10\n"),
    ("A=40000:PRINT A OR 1", "Overflow in 10\n"),
    ("A=40000:PRINT NOT A", "Overflow in 10\n"),
    ("PRINT 65535 AND 1", "Overflow in 10\n"),
    ("PRINT 1 XOR 70000", "Overflow in 10\n"),
    ("PRINT 1 EQV 40000", "Overflow in 10\n"),
    ("PRINT 1 IMP 40000", "Overflow in 10\n"),
    ("PRINT 32767.5 OR 0", "Overflow in 10\n"),
    ("PRINT -32769 OR 0", "Overflow in 10\n"),
    ("PRINT -32768.5 OR 0", "Overflow in 10\n"),
    ("A=0:PRINT 5 MOD A", "Division by zero in 10\n"),
    ("A=0:PRINT 5\\A", "Division by zero in 10\n"),
    ("PRINT 40000\\0", "Overflow in 10\n"),
]


@NEEDS_TOOLCHAIN
@pytest.mark.parametrize("body,expected", OVERFLOW_CASES)
def test_integer_operand_errors(tmp_path, body, expected):
    assert run_c(tmp_path, f"10 {body}\n20 PRINT \"after\"\n") == expected


@NEEDS_TOOLCHAIN
def test_integer_operands_in_range(tmp_path):
    """Boundary values that real MBASIC accepts, and rounding of 2.5."""
    source = ('10 PRINT 32767.4 OR 0\n20 PRINT -32768.4 AND -1\n'
              '30 A=2.5\n40 PRINT 7\\A;7 MOD A;NOT A;1 EQV 3;1 IMP 0;1 XOR A\n')
    assert run_c(tmp_path, source) == " 32767 \n-32768 \n 2  1 -4 -3 -2  2 \n"


STEP0_BODY = ('10 N=0\n20 FOR I={a} TO {b} STEP {s}\n30 N=N+1\n40 PRINT I;N\n'
              '50 IF N>=4 THEN PRINT "STOP":SYSTEM\n60 NEXT I\n70 PRINT "DONE"\n80 SYSTEM\n')
LOOPS = " 1  1 \n 1  2 \n 1  3 \n 1  4 \nSTOP\n"
LOOPS_3 = " 3  1 \n 3  2 \n 3  3 \n 3  4 \nSTOP\n"


@NEEDS_TOOLCHAIN
@pytest.mark.parametrize("a,b,expected", [(1, 3, LOOPS), (3, 1, LOOPS_3), (2, 2, "DONE\n")])
@pytest.mark.parametrize("step_line", ["constant", "variable"])
def test_for_step_zero(tmp_path, a, b, expected, step_line):
    source = STEP0_BODY.format(a=a, b=b, s="0" if step_line == "constant" else "Z")
    if step_line == "variable":
        source = source.replace("10 N=0\n", "10 N=0:Z=0\n")
    assert run_c(tmp_path, source) == expected


@NEEDS_TOOLCHAIN
def test_for_variable_step_keeps_its_direction(tmp_path):
    source = ('10 Z=-1:FOR I=3 TO 1 STEP Z:PRINT I;:NEXT I:PRINT\n'
              '20 Z=1:FOR I=1 TO 3 STEP Z:PRINT I;:NEXT I:PRINT\n'
              '30 Z=1:FOR I=3 TO 1 STEP Z:PRINT I;:NEXT I:PRINT "none"\n')
    assert run_c(tmp_path, source) == " 3  2  1 \n 1  2  3 \nnone\n"
