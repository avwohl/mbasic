"""WHILE/WEND pairing, FOR with a string limit, and a call cut short.

Every expected text was measured on MBASIC 5.21 (com/mbasic.com under cpmemu,
tests/HOW_TO_RUN_REAL_MBASIC.md), with ON ERROR GOTO a handler that prints
ERR and ERL and does RESUME NEXT.

- A WEND takes the stack entry that holds its own place (the WHILE stores the
  text pointer of its WEND). A WHILE with a string condition (Type mismatch)
  leaves no entry, so its WEND is "WEND without WHILE" (30) even inside an
  outer WHILE that is still active.
- FOR sets the variable, then reads the limit and the step. A string for
  either is Type mismatch (13), no loop is registered, and the NEXT is
  NEXT without FOR (1).
- A NEXT in an ELSE part of a nested loop is not the NEXT that the inner FOR
  found, so it is NEXT without FOR.
- The number arguments of LEFT$ RIGHT$ MID$ STRING$ INSTR INPUT$ are range
  checked as they are read: MID$("A",0, with the line cut off is Illegal
  function call (5), not Missing operand (22). The same holds for the MID$
  statement with a fourth argument, and for the MID$ statement cut off by the
  end of the line (MID$(A$,0,  and MID$(A$,1,300).
- A NEXT finds its FOR below a WHILE that is still open and discards the
  WHILE entry, so the WEND after the NEXT is WEND without WHILE (30).
  (Interpreter only: the JS semantic analyzer refuses this crossed nesting.)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from basic_runner import NODE, run_interpreter, run_javascript

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: loop and call error tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

HANDLER = '100 PRINT ERR;ERL:RESUME NEXT\n'
CASES = {
    "nested_while_string_condition": (
        '10 ON ERROR GOTO 100\n'
        '20 WHILE 1:PRINT "x":WHILE "a":PRINT "w":WEND:PRINT "y":GOTO 40:WEND\n'
        '40 PRINT "z":SYSTEM\n' + HANDLER,
        "x\n 13  20 \nw\n 30  20 \ny\nz\n"),
    "for_string_limit": (
        '10 ON ERROR GOTO 100\n20 FOR I=1 TO "a":PRINT "w":NEXT\n40 PRINT "z":SYSTEM\n' + HANDLER,
        " 13  20 \nw\n 1  20 \nz\n"),
    "for_string_step": (
        '10 ON ERROR GOTO 100\n20 FOR I=1 TO 2 STEP "a":PRINT "w":NEXT\n40 PRINT "z":SYSTEM\n'
        + HANDLER,
        " 13  20 \nw\n 1  20 \nz\n"),
    "inner_next_in_else_part": (
        '10 ON ERROR GOTO 100\n'
        '40 FOR I=1 TO 2:FOR J=1 TO 2:IF J=1 THEN PRINT I;J:NEXT ELSE PRINT "e":NEXT\n'
        '50 PRINT "d":SYSTEM\n' + HANDLER,
        " 1  1 \ne\n 1  40 \nd\n"),
    "mid_cut_off_after_zero_start": (
        '10 ON ERROR GOTO 100\n20 PRINT MID$("A",0,\n40 PRINT "z":SYSTEM\n' + HANDLER,
        " 5  20 \nz\n"),
    "mid_statement_extra_argument": (
        '10 ON ERROR GOTO 100\n15 A$="abc"\n30 MID$(A$,0,2,3)="x"\n40 PRINT "z":SYSTEM\n'
        + HANDLER,
        " 5  30 \nz\n"),
    "mid_statement_cut_off_zero_start": (
        '10 ON ERROR GOTO 100\n15 A$="abc"\n30 MID$(A$,0,\n40 PRINT "z":SYSTEM\n' + HANDLER,
        " 5  30 \nz\n"),
    "mid_statement_cut_off_long_count": (
        '10 ON ERROR GOTO 100\n15 A$="abc"\n30 MID$(A$,1,300\n40 PRINT "z":SYSTEM\n' + HANDLER,
        " 5  30 \nz\n"),
}

INTERPRETER_ONLY = {
    "next_discards_open_while": (
        '10 ON ERROR GOTO 100\n95 FOR K=1 TO 2:WHILE K:NEXT:WEND\n96 PRINT "e3":SYSTEM\n'
        + HANDLER,
        " 30  95 \ne3\n"),
}


@pytest.mark.parametrize("name", sorted(INTERPRETER_ONLY))
def test_interpreter_only(tmp_path, name):
    source, expected = INTERPRETER_ONLY[name]
    assert run_interpreter(tmp_path, source) == expected


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
