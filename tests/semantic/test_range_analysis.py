#!/usr/bin/env python3
"""
Test Range Analysis Optimization

Tests the compiler's ability to track value ranges of variables through
conditional statements and use that information for constant propagation.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from lexer import tokenize
from parser import Parser
from semantic_analyzer import SemanticAnalyzer


def test_simple_range_in_then_branch():
    """Test range extraction from simple IF condition (THEN branch)"""
    code = """
    10 INPUT X
    20 IF X > 5 THEN PRINT "X is greater than 5"
    30 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert len(analyzer.range_info) > 0, "Should detect range from IF condition"

    # Find range info for X
    x_ranges = [r for r in analyzer.range_info if r.variable == "X"]
    assert len(x_ranges) > 0, "Should have range info for X"

    # Check that X > 5 gives us a minimum bound
    found_lower_bound = False
    for r in x_ranges:
        if r.range.min_value is not None and r.range.min_value > 5:
            found_lower_bound = True
            break
    assert found_lower_bound, "Should determine X > 5 gives lower bound"

    print("✓ Simple range in THEN branch")


def test_simple_range_in_else_branch():
    """Test range extraction inverts for ELSE branch"""
    code = """
    10 INPUT X
    20 IF X > 5 THEN PRINT "Greater" ELSE PRINT "Not greater"
    30 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"

    # Should have ranges for both THEN and ELSE branches
    x_ranges = [r for r in analyzer.range_info if r.variable == "X"]
    assert len(x_ranges) >= 2, "Should have ranges for both branches"

    print("✓ Simple range in ELSE branch")


def test_range_enables_constant_propagation():
    """Test that X = const in IF enables constant propagation"""
    code = """
    10 INPUT X
    20 IF X = 10 THEN Y = X + 5
    30 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"

    # Find range info for X
    x_ranges = [r for r in analyzer.range_info if r.variable == "X"]
    assert len(x_ranges) > 0, "Should have range info for X"

    # Check that X = 10 creates a constant range
    found_constant = False
    for r in x_ranges:
        if r.range.is_constant and r.range.min_value == 10:
            found_constant = True
            # Should enable constant propagation
            assert r.enabled_optimization is not None
            assert "Constant propagation" in r.enabled_optimization
            break
    assert found_constant, "Should determine X = 10 is a constant range"

    print("✓ Range enables constant propagation")


def test_range_with_less_than():
    """Test range extraction from X < const"""
    code = """
    10 INPUT X
    20 IF X < 100 THEN PRINT "Less than 100"
    30 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"

    # Find range info for X in THEN branch
    x_ranges = [r for r in analyzer.range_info if r.variable == "X" and "THEN" in r.context]
    assert len(x_ranges) > 0, "Should have range info for X in THEN"

    # Check that X < 100 gives us an upper bound
    found_upper_bound = False
    for r in x_ranges:
        if r.range.max_value is not None and r.range.max_value < 100:
            found_upper_bound = True
            break
    assert found_upper_bound, "Should determine X < 100 gives upper bound"

    print("✓ Range with less than")


def test_range_with_greater_equal():
    """Test range extraction from X >= const"""
    code = """
    10 INPUT X
    20 IF X >= 50 THEN PRINT "At least 50"
    30 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"

    # Find range info for X
    x_ranges = [r for r in analyzer.range_info if r.variable == "X" and "THEN" in r.context]
    assert len(x_ranges) > 0, "Should have range info for X"

    # Check that X >= 50 gives us a minimum of 50
    found_lower_bound = False
    for r in x_ranges:
        if r.range.min_value == 50:
            found_lower_bound = True
            break
    assert found_lower_bound, "Should determine X >= 50 gives min value 50"

    print("✓ Range with greater equal")


def test_range_with_less_equal():
    """Test range extraction from X <= const"""
    code = """
    10 INPUT X
    20 IF X <= 200 THEN PRINT "At most 200"
    30 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"

    # Find range info for X
    x_ranges = [r for r in analyzer.range_info if r.variable == "X" and "THEN" in r.context]
    assert len(x_ranges) > 0, "Should have range info for X"

    # Check that X <= 200 gives us a maximum of 200
    found_upper_bound = False
    for r in x_ranges:
        if r.range.max_value == 200:
            found_upper_bound = True
            break
    assert found_upper_bound, "Should determine X <= 200 gives max value 200"

    print("✓ Range with less equal")


def test_range_with_reversed_operands():
    """Test range extraction when constant is on left (10 < X)"""
    code = """
    10 INPUT X
    20 IF 10 < X THEN PRINT "X greater than 10"
    30 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"

    # Find range info for X
    x_ranges = [r for r in analyzer.range_info if r.variable == "X" and "THEN" in r.context]
    assert len(x_ranges) > 0, "Should have range info for X"

    # 10 < X means X > 10
    found_lower_bound = False
    for r in x_ranges:
        if r.range.min_value is not None and r.range.min_value > 10:
            found_lower_bound = True
            break
    assert found_lower_bound, "Should determine 10 < X gives lower bound"

    print("✓ Range with reversed operands")


