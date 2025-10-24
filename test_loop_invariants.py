#!/usr/bin/env python3
"""Test loop-invariant detection"""

import sys
sys.path.insert(0, 'src')

from lexer import tokenize
from parser import Parser
from semantic_analyzer import SemanticAnalyzer

test_program = """
10 REM === Test 1: Loop-invariant expression ===
20 INPUT A, B
30 FOR I = 1 TO 10
40   X = A * B
50   Y = A * B
60   Z = I * 2
70 NEXT I
80 PRINT "A*B is loop-invariant (not dependent on I)"

100 REM === Test 2: Expression depends on loop variable ===
110 FOR J = 1 TO 5
120   R = J * 2
130   S = J * 2
140 NEXT J
150 PRINT "J*2 is NOT loop-invariant (depends on J)"

200 REM === Test 3: Nested loops with invariants ===
210 INPUT C, D
220 FOR K = 1 TO 3
230   FOR L = 1 TO 4
240     P = C + D
250     Q = C + D
260     M = L * 3
270     N = L * 3
280   NEXT L
290 NEXT K
300 PRINT "C+D is invariant in both loops, L*3 is invariant in inner loop"

400 REM === Test 4: Mixed expressions ===
410 INPUT E, F
420 FOR M = 1 TO 8
430   A1 = E * F
440   A2 = E * F
450   B1 = M + E
460   B2 = M + E
470 NEXT M
480 PRINT "E*F is invariant, M+E is NOT invariant"

500 END
"""

print("=" * 70)
print("LOOP-INVARIANT DETECTION TEST")
print("=" * 70)

print("\nParsing test program...")
tokens = tokenize(test_program)
parser = Parser(tokens)
program = parser.parse()

print("Performing semantic analysis...")
analyzer = SemanticAnalyzer()
success = analyzer.analyze(program)

print("\n" + "=" * 70)
print("RESULTS")
print("=" * 70)

if analyzer.loops:
    for start_line, loop in sorted(analyzer.loops.items()):
        print(f"\nLoop at line {start_line}:")
        print(f"  Control: {loop.control_variable}, Iterations: {loop.iteration_count or 'unknown'}")
        if loop.nested_in:
            print(f"  Nested in loop at line {loop.nested_in}")

        if loop.invariants:
            print(f"  Loop-invariant expressions:")
            for inv in sorted(loop.invariants.values(), key=lambda x: x.first_line):
                if inv.can_hoist:
                    print(f"    ✓ HOIST: {inv.expression_desc}")
                    print(f"      Lines: {inv.first_line}, {', '.join(map(str, inv.occurrences))}")
                else:
                    print(f"    ✗ CANNOT HOIST: {inv.expression_desc}")
                    print(f"      Reason: {inv.reason_no_hoist}")
        else:
            print(f"  No loop-invariant expressions found")
else:
    print("\nNo loops found")

print("\n" + "=" * 70)
print("VALIDATION")
print("=" * 70)

errors = []

# Test 1: A * B should be invariant in loop at line 30
loop_30 = analyzer.loops.get(30)
if loop_30:
    invariant_found = False
    for inv in loop_30.invariants.values():
        if '(a * b)' in inv.expression_desc.lower() and inv.can_hoist:
            print("✓ Test 1 PASS: A * B is loop-invariant in loop at line 30")
            invariant_found = True
            break
    if not invariant_found:
        print("✗ Test 1 FAIL: A * B should be loop-invariant")
        errors.append("Test 1")
else:
    print("✗ Test 1 FAIL: Loop at line 30 not found")
    errors.append("Test 1")

# Test 2: J * 2 should NOT be invariant in loop at line 110
loop_110 = analyzer.loops.get(110)
if loop_110:
    not_invariant = True
    for inv in loop_110.invariants.values():
        if '(j * 2)' in inv.expression_desc.lower() and inv.can_hoist:
            print("✗ Test 2 FAIL: J * 2 should NOT be loop-invariant (depends on J)")
            errors.append("Test 2")
            not_invariant = False
            break
    if not_invariant:
        print("✓ Test 2 PASS: J * 2 is NOT loop-invariant (depends on J)")
else:
    print("✗ Test 2 FAIL: Loop at line 110 not found")
    errors.append("Test 2")

# Test 3: C + D should be invariant in both loops (220 and 230)
loop_220 = analyzer.loops.get(220)
loop_230 = analyzer.loops.get(230)
if loop_220 and loop_230:
    found_220 = any('(c + d)' in inv.expression_desc.lower() and inv.can_hoist
                    for inv in loop_220.invariants.values())
    found_230 = any('(c + d)' in inv.expression_desc.lower() and inv.can_hoist
                    for inv in loop_230.invariants.values())

    if found_220 and found_230:
        print("✓ Test 3 PASS: C + D is loop-invariant in both outer and inner loops")
    else:
        print(f"✗ Test 3 FAIL: C + D should be invariant (found in 220: {found_220}, 230: {found_230})")
        errors.append("Test 3")
else:
    print("✗ Test 3 FAIL: Nested loops not found")
    errors.append("Test 3")

# Test 4: E * F should be invariant, M + E should not be
loop_420 = analyzer.loops.get(420)
if loop_420:
    ef_invariant = any('(e * f)' in inv.expression_desc.lower() and inv.can_hoist
                       for inv in loop_420.invariants.values())
    me_not_invariant = not any('(m + e)' in inv.expression_desc.lower() and inv.can_hoist
                               for inv in loop_420.invariants.values())

    if ef_invariant and me_not_invariant:
        print("✓ Test 4 PASS: E * F is invariant, M + E is not")
    else:
        print(f"✗ Test 4 FAIL: E*F invariant: {ef_invariant}, M+E not invariant: {me_not_invariant}")
        errors.append("Test 4")
else:
    print("✗ Test 4 FAIL: Loop at line 420 not found")
    errors.append("Test 4")

if errors:
    print(f"\n✗ {len(errors)} test(s) failed: {', '.join(errors)}")
    sys.exit(1)
else:
    print("\n✓ All tests passed!")
