#!/usr/bin/env python3
"""Errors are reported the way MBASIC 5.21 reports them.

Every expectation here was measured against the real binary under cpmemu -
`utils/crosscheck_tests.py` runs the same comparison over the test programs,
and the scratch harness that produced these ran each provocation as its own
program on both engines.

What was wrong. The message was built out of the Python exception:

    ?RuntimeError in 50: Cannot open NOSUCH.DAT: Cannot open NOSUCH.DAT: No such file or directory
      50 OPEN "I",1,"NOSUCH.DAT"

against the binary's

    File not found in 50

- a leading '?', the Python class name, the Python text, and an echo of the
source line, none of which MBASIC prints. The Python detail is not lost; it
still goes to stderr through debug_log_error.

Three other things were wrong and are covered here:

* A failed CHAIN or MERGE reported the failure by *printing* it, which left the
  PC alone, so the program carried on to the next line. It has to stop.
* A float divide by zero is not an error at all on 5.21 when no handler is
  armed: it prints a bare "Division by zero", substitutes machine infinity and
  carries on. We stopped the program. The integer forms, 5 \\ 0 and 5 MOD 0,
  really are fatal - the two go through different code in the binary.
* Several conditions were not detected at all: A$ = 5, C% = 40000, a second DIM
  of the same array, MID$("A",0), and a FOR or WHILE with no terminator.
"""

import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

results = []


def check(condition, label):
    results.append(bool(condition))
    print(f"{'PASS' if condition else 'FAIL'}: {label}")


CHROME = ('MBASIC-', '100%', '(Tip:', 'Type HELP')


def run(program):
    """Run a program through the CLI and return its output lines.

    A subprocess rather than an embedded Interpreter, because the thing under
    test is how the error is *reported* - which happens in interactive.py, not
    in the interpreter.
    """
    with tempfile.TemporaryDirectory(prefix='mbasic-errors-') as tmp:
        source = Path(tmp) / 'case.bas'
        source.write_text(program + '\n')
        # cwd is the temp directory, not the repo: several of these open files,
        # and a program that stops early leaves them behind.
        done = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / 'mbasic'), '--ui', 'cli', str(source)],
            input='RUN\nSYSTEM\n', capture_output=True, text=True,
            cwd=tmp, timeout=60)
        out = done.stdout
    keep = [l for l in out.split('\n')
            if not l.startswith(CHROME) and l not in ('Ready', 'Goodbye')]
    while keep and keep[-1].strip() == '':
        keep.pop()
    return keep


#: (name, provocation at line 10, expected output) - line 20 prints AFTER, so
#: the expectation covers both the message and whether the program stopped.
CASES = [
    ('NEXT without FOR', '10 NEXT I', ['NEXT without FOR in 10']),
    ('RETURN without GOSUB', '10 RETURN', ['RETURN without GOSUB in 10']),
    ('Out of DATA', '10 READ X', ['Out of DATA in 10']),
    ('Illegal function call', '10 PRINT SQR(-1)', ['Illegal function call in 10']),
    ('MID$ start of zero', '10 PRINT MID$("A",0)', ['Illegal function call in 10']),
    ('Undefined line number', '10 GOTO 9999', ['Undefined line number in 10']),
    ('Subscript out of range', '5 DIM Q(3)\n10 Q(9)=1',
     ['Subscript out of range in 10']),
    ('Duplicate Definition', '5 DIM Q(3)\n10 DIM Q(3)',
     ['Duplicate Definition in 10']),
    ('Type mismatch, number into string', '10 A$ = 5', ['Type mismatch in 10']),
    ('Type mismatch, string into number', '10 A = "X"', ['Type mismatch in 10']),
    ('Undefined user function', '10 PRINT FNZ(1)', ['Undefined user function in 10']),
    ('RESUME without error', '10 RESUME', ['RESUME without error in 10']),
    ('Integer overflow', '10 C% = 40000', ['Overflow in 10']),
    ('Integer divide by zero', '10 PRINT 5 \\ 0', ['Division by zero in 10']),
    ('MOD by zero', '10 PRINT 5 MOD 0', ['Division by zero in 10']),
    ('FOR with no NEXT', '10 FOR I=1 TO 3', ['FOR Without NEXT in 10']),
    ('WHILE with no WEND', '10 WHILE 1', ['WHILE without WEND in 10']),
    ('WEND with no WHILE', '10 WEND', ['WEND without WHILE in 10']),
    ('Bad file number', '10 PRINT #9,"X"', ['Bad file number in 10']),
    ('File not found', '10 OPEN "I",1,"NOSUCH.XYZ"', ['File not found in 10']),
    # These two used to print and carry on.
    ('CHAIN of a missing file', '10 CHAIN "NOSUCH.BAS"', ['File not found in 10']),
    ('MERGE of a missing file', '10 MERGE "NOSUCH.BAS"', ['File not found in 10']),
]


