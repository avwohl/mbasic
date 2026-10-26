"""The operands of OPEN: a mode that is a variable or an expression, and the order of the errors.

Every expected text was measured on MBASIC 5.21 (com/mbasic.com under cpmemu,
tests/HOW_TO_RUN_REAL_MBASIC.md) started with /F:15. The binary:

- takes the mode from any string expression (OPEN M$,#1,F$ and OPEN CHR$(79),...).
  Only the first letter counts: "Output" is "O", "o" is "O". Before, a mode
  that was not a literal was always input;
- checks the operands in this order: the mode (a number is Type mismatch, a
  first letter that is not I, O or R is Bad file mode, and so is ""), then
  the file number (Bad file number), then the name (a number is Type mismatch),
  then File already open, then the file itself (File not found);
- reads the record length for a random file only. For another mode it opens
  the file first (File not found comes before) and then says Syntax error; the
  file stays open.

This interpreter keeps OPEN "A" (append) as an extension, where the binary says
Bad file mode, so no test here uses it.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from basic_runner import NODE, run_interpreter, run_javascript

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: OPEN operand tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

F = '"ZZ1.DAT"'


def line10(text):
    return f"10 {text}\n"


CASES = {
    "mode_variable_output": (line10('M$="O":OPEN M$,#1,' + F + ':PRINT #1,"x":CLOSE:OPEN "I",#1,'
                                    + F + ':LINE INPUT #1,A$:PRINT A$'), "x\n"),
    "mode_variable_lower_case": (line10('M$="o":OPEN M$,#1,' + F + ':PRINT #1,"x":CLOSE:OPEN "i",#1,'
                                        + F + ':LINE INPUT #1,A$:PRINT A$'), "x\n"),
    "mode_word_first_letter": (line10('OPEN "OUTPUT",#1,' + F + ':PRINT #1,"x":CLOSE:OPEN "I",#1,'
                                      + F + ':LINE INPUT #1,A$:PRINT A$'), "x\n"),
    "mode_variable_word": (line10('M$="Output":OPEN M$,#1,' + F + ':PRINT "ok"'), "ok\n"),
    "mode_function": (line10('OPEN CHR$(79),#1,' + F + ':PRINT #1,"x":CLOSE:PRINT "ok"'), "ok\n"),
    "mode_concatenation_is_input": (line10('OPEN "I"+"",#1,' + F), "File not found in 10\n"),
    "mode_empty": (line10('OPEN "",#1,' + F), "Bad file mode in 10\n"),
    "mode_unknown_letter": (line10('OPEN "Q",#1,' + F), "Bad file mode in 10\n"),
    "mode_unknown_in_variable": (line10('M$="X":OPEN M$,#1,' + F), "Bad file mode in 10\n"),
    "mode_number": (line10("OPEN 1,#1," + F), "Type mismatch in 10\n"),
    # the mode is checked before the file number and the name
    "bad_mode_before_file_number": (line10('OPEN "Q",#99,' + F), "Bad file mode in 10\n"),
    "bad_mode_before_name_type": (line10('OPEN "Q",#1,1'), "Bad file mode in 10\n"),
    "bad_mode_before_both": (line10('OPEN "Q",#99,1'), "Bad file mode in 10\n"),
    "empty_mode_before_both": (line10('OPEN "",#99,1'), "Bad file mode in 10\n"),
    "bad_mode_before_length_type": (line10('OPEN "Q",#1,' + F + ',"x"'), "Bad file mode in 10\n"),
    "bad_mode_before_already_open": (
        line10('OPEN "O",#1,' + F + ':OPEN "Q",#1,"ZZ2.DAT"'), "Bad file mode in 10\n"),
    "number_mode_before_file_number": (line10("OPEN 1,#99," + F), "Type mismatch in 10\n"),
    # the file number before the name
    "file_number_before_name_type": (line10('OPEN "O",#99,1'), "Bad file number in 10\n"),
    "name_type": (line10('OPEN "O",#1,1'), "Type mismatch in 10\n"),
    "name_type_before_length": (line10('OPEN "O",#1,1,5'), "Type mismatch in 10\n"),
    "already_open_before_file_not_found": (
        line10('OPEN "O",#1,' + F + ':OPEN "I",#1,"NOFILE.DAT"'), "File already open in 10\n"),
    "already_open": (line10('OPEN "O",#1,' + F + ':OPEN "O",#1,"ZZ2.DAT"'), "File already open in 10\n"),
    # a record length is for a random file only
    "length_for_output": (line10('OPEN "O",#1,' + F + ',5'), "Syntax error in 10\n"),
    "length_for_output_not_read": (line10('OPEN "O",#1,' + F + ',"x"'), "Syntax error in 10\n"),
    "length_for_input_file_not_found": (line10('OPEN "I",#1,"NOFILE.DAT",5'), "File not found in 10\n"),
    "length_not_read_for_input": (line10('OPEN "I",#1,"NOFILE.DAT","x"'), "File not found in 10\n"),
    "length_type_for_random": (line10('OPEN "R",#1,' + F + ',"x"'), "Type mismatch in 10\n"),
    "length_fraction_for_random": (line10('OPEN "R",#1,' + F + ',5.5:PRINT "ok"'), "ok\n"),
    # trapped, and the file stays open after the Syntax error
    "mode_errors_trapped": (
        '10 ON ERROR GOTO 100\n20 M$="O":OPEN M$,#1,' + F + ':PRINT #1,"x":CLOSE\n'
        '30 M$="X":OPEN M$,#1,' + F + ':PRINT "no"\n40 M=1:OPEN M,#1,' + F + ':PRINT "no2"\n'
        '50 END\n100 PRINT ERR;ERL:RESUME NEXT\n',
        " 54  30 \nno\n 13  40 \nno2\n"),
    "length_error_leaves_file_open": (
        '10 ON ERROR GOTO 100\n20 OPEN "O",#1,' + F + ',5:PRINT "after"\n'
        '30 PRINT #1,"hi":CLOSE:PRINT "closed"\n40 OPEN "I",#1,' + F + ':LINE INPUT #1,A$:PRINT A$\n'
        '50 END\n100 PRINT ERR;ERL:RESUME NEXT\n',
        " 2  20 \nafter\nclosed\nhi\n"),
    "length_error_then_open_again": (
        '10 ON ERROR GOTO 100\n20 OPEN "O",#1,' + F + ',5\n30 OPEN "O",#1,"ZZ2.DAT"\n40 END\n'
        '100 PRINT ERR;ERL:RESUME NEXT\n',
        " 2  20 \n 55  30 \n"),
    "file_not_found_trapped": (
        '10 ON ERROR GOTO 100\n20 OPEN "I",1,"NOFILE.DAT":PRINT "n"\n30 END\n'
        '100 PRINT ERR;ERL:RESUME NEXT\n',
        " 53  20 \nn\n"),
}

# the JavaScript random-file statements (FIELD, LSET, GET, PUT) do not work yet
INTERPRETER_ONLY = {
    "random_mode_variable": (
        '10 M$="R":OPEN M$,#1,' + F + ',10:FIELD #1,10 AS A$:LSET A$="hi":PUT #1,1:CLOSE\n'
        '20 OPEN "R",#1,' + F + ',10:FIELD #1,10 AS B$:GET #1,1:PRINT B$\n',
        "hi        \n"),
}


@pytest.mark.parametrize("name", sorted(CASES) + sorted(INTERPRETER_ONLY))
def test_interpreter(tmp_path, name):
    source, expected = {**CASES, **INTERPRETER_ONLY}[name]
    assert run_interpreter(tmp_path, source) == expected


@pytest.mark.skipif(NODE is None, reason="Node.js is needed to execute generated JavaScript")
@pytest.mark.parametrize("name", sorted(CASES))
def test_javascript(tmp_path, name):
    source, expected = CASES[name]
    assert run_javascript(tmp_path, source) == expected


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
