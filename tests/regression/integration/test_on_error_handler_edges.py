"""ON ERROR edges inside and around a handler (issues 37, 44, 45, 46, 47).

Every expected text below was measured on MBASIC 5.21 (com/mbasic.com under
cpmemu, tests/HOW_TO_RUN_REAL_MBASIC.md). The binary:

- reports an error inside a handler as an untrapped error at the line where it
  happens (#47), even when ON ERROR is armed again inside the handler;
- takes ON ERROR GOTO 0 inside a handler as "turn the handler off, then raise
  the pending error again at the line that first failed" (#44);
- checks the line of ON ERROR GOTO when the statement runs (#45);
- ends quietly (Ok) when a handler ends with END (#46);
- says "No RESUME in <last line>" when a handler runs off the end (#37);
- keeps the handler "live" after a GOTO out of it: only RESUME ends the
  handler, so the next error is untrapped.

The JavaScript compiler (issue 41) now prints "<message> in <line>" like the
binary. Two differences remain and are kept in the expected text below: after
ON ERROR GOTO 0 in a handler (#44) the line is the line inside the handler,
where the binary names the line that first failed, and "No RESUME" (#37) has
no " in <line>".
"""
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: ON ERROR handler edge tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

ROOT = Path(__file__).resolve().parents[3]
NODE = shutil.which("node")

# name: (program, interpreter output that must appear, text that must not appear,
#        JavaScript stdout)
CASES = {
    # #47: ERROR 7 in the handler
    "error_in_handler": (
        '10 ON ERROR GOTO 100\n20 ERROR 5\n30 PRINT "no"\n40 END\n'
        '100 PRINT "H"\n110 ERROR 7\n120 PRINT "x"\n130 END\n',
        "H\nOut of memory in 110\n", "Illegal function call", "H\nOut of memory in 110\n"),
    # #47: READ with no DATA in the handler
    "read_in_handler": (
        '10 ON ERROR GOTO 100\n20 ERROR 5\n40 END\n100 PRINT "H"\n110 READ Q\n130 END\n',
        "H\nOut of DATA in 110\n", "Illegal function call", "H\nOut of DATA in 110\n"),
    # #47: type mismatch in the handler
    "mismatch_in_handler": (
        '10 ON ERROR GOTO 100\n20 ERROR 5\n40 END\n100 PRINT "H"\n110 A=1:A$=A\n130 END\n',
        "H\nType mismatch in 110\n", "Illegal function call",
        None),  # the JavaScript compiler does not check A$=A at run time
    # #47: a second ON ERROR inside the handler does not trap the next error
    "rearmed_in_handler": (
        '10 ON ERROR GOTO 100\n20 ERROR 5\n30 END\n100 ON ERROR GOTO 200\n'
        '110 PRINT "after"\n120 ERROR 9\n200 PRINT "h2"\n210 END\n',
        "after\nSubscript out of range in 120\n", "h2", "after\nSubscript out of range in 120\n"),
    # #44: ON ERROR GOTO 0 in the handler raises the pending error at line 30
    "goto0_in_handler": (
        '10 ON ERROR GOTO 100\n20 PRINT "A"\n30 ERROR 5\n40 PRINT "not here"\n50 END\n'
        '100 PRINT "H";ERR;ERL\n110 ON ERROR GOTO 0\n120 PRINT "after"\n130 END\n',
        "A\nH 5  30 \nIllegal function call in 30\n", "after",
        "A\nH 5  30 \nIllegal function call in 110\n"),
    "goto0_in_handler_division": (
        '10 ON ERROR GOTO 100\n20 X=1/0\n30 END\n100 ON ERROR GOTO 0\n110 PRINT "after"\n',
        "Division by zero in 20\n", "after", "Division by zero in 100\n"),
    # #45: the line is looked up when ON ERROR runs
    "missing_handler_line": (
        '10 PRINT "start"\n20 ON ERROR GOTO 999\n30 PRINT "after on error"\n40 END\n',
        "start\nUndefined line number in 20\n", "after on error",
        "start\nUndefined line number in 20\n"),
    # #46: END ends the handler and the program, no error
    "end_in_handler": (
        '10 ON ERROR GOTO 100\n20 ERROR 5\n30 PRINT "no"\n100 PRINT "H"\n110 END\n',
        "H\n", "Illegal function call", "H\n"),
    # #37: off the end of the program inside a handler
    "off_the_end": (
        '10 ON ERROR GOTO 100\n20 PRINT "A"\n30 ERROR 5\n40 END\n100 PRINT "H"\n110 PRINT ERR;ERL\n',
        "A\nH\n 5  30 \nNo RESUME in 110\n", "Illegal function call",
        "A\nH\n 5  30 \nNo RESUME\n"),
    "off_the_end_division": (
        '10 ON ERROR GOTO 100\n20 X=1/0\n30 END\n100 PRINT "H"\n',
        "H\nNo RESUME in 100\n", "Division by zero", "H\nNo RESUME\n"),
    # a GOTO out of a handler does not end the handler: the next error is fatal
    "goto_out_then_error": (
        '10 ON ERROR GOTO 100\n20 ERROR 5\n30 ERROR 9\n40 END\n100 PRINT "H";ERR\n110 GOTO 30\n',
        "H 5 \nSubscript out of range in 30\n", "H 9", "H 5 \nSubscript out of range in 30\n"),
    # a handler that ends with RESUME NEXT still works
    "resume_next": (
        '10 ON ERROR GOTO 100\n20 ERROR 5\n30 PRINT "back"\n40 ERROR 9\n50 PRINT "again"\n60 END\n'
        '100 PRINT "H";ERR\n110 RESUME NEXT\n',
        "H 5 \nback\nH 9 \nagain\n", "No RESUME", "H 5 \nback\nH 9 \nagain\n"),
}


def run_cli(directory, source):
    (directory / "e.bas").write_text(source)
    result = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(directory / "e.bas"), "--ui", "cli"],
        input="RUN\nSYSTEM\n", cwd=directory, capture_output=True, text=True, timeout=60)
    return result.stdout.replace("\r", "")


@pytest.mark.parametrize("name", sorted(CASES))
def test_interpreter(tmp_path, name):
    source, shown, absent, _ = CASES[name]
    out = run_cli(tmp_path, source)
    assert shown in out, out
    assert absent not in out, out


@pytest.mark.skipif(NODE is None, reason="Node.js is needed to execute generated JavaScript")
@pytest.mark.parametrize("name", sorted(CASES))
def test_javascript(tmp_path, name):
    source, _, _, expected = CASES[name]
    if expected is None:
        pytest.skip("known JavaScript difference")
    (tmp_path / "e.bas").write_text(source)
    compiled = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(tmp_path / "e.bas"),
         "--compile-js", str(tmp_path / "e.js")],
        cwd=tmp_path, capture_output=True, text=True, timeout=60)
    assert compiled.returncode == 0, compiled.stdout + compiled.stderr
    result = subprocess.run([NODE, str(tmp_path / "e.js")], cwd=tmp_path,
                            capture_output=True, text=True, timeout=60)
    assert result.stdout == expected, result.stdout + result.stderr


def test_error_in_handler_needs_no_python_traceback(tmp_path):
    out = run_cli(tmp_path, CASES["error_in_handler"][0])
    assert "Traceback" not in out and "AttributeError" not in out, out


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
