#!/usr/bin/env python3
"""Test branch optimization"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from lexer import tokenize
from parser import Parser
from semantic_analyzer import SemanticAnalyzer

# Test 1: Always-true condition
test1 = """
10 IF 1 THEN PRINT "TRUE"
20 END
"""

# Test 2: Always-false condition
test2 = """
10 IF 0 THEN PRINT "TRUE"
20 END
"""

# Test 3: Always-true with GOTO
test3 = """
10 IF 1 THEN GOTO 100
20 PRINT "UNREACHABLE"
30 END
100 PRINT "REACHABLE"
110 END
"""

# Test 4: Always-false with GOTO
test4 = """
10 IF 0 THEN GOTO 100
20 PRINT "REACHABLE"
30 END
100 PRINT "UNREACHABLE"
110 END
"""

# Test 5: Constant expression evaluation
test5 = """
10 A = 5
20 IF A > 3 THEN PRINT "TRUE"
30 END
"""

# Test 6: Multiple constant conditions
test6 = """
10 IF 1 THEN PRINT "ONE"
20 IF 0 THEN PRINT "TWO"
30 IF 1 + 1 THEN PRINT "THREE"
40 END
"""

# Test 7: Always-false with ELSE
test7 = """
10 IF 0 THEN GOTO 100 ELSE GOTO 200
20 END
100 PRINT "UNREACHABLE"
110 END
200 PRINT "REACHABLE"
210 END
"""

# Test 8: Complex constant expression
test8 = """
10 A = 10
20 B = 20
30 IF (A + B) > 25 THEN PRINT "TRUE"
40 END
"""

print("=" * 70)
print("BRANCH OPTIMIZATION TEST")
print("=" * 70)

tests = [
    (test1, "Always-true simple", 1, 0),  # 1 true, 0 false
    (test2, "Always-false simple", 0, 1),  # 0 true, 1 false
    (test3, "Always-true with GOTO", 1, 0),
    (test4, "Always-false with GOTO", 0, 1),
    (test5, "Constant expression TRUE", 1, 0),
    (test6, "Multiple constant conditions", 2, 1),  # 2 true, 1 false
    (test7, "Always-false with ELSE", 0, 1),
    (test8, "Complex constant expression", 1, 0),
]

passed = 0
failed = 0

for i, (test_code, description, expected_true, expected_false) in enumerate(tests, 1):
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

        always_true = [bo for bo in analyzer.branch_optimizations if bo.always_true]
        always_false = [bo for bo in analyzer.branch_optimizations if bo.always_false]

        true_count = len(always_true)
        false_count = len(always_false)

        if true_count == expected_true and false_count == expected_false:
            print(f"  ✓ PASS: Found {true_count} always-TRUE, {false_count} always-FALSE")
            for bo in always_true:
                print(f"    Line {bo.line}: IF {bo.condition} (always TRUE)")
                if bo.unreachable_branch:
                    print(f"      Unreachable: {bo.unreachable_branch}")
            for bo in always_false:
                print(f"    Line {bo.line}: IF {bo.condition} (always FALSE)")
                if bo.unreachable_branch:
                    print(f"      Unreachable: {bo.unreachable_branch}")
            passed += 1
        else:
            print(f"  ✗ FAIL: Expected {expected_true} TRUE and {expected_false} FALSE")
            print(f"          Got {true_count} TRUE and {false_count} FALSE")
            for bo in analyzer.branch_optimizations:
                print(f"    Line {bo.line}: IF {bo.condition}")
                print(f"      Constant: {bo.is_constant}, Value: {bo.constant_value}")
                print(f"      Always true: {bo.always_true}, Always false: {bo.always_false}")
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
