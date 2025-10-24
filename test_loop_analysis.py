#!/usr/bin/env python3
"""Test comprehensive loop analysis"""

import sys
sys.path.insert(0, 'src')

from lexer import tokenize
from parser import Parser
from semantic_analyzer import SemanticAnalyzer

test_program = """
10 REM === Test 1: Simple FOR loop with constant bounds ===
20 FOR I = 1 TO 10
30   X = A * B
40   Y = A * B
50   Z = A * B + I
60 NEXT I
70 PRINT "Loop 1: should detect A*B as loop-invariant (occurs 3 times)"

100 REM === Test 2: Nested loops ===
110 FOR J = 1 TO 5
120   FOR K = 1 TO 3
130     W = C + D
140     V = C + D
150   NEXT K
160 NEXT J
170 PRINT "Loop 2: nested loops, C+D is loop-invariant"

200 REM === Test 3: Loop with varying bounds ===
210 INPUT N
220 FOR M = 1 TO N
230   R = E * F
240   S = E * F
250 NEXT M
260 PRINT "Loop 3: unknown iteration count"

300 REM === Test 4: Small loop good for unrolling ===
310 FOR P = 1 TO 3
320   ARR(P) = P * 2
330 NEXT P
340 PRINT "Loop 4: can be unrolled (3 iterations)"

400 END
"""

print("=" * 70)
print("LOOP ANALYSIS TEST")
print("=" * 70)

print("\nParsing test program...")
tokens = tokenize(test_program)
parser = Parser(tokens)
program = parser.parse()

print("Performing semantic analysis...")
analyzer = SemanticAnalyzer()
success = analyzer.analyze(program)

print("\n" + "=" * 70)
print("LOOP ANALYSIS RESULTS")
print("=" * 70)

if analyzer.loops:
    for start_line, loop in sorted(analyzer.loops.items()):
        print(f"\nLoop at line {start_line} ({loop.loop_type.value}):")
        print(f"  End line: {loop.end_line}")
        if loop.control_variable:
            print(f"  Control variable: {loop.control_variable}")
        if loop.start_value is not None:
            print(f"  Start: {loop.start_value}")
        if loop.end_value is not None:
            print(f"  End: {loop.end_value}")
        if loop.step_value is not None:
            print(f"  Step: {loop.step_value}")
        if loop.iteration_count is not None:
            print(f"  Iterations: {loop.iteration_count}")
        if loop.can_unroll:
            print(f"  ✓ Can unroll (factor: {loop.unroll_factor})")
        if loop.nested_in:
            print(f"  Nested in loop at line: {loop.nested_in}")
        if loop.contains_loops:
            print(f"  Contains nested loops: {loop.contains_loops}")
        if loop.variables_modified:
            print(f"  Modifies: {', '.join(sorted(loop.variables_modified))}")
        if loop.invariants:
            print(f"  Loop-invariant expressions:")
            for inv in loop.invariants.values():
                if inv.can_hoist:
                    print(f"    ✓ {inv.expression_desc} (can hoist, {len(inv.occurrences) + 1} occurrences)")
                else:
                    print(f"    ✗ {inv.expression_desc} ({inv.reason_no_hoist})")
else:
    print("\nNo loops found")

print("\n" + "=" * 70)
print("CSE ANALYSIS")
print("=" * 70)

if analyzer.common_subexpressions:
    for cse in sorted(analyzer.common_subexpressions.values(), key=lambda x: x.first_line):
        print(f"\n{cse.expression_desc}")
        print(f"  Lines: {cse.first_line}, {', '.join(map(str, cse.occurrences))}")
        print(f"  Total: {len(cse.occurrences) + 1} times")
else:
    print("\nNo CSEs found")

if success:
    print("\n✓ Analysis completed successfully!")
else:
    print("\n✗ Analysis failed!")
    sys.exit(1)
