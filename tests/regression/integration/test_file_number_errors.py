"""The errors of a file statement or function on a file number that is not open, or open in the wrong mode.

Every expected text was measured on MBASIC 5.21 (com/mbasic.com under cpmemu,
tests/HOW_TO_RUN_REAL_MBASIC.md) started with /F:15, as this interpreter allows
15 files (the default /F:3 gives the same table with 3 where 15 is). For a file
number that no OPEN made:

- PRINT#, PRINT# USING, WRITE#, INPUT#, LINE INPUT#, GET and PUT: Bad file mode
  (54) for 0 to 15, Bad file number (52) for 16 to 255, Illegal function call
  (5) for 256 and for a negative number. 2.5 counts as 3.
- FIELD, EOF, LOC and LOF: Bad file number for 0 to 255, Illegal function call
  above that.
- CLOSE: no error for 0 to 15, Bad file number for 16 to 255, Illegal function
  call above that.
- INPUT$(1,#n): Input past end (62) for 0 to 15, then as above.
- OPEN: Bad file number for 0 and 16 to 255, Illegal function call above that.

For a file that is open in the wrong mode the error is Bad file mode: INPUT#,
LINE INPUT#, EOF and INPUT$ on a file that is open for output;
PRINT#, PRINT# USING, WRITE#, GET, PUT and FIELD on a file that is open for
input; GET, PUT and FIELD on a sequential file. OPEN of a file that is not
there for input is File not found.

OPEN "A" is a kept extension (the binary says Bad file mode at the OPEN). The
tests with "on_append" in the name only show that this interpreter gives the
same message for the input statements on such a file.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from basic_runner import NODE, run_interpreter, run_javascript

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: file number error tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

MODE = "Bad file mode"
NUMBER = "Bad file number"
ILLEGAL = "Illegal function call"
PAST_END = "Input past end"

# statement template -> message for the number classes (low = 0..15, high = 16..255, out = 256, -1)
WITH_MODE = {
    "print": 'PRINT #{n},"x"',
    "print_using": 'PRINT #{n},USING "##";5',
    "write": 'WRITE #{n},1,"a"',
    "input": "INPUT #{n},A",
    "line_input": "LINE INPUT #{n},A$",
    "get": "GET #{n}",
    "put": "PUT #{n}",
}
ALWAYS_NUMBER = {
    "field": "FIELD #{n},5 AS A$",
    "eof": "X=EOF({n})",
    "loc": "X=LOC({n})",
    "lof": "X=LOF({n})",
}
LOW = ["0", "1", "3", "4", "15", "2.5"]
HIGH = ["16", "255"]
OUT = ["256", "-1"]

CASES = {}      # name -> (program, expected output)


def add_unopened(kind, template, low, high, out):
    for numbers, message in ((LOW, low), (HIGH, high), (OUT, out)):
        for n in numbers:
            name = f"{kind}_{n.replace('-', 'minus').replace('.', 'point')}"
            expected = "after\n" if message is None else f"{message} in 10\n"
            CASES[name] = (f'10 {template.format(n=n)}\n20 PRINT "after"\n', expected)


for kind, template in WITH_MODE.items():
    add_unopened(kind, template, MODE, NUMBER, ILLEGAL)
for kind, template in ALWAYS_NUMBER.items():
    add_unopened(kind, template, NUMBER, NUMBER, ILLEGAL)
add_unopened("close", "CLOSE #{n}", None, NUMBER, ILLEGAL)
add_unopened("input_function", "A$=INPUT$(1,#{n})", PAST_END, NUMBER, ILLEGAL)
for n, message in (("3", None), ("15", None), ("16", NUMBER), ("0", NUMBER),
                   ("255", NUMBER), ("256", ILLEGAL), ("-1", ILLEGAL)):
    expected = "ok\n" if message is None else f"{message} in 10\n"
    CASES[f"open_{n.replace('-', 'minus')}"] = (
        f'10 OPEN "O",#{n},"ZZ5.DAT":PRINT "ok":CLOSE #{n}:KILL "ZZ5.DAT"\n', expected)

# a file that is open in the wrong mode
MAKE_INPUT = 'OPEN "O",#3,"ZZ5.DAT":PRINT #3,"x":CLOSE:OPEN "I",#3,"ZZ5.DAT"'
MAKE_APPEND = 'OPEN "O",#3,"ZZ5.DAT":PRINT #3,"x":CLOSE:OPEN "A",#3,"ZZ5.DAT"'
OPEN_OUTPUT = 'OPEN "O",#3,"ZZ5.DAT"'
WRONG_MODE = {
    "input_on_output": f'{OPEN_OUTPUT}:INPUT #3,A$',
    "line_input_on_output": f'{OPEN_OUTPUT}:LINE INPUT #3,A$',
    "eof_on_output": f'{OPEN_OUTPUT}:X=EOF(3)',
    "input_function_on_output": f'{OPEN_OUTPUT}:A$=INPUT$(1,#3)',
    "get_on_output": f'{OPEN_OUTPUT}:GET #3',
    "put_on_output": f'{OPEN_OUTPUT}:PUT #3',
    "field_on_output": f'{OPEN_OUTPUT}:FIELD #3,5 AS A$',
    "print_on_input": f'{MAKE_INPUT}:PRINT #3,"x"',
    "print_using_on_input": f'{MAKE_INPUT}:PRINT #3,USING "#";5',
    "write_on_input": f'{MAKE_INPUT}:WRITE #3,5',
    "put_on_input": f'{MAKE_INPUT}:PUT #3',
    "get_on_input": f'{MAKE_INPUT}:GET #3',
    "field_on_input": f'{MAKE_INPUT}:FIELD #3,5 AS A$',
    "input_on_append": f'{MAKE_APPEND}:INPUT #3,A',
    "input_function_on_append": f'{MAKE_APPEND}:A$=INPUT$(1,#3)',
    "eof_on_append": f'{MAKE_APPEND}:X=EOF(3)',
    "get_on_append": f'{MAKE_APPEND}:GET #3',
}
for name, line in WRONG_MODE.items():
    CASES[name] = (f'10 {line}\n20 PRINT "no"\n', f"{MODE} in 10\n")
CASES["input_function_past_end"] = (
    '10 OPEN "O",#1,"ZZ5.DAT":PRINT #1,"a":CLOSE:OPEN "I",#1,"ZZ5.DAT":A$=INPUT$(5,#1)\n'
    '20 PRINT "no"\n', "Input past end in 10\n")
CASES["open_missing_input_file"] = ('10 OPEN "I",#3,"ZZ5.DAT"\n20 PRINT "no"\n',
                                    "File not found in 10\n")

# GET and PUT of a random file need no FIELD: the record buffer is there from
# OPEN on (measured; a PUT before anything is in it writes what was in that
# memory on the binary, spaces here, so only LOC and the record read back count)
CASES["get_put_before_field"] = (
    '10 OPEN "R",#1,"ZZ5.DAT",4:PUT #1,1:PUT #1:PRINT LOC(1):CLOSE #1\n'
    '20 OPEN "R",#1,"ZZ5.DAT",4:GET #1,2:FIELD #1,4 AS A$:PRINT LEN(A$):CLOSE\n',
    " 2 \n 4 \n")

# trapped: ERR 54 at the line of the statement, and RESUME NEXT goes on
CASES["print_after_close_trapped"] = (
    '10 OPEN "O",#3,"ZZ5.DAT":PRINT #3,"x":CLOSE #3:PRINT "ok":ON ERROR GOTO 100:PRINT #3,"y"\n'
    '20 PRINT "no":END\n100 PRINT ERR;ERL:RESUME NEXT\n',
    "ok\n 54  10 \nno\n")
CASES["unopened_chain_trapped"] = (
    '10 ON ERROR GOTO 100\n20 PRINT #1,"x":PRINT "n1"\n30 INPUT #1,A:PRINT "n2"\n'
    '40 X=EOF(1):PRINT "n3"\n50 X=LOF(2):PRINT "n4"\n60 CLOSE #1:PRINT "n5"\n'
    '70 A$=INPUT$(1,#1):PRINT "n6"\n80 END\n100 PRINT ERR;ERL:RESUME NEXT\n',
    " 54  20 \nn1\n 54  30 \nn2\n 52  40 \nn3\n 52  50 \nn4\nn5\n 62  70 \nn6\n")


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
