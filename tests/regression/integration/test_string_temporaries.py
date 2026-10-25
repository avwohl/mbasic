"""String formula too complex (issue 30), measured on MBASIC 5.21.

The binary keeps ten string temporaries (numtmp in bistrs.mac). A string
function result or a string literal holds one until the operator or function
that uses it is done; a string variable holds none. A right-nested sum such as
CHR$(65)+(CHR$(65)+(...)) holds one temporary per level while the inside is
worked out. On the binary, ten levels print 10 and eleven stop with
"String formula too complex in 10". Measured with CHR$ nests of depth 5 to 14,
literal nests, variable nests, LEFT$ nests and MID$ argument nests.
"""
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: string temporaries tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

ROOT = Path(__file__).resolve().parents[3]
TOO_COMPLEX = "String formula too complex in 10"


def run_cli(directory, source):
    (directory / "s.bas").write_text(source)
    return subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(directory / "s.bas"), "--ui", "cli"],
        input="RUN\nSYSTEM\n", cwd=directory, capture_output=True, text=True, timeout=60).stdout


def nest(item, last, depth):
    """item+(item+(...+(last))) with depth terms."""
    return "".join(item + "+(" for _ in range(depth - 1)) + last + ")" * (depth - 1)


def length_program(expression):
    return f"10 B$={expression}\n20 PRINT LEN(B$)\n30 SYSTEM\n"


@pytest.mark.parametrize("depth, ok", [(5, True), (9, True), (10, True), (11, False), (13, False)])
def test_chr_nest(tmp_path, depth, ok):
    # binary: 5 -> 5, 9 -> 9, 10 -> 10, 11 and 13 -> String formula too complex in 10
    out = run_cli(tmp_path, length_program(nest("CHR$(65)", "CHR$(70)", depth)))
    if ok:
        assert f" {depth} \n" in out and "too complex" not in out, out
    else:
        assert TOO_COMPLEX in out, out


@pytest.mark.parametrize("depth, ok", [(10, True), (11, False)])
def test_literal_nest(tmp_path, depth, ok):
    # a string literal holds a temporary too: 10 -> 10, 11 -> too complex
    out = run_cli(tmp_path, length_program(nest('"A"', '"F"', depth)))
    assert (TOO_COMPLEX in out) == (not ok), out


def test_literals_and_function_mix(tmp_path):
    # ten literals and an eleventh term that is a function result: too complex
    out = run_cli(tmp_path, length_program(nest('"A"', "CHR$(70)", 11)))
    assert TOO_COMPLEX in out, out
    out = run_cli(tmp_path, length_program(nest('"A"', "CHR$(70)", 10)))
    assert " 10 \n" in out, out


def test_variables_hold_no_temporary(tmp_path):
    # binary: V$ nests of 11 and 13 terms print 11 and 13
    out = run_cli(tmp_path, '5 V$="Q"\n' + length_program(nest("V$", "V$", 13)))
    assert " 13 \n" in out and "too complex" not in out, out


def test_left_nested_sum_frees_as_it_goes(tmp_path):
    # binary: fifteen CHR$ terms added from the left print 15
    out = run_cli(tmp_path, length_program("+".join(["CHR$(65)"] * 15)))
    assert " 15 \n" in out, out


@pytest.mark.parametrize("depth, ok", [(9, True), (10, False)])
def test_function_argument_nest(tmp_path, depth, ok):
    # LEFT$("AB"+LEFT$("AB"+...,1),1): binary 9 -> 1, 10 -> too complex
    expression = "".join('LEFT$("AB"+' for _ in range(depth)) + '"C"' + ",1)" * depth
    out = run_cli(tmp_path, length_program(expression))
    assert (TOO_COMPLEX in out) == (not ok), out


def test_earlier_argument_stays_held(tmp_path):
    # MID$(CHR$(65)+"X",LEN(CHR$(65)+<inner>),1) nested: binary 4 -> 1, 5 -> too complex
    def mid(depth):
        text = "CHR$(66)"
        for _ in range(depth):
            text = f'MID$(CHR$(65)+"X",LEN(CHR$(65)+{text}),1)'
        return text
    assert " 1 \n" in run_cli(tmp_path, length_program(mid(4)))
    assert TOO_COMPLEX in run_cli(tmp_path, length_program(mid(5)))


def test_numeric_function_over_a_string_nest(tmp_path):
    # IF LEN(<nest>)>0: binary 10 terms -> yes, 11 terms -> too complex
    def program(depth):
        return f'10 IF LEN({nest(chr(34) + "A" + chr(34), chr(34) + "F" + chr(34), depth)})>0 THEN PRINT "yes"\n30 SYSTEM\n'
    assert "yes" in run_cli(tmp_path, program(10))
    assert TOO_COMPLEX in run_cli(tmp_path, program(11))


def test_error_is_trappable_as_error_16(tmp_path):
    source = ("5 ON ERROR GOTO 100\n" + length_program(nest("CHR$(65)", "CHR$(70)", 12)).replace("30 SYSTEM\n", "")
              + '30 SYSTEM\n100 PRINT "ERR";ERR;"ERL";ERL\n110 RESUME 30\n')
    out = run_cli(tmp_path, source)
    assert "ERR 16 ERL 10" in out, out


NODE = shutil.which("node")


def run_js(directory, source):
    (directory / "s.bas").write_text(source)
    compiled = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(directory / "s.bas"),
         "--compile-js", str(directory / "s.js")],
        cwd=directory, capture_output=True, text=True, timeout=60)
    assert compiled.returncode == 0, compiled.stdout + compiled.stderr
    result = subprocess.run([NODE, str(directory / "s.js")], cwd=directory,
                            capture_output=True, text=True, timeout=60)
    return result.stdout + result.stderr


@pytest.mark.skipif(NODE is None, reason="Node.js is needed to execute generated JavaScript")
@pytest.mark.parametrize("item, last, depth, ok", [
    ("CHR$(65)", "CHR$(70)", 10, True),
    ("CHR$(65)", "CHR$(70)", 11, False),
    ('"A"', '"F"', 10, True),
    ('"A"', '"F"', 11, False),
    ("V$", "V$", 13, True),
])
def test_javascript_backend(tmp_path, item, last, depth, ok):
    out = run_js(tmp_path, '5 V$="Q"\n' + length_program(nest(item, last, depth)))
    if ok:
        assert out.strip() == str(depth), out
    else:
        assert "String formula too complex" in out, out


@pytest.mark.skipif(NODE is None, reason="Node.js is needed to execute generated JavaScript")
def test_javascript_error_is_trappable(tmp_path):
    source = ("5 ON ERROR GOTO 100\n" + length_program(nest("CHR$(65)", "CHR$(70)", 12)).replace("30 SYSTEM\n", "")
              + '30 SYSTEM\n100 PRINT "ERR";ERR\n110 RESUME 30\n')
    assert "ERR 16" in run_js(tmp_path, source)
