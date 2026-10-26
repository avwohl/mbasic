"""CVI, CVS and CVD of a long string, and the order of argument errors.

Every expected text was measured on MBASIC 5.21 (com/mbasic.com under cpmemu,
tests/HOW_TO_RUN_REAL_MBASIC.md). A random test of the built-in functions
against the binary found these:

- CVI, CVS and CVD read the first 2, 4 or 8 bytes of a longer string
  (CVI("abc") is 25185). A shorter string is Illegal function call (5); the
  interpreter refused a longer one and the JavaScript backend did not check.
- An argument that the binary range-checks as it reads it (the start of
  MID$, the count of LEFT$ and STRING$) gives Illegal function call before a
  later argument can give Type mismatch: MID$("a",-1,"x") and
  STRING$(300,"a"+1) are error 5.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from basic_runner import NODE, run_interpreter, run_javascript

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: function argument tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

CASES = {
    'cv_long_and_short': (
        '10 ON ERROR GOTO 100\n'
        '20 PRINT CVI("ab");CVI("abc")\n'
        '30 PRINT CVI("a")\n'
        '40 PRINT CVS(MKS$(1.5)+"zz");CVD(MKD$(2.5)+"q")\n'
        '50 X=CVS("abc")\n'
        '60 X=CVD("abcdefg")\n'
        '95 PRINT "z":END\n'
        '100 PRINT "E";ERR;ERL:RESUME NEXT\n',
        ' 25185  25185 \nE 5  30 \n 1.5  2.5 \nE 5  50 \nE 5  60 \nz\n'),
    'range_before_type': (
        '10 ON ERROR GOTO 100\n'
        '20 PRINT MID$("&H41",-1,"a")\n'
        '30 PRINT MID$("",-1,"A")\n'
        '40 PRINT MID$("abc",0,"A")\n'
        '50 PRINT MID$("abc",2,"A")\n'
        '60 PRINT LEFT$("abc",-1,"x")\n'
        '70 PRINT STRING$(-1,2.5)\n'
        '80 PRINT STRING$(300,"a"+1)\n'
        '90 END\n'
        '100 PRINT "E";ERR;ERL:RESUME NEXT\n',
        'E 5  20 \nE 5  30 \nE 5  40 \nE 13  50 \nE 5  60 \nE 5  70 \nE 5  80 \n'),
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
