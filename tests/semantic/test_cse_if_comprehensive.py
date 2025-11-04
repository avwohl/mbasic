#!/usr/bin/env python3
"""Comprehensive CSE with IF THEN ELSE test"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from lexer import tokenize
from parser import Parser
from semantic_analyzer import SemanticAnalyzer

test_program = """
10 REM === Scenario 1: Expression computed before IF, available after ===
20 X1 = A + B
30 IF C THEN Y1 = 10
40 X2 = A + B
50 PRINT "Should detect A+B as CSE at lines 20, 40"

60 REM === Scenario 2: Expression computed in both branches ===
70 IF D THEN M1 = E * F ELSE M2 = E * F
80 M3 = E * F
90 PRINT "Should detect E*F as CSE at lines 70, 80"

100 REM === Scenario 3: Expression invalidated in one branch ===
110 N1 = G * 2
120 IF H THEN G = 100
130 N2 = G * 2
140 PRINT "Should NOT detect G*2 as CSE (G modified)"

150 REM === Scenario 4: Expression computed in THEN only ===
160 IF I THEN P1 = J + K
170 P2 = J + K
180 PRINT "May or may not detect - depends on control flow"

190 REM === Scenario 5: Nested IFs with CSE ===
200 Q1 = L * M
210 IF N THEN Q2 = L * M
220 IF O THEN Q3 = L * M
230 Q4 = L * M
240 PRINT "Should detect L*M across nested IFs"

250 REM === Scenario 6: Multiple expressions in branches ===
260 IF P THEN R1 = S + T: R2 = U - V ELSE R3 = S + T: R4 = U - V
270 R5 = S + T
280 R6 = U - V
290 PRINT "Should detect both S+T and U-V"

300 END
"""

print("=" * 70)
print("COMPREHENSIVE CSE WITH IF THEN ELSE TEST")
print("=" * 70)

print("\nParsing test program...")
tokens = tokenize(test_program)
parser = Parser(tokens)
program = parser.parse()

print("Performing semantic analysis...")
analyzer = SemanticAnalyzer()
success = analyzer.analyze(program)

# Print just the CSE section
print("\n" + "=" * 70)
print("CSE RESULTS")
print("=" * 70)

if analyzer.common_subexpressions:
    for cse in sorted(analyzer.common_subexpressions.values(), key=lambda x: x.first_line):
        print(f"\n{cse.expression_desc}")
        print(f"  Lines: {cse.first_line}, {', '.join(map(str, cse.occurrences))}")
        print(f"  Total: {len(cse.occurrences) + 1} times")
else:
    print("\nNo CSEs found")

if success:
    print("\n✓ Test passed!")
else:
    print("\n✗ Test failed!")
    sys.exit(1)
