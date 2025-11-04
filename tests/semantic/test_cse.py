#!/usr/bin/env python3
"""Test Common Subexpression Elimination (CSE)"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from lexer import tokenize
from parser import Parser
from semantic_analyzer import SemanticAnalyzer

# Test CSE detection across multiple scenarios
test_program = """
10 REM === Test 1: Simple CSE ===
20 X = A + B
30 Y = A + B
40 Z = A + B

50 REM === Test 2: CSE with different variables ===
60 P = X * Y
70 Q = X * Y + 1
80 R = X * Y - 1

90 REM === Test 3: CSE invalidation ===
100 M = N * 2
110 K = N * 2
120 N = 10
130 L = N * 2

140 REM === Test 4: CSE with array subscripts ===
150 DIM ARR(10)
160 A1 = ARR(I + J)
170 A2 = ARR(I + J)

180 REM === Test 5: CSE with function calls ===
190 F1 = SQR(X)
200 F2 = SQR(X) + 1
210 F3 = SQR(X) - 1

220 REM === Test 6: Complex expressions ===
230 E1 = (A + B) * (C - D)
240 E2 = (A + B) * (C - D)
250 E3 = (A + B) * (C - D) + 5

260 REM === Test 7: No CSE after modification ===
270 V1 = W + Z
280 V2 = W + Z
290 W = 100
300 V3 = W + Z

310 REM === Test 8: CSE within same line ===
320 RESULT = (U + V) + (U + V) + (U + V)

330 REM === Test 9: CSE with INPUT (should invalidate) ===
340 T1 = S * 2
350 INPUT S
360 T2 = S * 2

370 REM === Test 10: CSE that survives across lines ===
380 G1 = H * 3
390 PRINT "Hello"
400 G2 = H * 3
410 G3 = H * 3

420 END
"""

print("=" * 70)
print("COMMON SUBEXPRESSION ELIMINATION (CSE) TEST")
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
    print(f"Total CSE opportunities found: {len(analyzer.common_subexpressions)}")
    print("=" * 70)

    # Analyze the CSEs
    if analyzer.common_subexpressions:
        total_computations = 0
        total_eliminations = 0

        for cse in analyzer.common_subexpressions.values():
            computations = len(cse.occurrences) + 1
            eliminations = len(cse.occurrences)  # All but the first
            total_computations += computations
            total_eliminations += eliminations

        print(f"\nOptimization Impact:")
        print(f"  Total redundant computations: {total_eliminations}")
        print(f"  Average uses per CSE: {total_computations / len(analyzer.common_subexpressions):.1f}")

    print("\n✓ CSE test passed!")
else:
    print("\n✗ Test failed!")
    sys.exit(1)
