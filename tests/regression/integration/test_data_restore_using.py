"""DATA with nothing in it, RESTORE to a line, and PRINT USING with no field.

Every expected text was measured on MBASIC 5.21 (com/mbasic.com under cpmemu,
tests/HOW_TO_RUN_REAL_MBASIC.md). A random READ and PRINT USING test against
the binary found these:

- DATA with nothing after it (DATA, or DATA followed by :) is one empty item:
  READ A$ gives "" and READ A gives 0. Before, READ went on to the next DATA.
- RESTORE n goes to the first DATA item at or after line n (the JavaScript
  backend went to the first item of the program). RESTORE of a line that is
  not in the program is Undefined line number (8), and the next READ is Out
  of DATA (4).
- READ of a bad item into a number variable stores the number the item
  starts with (12x gives 12, 7.6x gives 8 to an integer, "q" and x y give 0)
  and then is Syntax error (2) at the DATA line. When that number does not
  fit an integer variable (40000x), the error is Overflow (6) at the READ line
  and the variable keeps its value.
- A program line keeps its trailing spaces, so an unclosed string at the end
  of a line ends with them (A$="ab<space><space> is 4 long). An unquoted DATA
  item still drops them.
- PRINT USING a format with no field prints the text and then stops with
  Illegal function call (5) before the end of the line: the message of the
  handler follows on the same line.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from basic_runner import NODE, run_interpreter, run_javascript

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: DATA, RESTORE and USING tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

CASES = {
    'empty_data_is_one_item': (
        '10 ON ERROR GOTO 100\n'
        '20 READ A$,B$:PRINT "[";A$;"][";B$;"]"\n'
        '30 DATA \n'
        '40 DATA x,y\n'
        '50 RESTORE 60:R=5:READ R,S:PRINT "R=";R;"S=";S\n'
        '60 DATA 1, x y ,7\n'
        '70 RESTORE 60:READ R:PRINT R:READ S:PRINT S\n'
        '80 RESTORE 90:READ R%:PRINT R%\n'
        '90 DATA \n'
        '95 PRINT "z":END\n'
        '100 PRINT "E";ERR;ERL:RESUME NEXT\n',
        '[][x]\nE 2  60 \nR= 1 S= 0 \n 1 \nE 2  60 \n 0 \n 0 \nz\n'),
    'empty_items_around_commas': (
        '10 ON ERROR GOTO 100\n'
        '20 READ A$,B$,C$,D$,E$,F$:PRINT "[";A$;"][";B$;"][";C$;"][";D$;"][";E$;"][";F$;"]"\n'
        '30 DATA 1,\n'
        '40 DATA ,2\n'
        '50 DATA:DATA x\n'
        '60 READ G:PRINT G\n'
        '70 DATA ,\n'
        '95 PRINT "z":END\n'
        '100 PRINT "E";ERR;ERL:RESUME NEXT\n',
        '[1][][][2][][x]\n 0 \nz\n'),
    'read_bad_second_item': (
        '10 ON ERROR GOTO 100\n'
        '20 R=5:S=6:READ R,S:PRINT "a";R;S\n'
        '30 DATA 1, x y ,7\n'
        '40 RESTORE 60:R=5:READ R,S:PRINT "b";R;S\n'
        '60 DATA 1,x y\n'
        '70 RESTORE 80:R=5:READ R,S:PRINT "c";R;S\n'
        '80 DATA 1, xy\n'
        '95 PRINT "z":END\n'
        '100 PRINT "E";ERR;ERL:RESUME NEXT\n',
        'E 2  30 \na 1  0 \nE 2  60 \nb 1  0 \nE 2  80 \nc 1  0 \nz\n'),
    'read_number_prefix': (
        '10 ON ERROR GOTO 100\n'
        '20 RESTORE 50:S=6:READ S:PRINT "b";S\n'
        '30 RESTORE 70:S%=6:READ S%:PRINT "c";S%\n'
        '40 RESTORE 90:S=6:READ S:PRINT "d";S\n'
        '45 RESTORE 92:S=6:READ S:PRINT "e";S\n'
        '46 RESTORE 94:S%=6:READ S%:PRINT "f";S%\n'
        '47 RESTORE 96:S=6:READ S:PRINT "g";S\n'
        '48 GOTO 98\n'
        '50 DATA 3.5 abc\n'
        '70 DATA 40000x\n'
        '90 DATA "q"\n'
        '92 DATA -\n'
        '94 DATA 7.6x\n'
        '96 DATA 1E3x\n'
        '98 PRINT "z":END\n'
        '100 PRINT "E";ERR;ERL:RESUME NEXT\n',
        'E 2  50 \nb 3.5 \nE 6  30 \nc 6 \nE 2  90 \nd 0 \ne 0 \nE 2  94 \nf 8 \nE 2  96 \ng 1000 \nz\n'),
    'unclosed_string_keeps_trailing_spaces': (
        '10 A$="ab  \n'
        '20 PRINT LEN(A$)\n'
        '30 READ B$:PRINT LEN(B$)\n'
        '40 DATA "cd  \n'
        '50 READ C$:PRINT LEN(C$)\n'
        '60 DATA ef  \n'
        '70 END\n',
        ' 4 \n 4 \n 2 \n'),
    'restore_line': (
        '10 ON ERROR GOTO 100\n'
        '20 RESTORE 45:READ A:PRINT A\n'
        '30 DATA 1,2\n'
        '40 DATA 3\n'
        '45 PRINT "x"\n'
        '50 DATA 5\n'
        '60 RESTORE 40:READ A,B:PRINT A;B\n'
        '70 RESTORE 55:READ A:PRINT A\n'
        '80 RESTORE 75:READ A:PRINT A\n'
        '90 RESTORE 999:READ A:PRINT A\n'
        '95 PRINT "z":END\n'
        '100 PRINT "E";ERR;ERL:RESUME NEXT\n',
        ' 5 \nx\n 3  5 \nE 8  70 \nE 4  70 \n 3 \nE 8  80 \nE 4  80 \n 3 \nE 8  90 \nE 4  90 \n 3 \nz\n'),
    'using_without_field': (
        '10 ON ERROR GOTO 100\n'
        '20 PRINT USING "%";1E6;-1E6\n'
        '30 PRINT USING "ab";1\n'
        '40 PRINT "z":END\n'
        '100 PRINT "E";ERR;ERL:RESUME NEXT\n',
        '%E 5  20 \nabE 5  30 \nz\n'),
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