def test_the_message_and_the_halt():
    print("Untrapped errors: the message, and stopping")
    print("-" * 60)
    # One CLI subprocess per case, and these dominate the file's runtime: 22 of
    # them, about eight tenths of a second each, took it to 30s - which is
    # exactly run_regression.py's per-test timeout, so it was being killed on
    # roughly half of all runs, and a killed test reports no output at all.
    # The cases are independent and each already runs in its own temp
    # directory, so let them overlap; map keeps the results in order.
    with ThreadPoolExecutor(max_workers=4) as pool:
        outputs = list(pool.map(
            lambda case: run(case[1] + '\n20 PRINT "AFTER"\n30 SYSTEM'), CASES))
    for (name, _program, expected), got in zip(CASES, outputs):
        check(got == expected, f"{name:36} -> {got}"
              + ("" if got == expected else f"   (want {expected})"))


def test_a_float_divide_by_zero_is_a_warning():
    """No line number, and the program carries on with machine infinity."""
    print("\nA float divide by zero warns and continues")
    print("-" * 60)

    got = run('10 A = 1/0\n20 PRINT "AFTER"\n30 SYSTEM')
    check(got == ['Division by zero', 'AFTER'], f"{'bare message, no line':36} -> {got}")

    got = run('10 A = 1/0\n15 PRINT "A=";A\n20 PRINT "AFTER"\n30 SYSTEM')
    check(got == ['Division by zero', 'A= 1.70141E+38 ', 'AFTER'],
          f"{'machine infinity, not an error':36} -> {got}")

    got = run('10 PRINT -1/0\n20 SYSTEM')
    check(got == ['Division by zero', '-1.70141E+38 '],
          f"{'the dividend keeps its sign':36} -> {got}")

    # With a handler armed it is an ordinary trappable error instead.
    got = run('10 ON ERROR GOTO 100\n20 A = 1/0\n30 PRINT "A=";A\n40 SYSTEM\n'
              '100 PRINT "ERR=";ERR;"ERL=";ERL\n110 RESUME NEXT')
    check(got == ['ERR= 11 ERL= 20 ', 'A= 0 '],
          f"{'ON ERROR traps it, ERR 11':36} -> {got}")


def test_err_reports_the_right_code():
    """ERR had been 5, "Illegal function call", for a dozen real codes.

    The reporter and the ERR variable were reading two different copies of the
    same guesswork, so the printed message could be right while ERR was wrong.
    Both now go through src/error_codes.py.
    """
    print("\nERR inside a handler")
    print("-" * 60)
    got = run('10 ON ERROR GOTO 200\n'
              '20 OPEN "I",1,"NOSUCH.DAT"\n'
              '30 A$ = STRING$(200,65) : A$ = A$ + A$\n'
              '40 C% = 40000\n'
              '50 PRINT MID$("A",0)\n'
              '60 RESUME 70\n'
              '70 PRINT "done"\n'
              '80 SYSTEM\n'
              '200 PRINT "ERR=";ERR;"ERL=";ERL\n'
              '210 RESUME NEXT')
    expected = ['ERR= 53 ERL= 20 ', 'ERR= 15 ERL= 30 ', 'ERR= 6 ERL= 40 ',
                'ERR= 5 ERL= 50 ', 'ERR= 20 ERL= 60 ', 'done']
    check(got == expected, f"{'five errors, five codes':36} -> {got}"
          + ("" if got == expected else f"   (want {expected})"))

    # ERROR n reports n, whatever the message. It used to raise the literal
    # text "ERROR 21", which mapped back to 5.
    got = run('10 ON ERROR GOTO 100\n20 ERROR 21\n30 SYSTEM\n'
              '100 PRINT "ERR=";ERR\n110 RESUME NEXT')
    check(got == ['ERR= 21 '], f"{'ERROR 21 is error 21':36} -> {got}")

    # And untrapped it prints the message from the table. 21 has no message on
    # 5.21, and every code that has none prints "Unprintable error".
    got = run('10 ERROR 21\n20 PRINT "AFTER"\n30 SYSTEM')
    check(got == ['Unprintable error in 10'],
          f"{'an unnamed code is Unprintable':36} -> {got}")


def test_a_direct_statement_has_no_line_number():
    """Typed at the Ok prompt, the message appears on its own."""
    print("\nDirect mode drops the ' in <line>'")
    print("-" * 60)
    done = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / 'mbasic'), '--ui', 'cli'],
        input='RETURN\nPRINT SQR(-1)\nSYSTEM\n', capture_output=True, text=True,
        cwd=tempfile.gettempdir(), timeout=60)
    keep = [l for l in done.stdout.split('\n')
            if not l.startswith(CHROME) and l not in ('Ready', 'Goodbye', '')]
    check(keep == ['RETURN without GOSUB', 'Illegal function call'],
          f"{'no line number when typed':36} -> {keep}")


if __name__ == "__main__":
    print("MBASIC 5.21 error reporting")
    print("=" * 60)

    test_the_message_and_the_halt()
    test_a_float_divide_by_zero_is_a_warning()
    test_err_reports_the_right_code()
    test_a_direct_statement_has_no_line_number()

    failed = results.count(False)
    print("\n" + "=" * 60)
    print(f"Results: {results.count(True)} passed, {failed} failed")

    if failed:
        print("❌ Some tests failed")
        sys.exit(1)
    print("✅ All tests passed!")
    sys.exit(0)
