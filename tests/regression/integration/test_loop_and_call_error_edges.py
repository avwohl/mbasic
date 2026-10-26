"""WHILE/WEND pairing, FOR with a string limit, and a call cut short.

Every expected text was measured on MBASIC 5.21 (com/mbasic.com under cpmemu,
tests/HOW_TO_RUN_REAL_MBASIC.md), with ON ERROR GOTO a handler that prints
ERR and ERL and does RESUME NEXT.

- A WEND takes the stack entry that holds its own place (the WHILE stores the
  text pointer of its WEND). A WHILE with a string condition (Type mismatch)
  leaves no entry, so its WEND is "WEND without WHILE" (30) even inside an
  outer WHILE that is still active.
- FOR reads the limit and the step before it sets the variable. A string for
  either is Type mismatch (13), the variable keeps its old value, no loop is
  registered, and the NEXT is NEXT without FOR (1). A FOR with no NEXT is
  FOR Without NEXT (26), and the variable keeps its old value too.
- A NEXT in an ELSE part of a nested loop is not the NEXT that the inner FOR
  found, so it is NEXT without FOR.
- The number arguments of LEFT$ RIGHT$ MID$ STRING$ INSTR INPUT$ are range
  checked as they are read: MID$("A",0, with the line cut off is Illegal
  function call (5), not Missing operand (22). The same holds for the MID$
  statement with a fourth argument, and for the MID$ statement cut off by the
  end of the line (MID$(A$,0,  and MID$(A$,1,300).
- A FOR with a double-precision variable (I#, or a DEFDBL letter) is Type
  mismatch (13) after the start is worked out and before the limit is read;
  the variable keeps its value.
- A FOR enters the NEXT its scan ends at. When that NEXT names another
  variable (FOR I ... NEXT J, or a FOR L whose scan ends at NEXT K), the FOR
  is NEXT without FOR (1), reported at the line of the NEXT, before the body
  runs and before the variable is set. RESUME NEXT goes on after the FOR.
- RESUME and RESUME NEXT make ERL the current line: until a new line starts,
  an error on the line they go back to is reported at ERL (the line of the
  NEXT above, the DATA line after READ of a bad item).
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
    "for_error_keeps_variable": (
        '10 ON ERROR GOTO 100\n20 I=7:FOR I=5 TO "a":PRINT "w":NEXT\n30 PRINT "I=";I\n'
        '40 J=7:FOR J=5 TO 6:PRINT "b"\n50 PRINT "J=";J:SYSTEM\n' + HANDLER,
        " 13  20 \nw\n 1  20 \nI= 7 \n 26  40 \nb\nJ= 7 \n"),
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
    'for_next_of_another_name': (
        '10 ON ERROR GOTO 100\n'
        '20 I=9:FOR I=1 TO 2:PRINT "a":NEXT J\n'
        '30 PRINT "I=";I\n'
        '40 FOR K=1 TO 2:FOR L=1 TO 2:PRINT "b";\n'
        '50 NEXT K:PRINT "c"\n'
        '60 PRINT "d":X=1/0:PRINT "e"\n'
        '70 PRINT "f"\n'
        '80 END\n'
        '100 PRINT "E";ERR;ERL:RESUME NEXT\n',
        'E 1  20 \na\nE 1  20 \nI= 9 \nE 26  40 \nE 1  50 \nbE 1  50 \nc\nd\nE 11  60 \ne\nf\n'),
    'erl_stays_after_resume_from_for': (
        '10 ON ERROR GOTO 100\n'
        '20 FOR I=1 TO 2:X=1/0:PRINT "a"\n'
        '30 NEXT J\n'
        '40 END\n'
        '100 PRINT "E";ERR;ERL:RESUME NEXT\n',
        'E 1  30 \nE 11  30 \na\nE 1  30 \n'),
    'erl_stays_after_resume_from_data': (
        '10 ON ERROR GOTO 100\n'
        '20 READ A:X=1/0:PRINT "a"\n'
        '25 X=1/0\n'
        '30 DATA "x"\n'
        '40 END\n'
        '100 PRINT "E";ERR;ERL:RESUME NEXT\n',
        'E 2  30 \nE 11  30 \na\nE 11  25 \n'),
    'for_double_variable': (
        '10 ON ERROR GOTO 100\n'
        '20 FOR I#=1/0 TO 2:PRINT "b":NEXT\n'
        '30 DEFDBL D:FOR D=1 TO 2:PRINT "c":NEXT\n'
        '40 FOR J!=1 TO 1:PRINT "d":NEXT\n'
        '50 FOR K#=1 TO "a":NEXT\n'
        '60 END\n'
        '100 PRINT "E";ERR;ERL:RESUME NEXT\n',
        'E 11  20 \nb\nE 1  20 \nE 13  30 \nc\nE 1  30 \nd\nE 13  50 \nE 1  50 \n'),
    'for_double_variable_order': (
        '10 ON ERROR GOTO 100\n'
        '20 K#=7:FOR K#=1 TO 1/0:PRINT "b";K#:NEXT\n'
        '30 K#=7:FOR K#=5 TO 9:PRINT "c";K#\n'
        '40 PRINT K#\n'
        '60 END\n'
        '100 PRINT "E";ERR;ERL:RESUME NEXT\n',
        'E 13  20 \nb 7 \nE 1  20 \nE 13  30 \nc 7 \n 7 \n'),
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
