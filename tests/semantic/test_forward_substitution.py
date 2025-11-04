#!/usr/bin/env python3
"""Test forward substitution optimizations"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from lexer import tokenize
from parser import Parser
from semantic_analyzer import SemanticAnalyzer

# Test 1: Single-use temporary - can substitute
test1 = """
10 A = 10
20 B = 20
30 TEMP = A + B
40 PRINT TEMP
50 END
"""

# Test 2: Dead store - variable never used
test2 = """
10 A = 10
20 TEMP = A * 2
30 PRINT A
40 END
"""

# Test 3: Multiple uses - cannot substitute
test3 = """
10 A = 10
20 TEMP = A * 2
30 PRINT TEMP
40 PRINT TEMP
50 END
"""

# Test 4: Simple constant - skip (already optimized)
test4 = """
10 X = 42
20 PRINT X
30 END
"""

# Test 5: Simple variable copy - use copy propagation instead
test5 = """
10 A = 10
20 B = A
30 PRINT B
40 END
"""

# Test 6: Complex expression with single use
test6 = """
10 A = 10
20 B = 20
30 C = 5
40 RESULT = (A + B) * C / 2
50 PRINT RESULT
60 END
"""

# Test 7: Multiple variables, some substitutable
test7 = """
10 A = 10
20 B = 20
30 TEMP1 = A + B
40 TEMP2 = A * B
50 PRINT TEMP1
60 PRINT TEMP2
70 PRINT TEMP1
80 END
"""

# Test 8: Expression with function call - has side effects
test8 = """
10 DEF FNTEST(X) = X * 2
20 A = 10
30 TEMP = FNTEST(A)
40 PRINT TEMP
50 END
"""

print("=" * 70)
print("FORWARD SUBSTITUTION OPTIMIZATION TEST")
print("=" * 70)

tests = [
    (test1, "Single-use temporary", 1, 0),  # 1 substitutable, 0 dead
    (test2, "Dead store", 0, 1),  # 0 substitutable, 1 dead
    (test3, "Multiple uses", 0, 0),  # 0 substitutable, 0 dead (multi-use)
    (test4, "Simple constant", 0, 0),  # Skip simple constants
    (test5, "Simple variable copy", 0, 0),  # Use copy propagation
    (test6, "Complex expression", 1, 0),  # 1 substitutable
    (test7, "Mixed scenarios", 1, 0),  # TEMP2 substitutable, TEMP1 multi-use
    (test8, "Function call side effect", 0, 0),  # Has side effects
]

passed = 0
failed = 0

for i, (test_code, description, expected_subst, expected_dead) in enumerate(tests, 1):
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

        substitutable = [fs for fs in analyzer.forward_substitutions if fs.can_substitute]
        dead_stores = [fs for fs in analyzer.forward_substitutions if fs.use_count == 0]

        subst_count = len(substitutable)
        dead_count = len(dead_stores)

        if subst_count == expected_subst and dead_count == expected_dead:
            print(f"  ✓ PASS: Found {subst_count} substitutable, {dead_count} dead")
            for fs in substitutable:
                print(f"    Line {fs.line}: {fs.variable} = {fs.expression}")
                print(f"      {fs.reason}")
            for fs in dead_stores:
                print(f"    Line {fs.line}: {fs.variable} = {fs.expression} (DEAD)")
            passed += 1
        else:
            print(f"  ✗ FAIL: Expected {expected_subst} substitutable and {expected_dead} dead")
            print(f"          Got {subst_count} substitutable and {dead_count} dead")
            for fs in analyzer.forward_substitutions:
                print(f"    Line {fs.line}: {fs.variable} = {fs.expression}")
                print(f"      Uses: {fs.use_count}, Can substitute: {fs.can_substitute}")
                print(f"      Reason: {fs.reason}")
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
