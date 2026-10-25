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


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
