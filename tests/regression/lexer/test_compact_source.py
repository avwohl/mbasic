#!/usr/bin/env python3
"""Compact (crunched) source: what MBASIC 5.21 accepts and what it rejects.

Every expectation here was checked against the real MBASIC 5.21 binary.
MBASIC 5.21 CRUNCH does NOT split a reserved word off the front of a name.
A reserved word counts as a reserved word only when the next character is not
a letter, a digit or a dot.  So "PRINTX", "GOTO30", "IFA=1" and "NEXTI" are
variable names in real MBASIC (and a syntax error when used as a statement),
and so is "FORTUNE" or "TOTAL".  The lexer must do the same.  See
docs/history/KEYWORD_IDENTIFIER_SPLITTING.md for the earlier splitting attempt.

What real MBASIC does accept, and this test checks:
  - no space after the line number ("10PRINT 1")
  - a reserved word directly after a number ("IF A=1THEN 40", "7MOD 3")
  - a reserved word directly before a quote or bracket ("PRINT"A"", "PRINT(1)")
  - "1ELSE" (the E of ELSE does not start an exponent), "1E", "5.E2"
  - "GO TO 30" and "GO SUB 30" as GOTO and GOSUB
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.lexer import Lexer
from src.parser import Parser
from src.tokens import TokenType as T
from src.editing import ProgramManager
from src.parser import TypeInfo


def lex(text):
    """Token list for one line, without the line number and EOF."""
    toks = Lexer(text).tokenize()
    return [(t.type, t.value) for t in toks if t.type not in (T.LINE_NUMBER, T.EOF)]


def types(text):
    return [t for t, _ in lex(text)]


failures = []


def check(name, got, want):
    if got != want:
        failures.append(f"{name}: got {got!r}, want {want!r}")


# --- Real MBASIC does not split names: these stay one identifier -----------
for name in ["printx", "goto30", "print1", "ifa", "nexti", "fortune", "total",
             "tox", "andy", "note", "origin", "forx", "datax", "remx", "thenx"]:
    check(f"identifier {name}", lex(f"10 {name}=1")[0], (T.IDENTIFIER, name))

# Suffixes end a name; the keyword rule still applies to the whole name
check("PRINTA$ is one name", lex("10 PRINTA$")[0], (T.IDENTIFIER, "printa$"))
check("FORI is one name", types("10 FORI=1TO3")[0], T.IDENTIFIER)

# Names with a dot continue the name (real MBASIC: no keyword inside)
check("A.B is one name", lex("10 A.B=4")[0], (T.IDENTIFIER, "a.b"))
check("TO.X is one name", lex("10 TO.X=4")[0], (T.IDENTIFIER, "to.x"))

# --- Keywords that are delimited are keywords --------------------------------
check("PRINT with space", types("10 PRINT X"), [T.PRINT, T.IDENTIFIER])
check("PRINT before quote", types('10 PRINT"A"'), [T.PRINT, T.STRING])
check("PRINT before bracket", types("10 PRINT(1)"),
      [T.PRINT, T.LPAREN, T.NUMBER, T.RPAREN])
check("keyword after number", types("10 IF A=1THEN 40"),
      [T.IF, T.IDENTIFIER, T.EQUAL, T.NUMBER, T.THEN, T.NUMBER])
check("AND after number", types("10 IF A=1AND B=2 THEN 40")[3:6],
      [T.NUMBER, T.AND, T.IDENTIFIER])
check("MOD after number", types("10 PRINT 7MOD 3"),
      [T.PRINT, T.NUMBER, T.MOD, T.NUMBER])
check("TO after space", types("10 FOR I=1TO 3")[3:6],
      [T.NUMBER, T.TO, T.NUMBER])
# 1TO3 is the number 1 and the name TO3: real MBASIC gives a syntax error
check("1TO3 is a name", types("10 FOR I=1TO3")[3:6],
      [T.NUMBER, T.IDENTIFIER])
check("colon ends a keyword", types("10 PRINT:PRINT"), [T.PRINT, T.COLON, T.PRINT])
check("PRINT#1", types("10 PRINT#1"), [T.PRINT, T.HASH, T.NUMBER])
check("FNA is a name token", lex("10 X=FNA(1)")[2], (T.IDENTIFIER, "fna"))

# --- Number followed by E ----------------------------------------------------
check("1ELSE", types("10 PRINT 1ELSE PRINT 2")[:3], [T.PRINT, T.NUMBER, T.ELSE])
check("1E is 1", lex("10 PRINT 1E")[1], (T.NUMBER, 1.0))
check("1D is 1", lex("10 PRINT 1D")[1], (T.NUMBER, 1.0))
check("1E+ is 1", lex("10 PRINT 1E+")[1], (T.NUMBER, 1.0))
check("1E5", lex("10 PRINT 1E5")[1], (T.NUMBER, 100000.0))
check("1E-2", lex("10 PRINT 1E-2")[1], (T.NUMBER, 0.01))
check("1D2", lex("10 PRINT 1D2")[1], (T.NUMBER, 100.0))
check("5.E2", lex("10 PRINT 5.E2")[1], (T.NUMBER, 500.0))
check("1.5E", lex("10 PRINT 1.5E")[1], (T.NUMBER, 1.5))
check("1EQV 0", types("10 PRINT 1EQV 0")[:3], [T.PRINT, T.NUMBER, T.EQV])
check("1.E is 1", lex("10 PRINT 1.E")[1], (T.NUMBER, 1.0))
check("1.ELSE", types("10 PRINT 1.ELSE PRINT 2")[:3], [T.PRINT, T.NUMBER, T.ELSE])
check("1.EQV 0", types("10 PRINT 1.EQV 0")[:3], [T.PRINT, T.NUMBER, T.EQV])
check("30ELSE 40", types("10 IF X=1THEN 30ELSE 40")[-3:], [T.NUMBER, T.ELSE, T.NUMBER])

# --- GO TO / GO SUB ----------------------------------------------------------
check("GO TO 30", lex("10 GO TO 30")[:2], [(T.GOTO, "goto"), (T.NUMBER, 30)])
check("GO SUB 30", lex("10 GO SUB 30")[:2], [(T.GOSUB, "gosub"), (T.NUMBER, 30)])
check("go to 30", lex("10 go to 30")[0], (T.GOTO, "goto"))
check("IF THEN GO TO", types("10 IF X THEN GO TO 30")[-2:], [T.GOTO, T.NUMBER])
check("ON X GO TO", types("10 ON X GO TO 20,30")[2], T.GOTO)
check("GO alone", lex("10 GO=1")[0], (T.IDENTIFIER, "go"))
check("GO TOO is not GOTO", types("10 GO TOO")[0], T.IDENTIFIER)
check("GO TO30 is not GOTO (real MBASIC: syntax error)",
      types("10 GO TO30")[0], T.IDENTIFIER)
check("GO X", types("10 GO X")[0], T.IDENTIFIER)

# --- The parser takes the accepted forms -------------------------------------
def parses(text):
    try:
        Parser(Lexer(text).tokenize()).parse_program()
        return True
    except Exception:
        return False


for good in ['10 IF A=1THEN 40', '10 IF A=1THEN 30ELSE 40', '10 PRINT"A"',
             '10 GO TO 30', '10 GO SUB 30', '10 FOR I=1TO 3:NEXT',
             '10 TOTAL=5:FORTUNE=1:PRINT TOTAL;FORTUNE']:
    check(f"parse {good}", parses(good), True)

# --- Loading a file: no space needed after the line number -------------------
def_types = {letter: TypeInfo.SINGLE for letter in 'abcdefghijklmnopqrstuvwxyz'}
with tempfile.TemporaryDirectory() as d:
    path = os.path.join(d, "compact.bas")
    with open(path, "w") as f:
        f.write('10PRINT"A"\n20GOTO 40\n30PRINT"skipped"\n40END\n')
    manager = ProgramManager(def_types)
    ok, errors = manager.load_from_file(path)
    check("load compact file ok", ok, True)
    check("load compact file errors", errors, [])
    check("load compact file lines", sorted(manager.lines), [10, 20, 30, 40])

if failures:
    print(f"FAILED: {len(failures)} check(s)")
    for line in failures:
        print("  " + line)
    sys.exit(1)

print("compact source tests passed")
