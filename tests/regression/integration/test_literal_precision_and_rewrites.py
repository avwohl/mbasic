"""Number literal precision, string length, and the rewrites of the compiler.

Every expected text was measured on MBASIC 5.21 (com/mbasic.com under cpmemu,
tests/HOW_TO_RUN_REAL_MBASIC.md). A random PRINT test against the binary found
the three faults:

- A numeric constant is double when more than 7 digits are typed from the
  first one that is not 0, trailing zeros included: 1000000.0, 10000000 and
  123456.70 are double, 0.1234567, 01234567 and .001234567 are single.
- A string holds at most 255 characters: A$+A$ of 400 is String too long (15),
  in the JavaScript backend too.
- The semantic analyzer must not rewrite X AND -1, X OR 0 or X XOR 0 to X
  (the operators round to 16-bit integers: 2.6 AND -1 is 3, 40000 OR 0 is
  Overflow), nor X * 1# to X (the result is double). The JavaScript backend
  uses the rewritten tree. The constant folder rounds the operands of the
  logical operators to 16-bit integers too, and gives up on one out of range.
- VAL stops at the MBF range: above 1.70141E+38 is Overflow (6), below
  2^-129 is 0. (After that Overflow the binary's RESUME NEXT goes astray, so
  the test resumes at a line number.)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from basic_runner import NODE, run_interpreter, run_javascript

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: literal and rewrite tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

CASES = {
    'literal_8_digits_is_double': (
        '10 PRINT 1000000.0;1000000!;1E6;1000000;CSNG(1000000.0)\n'
        '20 PRINT 9999999.0;10000000.0;999999.0;1234567.0;100000.0\n'
        '30 A=1000000.0:PRINT A;STR$(1000000.0);1E6*1\n'
        '40 PRINT 1000000.0#;1D6;0.1;.01;1E-7\n'
        '50 END\n',
        ' 1000000  1E+06  1E+06  1E+06  1E+06 \n 9999999  10000000  999999  1234567  100000 \n 1E+06  1000000 1E+06 \n 1000000  1000000  .1  .01  .0000001 \n'),
    'literal_digits_counted': (
        '10 PRINT 0000001.0;0.1234567;.1234567;.12345678;00.1234567\n'
        '20 PRINT 1234567.0E0;12345678E-1;1.000000E3;1.0000000E3;100000.00\n'
        '30 PRINT 0.0000001;1.0000000;10000000;0000000000001\n'
        '40 PRINT 123456.7;1234567.;12345670;.0012345678\n'
        '50 PRINT 10000000!;1234567.0!;1D0;-1234567.0\n'
        '60 END\n',
        ' 1  .123457  .123457  .12345678  .123457 \n 1234567  1234567.8  1000  1000  100000 \n .0000001  1  10000000  1 \n 123457  1.23457E+06  12345670  .0012345678 \n 1E+07  1.23457E+06  1 -1234567 \n'),
    'literal_leading_zeros': (
        '10 PRINT 01234567;.001234567;0.001234567;123456.70;1234567.00\n'
        '20 PRINT 001234567;.0000001234567;1.234567E-3;1.2345670E-3;12345.670\n'
        '30 END\n',
        ' 1.23457E+06  1.23457E-03  1.23457E-03  123456.7  1234567 \n 1.23457E+06  1.23457E-07  1.23457E-03  .001234567  12345.67 \n'),
    'identities_keep_rounding_and_precision': (
        '10 ON ERROR GOTO 100:A=1/3:B=.3:Z=0:H=.5\n'
        '20 PRINT (A+Z)*1#;(A+Z)+0#;(A+Z)-0#;(A+Z)/1#\n'
        '30 PRINT (B+B+2) AND -1;(B+B+2) AND (B+B+2);(B+B+2) OR 0;(B+B+2) XOR 0\n'
        '40 PRINT (B+B+2) OR (B+B+2);(B+2.3) AND ((B+2.3) OR 7)\n'
        '50 PRINT (H+1)*4;(H+1)*2;(H+5)\\2;(H+5)/4;(H+1)^2;(B+1)^3\n'
        '60 PRINT (Z+40000) AND -1;(Z+40000) XOR 0;(Z+40000) AND (Z+40000)\n'
        '70 PRINT -(-(A+Z));NOT(NOT(B+2))\n'
        '80 END\n'
        '100 PRINT "E";ERR;ERL:RESUME NEXT\n',
        ' .3333333432674408  .3333333432674408  .3333333432674408  .3333333432674408 \n 3  3  3  3 \n 3  3 \n 6  3  3  1.375  2.25  2.197 \nE 6  60 \n .333333  2 \n'),
    'folded_logical_operands': (
        '10 ON ERROR GOTO 100\n'
        '20 PRINT (15 EQV 7)+(-32769 XOR -32769)\n'
        '30 PRINT (2.6 AND 3)+0;NOT 2.6;(NOT 40000)+1\n'
        '40 END\n'
        '100 PRINT "E";ERR;ERL:RESUME NEXT\n',
        'E 6  20 \n 3 -4 E 6  30 \n'),
    'val_range': (
        '10 ON ERROR GOTO 100\n'
        '20 PRINT VAL("1.7014E38")\n'
        '30 N=1:PRINT VAL("1.702E38")\n'
        '40 N=2:PRINT VAL("-1E39")\n'
        '50 PRINT VAL("1E-39"):PRINT VAL("1E-38")\n'
        '60 END\n'
        '100 PRINT "E";ERR;ERL:IF N=1 THEN RESUME 40 ELSE RESUME 50\n',
        ' 1.7014D+38 \nE 6  30 \nE 6  40 \n 0 \n 1D-38 \n'),
    'string_too_long': (
        '10 ON ERROR GOTO 100\n'
        '20 A$=STRING$(200,"a"):B$=A$+A$:PRINT LEN(B$)\n'
        '30 B$=A$+STRING$(55,"b"):PRINT LEN(B$)\n'
        '40 PRINT LEN(A$+A$)\n'
        '50 PRINT "z":END\n'
        '100 PRINT "E";ERR;ERL:RESUME NEXT\n',
        'E 15  20 \n 0 \n 255 \nE 15  40 \nz\n'),
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
