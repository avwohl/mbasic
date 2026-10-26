"""DATA text after a closing quote ("q"x), and ON ERROR GOTO 0 after a READ error.

Every expected text was measured on MBASIC 5.21 (com/mbasic.com under cpmemu,
tests/HOW_TO_RUN_REAL_MBASIC.md). The binary:

- reads the quoted string, stores it in the variable, and then stops with a
  Syntax error reported at the DATA line when it finds text behind the closing
  quote (the quote followed by x, a space and x, a digit, or a '). Spaces up to a
  comma, a colon or the end of the line are fine ("q" ,5);
- puts the DATA pointer back to where the READ statement began, so the same
  item is read again by the next READ and gives the same error;
- READ into a number variable of such an item is a Syntax error at the DATA
  line as well (every quoted item is);
- reports ON ERROR GOTO 0 inside the handler of a READ error at the DATA line
  (the line that ERL shows), not at the READ line.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from basic_runner import NODE, run_interpreter, run_javascript

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: DATA quote tail tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

HANDLER = '100 PRINT ERR;ERL;A$:RESUME NEXT\n'

CASES = {
    "text_after_quote": ('10 DATA "q"x\n20 PRINT "start"\n30 READ A$:PRINT A$\n',
                         "start\nSyntax error in 10\n"),
    "space_then_text": ('10 DATA "q" x\n20 PRINT "start"\n30 READ A$:PRINT A$\n',
                        "start\nSyntax error in 10\n"),
    "digit_after_quote": ('10 DATA "q"1\n20 PRINT "start"\n30 READ A$:PRINT A$\n',
                          "start\nSyntax error in 10\n"),
    "apostrophe_after_quote": ('10 DATA "q"\'c\n20 READ A$:PRINT A$\n',
                               "Syntax error in 10\n"),
    "two_quoted_items": ('10 DATA "a""b"\n20 READ A$:PRINT A$\n', "Syntax error in 10\n"),
    "quote_space_quote": ('10 DATA "a" "b"\n20 READ A$:PRINT A$\n', "Syntax error in 10\n"),
    "item_after_good_item": (
        '10 PRINT "start"\n20 DATA 1,"q"x,3\n30 READ A:PRINT A\n40 READ A$:PRINT A$\n',
        "start\n 1 \nSyntax error in 20\n"),
    "spaces_before_comma_are_fine": ('10 DATA "q" ,5\n20 READ A$,B:PRINT A$;B\n', "q 5 \n"),
    "trailing_spaces_are_fine": ('10 DATA "q"  \n20 READ A$:PRINT A$\n', "q\n"),
    "colon_ends_the_item": ('10 DATA "q":PRINT "z"\n20 READ A$:PRINT A$\n', "z\nq\n"),
    "rem_after_colon": ('10 DATA "q" :REM c\n20 READ A$:PRINT A$\n', "q\n"),
    "quote_inside_unquoted": ('10 DATA x"q"\n20 READ A$:PRINT A$\n', 'x"q"\n'),
    # the string is stored first; the next READ reads the same item again
    "string_stored_then_error": (
        '10 ON ERROR GOTO 100\n20 A$="old":READ A$:PRINT "A=";A$\n30 READ C$:PRINT "C=";C$\n'
        '40 READ D$:PRINT "D=";D$\n50 END\n90 DATA "q"x,"r",s\n' + HANDLER,
        " 2  90 q\nA=q\n 2  90 q\nC=q\n 2  90 q\nD=q\n"),
    "second_variable_not_stored": (
        '10 ON ERROR GOTO 100\n20 A$="old":B$="old":READ A$,B$:PRINT "A=";A$;" B=";B$\n'
        '30 READ C$:PRINT "C=";C$\n50 END\n90 DATA "q"x,"r",s\n'
        '100 PRINT ERR;ERL;A$;B$:RESUME NEXT\n',
        " 2  90 qold\nA=q B=old\n 2  90 qold\nC=q\n"),
    "number_variable": (
        '10 ON ERROR GOTO 100\n20 READ A:PRINT "A=";A\n30 READ C$:PRINT "C=";C$\n50 END\n'
        '90 DATA "q"x,"r",s\n100 PRINT ERR;ERL;A:RESUME NEXT\n',
        " 2  90  0 \nA= 0 \n 2  90  0 \nC=q\n"),
    "data_in_two_statements": (
        '10 ON ERROR GOTO 100\n20 A$="old":READ A$:PRINT "A=";A$\n30 READ C$:PRINT "C=";C$\n'
        '40 READ D$:PRINT "D=";D$\n50 END\n90 DATA "q"x:DATA "r",s\n' + HANDLER,
        " 2  90 q\nA=q\n 2  90 q\nC=q\n 2  90 q\nD=q\n"),
    "for_loop": (
        '10 ON ERROR GOTO 100\n20 FOR I=1 TO 3:READ A$:PRINT "A=";A$:NEXT\n50 END\n'
        '90 DATA "q"x,"r"\n' + HANDLER,
        " 2  90 q\nA=q\n 2  90 q\nA=q\n 2  90 q\nA=q\n"),
    # ON ERROR GOTO 0 in the handler: the error is reported at the DATA line
    "goto0_quote_tail": (
        '10 A$="old":ON ERROR GOTO 100\n20 RESTORE:READ A$:PRINT "A=";A$\n50 END\n90 DATA "q"1\n'
        '100 PRINT ERR;ERL;A$:ON ERROR GOTO 0\n',
        " 2  90 q\nSyntax error in 90\n"),
    "goto0_bad_number": (
        '10 ON ERROR GOTO 100\n20 READ A\n30 END\n90 DATA abc\n'
        '100 PRINT ERR;ERL:ON ERROR GOTO 0\n',
        " 2  90 \nSyntax error in 90\n"),
    "goto0_quoted_to_number": (
        '10 ON ERROR GOTO 100\n20 READ A\n30 END\n90 DATA "q"\n'
        '100 PRINT ERR;ERL:ON ERROR GOTO 0\n',
        " 2  90 \nSyntax error in 90\n"),
    "goto0_second_item": (
        '10 ON ERROR GOTO 100\n20 READ A,B\n30 END\n90 DATA 1,xyz\n'
        '100 PRINT ERR;ERL:ON ERROR GOTO 0\n',
        " 2  90 \nSyntax error in 90\n"),
    # an error at the READ line (&O19) stays at the READ line
    "goto0_read_line_error": (
        '10 ON ERROR GOTO 100\n20 READ A\n30 END\n90 DATA &O19\n'
        '100 PRINT ERR;ERL:ON ERROR GOTO 0\n',
        " 2  20 \nSyntax error in 20\n"),
    "goto0_out_of_data": (
        '10 ON ERROR GOTO 100\n20 READ A\n30 END\n100 PRINT ERR;ERL:ON ERROR GOTO 0\n',
        " 4  20 \nOut of DATA in 20\n"),
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
