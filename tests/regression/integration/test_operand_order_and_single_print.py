"""The left operand of an integer operator, and the six digits of a single.

Every expected text was measured on MBASIC 5.21 (com/mbasic.com under cpmemu,
tests/HOW_TO_RUN_REAL_MBASIC.md). Both were found by utils/fuzz_real.py.

- AND, OR, XOR, EQV, IMP, \\ and MOD make the left operand a 16-bit integer
  before the right operand is read: 65535 AND 1/0 is Overflow (6), not
  Division by zero (11), and "a" AND 1/0 is Type mismatch (13).
- PRINT and STR$ of a single take its six digits as FOUT does: the number is
  divided or multiplied by ten in single precision, one step at a time, until
  it lies in 99999.95 .. 999999.5, and then .5 is added. 1073774592 prints as
  1.07377E+09 (the nearest six digits), but 1033774976 prints as 1.03378E+09.
  The values are built by exact halving and doubling, so MBASIC's own reading
  of a typed constant (not emulated) cannot change them.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: operand order and single print tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

from basic_runner import NODE, run_interpreter, run_javascript

HANDLER = '100 PRINT "E";ERR;ERL:RESUME NEXT\n'
CASES = {
    "integer_operator_left_first": (
        '10 ON ERROR GOTO 100\n'
        '20 PRINT 65535 AND 1/0\n'
        '30 PRINT 65535 OR 1\\0\n'
        '40 PRINT 65535 \\ (1/0)\n'
        '50 PRINT 65535 MOD (1/0)\n'
        '60 PRINT 65535 IMP 0.25\\0\n'
        '70 PRINT 2.5 AND 1/0\n'
        '80 PRINT 1 IMP 65535\n'
        '90 SYSTEM\n' + HANDLER,
        "E 6  20 \nE 6  30 \nE 6  40 \nE 6  50 \nE 6  60 \nE 11  70 \nE 6  80 \n"),
    "integer_operator_string_operand": (
        '10 ON ERROR GOTO 100\n'
        '20 PRINT "a" AND 1/0\n'
        '30 PRINT "a" MOD 1\\0\n'
        '40 PRINT 65535 AND "a"\n'
        '50 PRINT 1 OR "a"\n'
        '90 SYSTEM\n' + HANDLER,
        "E 13  20 \nE 13  30 \nE 6  40 \nE 13  50 \n"),
    "single_six_digits_as_fout": (
        '10 X!=1073774592!:PRINT X!;-X!;STR$(X!)\n'
        '20 X!=1000*40000+-32769*32768:PRINT X!\n'
        '30 X!=16152734!:FOR J=1 TO 6:X!=X!*2:NEXT:PRINT X!\n'
        '40 X!=13421766!:FOR J=1 TO 27:X!=X!/2:NEXT:PRINT X!\n'
        '50 X!=12945352!:FOR J=1 TO 20:X!=X!/2:NEXT:PRINT X!\n'
        '60 SYSTEM\n',
        " 1.07377E+09 -1.07377E+09  1.07377E+09\n-1.03377E+09 \n 1.03378E+09 \n"
        " .1 \n 12.3456 \n"),
}


@pytest.mark.parametrize("name", sorted(CASES))
def test_interpreter(tmp_path, name):
    source, expected = CASES[name]
    assert run_interpreter(tmp_path, source) == expected


@pytest.mark.skipif(NODE is None, reason="Node.js is needed to execute generated JavaScript")
@pytest.mark.parametrize("name", sorted(CASES))
def test_javascript(tmp_path, name):
    source, expected = CASES[name]
    assert run_javascript(tmp_path, source) == expected


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
