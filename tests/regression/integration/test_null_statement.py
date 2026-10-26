"""NULL is a statement: NULL count, with the count a byte.

Every expected text was measured on MBASIC 5.21 (com/mbasic.com under cpmemu,
tests/HOW_TO_RUN_REAL_MBASIC.md), with ON ERROR GOTO a handler that prints
ERR and ERL and does RESUME NEXT:

- NULL 2, NULL 0, NULL 255 and NULL 1.6 run. No null byte reaches the output
  under cpmemu, and nothing prints them here.
- NULL -1 and NULL 256 are Illegal function call (5), NULL 40000 is Overflow
  (6), NULL "a" is Type mismatch (13), NULL alone is Missing operand (22).
- NULL 2,3 is a Syntax error (2). NULL is a reserved word, so NULL=2 and
  X=NULL are Syntax errors too.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from basic_runner import NODE, run_interpreter, run_javascript

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: NULL statement tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

HANDLER = '100 PRINT "E";ERR;ERL:RESUME NEXT\n'

CASES = {
    "counts": (
        '10 ON ERROR GOTO 100\n20 NULL 2:PRINT "ab"\n40 NULL 0:PRINT "ef"\n50 NULL -1\n'
        '60 NULL 255\n61 NULL 256\n62 NULL "a"\n63 NULL 1.6:PRINT "gh"\n64 NULL 0:NULL\n'
        '68 NULL 40000\n70 END\n' + HANDLER,
        "ab\nef\nE 5  50 \nE 5  61 \nE 13  62 \ngh\nE 22  64 \nE 6  68 \n"),
    "reserved_word": (
        '10 ON ERROR GOTO 100\n65 NULL 2,3\n66 NULL=2\n67 X=NULL\n70 PRINT "z":END\n' + HANDLER,
        "E 2  65 \nE 2  66 \nE 2  67 \nz\n"),
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


def test_list_keeps_null(tmp_path):
    """LIST shows the statement as it was typed."""
    from basic_runner import ROOT
    import subprocess
    (tmp_path / "n.bas").write_text('10 NULL 2:PRINT "a"\n')
    result = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(tmp_path / "n.bas"), "--ui", "cli"],
        input="LIST\nSYSTEM\n", cwd=tmp_path, capture_output=True, text=True, timeout=60)
    assert '10 NULL 2:PRINT "a"' in result.stdout.replace("\r", "")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
