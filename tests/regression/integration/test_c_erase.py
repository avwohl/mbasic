"""ERASE in the C backend and the interpreter (issue 60), measured on MBASIC 5.21.

Every expected text below was measured on com/mbasic.com under cpmemu
(tests/HOW_TO_RUN_REAL_MBASIC.md). The binary:

- makes ERASE delete the array: the next use dimensions it again with the
  subscripts 0..10 (OPTION BASE 1: 1..10), all elements 0 or "";
- allows a DIM of an erased array, with any size and any number of subscripts;
- says "Duplicate Definition" for a DIM of an array that exists (after a DIM
  or after a use);
- says "Illegal function call" for ERASE of an array that does not exist:
  never dimensioned, never used, or erased already;
- says "Subscript out of range" for a use with another number of subscripts.

The C backend keeps the storage of such an array at the size of the largest
shape the program can give it, and the shape as run-time state. A loop of
1000 DIM and ERASE must not run out of memory. (The binary prints done 201 for
200 rounds; 1000 rounds take too long under the emulator to measure.)
The tests that compile need uc80, um80, ul80 and cpmemu, and skip without them.
"""
import subprocess
import sys
from pathlib import Path

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: C ERASE tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_c_backend import (NEEDS_TOOLCHAIN, compile_c, run_compiled,  # noqa: E402
                            run_interpreted)

# name: (program, output of the binary)
CASES = {
    # the issue: A(4) was Subscript out of range after ERASE
    "one_dim_default_after_erase": (
        '10 DIM A(3)\n20 A(1)=1\n30 ERASE A\n40 PRINT A(4);A(10)\n'
        '50 A(10)=7:PRINT A(10)\n70 PRINT A(11)\n',
        " 0  0 \n 7 \nSubscript out of range in 70\n"),
    "two_dim_default_after_erase": (
        '10 DIM A(3,3)\n20 A(1,1)=1\n30 ERASE A\n40 A(5,5)=2:PRINT A(5,5);A(1,1);A(10,10)\n'
        '60 PRINT A(11,0)\n',
        " 2  0  0 \nSubscript out of range in 60\n"),
    # DIM again, with a bigger size, with two subscripts, with one again
    "dim_again_with_other_shapes": (
        '10 DIM A(3)\n20 ERASE A\n30 DIM A(20)\n40 A(20)=5:PRINT A(20)\n50 ERASE A\n'
        '60 DIM A(2,2)\n70 A(2,2)=4:PRINT A(2,2)\n80 ERASE A\n90 DIM A(2)\n'
        '100 A(1)=1:PRINT A(1)\n120 PRINT A(3)\n',
        " 5 \n 4 \n 1 \nSubscript out of range in 120\n"),
    # a use with the wrong number of subscripts is Subscript out of range
    "other_number_of_subscripts": (
        '10 DIM A(3)\n20 A(1)=1\n30 ERASE A\n40 DIM A(2,2)\n'
        '50 A(2,2)=5:PRINT A(2,2),A(1,1)\n60 PRINT A(1)\n',
        " 5             0 \nSubscript out of range in 60\n"),
    "string_array": (
        '20 DIM S$(3)\n30 S$(2)="hi":PRINT S$(2)\n40 ERASE S$\n'
        '50 PRINT "[";S$(2);"]";S$(10)\n60 S$(10)="z":PRINT S$(10)\n70 DIM S$(4)\n',
        "hi\n[]\nz\nDuplicate Definition in 70\n"),
    "option_base_1": (
        '10 OPTION BASE 1\n20 DIM A(3)\n30 ERASE A\n40 PRINT A(10);A(1)\n50 PRINT A(0)\n',
        " 0  0 \nSubscript out of range in 50\n"),
    "typed_arrays_and_erase_list": (
        '10 DIM A%(2),B$(2)\n20 A%(2)=5:B$(2)="q"\n30 ERASE A%,B$\n'
        '40 PRINT A%(2);"[";B$(2);"]"\n50 A%(9)=3:B$(9)="r":PRINT A%(9);B$(9)\n'
        '60 ERASE B$:ERASE A%:PRINT "ok"\n70 PRINT A%(1)\n',
        " 0 []\n 3 r\nok\n 0 \n"),
    "erase_twice": (
        '10 DIM A(3)\n20 ERASE A\n30 ERASE A\n40 PRINT "ok"\n',
        "Illegal function call in 30\n"),
    "erase_never_used": (
        '20 ERASE Q\n30 PRINT "x"\n',
        "Illegal function call in 20\n"),
    "erase_before_first_use": (
        '10 ERASE A\n20 A(1)=1\n',
        "Illegal function call in 10\n"),
}


def run_interpreter(tmp_path, source):
    (tmp_path / "prog.bas").write_text(source)
    return run_interpreted(tmp_path, "")


@pytest.mark.parametrize("name", sorted(CASES))
def test_interpreter_matches_binary(tmp_path, name):
    source, expected = CASES[name]
    assert run_interpreter(tmp_path, source) == expected


@NEEDS_TOOLCHAIN
@pytest.mark.parametrize("name", sorted(CASES))
def test_compiled_matches_binary(tmp_path, name):
    source, expected = CASES[name]
    result = compile_c(tmp_path, source)
    assert result.returncode == 0, result.stdout + result.stderr
    assert run_compiled(tmp_path, "") == expected


@NEEDS_TOOLCHAIN
def test_dim_erase_loop_does_not_run_out_of_memory(tmp_path):
    """1000 rounds of DIM A(100), ERASE A leave the memory as it was."""
    source = ('10 FOR I=1 TO 1000\n20 DIM A(100)\n30 A(100)=I\n40 ERASE A\n50 NEXT\n'
              '60 PRINT "done";I\n70 SYSTEM\n')
    result = compile_c(tmp_path, source)
    assert result.returncode == 0, result.stdout + result.stderr
    assert run_compiled(tmp_path, "") == "done 1001 \n"
