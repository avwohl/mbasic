#!/usr/bin/env python3
"""Test IF-GOTO loop detection"""

import sys
sys.path.insert(0, 'src')

from lexer import tokenize
from parser import Parser
from semantic_analyzer import SemanticAnalyzer

test_program = """
10 REM === Test IF-GOTO loop (classic BASIC style) ===
20 INPUT A, B
30 I = 0
40 X = A * B
50 Y = A * B
60 I = I + 1
70 IF I < 10 THEN 40
80 PRINT "A*B should be loop-invariant"

100 REM === Nested IF-GOTO loops ===
110 INPUT C, D
120 J = 0
130 K = 0
140 P = C + D
150 Q = C + D
160 K = K + 1
170 IF K < 3 THEN 140
180 J = J + 1
190 IF J < 5 THEN 130
200 PRINT "C+D should be invariant"

300 END
"""

print("=" * 70)
print("IF-GOTO LOOP DETECTION TEST")
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
        if loop.nested_in:
            print(f"  Nested in loop at line: {loop.nested_in}")
        if loop.contains_loops:
            print(f"  Contains nested loops: {loop.contains_loops}")
        if loop.variables_modified:
            print(f"  Modifies: {', '.join(sorted(loop.variables_modified))}")
        if loop.invariants:
            print(f"  Loop-invariant expressions:")
            for inv in sorted(loop.invariants.values(), key=lambda x: x.first_line):
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
