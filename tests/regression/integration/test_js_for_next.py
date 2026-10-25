"""FOR/NEXT in generated JavaScript: bare NEXT with INTEGER variables, and loops on one line.

The expected output of each program was checked against real MBASIC 5.21 (cpmemu) and the
interpreter.
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


def run_js(tmp_path, source):
    basic = tmp_path / "prog.bas"
    basic.write_text(source)
    output = tmp_path / "prog.js"
    result = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(basic), "--compile-js", str(output)],
        cwd=ROOT, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    # A loop that never ends makes subprocess.run raise TimeoutExpired: the test fails.
    run = subprocess.run([NODE, str(output)], capture_output=True, text=True, timeout=10)
    assert run.returncode == 0, run.stderr
    return run.stdout


def numbers(*items):
    return "".join(f" {item} \n" for item in items)


# Bare NEXT must find a loop whose variable is INTEGER (issue 14)
BARE_NEXT = [
    ("DEFINT", "10 DEFINT I\n20 FOR I=1 TO 3\n30 PRINT I\n40 NEXT\n50 SYSTEM\n", numbers(1, 2, 3)),
    ("percent", "10 FOR I%=1 TO 3\n30 PRINT I%\n40 NEXT\n50 SYSTEM\n", numbers(1, 2, 3)),
    ("double", "10 FOR D#=1 TO 3\n30 PRINT D#\n40 NEXT\n50 SYSTEM\n", numbers(1, 2, 3)),
    ("plain", "10 FOR I=1 TO 3\n30 PRINT I\n40 NEXT\n50 SYSTEM\n", numbers(1, 2, 3)),
    ("nested", "10 DEFINT I-J\n20 FOR I=1 TO 2\n25 FOR J=1 TO 2\n30 PRINT I;J\n40 NEXT\n45 NEXT\n50 SYSTEM\n",
     " 1  1 \n 1  2 \n 2  1 \n 2  2 \n"),
]


@pytest.mark.parametrize("name,source,expected", BARE_NEXT, ids=[c[0] for c in BARE_NEXT])
def test_bare_next_finds_loop(tmp_path, name, source, expected):
    assert run_js(tmp_path, source) == expected


# FOR, GOSUB and ON GOSUB that are not the last statement on their line, NEXT J,I, and loops that
# run zero times (issue 13). The expected text is the output of real MBASIC 5.21.
ONE_LINE = [
    ('for_next_on_one_line',
     '10 FOR I=1 TO 3:PRINT I:NEXT I\n20 PRINT "done"\n30 SYSTEM\n',
     ' 1 \n 2 \n 3 \ndone\n'),
    ('nested_loops_on_one_line',
     '10 FOR I=1 TO 2:FOR J=1 TO 2:PRINT I;J:NEXT J:NEXT I\n20 SYSTEM\n',
     ' 1  1 \n 1  2 \n 2  1 \n 2  2 \n'),
    ('bare_next_on_one_line',
     '10 FOR I=1 TO 3:PRINT I;:NEXT:PRINT "end"\n20 SYSTEM\n',
     ' 1  2  3 end\n'),
    ('next_after_if_on_next_line',
     '10 FOR I=1 TO 3:IF I=2 THEN PRINT "two"\n20 NEXT:PRINT "end"\n30 SYSTEM\n',
     'two\nend\n'),
    ('inner_loop_on_second_line',
     '10 FOR I=1 TO 2\n20 FOR J=1 TO 2:PRINT I;J:NEXT:NEXT\n30 SYSTEM\n',
     ' 1  1 \n 1  2 \n 2  1 \n 2  2 \n'),
    ('for_for_then_next_next',
     '10 FOR I=1 TO 2:FOR J=1 TO 2\n20 PRINT I;J:NEXT J:NEXT I\n30 SYSTEM\n',
     ' 1  1 \n 1  2 \n 2  1 \n 2  2 \n'),
    ('next_j_i',
     '10 FOR I=1 TO 2\n20 FOR J=1 TO 2\n30 PRINT I;J\n40 NEXT J,I\n50 PRINT "done"\n60 SYSTEM\n',
     ' 1  1 \n 1  2 \n 2  1 \n 2  2 \ndone\n'),
    ('next_j_i_on_one_line',
     '10 FOR I=1 TO 2:FOR J=1 TO 2:PRINT I;J:NEXT J,I\n20 PRINT "d"\n30 SYSTEM\n',
     ' 1  1 \n 1  2 \n 2  1 \n 2  2 \nd\n'),
    ('zero_iterations_keep_rest_of_line',
     '10 FOR I=5 TO 1:PRINT I:NEXT:PRINT "end"\n20 PRINT "next"\n30 SYSTEM\n',
     'end\nnext\n'),
    ('gosub_not_last',
     '10 GOSUB 100:PRINT "back"\n20 PRINT "x":GOSUB 100:PRINT "y":GOSUB 100\n30 SYSTEM\n100 PRINT "sub":RETURN\n',
     'sub\nback\nx\nsub\ny\nsub\n'),
    ('on_gosub_not_last',
     '10 ON 2 GOSUB 100,200:PRINT "back"\n20 ON 5 GOSUB 100,200:PRINT "out"\n30 SYSTEM\n100 PRINT "s1":RETURN\n200 PRINT "s2":RETURN\n',
     's2\nback\nout\n'),
    ('for_inside_if_then',
     '10 X=1\n20 IF X=1 THEN FOR I=1 TO 3:PRINT I;:NEXT I:PRINT "a"\n30 PRINT "b"\n40 X=0\n50 IF X=1 THEN FOR I=1 TO 3:PRINT I;:NEXT I:PRINT "a"\n60 PRINT "c"\n70 SYSTEM\n',
     ' 1  2  3 a\nb\nc\n'),
    ('gosub_inside_if_then',
     '10 X=1\n20 IF X=1 THEN GOSUB 100:PRINT "after"\n30 IF X=2 THEN GOSUB 100 ELSE PRINT "else"\n40 IF X=1 THEN GOSUB 100 ELSE PRINT "else"\n50 PRINT "end"\n60 SYSTEM\n100 PRINT "sub":RETURN\n',
     'sub\nafter\nelse\nsub\nend\n'),
    ('next_then_print_variable',
     '10 FOR I=1 TO 3:PRINT I;:NEXT I:PRINT "after";I\n20 FOR J=1 TO 2:FOR K=1 TO 2:PRINT J;K;:NEXT K,J:PRINT\n30 SYSTEM\n',
     ' 1  2  3 after 4 \n 1  1  1  2  2  1  2  2 \n'),
    ('zero_iterations_inner_loop',
     '10 FOR I=1 TO 2:FOR J=5 TO 1:PRINT "no":NEXT J:PRINT "mid";I:NEXT I\n20 SYSTEM\n',
     'mid 1 \nmid 2 \n'),
    ('if_then_line_else_line',
     '10 IF 1=2 THEN 50 ELSE 60\n50 PRINT "wrong"\n60 PRINT "ok"\n70 IF 1=1 THEN PRINT "t" ELSE 90\n80 SYSTEM\n90 PRINT "bad"\n',
     'ok\nt\n'),
    ('next_inside_if_else',
     '10 FOR I=1 TO 3:IF I=2 THEN NEXT ELSE PRINT "I=";I\n20 PRINT "end"\n30 SYSTEM\n',
     'I= 1 \nend\n'),
    ('next_inside_if_then',
     '10 FOR I=1 TO 3:IF I<3 THEN PRINT "lt";I:NEXT I\n20 PRINT "end"\n30 SYSTEM\n',
     'lt 1 \nlt 2 \nend\n'),
    ('gosub_inside_loop',
     '10 FOR I=1 TO 2:GOSUB 100:NEXT:PRINT "e"\n20 SYSTEM\n100 PRINT "s";I:RETURN\n',
     's 1 \ns 2 \ne\n'),
]


@pytest.mark.parametrize("name,source,expected", ONE_LINE, ids=[c[0] for c in ONE_LINE])
def test_statements_after_for_gosub_and_next(tmp_path, name, source, expected):
    assert run_js(tmp_path, source) == expected


if __name__ == "__main__":
    if NODE is None:
        print("Node.js unavailable: JavaScript execution tests skipped")
        sys.exit(2)
    sys.exit(pytest.main([__file__, "-q", "-p", "no:cacheprovider"]))
