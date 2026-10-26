"""A number argument is range-checked as soon as it is read, before the count.

Every expected text was measured on MBASIC 5.21 (com/mbasic.com under cpmemu,
tests/HOW_TO_RUN_REAL_MBASIC.md). The binary reads the arguments of LEFT$,
RIGHT$, MID$, STRING$, INSTR and INPUT$ one by one and range-checks a number
argument (CONINT, a byte) at once, before it looks at what follows. So an extra
argument alone is a Syntax error, but with a bad byte before it the error is
Illegal function call (or Overflow above 32767):

    MID$("A",1,2,3)    Syntax error
    MID$("A",0,2,3)    Illegal function call (a start of 0 is checked first)
    MID$("A",0,"x",3)  Illegal function call (before the type of "x")

SPACE$ and CHR$ read their one argument as a plain expression: SPACE$(-1,2) is
a Syntax error. A string where a number is needed stays Type mismatch.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from basic_runner import NODE, run_interpreter, run_javascript

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: early argument range tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

ILLEGAL = "Illegal function call in 10\n"
SYNTAX = "Syntax error in 10\n"
OVERFLOW = "Overflow in 10\n"

EXPRESSIONS = {
    # a bad byte before the count error
    'MID$("A",0,2,3)': ILLEGAL,
    'MID$("A",256,2,3)': ILLEGAL,
    'MID$("A",0,-1,3)': ILLEGAL,
    'MID$("A",1,-1,3)': ILLEGAL,
    'MID$("A",0,"x",3)': ILLEGAL,
    'MID$("A",0,2,"x")': ILLEGAL,
    'MID$("A",0,2,3,4)': ILLEGAL,
    'MID$("A",0,2,3,4,5)': ILLEGAL,
    'LEFT$("A",-1,2)': ILLEGAL,
    'LEFT$("A",300,2)': ILLEGAL,
    'LEFT$("A",-1,"x")': ILLEGAL,
    'RIGHT$("A",-1,2)': ILLEGAL,
    'STRING$(-1,2,3)': ILLEGAL,
    'STRING$(300,"A",3)': ILLEGAL,
    'STRING$(300)': ILLEGAL,
    'INSTR(0,"A","B",4)': ILLEGAL,
    'INSTR(-1,"A","B",4)': ILLEGAL,
    'INSTR(300,"A","B",4)': ILLEGAL,
    'INSTR(300,1,"B")': ILLEGAL,
    'INSTR(0,1,"B")': ILLEGAL,
    'INSTR(0,"A")': ILLEGAL,
    'INSTR(0)': ILLEGAL,
    'INPUT$(300,1,2)': ILLEGAL,
    'INPUT$(1,300,2)': ILLEGAL,
    # a byte over 32767 is Overflow first
    'MID$("A",40000,2,3)': OVERFLOW,
    'MID$("A",1,40000,3)': OVERFLOW,
    'LEFT$("A",40000,2)': OVERFLOW,
    'STRING$(40000,2,3)': OVERFLOW,
    'INSTR(40000,"A","B",4)': OVERFLOW,
    # good bytes: the extra argument is the error
    'MID$("A",1,2,3)': SYNTAX,
    'MID$("A",1.5,2,3)': SYNTAX,
    'MID$("A",1,2,"x")': SYNTAX,
    'MID$("A",1,2,3,"x")': SYNTAX,
    'LEFT$("A",1,2)': SYNTAX,
    'LEFT$("A",1,300)': SYNTAX,
    'RIGHT$("A",1,2)': SYNTAX,
    'STRING$(1,2,3)': SYNTAX,
    'STRING$(1,300,3)': SYNTAX,
    'STRING$(1,"A",3)': SYNTAX,
    'INSTR(1,"A","B",4)': SYNTAX,
    'INSTR(1,"A","B",4,5)': SYNTAX,
    'INPUT$(1,2,3)': SYNTAX,
    # one-argument functions have no early check
    'SPACE$(-1,2)': SYNTAX,
    'SPACE$(300,2)': SYNTAX,
    'CHR$(300,1)': SYNTAX,
    'CHR$(-1,1)': SYNTAX,
    # unchanged: the count with a good start, and a wrong type first
    'MID$("A",0)': ILLEGAL,
    'MID$("A",1,300)': ILLEGAL,
    'MID$(1,0,2,3)': "Type mismatch in 10\n",
    'MID$("A","x",2,3)': "Type mismatch in 10\n",
    'LEFT$(1,-1,2)': "Type mismatch in 10\n",
}

SOURCES = {expr: f"10 PRINT {expr}\n" for expr in EXPRESSIONS}

TRAPPED = ('10 ON ERROR GOTO 100\n20 PRINT MID$("A",0,2,3):PRINT "after"\n30 END\n'
           '100 PRINT ERR;ERL:RESUME NEXT\n')
TRAPPED_OUT = " 5  20 \nafter\n"


@pytest.mark.parametrize("expr", sorted(EXPRESSIONS))
def test_interpreter(tmp_path, expr):
    assert run_interpreter(tmp_path, SOURCES[expr]) == EXPRESSIONS[expr]


@pytest.mark.skipif(NODE is None, reason="Node.js is needed to execute generated JavaScript")
@pytest.mark.parametrize("expr", sorted(EXPRESSIONS))
def test_javascript(tmp_path, expr):
    assert run_javascript(tmp_path, SOURCES[expr]) == EXPRESSIONS[expr]


def test_trapped_interpreter(tmp_path):
    assert run_interpreter(tmp_path, TRAPPED) == TRAPPED_OUT


@pytest.mark.skipif(NODE is None, reason="Node.js is needed to execute generated JavaScript")
def test_trapped_javascript(tmp_path):
    assert run_javascript(tmp_path, TRAPPED) == TRAPPED_OUT


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
