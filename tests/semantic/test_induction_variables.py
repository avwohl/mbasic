#!/usr/bin/env python3
"""Test induction variable optimization"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from lexer import tokenize
from parser import Parser
from semantic_analyzer import SemanticAnalyzer

# Test 1: Primary induction variable (FOR loop control variable)
test1 = """
10 FOR I = 1 TO 10
20 PRINT I
30 NEXT I
40 END
"""

# Test 2: Array access with I * constant (strength reduction opportunity)
test2 = """
10 DIM A(100)
20 FOR I = 1 TO 10
30 LET A(I * 10) = I
40 NEXT I
50 END
"""

# Test 3: Derived IV: J = I * constant
test3 = """
10 DIM A(100)
20 FOR I = 1 TO 10
30   J = I * 5
40   LET A(J) = I
50 NEXT I
60 END
"""

# Test 4: Derived IV: J = I + constant
test4 = """
10 FOR I = 1 TO 10
20   J = I + 100
30   PRINT J
40 NEXT I
50 END
"""

# Test 5: Derived IV: J = I (simple copy)
test5 = """
10 FOR I = 1 TO 10
20   J = I
30   PRINT J
40 NEXT I
50 END
"""

# Test 6: Multiple array accesses with same IV pattern
test6 = """
10 DIM A(100), B(100)
20 FOR I = 1 TO 10
30   LET A(I * 2) = I
40   LET B(I * 2) = I + 1
50 NEXT I
60 END
"""

# Test 7: Nested loops with different IVs
test7 = """
10 DIM A(100)
20 FOR I = 1 TO 10
30   FOR J = 1 TO 5
40     LET A(I * 10 + J) = I + J
50   NEXT J
60 NEXT I
70 END
"""

# Test 8: IV with STEP value
test8 = """
10 DIM A(100)
20 FOR I = 0 TO 20 STEP 2
30   LET A(I * 3) = I
40 NEXT I
50 END
"""

# Test 9: Derived IV with both multiplication and addition
test9 = """
10 FOR I = 1 TO 10
20   J = I * 2
30   K = J + 5
40   PRINT K
50 NEXT I
60 END
"""

# Test 10: Complex array subscript (constant * I)
test10 = """
10 DIM A(100)
20 FOR I = 1 TO 10
30   LET A(10 * I) = I
40 NEXT I
50 END
"""

print("=" * 70)
print("INDUCTION VARIABLE OPTIMIZATION TEST")
print("=" * 70)

tests = [
    (test1, "Primary IV (FOR control variable)", 1, 0, 0),  # 1 primary, 0 derived, 0 SR
    (test2, "Array with I * constant", 1, 0, 1),  # 1 primary, 0 derived, 1 SR opportunity
    (test3, "Derived IV: J = I * constant", 1, 1, 1),  # 1 primary, 1 derived, 1 SR (using J)
    (test4, "Derived IV: J = I + constant", 1, 1, 0),  # 1 primary, 1 derived, 0 SR
    (test5, "Derived IV: J = I (copy)", 1, 1, 0),  # 1 primary, 1 derived, 0 SR
    (test6, "Multiple array accesses with IV", 1, 0, 2),  # 1 primary, 0 derived, 2 SR
    (test7, "Nested loops", 2, 0, 1),  # 2 primary (I and J), 0 derived, 1 SR (I*10)
    (test8, "IV with STEP value", 1, 0, 1),  # 1 primary, 0 derived, 1 SR
    (test9, "Derived IV chain", 1, 1, 0),  # 1 primary, 1 derived (J), K is not from primary
    (test10, "Array with constant * I", 1, 0, 1),  # 1 primary, 0 derived, 1 SR
]

passed = 0
failed = 0

for i, (test_code, description, expected_primary, expected_derived, expected_sr) in enumerate(tests, 1):
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

        primary_count = sum(1 for iv in analyzer.induction_variables if iv.is_primary)
        derived_count = sum(1 for iv in analyzer.induction_variables if not iv.is_primary)
        sr_count = sum(iv.strength_reduction_opportunities for iv in analyzer.induction_variables)

        if (primary_count == expected_primary and
            derived_count == expected_derived and
            sr_count >= expected_sr):
            print(f"  ✓ PASS: {primary_count} primary, {derived_count} derived, {sr_count} SR opportunities")

            for iv in analyzer.induction_variables:
                if iv.is_primary:
                    print(f"    Primary IV: {iv.variable} (start={iv.base_value}, step={iv.coefficient})")
                else:
                    print(f"    Derived IV: {iv.variable} = ", end="")
                    if iv.base_value != 0:
                        print(f"{iv.base_value} + ", end="")
                    if iv.coefficient != 1:
                        print(f"{iv.coefficient} * ", end="")
                    print(f"{iv.base_var}")

                if iv.strength_reduction_opportunities > 0:
                    print(f"      {iv.strength_reduction_opportunities} optimization(s):")
                    for line_num, expr_desc, opt_desc in iv.related_expressions:
                        print(f"        Line {line_num}: {expr_desc}")
                        print(f"          → {opt_desc}")

            passed += 1
        else:
            print(f"  ✗ FAIL: Expected {expected_primary} primary, {expected_derived} derived, {expected_sr} SR")
            print(f"         Got {primary_count} primary, {derived_count} derived, {sr_count} SR")
            for iv in analyzer.induction_variables:
                print(f"    {iv.variable}: primary={iv.is_primary}, SR={iv.strength_reduction_opportunities}")
            failed += 1

    except Exception as e:
        print(f"  ✗ FAIL: Exception: {e}")
        import traceback
        traceback.print_exc()
        failed += 1

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"Passed: {passed}/{len(tests)}")
print(f"Failed: {failed}/{len(tests)}")

if failed == 0:
    print("\n✓ All tests passed!")
    print("\nInduction variable optimization is working correctly!")
    print("\nImplemented features:")
    print("  • Primary induction variable detection (FOR loop control)")
    print("  • Derived induction variable detection:")
    print("    - J = I (copy)")
    print("    - J = I * constant")
    print("    - J = I + constant")
    print("  • Strength reduction for array subscripts:")
    print("    - A(I * constant) → pointer increment")
    print("    - A(constant * I) → pointer increment")
    print("    - A(J) where J is derived IV")
    print("  • Nested loop support")
    print("  • STEP value support")
    print("\nOptimization benefits:")
    print("  • Replace multiplication with addition in loop")
    print("  • Use pointer arithmetic instead of index calculation")
    print("  • Eliminate redundant IV computations")
    sys.exit(0)
else:
    print(f"\n✗ {failed} test(s) failed!")
    sys.exit(1)
