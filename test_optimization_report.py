#!/usr/bin/env python3
"""Test comprehensive optimization report"""

import sys
sys.path.insert(0, 'src')

from lexer import tokenize
from parser import Parser
from semantic_analyzer import SemanticAnalyzer

test_program = """
10 REM === Comprehensive optimization test ===
20 A% = 10
30 B% = 20
40 C = 5.5

50 REM === FOR loop with loop-invariant CSE ===
60 FOR I = 1 TO 100
70   X = A% + B%
80   Y = A% + B%
90   Z = I * 2
100   W = I * 2
110 NEXT I

200 REM === WHILE loop with invariant ===
210 INPUT D, E
220 N = 0
230 WHILE N < 50
240   P = D * E
250   Q = D * E
260   N = N + 1
270 WEND

300 REM === Nested loops ===
310 FOR J = 1 TO 5
320   FOR K = 1 TO 3
330     R = C * 2
340     S = C * 2
350   NEXT K
360 NEXT J

400 REM === Subroutine that doesn't modify ===
410 GOSUB 1000
420 T = A% + B%
430 PRINT "T should be CSE with X and Y"

500 REM === IF-GOTO loop ===
510 M = 0
520 U = D * E
530 V = D * E
540 M = M + 1
550 IF M < 10 THEN 520

600 END

1000 REM Subroutine - read only
1010 PRINT A% + B%
1020 RETURN
"""

print("=" * 70)
print("COMPREHENSIVE OPTIMIZATION REPORT TEST")
print("=" * 70)

print("\nParsing test program...")
tokens = tokenize(test_program)
parser = Parser(tokens)
program = parser.parse()

print("Performing semantic analysis...")
analyzer = SemanticAnalyzer()
success = analyzer.analyze(program)

if success:
    print("\n" + analyzer.get_report())
else:
    print("\n✗ Analysis failed!")
    for error in analyzer.errors:
        print(f"  {error}")
    sys.exit(1)
