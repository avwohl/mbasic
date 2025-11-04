#!/usr/bin/env python3
"""Test Boolean simplification optimizations"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from lexer import tokenize
from parser import Parser
from semantic_analyzer import SemanticAnalyzer

# Test 1: Relational operator inversion - NOT(A > B) -> A <= B
test1 = """
10 A = 10
20 B = 20
30 IF NOT(A > B) THEN PRINT "A <= B"
40 END
"""

# Test 2: NOT(A < B) -> A >= B
test2 = """
10 A = 10
20 B = 20
30 IF NOT(A < B) THEN PRINT "A >= B"
40 END
"""

# Test 3: NOT(A >= B) -> A < B
test3 = """
10 A = 10
20 B = 20
30 IF NOT(A >= B) THEN PRINT "A < B"
40 END
"""

# Test 4: NOT(A <= B) -> A > B
test4 = """
10 A = 10
20 B = 20
30 IF NOT(A <= B) THEN PRINT "A > B"
40 END
"""

# Test 5: NOT(A = B) -> A <> B
test5 = """
10 A = 10
20 B = 20
30 IF NOT(A = B) THEN PRINT "A <> B"
40 END
"""

# Test 6: NOT(A <> B) -> A = B
test6 = """
10 A = 10
20 B = 20
30 IF NOT(A <> B) THEN PRINT "A = B"
40 END
"""

# Test 7: De Morgan's law - NOT(A AND B) -> (NOT A) OR (NOT B)
test7 = """
10 A = 1
20 B = 0
30 C = NOT(A AND B)
40 END
"""

# Test 8: De Morgan's law - NOT(A OR B) -> (NOT A) AND (NOT B)
test8 = """
10 A = 1
20 B = 0
30 C = NOT(A OR B)
40 END
"""

# Test 9: Multiple simplifications in one program
test9 = """
10 A = 10
20 B = 20
30 IF NOT(A > B) THEN PRINT "Case 1"
40 IF NOT(A < B) THEN PRINT "Case 2"
50 X = NOT(A AND B)
60 Y = NOT(A OR B)
70 END
"""

# Test 10: Nested simplifications - NOT(NOT(A > B))
test10 = """
10 A = 10
20 B = 20
30 IF NOT(NOT(A > B)) THEN PRINT "A > B"
40 END
"""

# Test 11: Complex expression with De Morgan
test11 = """
10 A = 1
20 B = 1
30 C = 0
40 X = NOT((A AND B) OR C)
50 END
"""

# Test 12: Assignment with Boolean simplification
test12 = """
10 A = 10
20 B = 20
30 FLAG = NOT(A > B)
40 PRINT FLAG
50 END
"""

# Test 13: Absorption law - (A AND B) OR A -> A
test13 = """
10 A = 1
20 B = 1
30 C = (A AND B) OR A
40 END
"""

# Test 14: Absorption law - A OR (A AND B) -> A
test14 = """
10 A = 1
20 B = 1
30 C = A OR (A AND B)
40 END
"""

# Test 15: Absorption law - (A OR B) AND A -> A
test15 = """
10 A = 1
20 B = 1
30 C = (A OR B) AND A
40 END
"""

# Test 16: Absorption law - A AND (A OR B) -> A
test16 = """
10 A = 1
20 B = 1
30 C = A AND (A OR B)
40 END
"""

print("=" * 70)
print("BOOLEAN SIMPLIFICATION OPTIMIZATION TEST")
print("=" * 70)

tests = [
    (test1, "NOT(A > B) -> A <= B", 1),
    (test2, "NOT(A < B) -> A >= B", 1),
    (test3, "NOT(A >= B) -> A < B", 1),
    (test4, "NOT(A <= B) -> A > B", 1),
    (test5, "NOT(A = B) -> A <> B", 1),
    (test6, "NOT(A <> B) -> A = B", 1),
    (test7, "De Morgan: NOT(A AND B)", 1),
    (test8, "De Morgan: NOT(A OR B)", 1),
    (test9, "Multiple simplifications", 4),
    (test10, "Nested NOT simplification", 2),  # NOT(NOT(...)) + relational inversion
    (test11, "Complex De Morgan expression", 1),
    (test12, "Assignment with simplification", 1),
    (test13, "Absorption: (A AND B) OR A -> A", 1),
    (test14, "Absorption: A OR (A AND B) -> A", 1),
    (test15, "Absorption: (A OR B) AND A -> A", 1),
    (test16, "Absorption: A AND (A OR B) -> A", 1),
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

        # Count both algebraic simplifications and strength reductions
        # (Boolean simplifications are reported as strength reductions)
        simplification_count = len([sr for sr in analyzer.strength_reductions
                                    if 'NOT' in sr.reduction_type or 'De Morgan' in sr.reduction_type or 'Absorption' in sr.reduction_type])

        if simplification_count >= expected_count:
            print(f"  ✓ PASS: Found {simplification_count} simplification(s)")
            for sr in analyzer.strength_reductions:
                if 'NOT' in sr.reduction_type or 'De Morgan' in sr.reduction_type or 'Absorption' in sr.reduction_type:
                    print(f"    Line {sr.line}: {sr.original_expr} → {sr.reduced_expr}")
                    print(f"      {sr.reduction_type}")
            passed += 1
        else:
            print(f"  ✗ FAIL: Expected at least {expected_count} simplifications, found {simplification_count}")
            for sr in analyzer.strength_reductions:
                if 'NOT' in sr.reduction_type or 'De Morgan' in sr.reduction_type or 'Absorption' in sr.reduction_type:
                    print(f"    Line {sr.line}: {sr.original_expr} → {sr.reduced_expr}")
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
