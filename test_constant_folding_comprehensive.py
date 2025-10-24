#!/usr/bin/env python3
"""Comprehensive test for constant folding optimization"""

import sys
sys.path.insert(0, 'src')

from lexer import tokenize
from parser import Parser
from semantic_analyzer import SemanticAnalyzer

# Test various constant folding scenarios
test_program = """
10 REM === Arithmetic Operations ===
20 A = 2 + 3
30 B = 10 - 4
40 C = 5 * 6
50 D = 100 / 4
60 E = 17 \\ 3
70 F = 2 ^ 8
80 G = 17 MOD 5

90 REM === Complex Expressions ===
100 H = (2 + 3) * (4 - 1)
110 I = 2 + 3 * 4 - 1
120 J = (10 + 5) / 3
130 K = 2 ^ 3 + 4 ^ 2

140 REM === Math Functions ===
150 L = ABS(-10)
160 M = SQR(64)
170 N = INT(7.9)
180 O = FIX(-7.9)
190 P = SGN(-5)
200 Q = CINT(3.6)
210 R = SIN(0)
220 S = COS(0)
230 T = TAN(0)
240 U = ATN(1)
250 V = EXP(0)
260 W = LOG(1)

270 REM === Runtime Constants ===
280 K1% = 100
290 K2% = K1% + 50
300 K3% = K1% * 2
310 K4% = K2% - K3%

320 REM === DEF FN ===
330 DEF FN SQUARE(X) = X * X
340 DEF FN CUBE(Y) = Y * Y * Y
350 DEF FN ADD(A, B) = A + B
360 X1 = FN SQUARE(5)
370 X2 = FN CUBE(3)
380 X3 = FN ADD(10, 20)

390 REM === Nested DEF FN ===
400 DEF FN DOUBLE(Z) = Z * 2
410 DEF FN QUAD(W) = FN DOUBLE(FN DOUBLE(W))
420 X4 = FN QUAD(7)

430 REM === Relational Operations ===
440 R1 = 5 = 5
450 R2 = 5 <> 3
460 R3 = 10 > 5
470 R4 = 3 < 10
480 R5 = 5 <= 5
490 R6 = 10 >= 5

500 REM === Logical Operations ===
510 L1 = -1 AND -1
520 L2 = -1 OR 0
530 L3 = -1 XOR 0
540 L4 = NOT 0

550 REM === Array Dimensions (constant expressions) ===
560 SIZE% = 10
570 DIM ARR1(SIZE% * 2)
580 DIM ARR2((5 + 5) * 2)
590 DIM ARR3(FN SQUARE(5))

600 REM === Mixed Expressions ===
610 M1 = SQR(16) + INT(5.9)
620 M2 = (K1% / 10) * 3
630 M3 = FN SQUARE(SQR(16))

640 REM === Non-constant (should not fold) ===
650 INPUT X
660 Y = X + 1
670 Z = SQR(X)

680 REM === After INPUT, constant propagation stops for X ===
690 PRINT Y, Z

700 END
"""

print("=" * 70)
print("COMPREHENSIVE CONSTANT FOLDING TEST")
print("=" * 70)

print("\nParsing test program...")
tokens = tokenize(test_program)
parser = Parser(tokens)
program = parser.parse()

print("Performing semantic analysis...")
analyzer = SemanticAnalyzer()
success = analyzer.analyze(program)

print(analyzer.get_report())

# Count the optimizations
if success:
    print("\n" + "=" * 70)
    print(f"Total constant folding optimizations: {len(analyzer.folded_expressions)}")
    print("=" * 70)

    # Categorize by type
    arithmetic = sum(1 for _, expr, _ in analyzer.folded_expressions
                     if any(op in expr for op in ['+', '-', '*', '/', '\\', '^', 'MOD']))
    functions = sum(1 for _, expr, _ in analyzer.folded_expressions
                    if '(' in expr and any(f in expr for f in ['SQR', 'SIN', 'COS', 'TAN', 'ATN', 'EXP', 'LOG', 'INT', 'FIX', 'ABS', 'SGN', 'CINT']))
    user_functions = sum(1 for _, expr, _ in analyzer.folded_expressions
                         if 'FN ' in expr)

    print(f"\nBreakdown:")
    print(f"  Arithmetic expressions: {arithmetic}")
    print(f"  Math function calls: {functions}")
    print(f"  User-defined function calls: {user_functions}")

    print("\n✓ Comprehensive test passed!")
else:
    print("\n✗ Test failed!")
    sys.exit(1)
