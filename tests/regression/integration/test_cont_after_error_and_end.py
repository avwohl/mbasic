"""CONT after a run-time error or END, and a command-line load that aborts.

Measured on MBASIC 5.21 (cpmemu ../com/mbasic in a pty):
- CONT after a run-time error runs the failing statement again (also from the
  middle of a line and inside a FOR loop), so it prints the same error until
  the cause is fixed at the prompt; then the program carries on.
- CONT after END resumes at the statement after the END.
- CONT after the program ran off its end prints only Ok.
- A failing direct statement typed after the program stopped on an error
  prints the bare message ("Illegal function call", "Type mismatch"), with
  no " in <line>".
- A program edit after the error makes CONT print "Can't continue".
- "mbasic FILE" with a line over 255 bytes as the first line prints
  "Line buffer overflow in 10", then Ok, and stays at the prompt with an empty
  program (LIST prints only Ok).
"""
import subprocess
import sys
from pathlib import Path

try:
    import pytest  # noqa: F401
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: CONT tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

ROOT = Path(__file__).resolve().parents[3]


def run_cli(commands, args=()):
    return subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), *args, "--ui", "cli"],
        input=commands, cwd=ROOT, capture_output=True, text=True, timeout=60)


def lines_after_banner(stdout):
    out = [l for l in stdout.split("\n") if l.strip()]
    return out[out.index("Ok"):]


def test_cont_repeats_the_failing_statement():
    r = run_cli('10 PRINT "a"\n20 A$=1\n30 PRINT "c"\nRUN\nCONT\nCONT\n')
    assert lines_after_banner(r.stdout) == [
        "Ok", "a", "Type mismatch in 20", "Ok",
        "Type mismatch in 20", "Ok", "Type mismatch in 20", "Ok"]


def test_cont_repeats_return_error():
    r = run_cli('10 PRINT "a"\n20 RETURN\n30 PRINT "c"\nRUN\nCONT\n')
    assert lines_after_banner(r.stdout)[-4:] == [
        "RETURN without GOSUB in 20", "Ok", "RETURN without GOSUB in 20", "Ok"]


def test_cont_mid_line_error_does_not_rerun_earlier_statements():
    r = run_cli('10 PRINT "a":A$=1:PRINT "b"\n30 PRINT "c"\nRUN\nCONT\n')
    assert lines_after_banner(r.stdout) == [
        "Ok", "a", "Type mismatch in 10", "Ok", "Type mismatch in 10", "Ok"]


def test_cont_after_fixing_the_cause_in_a_for_loop():
    r = run_cli('5 Z=-1\n10 FOR I=1 TO 2\n20 PRINT I;LEFT$("abc",Z)\n'
                '40 NEXT:PRINT "done"\nRUN\nZ=2\nCONT\n')
    assert " 1 ab\n 2 ab\ndone\nOk" in r.stdout


def test_cont_after_fixing_the_cause_mid_line():
    r = run_cli('5 Z=-1\n10 PRINT "a":PRINT LEFT$("abc",Z):PRINT "b"\n'
                '30 PRINT "c"\nRUN\nZ=2\nCONT\nCONT\n')
    assert "ab\nb\nc\nOk\nOk" in r.stdout


def test_direct_statement_error_after_program_error_has_no_line():
    r = run_cli('10 PRINT 1\n20 PRINT LEFT$("a",-1)\nRUN\n'
                'PRINT LEFT$("a",-1)\nA$=1\nCONT\n')
    assert lines_after_banner(r.stdout)[-8:] == [
        "Illegal function call in 20", "Ok", "Illegal function call", "Ok",
        "Type mismatch", "Ok", "Illegal function call in 20", "Ok"]


def test_cont_after_error_then_program_edit_cannot_continue():
    r = run_cli('10 A$=1\nRUN\n20 REM\nCONT\n')
    assert "Type mismatch in 10\nOk\nCan't continue\nOk" in r.stdout


def test_cont_after_end_resumes_after_the_end():
    r = run_cli('10 PRINT "a"\n20 END\n30 PRINT "c"\nRUN\nCONT\nCONT\n')
    assert "a\nOk\nc\nOk\nOk" in r.stdout


def test_cont_after_end_in_the_middle_of_a_line():
    r = run_cli('10 PRINT "a":END:PRINT "b"\n30 PRINT "c"\nRUN\nCONT\nCONT\n')
    assert "a\nOk\nb\nc\nOk\nOk" in r.stdout


def test_cont_after_the_program_ran_off_its_end_prints_only_ok():
    r = run_cli('10 PRINT "a"\nRUN\nCONT\n')
    assert "a\nOk\nOk" in r.stdout
    assert "Can't continue" not in r.stdout


def test_command_line_load_with_first_line_over_255_bytes_reaches_the_prompt(tmp_path):
    bas = tmp_path / "zl1.bas"
    bas.write_text('10 PRINT "' + "A" * 300 + '"\n20 PRINT "two"\n')
    r = run_cli("LIST\nRUN\n", args=(str(bas),))
    assert r.returncode == 0, r.stderr
    assert "Line buffer overflow in 10" in r.stderr
    assert "Failed to load program" not in r.stderr
    assert r.stdout.split("\n").count("Ok") == 3  # prompt, after LIST, after RUN
    assert "two" not in r.stdout


def test_command_line_load_keeps_lines_before_the_long_line(tmp_path):
    bas = tmp_path / "zl2.bas"
    bas.write_text('10 PRINT "one"\n20 PRINT "two"\n30 PRINT "' + "B" * 300 + '"\n')
    r = run_cli("LIST\n", args=(str(bas),))
    assert "Line buffer overflow in 30" in r.stderr
    assert '10 PRINT "one"\n20 PRINT "two"\nOk' in r.stdout


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
