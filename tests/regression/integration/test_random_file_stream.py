"""PRINT#, WRITE#, INPUT# and LINE INPUT# on a random file use its record buffer.

The expected text was measured on MBASIC 5.21 (com/mbasic.com under cpmemu,
tests/HOW_TO_RUN_REAL_MBASIC.md):

- The statements work on the record buffer at a cursor. A line ends in CR LF.
  GET and PUT send the cursor back to the front of the record.
- A write that does not fit fills the record and then is FIELD overflow (50).
- A read that reaches the end of the record before the end of its item is
  FIELD overflow too (INPUT# of the blanks after the last line).
- The FIELD variables show the buffer at once.

The program blanks the buffer with LSET first: the binary starts a random file
with whatever was in that memory, and this interpreter with blanks.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from basic_runner import NODE, run_interpreter, run_javascript

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: random file stream tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

SOURCE = (
    '10 ON ERROR GOTO 900\n'
    '20 OPEN "R",#1,"zrp.dat",12:FIELD #1,12 AS F$:LSET F$=""\n'
    '30 PRINT #1,"HELLO";:PRINT #1,"AB":GOSUB 800\n'
    '50 PUT #1,1:PRINT #1,"XY":GOSUB 800\n'
    '70 PRINT #1,"0123456789":GOSUB 800\n'
    '90 PUT #1,2:GET #1,1:GOSUB 800\n'
    '100 INPUT #1,A$:PRINT "A=";A$\n'
    '110 INPUT #1,B$:PRINT "B=";B$\n'
    '120 GET #1,1:LINE INPUT #1,C$:PRINT "C=";C$\n'
    '130 WRITE #1,1,"z":GOSUB 800\n'
    '135 GET #1,2:INPUT #1,N:PRINT "N=";N\n'
    '140 CLOSE:KILL "zrp.dat":END\n'
    '800 FOR I=1 TO 12:PRINT ASC(MID$(F$,I,1));:NEXT:PRINT:RETURN\n'
    '900 PRINT "E";ERR;ERL:RESUME NEXT\n'
)
EXPECTED = ' 72  69  76  76  79  65  66  13  10  32  32  32 \n 88  89  13  10  79  65  66  13  10  32  32  32 \nE 50  70 \n 88  89  13  10  48  49  50  51  52  53  54  55 \n 72  69  76  76  79  65  66  13  10  32  32  32 \nA=HELLOAB\nE 50  110 \nB=\nC=HELLOAB\nE 50  130 \n 72  69  76  76  79  65  66  13  10  49  44  34 \nN= 0 \n'


def test_interpreter(tmp_path):
    assert run_interpreter(tmp_path, SOURCE) == EXPECTED


@pytest.mark.skipif(NODE is None, reason="Node.js is needed to execute generated JavaScript")
def test_javascript(tmp_path):
    assert run_javascript(tmp_path, SOURCE) == EXPECTED


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
