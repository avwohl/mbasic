"""Compile ^ chains to JavaScript and to CP/M (issue 26: ^ is left associative).

Expected output is what real MBASIC 5.21 prints under cpmemu; see
tests/regression/interpreter/test_power_assoc.py for the interpreter side.
"""
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: power associativity tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

ROOT = Path(__file__).resolve().parents[3]
NODE = shutil.which("node")

CASES = [
    ("2^3^2", "64"),
    ("2^-3^2", "1.95313E-03"),
    ("-2^2^3", "-64"),
    ("2^3^-1", ".125"),
    ("2^-2^-1", ".707107"),
    ("A^B^C", "64"),
    ("2*-3^2", "-18"),
    ("-A^B*C", "-16"),
    ("NOT 2^2", "-5"),
    ("2^2=4", "-1"),
    ("4^.5^2", "4"),
    ("2^-1^2", ".5"),
    ("2^3^2^2", "4096"),
    ("2^-2^3^2", "5.42101E-20"),
    ("2^+3^2", "64"),
    ("2^-3*2", ".25"),
    ("2^-3+2", "2.125"),
    ("2^3^-1^2", ".125"),
    ("2^NOT 1^2", ".25"),
    ("2^(3)^2", "64"),
    ("2^-2^3^-1", ".917004"),
    ("2^--2^2", "16"),
    ("2^-2^-2^2", ".957603"),
    ("2^+2^3", "64"),
    ("2^+-2^2", ".0625"),
    ("2^-+2^2", ".0625"),
    ("2^+2^-1^2", ".25"),
    ("3^+2^2^2", "6561"),
    ("2^NOT 2^2", ".03125"),
    ("2^NOT 3^2", "9.76563E-04"),
    ("2^-NOT 0^2", "2"),
    ("2^NOT 0=0", "1"),
    ("2^NOT 0+1", ".25"),
    ("2^NOT 1 AND 1", "0"),
    ("2^NOT 0*3", ".5"),
    ("2^-1+1", "1.5"),
    ("2^NOT 0^2^2", ".5"),
    ("2^NOT NOT 0^2", "1"),
    ("2^NOT 1 OR 1", "1"),
    ("2^(3^2)", "512"),
    ("(2^3)^2", "64"),
    ("(2^-3)^2", ".015625"),
    ("-2^-2^3", "-3.90625E-03"),
]


SOURCE = "10 A=2:B=3:C=2\n" + "".join(
    f"{20 + 10 * i} PRINT {expr}\n" for i, (expr, _) in enumerate(CASES))
WANT = [value for _, value in CASES]


def compile_to(tmp_path, flag, name):
    basic = tmp_path / "prog.bas"
    basic.write_text(SOURCE)
    output = tmp_path / name
    result = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(basic), flag, str(output)],
        cwd=ROOT, capture_output=True, text=True, timeout=120,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return output


@pytest.mark.skipif(NODE is None, reason="Node.js is needed")
def test_power_chains_in_javascript(tmp_path):
    output = compile_to(tmp_path, "--compile-js", "prog.js")
    result = subprocess.run([NODE, str(output)], cwd=tmp_path,
                            capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    assert [line.strip() for line in result.stdout.splitlines()] == WANT


def test_power_chains_in_c_source(tmp_path):
    """The C backend gets the same tree: the C text nests pow() calls on the left."""
    basic = tmp_path / "prog.bas"
    basic.write_text("10 INPUT A,B,C\n20 X=A^B^C\n30 Y=A^-B^C\n40 Z=A^+B^C\n")
    result = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(basic), "--compile-c", str(tmp_path / "prog")],
        cwd=ROOT, capture_output=True, text=True, timeout=120,
    )
    source = (tmp_path / "prog.c").read_text()
    assert "pow(pow(a, b), c)" in source, result.stdout + result.stderr
    assert "pow(a, (-pow(b, c)))" in source
    assert "pow(pow(a, (+b)), c)" in source


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
