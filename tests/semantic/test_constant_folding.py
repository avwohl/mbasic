#!/usr/bin/env python3
"""Test constant folding in semantic analyzer"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from lexer import tokenize
from parser import Parser
from semantic_analyzer import SemanticAnalyzer

test_program = """
10 REM Test program - demonstrates constant folding
20 REM Constants defined early
30 N% = 10
40 M% = N% * 2
50 REM Arrays using constant expressions and variables
60 DIM A(N%), B(5, M%), C(2+3)
70 TOTAL% = N% + M%
80 DIM D(TOTAL%)
90 REM DEF FN with constant evaluation
100 DEF FN DOUBLE(X) = X * 2
110 REM Loop (I% becomes non-constant)
120 FOR I% = 1 TO 10
130   A(I%) = FN DOUBLE(I%)
140 NEXT I%
150 REM Math functions
160 X = SQR(16)
170 Y = SIN(0)
180 Z = INT(3.7)
190 REM Complex expressions
200 RESULT = (2 + 3) * 4 - 1
210 RATIO = 100 / 10
220 REM Using constants in expressions
230 SIZE% = N% + 5
240 DOUBLE% = SIZE% * 2
250 REM Error handling
260 ON ERROR GOTO 1000
270 PRINT A(5)
280 END
1000 RESUME NEXT
"""

print("Parsing test program...")
tokens = tokenize(test_program)
parser = Parser(tokens)
program = parser.parse()

print("\nPerforming semantic analysis...")
analyzer = SemanticAnalyzer()
success = analyzer.analyze(program)

print(analyzer.get_report())

if success:
    print("\n✓ Semantic analysis passed!")
else:
    print("\n✗ Semantic analysis failed!")
    sys.exit(1)
