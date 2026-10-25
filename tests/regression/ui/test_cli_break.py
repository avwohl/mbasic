"""^C in the CLI: Break in <line> every time, CONT every time (issue 48).

Measured on MBASIC 5.21 under cpmemu in a pty (^C is byte 0x03):

    e.bas: 10 I=I+1 / 20 IF I<3 THEN PRINT "tick";I / 30 FOR J=1 TO 100000:NEXT J / 40 GOTO 10
    RUN, ^C, CONT, ^C, CONT, ^C, PRINT I  ->  "Break in 30" and Ok after each ^C
    (the binary prints it every time and CONT works every time)

    i.bas: 10 INPUT "X";A$ / 20 PRINT "got";A$
    RUN, ^C, CONT, hello  ->  "X? " then ^C gives "Break in 10" at once;
    CONT shows "X? " again; hello gives "gothello".

The CLI used to print a bare "Break" for the second ^C (CONT never armed the
break handler), then "Can't continue in 30"; and ^C at INPUT did nothing
until the next line was typed.
"""
import sys
import time
from pathlib import Path

try:
    import pexpect
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest or pexpect unavailable: CLI break tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

ROOT = Path(__file__).resolve().parents[3]
CTRL_C = "\x03"

TICKER = '10 I=I+1\n20 IF I<3 THEN PRINT "tick";I\n30 FOR J=1 TO 100000:NEXT J\n40 GOTO 10\n'
ASKER = '10 INPUT "X";A$\n20 PRINT "got";A$\n'


def start(tmp_path, source):
    path = tmp_path / "p.bas"
    path.write_text(source)
    child = pexpect.spawn(sys.executable, [str(ROOT / "mbasic"), str(path), "--ui", "cli"],
                          cwd=tmp_path, encoding="utf-8", timeout=20)
    child.expect("MBASIC> ")
    return child


def test_ctrl_c_after_cont_names_the_line_and_cont_works_again(tmp_path):
    child = start(tmp_path, TICKER)
    child.sendline("RUN")
    child.expect("tick 1")
    for _ in range(3):
        child.send(CTRL_C)
        child.expect("Break in 30")
        child.expect("MBASIC> ")
        child.sendline("CONT")
        child.expect("CONT")
        time.sleep(0.3)               # let the program run again
    child.send(CTRL_C)
    child.expect("Break in 30")
    child.expect("MBASIC> ")
    child.sendline("SYSTEM")
    child.expect("Goodbye")
    assert "Can't continue" not in child.before


def test_ctrl_c_at_input_breaks_at_once_and_cont_asks_again(tmp_path):
    child = start(tmp_path, ASKER)
    child.sendline("RUN")
    child.expect(r"X\? ")
    child.send(CTRL_C)
    child.expect("Break in 10")
    child.expect("MBASIC> ")
    child.sendline("CONT")
    child.expect(r"X\? ")
    child.sendline("hello")
    child.expect("gothello")
    child.expect("MBASIC> ")
    child.sendline("SYSTEM")
    child.expect("Goodbye")


TWO_INPUTS = '10 INPUT A$\n20 PRINT "got ";A$\n30 INPUT "name";B$\n40 PRINT "got2 ";B$\n'


def test_second_input_break_inside_a_continued_run_keeps_its_line(tmp_path):
    # Measured on MBASIC 5.21 under cpmemu: RUN, ^C, CONT, abc, ^C, CONT, xyz
    # -> "Break in 10", then "got abc", "name? ", "Break in 30", and the last
    # CONT shows "name? " (line 30 again, not line 10), then "got2 xyz".
    child = start(tmp_path, TWO_INPUTS)
    child.sendline("RUN")
    child.expect(r"\? ")
    child.send(CTRL_C)
    child.expect("Break in 10")
    child.expect("MBASIC> ")
    child.sendline("CONT")
    child.expect(r"\? ")
    child.sendline("abc")
    child.expect(r"name\? ")
    child.send(CTRL_C)
    child.expect("Break in 30")
    child.expect("MBASIC> ")
    child.sendline("CONT")
    child.expect(r"name\? ")
    child.sendline("xyz")
    child.expect("got2 xyz")
    child.sendline("SYSTEM")
    child.expect("Goodbye")


def run_script(tmp_path, source, commands):
    """Run the program, then the direct commands, piped; return the output."""
    import subprocess
    path = tmp_path / "p.bas"
    path.write_text(source)
    result = subprocess.run([sys.executable, str(ROOT / "mbasic"), "--ui", "cli", str(path)],
                            input="\n".join(commands) + "\nSYSTEM\n", cwd=tmp_path,
                            capture_output=True, text=True, timeout=30)
    return result.stdout


def test_cont_after_stop_resumes_at_the_next_statement(tmp_path):
    # Measured on MBASIC 5.21 under cpmemu: 10 PRINT 1 / 20 STOP / 30 PRINT 2,
    # RUN, CONT, CONT -> " 1", "Break in 20", Ok, " 2", Ok, then Ok only.
    out = run_script(tmp_path, "10 PRINT 1\n20 STOP\n30 PRINT 2\n", ["RUN", "CONT", "CONT"])
    assert out.count("Break in 20") == 1
    assert out.count(" 2 ") == 1
    assert "Can't continue" not in out


def test_cont_after_a_program_edit_cannot_continue(tmp_path):
    # Measured on MBASIC 5.21 under cpmemu: RUN, 30 PRINT 3, CONT -> "Can't continue"
    out = run_script(tmp_path, "10 PRINT 1\n20 STOP\n30 PRINT 2\n",
                     ["RUN", "30 PRINT 3", "CONT"])
    assert "Can't continue" in out
    assert " 3 " not in out


def test_cont_after_the_program_ended_prints_nothing(tmp_path):
    # Measured on MBASIC 5.21 under cpmemu: RUN to the end, CONT -> Ok only.
    out = run_script(tmp_path, "10 PRINT 1\n", ["RUN", "CONT"])
    assert "Can't continue" not in out


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
