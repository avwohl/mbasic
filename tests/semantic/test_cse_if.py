#!/usr/bin/env python3
"""Test CSE with IF THEN ELSE statements"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from lexer import tokenize
from parser import Parser
from semantic_analyzer import SemanticAnalyzer

# Test various CSE scenarios with IF statements
test_program = """
10 REM === Test 1: CSE before IF ===
20 X = A + B
30 Y = A + B
40 IF C THEN Z = A + B

50 REM === Test 2: CSE in both branches ===
60 IF D THEN M = E * F ELSE N = E * F
70 P = E * F

80 REM === Test 3: CSE available after IF ===
90 R = G + H
100 IF K THEN S = 10 ELSE S = 20
110 T = G + H

120 REM === Test 4: CSE invalidated in one branch ===
130 U = I * 2
140 IF L THEN I = 100
150 V = I * 2

160 REM === Test 5: CSE in both branches, different ===
170 IF M THEN W1 = J + K ELSE W2 = J - K
180 W3 = J + K
190 W4 = J - K

200 REM === Test 6: Nested IF with CSE ===
210 Q1 = P * Q
220 IF R1 THEN Q2 = P * Q
230 Q3 = P * Q

240 REM === Test 7: CSE computed in both branches ===
250 IF S1 = 1 THEN R1 = X * Y ELSE R2 = X * Y
260 R3 = X * Y

270 END
"""

print("=" * 70)
print("CSE WITH IF THEN ELSE TEST")
print("=" * 70)

print("\nParsing test program...")
tokens = tokenize(test_program)
parser = Parser(tokens)
program = parser.parse()

print("Performing semantic analysis...")
analyzer = SemanticAnalyzer()
success = analyzer.analyze(program)

print(analyzer.get_report())

if success:
    print("\n" + "=" * 70)
    print(f"CSE Analysis:")
    print("=" * 70)

    if analyzer.common_subexpressions:
        for cse in sorted(analyzer.common_subexpressions.values(), key=lambda x: x.first_line):
            print(f"\n{cse.expression_desc}:")
            print(f"  Lines: {cse.first_line}, {', '.join(map(str, cse.occurrences))}")

    print("\n✓ CSE IF test passed!")
else:
    print("\n✗ Test failed!")
    sys.exit(1)
