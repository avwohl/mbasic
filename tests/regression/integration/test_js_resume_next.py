"""RESUME and RESUME NEXT in the generated JavaScript (issue 58).

Every expected text below was measured on MBASIC 5.21 (com/mbasic.com under
cpmemu, tests/HOW_TO_RUN_REAL_MBASIC.md). The binary:

- continues RESUME NEXT at the next STATEMENT after the failing one, which
  can be on the same line;
- runs RESUME again for the failing statement only, not for the line (a
  handler that RESUMEs three times repeats ERROR 5 and no earlier statement);
- takes an error in the middle of a line the same way for a deferred Syntax
  error (MID$ (A$,2)="ZZ" with a space), and for errors inside FOR/NEXT,
  WHILE/WEND, GOSUB and the THEN and ELSE parts of IF;
- after an error in the CONDITION of an IF, RESUME NEXT continues after the
  first colon of the THEN part ("t1" is skipped, "t2" runs).

The interpreter does not match the binary for an error inside a multi-statement
THEN or ELSE part (see docs/dev/MBASIC_521_DIVERGENCES_TODO.md), so only the
JavaScript compiler is tested here.
"""
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: JavaScript RESUME tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

ROOT = Path(__file__).resolve().parents[3]
NODE = shutil.which("node")

# name: (program, stdout of MBASIC 5.21 for RUN)
CASES = {
    'resume_next_same_line': (
        '10 ON ERROR GOTO 900\n20 PRINT "a":ERROR 5:PRINT "b"\n30 PRINT "c"\n40 SYSTEM\n900 PRINT "E";ERR:RESUME NEXT\n',
        'a\nE 5 \nb\nc\n'),
    'resume_reruns_one_statement': (
        '10 ON ERROR GOTO 900\n20 I=I+1:PRINT "x";I:ERROR 5:PRINT "y";I\n30 PRINT "end"\n40 SYSTEM\n900 C=C+1:PRINT "E";ERR;ERL:IF C<3 THEN RESUME\n910 RESUME NEXT\n',
        'x 1 \nE 5  20 \nE 5  20 \nE 5  20 \ny 1 \nend\n'),
    'resume_next_after_deferred_syntax_error': (
        '10 ON ERROR GOTO 900\n20 A$="ABCDEFGH":MID$ (A$,2)="ZZ":PRINT A$\n30 PRINT "c"\n40 SYSTEM\n900 PRINT "E";ERR;ERL:RESUME NEXT\n',
        'E 2  20 \nABCDEFGH\nc\n'),
    'resume_next_for_while_gosub_if': (
        '10 ON ERROR GOTO 900\n20 FOR I=1 TO 2:PRINT "f";I:ERROR 5:PRINT "g";I:NEXT I:PRINT "after"\n30 J=0:WHILE J<2:J=J+1:ERROR 6:PRINT "w";J:WEND:PRINT "wafter"\n40 GOSUB 500:PRINT "back":ERROR 7:PRINT "z"\n50 X=1:IF X=1 THEN PRINT "t1":ERROR 8:PRINT "t2" ELSE PRINT "e1"\n60 PRINT "l1":ERROR 9\n70 PRINT "end":SYSTEM\n500 PRINT "sub":ERROR 10:PRINT "sub2":RETURN\n900 PRINT "E";ERR;ERL:RESUME NEXT\n',
        'f 1 \nE 5  20 \ng 1 \nf 2 \nE 5  20 \ng 2 \nafter\nE 6  30 \nw 1 \nE 6  30 \nw 2 \nwafter\nsub\nE 10  500 \nsub2\nback\nE 7  40 \nz\nt1\nE 8  50 \nt2\nl1\nE 9  60 \nend\n'),
    'resume_next_error_in_if_condition': (
        '10 ON ERROR GOTO 900\n20 X=0:IF 1/X THEN PRINT "t1":PRINT "t2"\n30 PRINT "n"\n40 IF 1 THEN PRINT "a":ERROR 5:PRINT "b":PRINT "c" ELSE PRINT "e"\n50 PRINT "end"\n60 SYSTEM\n900 PRINT "E";ERR;ERL:RESUME NEXT\n',
        'E 11  20 \nt2\nn\na\nE 5  40 \nb\nc\nend\n'),
    'resume_next_in_if_else_bodies': (
        '10 ON ERROR GOTO 900\n20 X=0:IF X=0 THEN PRINT "t":ERROR 5:PRINT "u" ELSE PRINT "e1":PRINT "e2"\n30 X=1:IF X=0 THEN PRINT "t" ELSE PRINT "e1":ERROR 6:PRINT "e2":PRINT "e3"\n40 FOR I=1 TO 3:IF I=2 THEN ERROR 7:PRINT "post";I\n50 NEXT I:PRINT "n":ERROR 8\n60 ON I GOSUB 500,500:PRINT "g";I:ERROR 9\n70 PRINT "end":SYSTEM\n500 PRINT "s";I:RETURN\n900 PRINT "E";ERR;ERL:RESUME NEXT\n',
        't\nE 5  20 \nu\ne1\nE 6  30 \ne2\ne3\nE 7  40 \npost 2 \nn\nE 8  50 \ng 4 \nE 9  60 \nend\n'),
    'resume_in_if_body': (
        '10 ON ERROR GOTO 900\n20 K=0:PRINT "a":K=K+1:PRINT "k";K:ERROR 5:PRINT "b";K\n30 IF K<2 THEN K=K+5:PRINT "if";K:ERROR 6:PRINT "z"\n40 PRINT "end":SYSTEM\n900 C=C+1:PRINT "E";ERR;ERL;C:IF C<3 THEN RESUME\n910 RESUME NEXT\n',
        'a\nk 1 \nE 5  20  1 \nE 5  20  2 \nE 5  20  3 \nb 1 \nif 6 \nE 6  30  4 \nz\nend\n'),
}


@pytest.mark.skipif(NODE is None, reason="Node.js is needed to execute generated JavaScript")
@pytest.mark.parametrize("name", sorted(CASES))
def test_javascript(tmp_path, name):
    source, expected = CASES[name]
    (tmp_path / "e.bas").write_text(source)
    compiled = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(tmp_path / "e.bas"),
         "--compile-js", str(tmp_path / "e.js")],
        cwd=tmp_path, capture_output=True, text=True, timeout=60)
    assert compiled.returncode == 0, compiled.stdout + compiled.stderr
    result = subprocess.run([NODE, str(tmp_path / "e.js")], cwd=tmp_path,
                            capture_output=True, text=True, timeout=60)
    assert result.stdout == expected, result.stdout + result.stderr


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
