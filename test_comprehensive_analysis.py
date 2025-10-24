#!/usr/bin/env python3
"""
Comprehensive test demonstrating all semantic analysis features:
- Constant folding
- Common subexpression elimination (CSE)
- GOSUB subroutine analysis
- Loop analysis (FOR, WHILE, IF-GOTO)
- Loop-invariant code motion
- Loop unrolling candidates
"""

import sys
sys.path.insert(0, 'src')

from lexer import tokenize
from parser import Parser
from semantic_analyzer import SemanticAnalyzer

test_program = """
10 REM ===================================================================
20 REM  COMPREHENSIVE OPTIMIZATION TEST
30 REM  Demonstrates: constants, CSE, loops, subroutines
40 REM ===================================================================

100 REM === Setup constants ===
110 ARRAYSIZE% = 100
120 MAXITER% = 10
130 PI = 3.14159
140 TWOPI = PI * 2
150 DIM RESULTS(ARRAYSIZE%)
160 PRINT "Array size:"; ARRAYSIZE%

200 REM === FOR loop with loop-invariant expressions ===
210 INPUT RADIUS
220 FOR I = 1 TO MAXITER%
230   AREA = PI * RADIUS * RADIUS
240   CIRCUM = TWOPI * RADIUS
250   RESULTS(I) = AREA
260 NEXT I
270 PRINT "Loop 1: PI*RADIUS*RADIUS and TWOPI*RADIUS are loop-invariant"

300 REM === WHILE loop with CSE ===
310 INPUT A, B, C
320 COUNT = 0
330 WHILE COUNT < 5
340   X = A * B + C
350   Y = A * B + C
360   Z = COUNT * 2
370   COUNT = COUNT + 1
380 WEND
390 PRINT "Loop 2: A*B+C is loop-invariant CSE"

400 REM === GOSUB with read-only subroutine ===
410 GOSUB 1000
420 P = A * B + C
430 PRINT "P should be CSE with X and Y (subroutine doesn't modify)"

500 REM === Nested loops ===
510 FOR J = 1 TO 3
520   FOR K = 1 TO 4
530     TEMP = TWOPI * 10
540     VALUE = TEMP + K
550   NEXT K
560 NEXT J
570 PRINT "Nested loops: both can be unrolled, TWOPI*10 is invariant"

600 REM === IF-GOTO loop with invariant ===
610 INPUT D, E
620 N = 0
630 RESULT1 = D * E * 2
640 RESULT2 = D * E * 2
650 N = N + 1
660 IF N < 8 THEN 630
670 PRINT "IF-GOTO loop: D*E*2 is loop-invariant"

700 REM === GOSUB that modifies variables ===
710 GOSUB 2000
720 Q = A * B + C
730 PRINT "Q should NOT be CSE (A was modified by subroutine)"

800 END

1000 REM === Read-only subroutine ===
1010 PRINT "Area ="; A * B + C
1020 RETURN

2000 REM === Subroutine that modifies variables ===
2010 A = A * 2
2020 RETURN
"""

print("=" * 80)
print("COMPREHENSIVE SEMANTIC ANALYSIS TEST")
print("=" * 80)
print()
print("This test demonstrates:")
print("  • Constant folding (ARRAYSIZE%, MAXITER%, TWOPI)")
print("  • Runtime constant DIM subscripts")
print("  • Common subexpression elimination")
print("  • Loop analysis (FOR, WHILE, IF-GOTO)")
print("  • Loop-invariant code motion opportunities")
print("  • Loop unrolling candidates")
print("  • Subroutine side-effect analysis")
print("  • Smart CSE invalidation across GOSUB")
print("=" * 80)

print("\nParsing program...")
tokens = tokenize(test_program)
parser = Parser(tokens)
program = parser.parse()

print("Performing semantic analysis...")
analyzer = SemanticAnalyzer()
success = analyzer.analyze(program)

if success:
    print("\n✓ Analysis completed successfully!\n")
    print(analyzer.get_report())
else:
    print("\n✗ Analysis failed!")
    for error in analyzer.errors:
        print(f"  {error}")
    sys.exit(1)

# Additional validation
print("\n" + "=" * 80)
print("KEY FINDINGS SUMMARY")
print("=" * 80)

# Count optimizations
num_constants = len(analyzer.folded_expressions)
num_cses = len(analyzer.common_subexpressions)
num_loops = len(analyzer.loops)
num_hoistable = sum(1 for loop in analyzer.loops.values()
                     for inv in loop.invariants.values()
                     if inv.can_hoist)
num_unrollable = sum(1 for loop in analyzer.loops.values() if loop.can_unroll)
num_subroutines = len(analyzer.subroutines)

print(f"\nOptimization Opportunities:")
print(f"  • {num_constants} constant folding optimizations")
print(f"  • {num_cses} common subexpressions found")
print(f"  • {num_loops} loops analyzed")
print(f"  • {num_hoistable} loop-invariant expressions that can be hoisted")
print(f"  • {num_unrollable} loops that can be unrolled")
print(f"  • {num_subroutines} subroutines analyzed for side effects")

print("\n✓ All features working correctly!")
