"""LOC and LOF of a file count sectors of 128 bytes.

Every expected text was measured on MBASIC 5.21 (com/mbasic.com under cpmemu,
tests/HOW_TO_RUN_REAL_MBASIC.md):

- LOC of an input file is the sectors read so far: 1 after the OPEN, then the
  position rounded up (128 bytes read is 1, 144 is 2). EOF does not change it.
- LOC of an output file is the sectors written out: the position rounded down
  (0 after the OPEN, 5 after 711 bytes).
- A line end is CR LF, two bytes, as in a CP/M file. The interpreter and the
  JavaScript backend write LF only and count each lone LF as two bytes.
- LOF is the size when the file was opened, rounded up; LOC of a random file
  is the record of the last GET or PUT.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from basic_runner import NODE, run_interpreter, run_javascript

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: LOC and LOF tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

CASES = {
    'line_by_line': (
        '10 OPEN "O",#1,"zl.dat":FOR I=1 TO 40:PRINT #1,"abcdefghijklmn":NEXT:CLOSE\n'
        '20 OPEN "I",#1,"zl.dat":P=0\n'
        '30 FOR I=1 TO 40:LINE INPUT #1,A$:P=P+16:PRINT P;LOC(1);:IF I MOD 8=0 THEN PRINT\n'
        '40 NEXT:PRINT:CLOSE\n'
        '50 OPEN "I",#1,"zl.dat":FOR I=1 TO 16:INPUT #1,A$:NEXT:PRINT LOC(1);:X$=INPUT$(1,#1):PRINT LOC(1):CLOSE\n'
        '80 KILL "zl.dat":END\n',
        ' 16  1  32  1  48  1  64  1  80  1  96  1  112  1  128  1 \n 144  2  160  2  176  2  192  2  208  2  224  2  240  2  256  2 \n 272  3  288  3  304  3  320  3  336  3  352  3  368  3  384  3 \n 400  4  416  4  432  4  448  4  464  4  480  4  496  4  512  4 \n 528  5  544  5  560  5  576  5  592  5  608  5  624  5  640  5 \n\n 2  3 \n'),
    'sizes': (
        '10 OPEN "O",#1,"zl.dat":PRINT LOF(1);LOC(1)\n'
        '20 FOR I=1 TO 40:PRINT #1,"line number ";I:NEXT:PRINT LOF(1);LOC(1):CLOSE\n'
        '30 OPEN "I",#1,"zl.dat":PRINT "in";LOF(1);LOC(1)\n'
        '40 FOR I=1 TO 40:LINE INPUT #1,A$:IF I MOD 5=0 THEN PRINT I;LOC(1);\n'
        '50 NEXT:PRINT:CLOSE\n'
        '60 OPEN "O",#1,"zm.dat":PRINT #1,"abc":CLOSE:OPEN "I",#1,"zm.dat":PRINT LOF(1);LOC(1):CLOSE\n'
        '70 OPEN "R",#1,"zr.dat",10:FIELD #1,10 AS F$:LSET F$="x":PUT #1,3:PRINT LOF(1);LOC(1):CLOSE:OPEN "R",#1,"zr.dat",10:PRINT LOF(1):CLOSE\n'
        '80 KILL "zl.dat":KILL "zm.dat":KILL "zr.dat":END\n',
        ' 0  0 \n 0  5 \nin 6  1 \n 5  1  10  2  15  3  20  3  25  4  30  5  35  5  40  6 \n 1  1 \n 0  3 \n 1 \n'),
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
