"""Compile and run the forms of issues 17, 21 and 24 in JavaScript.

Expected output is what real MBASIC 5.21 prints (see
tests/regression/interpreter/test_parser_forms.py for the interpreter side).
"""
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: JavaScript execution tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

ROOT = Path(__file__).resolve().parents[3]
NODE = shutil.which("node")


def build(tmp_path, source):
    basic = tmp_path / "prog.bas"
    basic.write_text(source)
    output = tmp_path / "prog.js"
    result = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(basic), "--compile-js", str(output)],
        cwd=ROOT, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return output


def run_js(tmp_path, source, stdin=""):
    output = build(tmp_path, source)
    result = subprocess.run([NODE, str(output)], input=stdin, cwd=tmp_path,
                            capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    return [line.strip() for line in result.stdout.splitlines()]


needs_node = pytest.mark.skipif(NODE is None, reason="Node.js is needed")


@needs_node
def test_sign_after_power(tmp_path):
    out = run_js(tmp_path, '''10 X=3
20 PRINT 2^-1
30 PRINT 2^-X
40 PRINT -2^2
50 PRINT 2^-1^2
60 PRINT X*-1
70 PRINT NOT -1
80 IF 2^-1=.5 THEN PRINT "IFOK"
90 PRINT 2^+1
100 PRINT -X^-2
110 A=2^-1:PRINT A;ABS(2^-1);4^-.5
120 END
''')
    assert out == [".5", ".125", "-4", ".5", "-3", "0", "IFOK", "2", "-.111111",
                   ".5  .5  .5"]


@needs_node
def test_line_input_array_element(tmp_path):
    out = run_js(tmp_path, '''10 DIM A$(3),B$(2,2)
20 LINE INPUT A$(1)
30 PRINT "[";A$(1);"]"
40 I=2
50 LINE INPUT "P";A$(I)
60 PRINT "[";A$(2);"]"
70 LINE INPUT B$(1,I)
80 PRINT "[";B$(1,2);"]"
90 END
''', "first\nsecond\nthird, x\n")
    assert [line for line in out if line.startswith(("[", "P["))] == \
        ["[first]", "P[second]", "[third, x]"]


@needs_node
def test_line_input_file_array_element(tmp_path):
    out = run_js(tmp_path, '''10 DIM A$(3)
20 OPEN "O",#1,"T.DAT"
30 PRINT #1,"hello, x"
40 PRINT #1,"world"
50 CLOSE #1
60 OPEN "I",#1,"T.DAT"
70 FOR I=1 TO 2
80 LINE INPUT #1,A$(I)
90 PRINT "[";A$(I);"]"
100 NEXT
110 CLOSE
120 END
''')
    assert out == ["[hello, x]", "[world]"]


@needs_node
def test_write_semicolon(tmp_path):
    out = run_js(tmp_path, '''10 WRITE 1;2
20 WRITE "a";"b";3
30 A=0:B$="":WRITE A;B$
40 OPEN "O",#1,"W.DAT":WRITE #1,3;4:CLOSE
50 OPEN "I",#1,"W.DAT":LINE INPUT #1,C$:PRINT C$:CLOSE
60 END
''')
    assert out == ['1,2', '"a","b",3', '0,""', '3,4']


if __name__ == "__main__":
    if NODE is None:
        print("Node.js unavailable: JavaScript execution tests skipped")
        sys.exit(2)
    sys.exit(pytest.main([__file__, "-q"]))
