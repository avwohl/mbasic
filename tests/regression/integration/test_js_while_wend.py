"""WHILE/WEND in generated JavaScript when they are on different lines (issue 57).

WHILE and WEND were a JavaScript while block. A case label of the line switch cannot stand inside
a block, so node stopped with SyntaxError. Now WHILE and WEND are jumps, as FOR and NEXT are.
Each expected output was measured on MBASIC 5.21 (cpmemu) and is the same in the interpreter.
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

pytestmark = pytest.mark.skipif(NODE is None, reason="Node.js is needed to execute generated JavaScript")


def compile_js(tmp_path, source, *flags):
    basic = tmp_path / "prog.bas"
    basic.write_text(source)
    output = tmp_path / "prog.js"
    result = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(basic), "--compile-js", str(output), *flags],
        cwd=ROOT, capture_output=True, text=True, timeout=30,
    )
    return result, output


def run_js(tmp_path, source):
    result, output = compile_js(tmp_path, source)
    assert result.returncode == 0, result.stdout + result.stderr
    run = subprocess.run([NODE, str(output)], capture_output=True, text=True, timeout=10)
    assert run.returncode == 0, run.stderr
    return run.stdout


CASES = [
    # The program of issue 57
    ("lines", '10 I=0\n20 WHILE I<3\n30 I=I+1\n40 PRINT I\n50 WEND\n60 PRINT "DONE"\n70 SYSTEM\n',
     " 1 \n 2 \n 3 \nDONE\n"),
    ("nested", '10 I=0\n20 WHILE I<2\n30 J=0\n40 WHILE J<2\n50 PRINT I;J\n60 J=J+1\n70 WEND\n80 I=I+1\n90 WEND\n'
               '100 PRINT "DONE"\n110 SYSTEM\n',
     " 0  0 \n 0  1 \n 1  0 \n 1  1 \nDONE\n"),
    ("gosub", '10 GOSUB 100\n20 PRINT "BACK"\n30 SYSTEM\n100 K=0\n110 WHILE K<3:K=K+1\n120 PRINT K\n'
              '130 WEND:PRINT "W";\n140 PRINT "R"\n150 RETURN\n',
     " 1 \n 2 \n 3 \nWR\nBACK\n"),
    ("goto out and zero passes",
     '10 I=0\n20 WHILE I<10\n30 I=I+1\n40 IF I=3 THEN 70\n50 PRINT I\n60 WEND\n70 PRINT "OUT";I\n'
     '80 WHILE 0\n90 PRINT "NEVER"\n100 WEND\n110 PRINT "END"\n120 SYSTEM\n',
     " 1 \n 2 \nOUT 3 \nEND\n"),
    ("while in then",
     '10 I=0\n20 IF I=0 THEN WHILE I<3:I=I+1\n30 PRINT I\n40 WEND:PRINT "X"\n50 SYSTEM\n',
     " 1 \n 2 \n 3 \nX\n"),
]


@pytest.mark.parametrize("name,source,expected", CASES, ids=[c[0] for c in CASES])
def test_while_wend(tmp_path, name, source, expected):
    assert run_js(tmp_path, source) == expected


def test_while_without_wend_is_a_run_time_error(tmp_path):
    # Measured: A, then "WHILE without WEND in 20"
    result, output = compile_js(tmp_path, '10 PRINT "A"\n20 WHILE 0\n30 PRINT "B"\n40 SYSTEM\n')
    assert result.returncode == 0, result.stderr
    run = subprocess.run([NODE, str(output)], capture_output=True, text=True, timeout=10)
    assert run.stdout == "A\nWHILE without WEND in 20\n"


def test_wend_without_while_does_not_compile(tmp_path):
    # Real MBASIC stops at run time with "WEND without WHILE in 20"; the compiler refuses the program
    result, _ = compile_js(tmp_path, '10 PRINT "A"\n20 WEND\n30 SYSTEM\n')
    assert result.returncode != 0


def test_browser_copy_is_valid_and_loops(tmp_path):
    # The browser build of a WHILE loop is _run(pc) with yield checks; it must parse
    result, output = compile_js(tmp_path, CASES[0][1])
    assert result.returncode == 0, result.stderr
    check = subprocess.run([NODE, "--check", str(output)], capture_output=True, text=True)
    assert check.returncode == 0, check.stderr
    text = output.read_text()
    assert "while (" in text and "_run(" in text
    assert "SyntaxError" not in check.stderr
