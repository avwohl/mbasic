#!/usr/bin/env python3
"""Test expression reassociation optimizations"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from lexer import tokenize
from parser import Parser
from semantic_analyzer import SemanticAnalyzer

# Test 1: Addition chain (A + 1) + 2 -> A + 3
test1 = """
10 A = 10
20 B = (A + 1) + 2
30 END
"""

# Test 2: Multiplication chain (A * 2) * 3 -> A * 6
test2 = """
10 A = 10
20 C = (A * 2) * 3
30 END
"""

# Test 3: Mixed addition 2 + (A + 3) -> A + 5
test3 = """
10 A = 10
20 D = 2 + (A + 3)
30 END
"""

# Test 4: Complex multiplication (A * B) * 2 * 3 -> (A * B) * 6
test4 = """
10 A = 10
20 B = 5
30 E = (A * B) * 2 * 3
40 END
"""

# Test 5: Longer addition chain 1 + A + 2 + 3 -> A + 6
test5 = """
10 A = 10
20 F = 1 + A + 2 + 3
30 END
"""

# Test 6: Longer multiplication chain 2 * A * 3 * 4 -> A * 24
test6 = """
10 A = 10
20 G = 2 * A * 3 * 4
30 END
"""

# Test 7: Addition with only constants - should be fully folded
test7 = """
10 X = (1 + 2) + 3
20 END
"""

# Test 8: Multiple reassociations in one line
test8 = """
10 A = 5
20 B = 10
30 X = (A + 1) + 2
40 Y = (B * 2) * 3
50 END
"""

# Test 9: Nested reassociations
test9 = """
10 A = 10
20 X = ((A + 1) + 2) + 3
30 END
"""

# Test 10: No reassociation needed (single constant)
test10 = """
10 A = 10
20 X = A + 5
30 END
"""

print("=" * 70)
print("EXPRESSION REASSOCIATION OPTIMIZATION TEST")
print("=" * 70)

tests = [
    (test1, "Addition chain (A + 1) + 2", 1),
    (test2, "Multiplication chain (A * 2) * 3", 1),
    (test3, "Mixed addition 2 + (A + 3)", 1),
    (test4, "Complex multiplication (A * B) * 2 * 3", 1),
    (test5, "Longer addition chain 1 + A + 2 + 3", 1),
    (test6, "Longer multiplication chain 2 * A * 3 * 4", 1),
    (test7, "All constants (should be fully folded)", 1),
    (test8, "Multiple reassociations", 2),
    (test9, "Nested reassociations", 1),
    (test10, "No reassociation needed", 0),
]

passed = 0
failed = 0

for i, (test_code, description, expected_count) in enumerate(tests, 1):
    print(f"\nTest {i}: {description}")

    try:
        tokens = tokenize(test_code)
        parser = Parser(tokens)
        program = parser.parse()
        analyzer = SemanticAnalyzer()
        success = analyzer.analyze(program)

        if not success:
            print(f"  ✗ FAIL: Analysis failed")
            print(f"    Errors: {analyzer.errors}")
            failed += 1
            continue

        reassoc_count = len(analyzer.expression_reassociations)

        if reassoc_count >= expected_count:
            print(f"  ✓ PASS: Found {reassoc_count} reassociation(s)")
            for er in analyzer.expression_reassociations:
                print(f"    Line {er.line}: {er.original_expr} → {er.reassociated_expr}")
                print(f"      {er.operation} ({er.savings})")
            passed += 1
        else:
            print(f"  ✗ FAIL: Expected at least {expected_count} reassociations, found {reassoc_count}")
            if analyzer.expression_reassociations:
                for er in analyzer.expression_reassociations:
                    print(f"    Line {er.line}: {er.original_expr} → {er.reassociated_expr}")
            failed += 1

    except Exception as e:
        print(f"  ✗ FAIL: Exception: {e}")
        import traceback
        traceback.print_exc()
        failed += 1

print("\n" + "=" * 70)
print(f"Results: {passed} passed, {failed} failed")
print("=" * 70)

if failed > 0:
    sys.exit(1)
