"""Variable names that are not JavaScript names (or are names of the generated program).

The expected text of each program was measured on MBASIC 5.21 (com/mbasic.com
under cpmemu, tests/HOW_TO_RUN_REAL_MBASIC.md). A BASIC name can have a dot
(A.B, X.Y$, FNA.B), and can be the name of a JavaScript word or of a name that the
generated program uses: MAIN, PROCESS, TRUE, FALSE, ARGUMENTS, ENUM, DEBUGGER,
IMPLEMENTS, WINDOW, DOCUMENT, REQUIRE, CONSOLE. All of them are plain
variables, and the compiled program must print what the interpreter prints.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from basic_runner import NODE, run_interpreter, run_javascript

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: JavaScript variable name tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

CASES = {
    "main": ("10 MAIN=1:PRINT MAIN\n", " 1 \n"),
    "process": ("10 PROCESS=2:PRINT PROCESS\n", " 2 \n"),
    "require": ("10 REQUIRE=3:PRINT REQUIRE\n", " 3 \n"),
    "console": ("10 CONSOLE=4:PRINT CONSOLE\n", " 4 \n"),
    "dot": ("10 A.B=5:PRINT A.B\n", " 5 \n"),
    "true_false": ("10 TRUE=6:FALSE=7:PRINT TRUE;FALSE\n", " 6  7 \n"),
    "arguments_eval": ("10 ARGUMENTS=8:EVAL=9:PRINT ARGUMENTS;EVAL\n", " 8  9 \n"),
    "static_yield_await_enum": (
        "10 STATIC=1:YIELD=2:AWAIT=3:ENUM=4:PRINT STATIC;YIELD;AWAIT;ENUM\n", " 1  2  3  4 \n"),
    "public_private_super": (
        "10 PUBLIC=1:PRIVATE=2:SUPER=3:EXTENDS=4:DEBUGGER=5:PRINT PUBLIC;PRIVATE;SUPER;EXTENDS;DEBUGGER\n",
        " 1  2  3  4  5 \n"),
    "window_global_document": (
        "10 WINDOW=1:GLOBAL=2:DOCUMENT=3:PRINT WINDOW;GLOBAL;DOCUMENT\n", " 1  2  3 \n"),
    "instanceof_implements": (
        "10 INSTANCEOF=1:IMPLEMENTS=2:INTERFACE=3:PACKAGE=4:PROTECTED=5:"
        "PRINT INSTANCEOF;IMPLEMENTS;INTERFACE;PACKAGE;PROTECTED\n", " 1  2  3  4  5 \n"),
    "undefined_nan_infinity": (
        "10 UNDEFINED=1:NAN=2:INFINITY=3:PRINT UNDEFINED;NAN;INFINITY\n", " 1  2  3 \n"),
    "dot_with_suffix": ('10 X.Y$="a":PRINT X.Y$:X.Y%=1:PRINT X.Y%\n', "a\n 1 \n"),
    "dot_array_for_def_fn_read_swap": (
        "10 DIM A.B(3):A.B(2)=7:PRINT A.B(2)\n20 FOR I.X=1 TO 3:PRINT I.X;:NEXT I.X:PRINT\n"
        "30 DEF FNA.B(X.Y)=X.Y*2:PRINT FNA.B(4)\n40 FOR MAIN=1 TO 2:PRINT MAIN;:NEXT:PRINT\n"
        "50 READ D.1,D.2$:PRINT D.1;D.2$\n60 DATA 5,hello\n70 SWAP D.1,MAIN:PRINT D.1;MAIN\n",
        " 7 \n 1  2  3 \n 8 \n 1  2 \n 5 hello\n 3  5 \n"),
}


@pytest.mark.parametrize("name", sorted(CASES))
def test_interpreter(tmp_path, name):
    source, expected = CASES[name]
    assert run_interpreter(tmp_path, source) == expected


@pytest.mark.skipif(NODE is None, reason="Node.js is needed to execute generated JavaScript")
@pytest.mark.parametrize("name", sorted(CASES))
def test_javascript(tmp_path, name):
    source, expected = CASES[name]
    assert run_javascript(tmp_path, source) == expected


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
