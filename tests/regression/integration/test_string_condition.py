"""A string used as a condition is Type mismatch (IF, WHILE).

Every expected text was measured on MBASIC 5.21 (com/mbasic.com under cpmemu,
tests/HOW_TO_RUN_REAL_MBASIC.md):

- 10 IF "a" THEN PRINT "y" is "Type mismatch in 10", and so are IF "" THEN ...
  ELSE ..., IF A$ THEN and IF NOT "a" THEN. A comparison of strings is a number
  and is fine: IF "a"="a" THEN prints y.
- WHILE "a" is "Type mismatch in 10" before the loop is entered. With a handler
  that ends in RESUME NEXT the body runs once, and then the WEND finds no WHILE:
  "WEND without WHILE" (error 30) at the line of the WHILE.
- The same error is trapped as ERR 13 and the IF line goes on after the IF.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from basic_runner import NODE, run_interpreter, run_javascript

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: string condition tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

TYPE_MISMATCH = "Type mismatch in 10\n"

CASES = {
    "if_string": ('10 IF "a" THEN PRINT "y"\n20 PRINT "z"\n', TYPE_MISMATCH),
    "if_empty_string_else": ('10 IF "" THEN PRINT "y" ELSE PRINT "n"\n', TYPE_MISMATCH),
    "if_variable": ('10 A$="x":IF A$ THEN PRINT "y"\n', TYPE_MISMATCH),
    "if_then_else": ('10 IF "a" THEN PRINT "y" ELSE PRINT "n"\n', TYPE_MISMATCH),
    "if_not_string": ('10 IF NOT "a" THEN PRINT "y"\n', TYPE_MISMATCH),
    "if_and_string": ('10 IF 1 AND "a" THEN PRINT "y"\n', TYPE_MISMATCH),
    "if_comparison_is_fine": ('10 IF "a"="a" THEN PRINT "y"\n', "y\n"),
    "if_comparison_and": ('10 IF ("a"="a") AND 1 THEN PRINT "y"\n', "y\n"),
    "while_string": ('10 WHILE "a":PRINT "w":WEND\n', TYPE_MISMATCH),
    "while_empty_variable": ('10 A$="":WHILE A$:PRINT "w":WEND:PRINT "e"\n', TYPE_MISMATCH),
    "while_not_string": ('10 WHILE NOT "a":PRINT "w":WEND:PRINT "e"\n', TYPE_MISMATCH),
    "on_goto_string": ('10 ON "a" GOTO 20,30\n20 PRINT "20"\n30 PRINT "30"\n', TYPE_MISMATCH),
    "on_goto_variable": ('10 A$="1":ON A$ GOTO 20,30\n20 PRINT "20"\n30 PRINT "30"\n', TYPE_MISMATCH),
    # ERR 13 at line 20; RESUME NEXT goes on behind the whole IF line
    "if_trapped": (
        '10 ON ERROR GOTO 100\n20 IF "a" THEN PRINT "y"\n30 PRINT "after"\n40 END\n'
        '100 PRINT ERR;ERL:RESUME NEXT\n',
        " 13  20 \nafter\n"),
    # RESUME NEXT runs the body (w); its WEND has no WHILE (ERR 30, ERL 20); RESUME NEXT goes on to z
    "while_trapped": (
        '10 ON ERROR GOTO 100\n20 WHILE "a":PRINT "w":WEND:PRINT "z"\n40 END\n'
        '100 PRINT ERR;ERL:RESUME NEXT\n',
        " 13  20 \nw\n 30  20 \nz\n"),
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