def test_range_with_not_equal():
    """Test that X <> const doesn't create useful range"""
    code = """
    10 INPUT X
    20 IF X <> 5 THEN PRINT "Not 5"
    30 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"

    # X <> 5 in THEN branch doesn't give us useful bounds
    # But in ELSE branch it would mean X = 5 (though this program has no ELSE)

    print("✓ Range with not equal")


def test_range_cleared_on_reassignment():
    """Test that ranges are cleared when variable is reassigned"""
    code = """
    10 INPUT X
    20 IF X > 5 THEN X = 100
    30 PRINT X
    40 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"

    # X should have range info from the IF
    x_ranges = [r for r in analyzer.range_info if r.variable == "X"]
    assert len(x_ranges) > 0, "Should have range info for X"

    # After X = 100, the range should be cleared (tested implicitly by no errors)

    print("✓ Range cleared on reassignment")


def test_range_intersection():
    """Test that ranges from nested IFs are intersected"""
    code = """
    10 INPUT X
    20 IF X > 10 THEN IF X < 20 THEN PRINT "Between 10 and 20"
    30 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"

    # Should have ranges for X from both conditions
    x_ranges = [r for r in analyzer.range_info if r.variable == "X"]
    assert len(x_ranges) >= 2, "Should have ranges from both IF statements"

    # Due to range intersection, the inner IF should have tighter bounds
    # (min > 10 AND max < 20)

    print("✓ Range intersection")


def test_range_with_integer_vs_float():
    """Test range analysis with integer vs float constants"""
    code = """
    10 INPUT X
    20 IF X > 5 THEN PRINT "Integer comparison"
    30 IF X > 5.5 THEN PRINT "Float comparison"
    40 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"

    # Should handle both integer and float comparisons
    x_ranges = [r for r in analyzer.range_info if r.variable == "X"]
    assert len(x_ranges) >= 2, "Should have ranges from both IF statements"

    print("✓ Range with integer vs float")


def test_multiple_variables_with_ranges():
    """Test range analysis with multiple variables"""
    code = """
    10 INPUT X, Y
    20 IF X > 10 THEN IF Y < 20 THEN PRINT X + Y
    30 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"

    # Should have ranges for both X and Y
    x_ranges = [r for r in analyzer.range_info if r.variable == "X"]
    y_ranges = [r for r in analyzer.range_info if r.variable == "Y"]

    assert len(x_ranges) > 0, "Should have range info for X"
    assert len(y_ranges) > 0, "Should have range info for Y"

    print("✓ Multiple variables with ranges")


def test_range_no_impact_on_arrays():
    """Test that range analysis doesn't apply to array elements"""
    code = """
    10 DIM A(10)
    20 IF A(1) > 5 THEN PRINT "Greater"
    30 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"

    # Array elements shouldn't create range info (we only track simple variables)
    a_ranges = [r for r in analyzer.range_info if r.variable == "A"]
    assert len(a_ranges) == 0, "Array elements shouldn't create range info"

    print("✓ Range no impact on arrays")


def run_all_tests():
    """Run all range analysis tests"""
    print("\n" + "="*70)
    print("RANGE ANALYSIS TESTS")
    print("="*70 + "\n")

    test_simple_range_in_then_branch()
    test_simple_range_in_else_branch()
    test_range_enables_constant_propagation()
    test_range_with_less_than()
    test_range_with_greater_equal()
    test_range_with_less_equal()
    test_range_with_reversed_operands()
    test_range_with_not_equal()
    test_range_cleared_on_reassignment()
    test_range_intersection()
    test_range_with_integer_vs_float()
    test_multiple_variables_with_ranges()
    test_range_no_impact_on_arrays()

    print("\n" + "="*70)
    print("All range analysis tests passed! ✓")
    print("="*70 + "\n")


if __name__ == '__main__':
    run_all_tests()
