#!/usr/bin/env python3
"""
Test Array Bounds Analysis

Tests the compiler's ability to detect array out-of-bounds accesses
with constant indices at compile time.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from lexer import tokenize
from parser import Parser
from semantic_analyzer import SemanticAnalyzer


def test_no_violations():
    """Test that valid array accesses produce no violations"""
    code = """
    10 DIM A(10)
    20 LET A(0) = 1
    30 LET A(5) = 2
    40 LET A(10) = 3
    50 X = A(0) + A(5) + A(10)
    60 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert len(analyzer.array_bounds_violations) == 0, "Valid accesses should not cause violations"

    print("✓ No violations")


def test_index_too_high():
    """Test detection of index exceeding upper bound"""
    code = """
    10 DIM A(10)
    20 LET A(11) = 100
    30 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert len(analyzer.array_bounds_violations) == 1, "Should detect 1 violation"

    violation = analyzer.array_bounds_violations[0]
    assert violation.array_name == "A"
    assert violation.subscript_value == 11
    assert violation.upper_bound == 10
    assert violation.access_type == "write"

    print("✓ Index too high")


def test_index_too_low_base0():
    """Test detection of negative index with OPTION BASE 0"""
    code = """
    10 OPTION BASE 0
    20 DIM A(10)
    30 X = A(-1)
    40 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert len(analyzer.array_bounds_violations) == 1, "Should detect 1 violation"

    violation = analyzer.array_bounds_violations[0]
    assert violation.array_name == "A"
    assert violation.subscript_value == -1
    assert violation.lower_bound == 0
    assert violation.access_type == "read"

    print("✓ Index too low (BASE 0)")


def test_index_too_low_base1():
    """Test detection of index below BASE 1"""
    code = """
    10 OPTION BASE 1
    20 DIM A(10)
    30 LET A(0) = 100
    40 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert len(analyzer.array_bounds_violations) == 1, "Should detect 1 violation"

    violation = analyzer.array_bounds_violations[0]
    assert violation.array_name == "A"
    assert violation.subscript_value == 0
    assert violation.lower_bound == 1
    assert violation.upper_bound == 10

    print("✓ Index too low (BASE 1)")


def test_multidimensional_array():
    """Test bounds checking for multi-dimensional arrays"""
    code = """
    10 DIM B(5, 10)
    20 LET B(6, 5) = 100
    30 LET B(3, 11) = 200
    40 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert len(analyzer.array_bounds_violations) == 2, "Should detect 2 violations"

    # First dimension violation
    v1 = [v for v in analyzer.array_bounds_violations if v.dimension_index == 0][0]
    assert v1.subscript_value == 6
    assert v1.upper_bound == 5

    # Second dimension violation
    v2 = [v for v in analyzer.array_bounds_violations if v.dimension_index == 1][0]
    assert v2.subscript_value == 11
    assert v2.upper_bound == 10

    print("✓ Multi-dimensional array")


def test_read_and_write_violations():
    """Test both read and write violations"""
    code = """
    10 DIM A(5)
    20 LET A(6) = 10
    30 X = A(7)
    40 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert len(analyzer.array_bounds_violations) == 2, "Should detect 2 violations"

    write_violations = [v for v in analyzer.array_bounds_violations if v.access_type == "write"]
    read_violations = [v for v in analyzer.array_bounds_violations if v.access_type == "read"]

    assert len(write_violations) == 1, "Should have 1 write violation"
    assert len(read_violations) == 1, "Should have 1 read violation"

    print("✓ Read and write violations")


def test_variable_index_no_violation():
    """Test that variable indices don't cause violations (can't be checked at compile time)"""
    code = """
    10 DIM A(10)
    20 INPUT I
    30 LET A(I) = 100
    40 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert len(analyzer.array_bounds_violations) == 0, "Variable indices (from INPUT) cannot be checked at compile time"

    print("✓ Variable index (no violation detected)")


def test_constant_expression_index():
    """Test bounds checking with constant expression indices"""
    code = """
    10 DIM A(10)
    20 LET A(5 + 6) = 100
    30 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert len(analyzer.array_bounds_violations) == 1, "Should detect violation from constant expression"

    violation = analyzer.array_bounds_violations[0]
    assert violation.subscript_value == 11  # 5 + 6 = 11

    print("✓ Constant expression index")


def test_multiple_violations_same_array():
    """Test multiple violations on the same array"""
    code = """
    10 DIM A(5)
    20 LET A(-1) = 1
    30 LET A(6) = 2
    40 LET A(7) = 3
    50 X = A(10)
    60 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert len(analyzer.array_bounds_violations) == 4, "Should detect 4 violations"

    print("✓ Multiple violations same array")


def test_input_statement():
    """Test bounds checking for INPUT into array"""
    code = """
    10 DIM A(5)
    20 INPUT A(10)
    30 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert len(analyzer.array_bounds_violations) == 1, "Should detect violation in INPUT"
    assert analyzer.array_bounds_violations[0].access_type == "write"

    print("✓ INPUT statement")


def test_read_statement():
    """Test bounds checking for READ into array"""
    code = """
    10 DIM A(5)
    20 DATA 1, 2, 3
    30 READ A(6)
    40 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert len(analyzer.array_bounds_violations) == 1, "Should detect violation in READ"
    assert analyzer.array_bounds_violations[0].access_type == "write"

    print("✓ READ statement")


def test_array_in_expression():
    """Test bounds checking for arrays used in expressions"""
    code = """
    10 DIM A(5), B(5)
    20 X = A(10) + B(3)
    30 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert len(analyzer.array_bounds_violations) == 1, "Should detect 1 violation (A(10))"

    violation = analyzer.array_bounds_violations[0]
    assert violation.array_name == "A"
    assert violation.subscript_value == 10

    print("✓ Array in expression")


def test_array_in_if_condition():
    """Test bounds checking in IF conditions"""
    code = """
    10 DIM A(5)
    20 IF A(10) > 0 THEN PRINT "YES"
    30 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert len(analyzer.array_bounds_violations) == 1, "Should detect violation in IF"

    print("✓ Array in IF condition")


def test_nested_array_subscripts():
    """Test bounds checking with array as subscript"""
    code = """
    10 DIM A(5), B(5)
    20 I = 2
    30 X = A(B(10))
    40 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    # Should detect violation in B(10), but not A(B(10)) since B(10) is not a constant
    assert len(analyzer.array_bounds_violations) >= 1, "Should detect violation in B(10)"

    b_violations = [v for v in analyzer.array_bounds_violations if v.array_name == "B"]
    assert len(b_violations) == 1

    print("✓ Nested array subscripts")


def run_all_tests():
    """Run all array bounds tests"""
    print("\n" + "="*70)
    print("ARRAY BOUNDS ANALYSIS TESTS")
    print("="*70 + "\n")

    test_no_violations()
    test_index_too_high()
    test_index_too_low_base0()
    test_index_too_low_base1()
    test_multidimensional_array()
    test_read_and_write_violations()
    test_variable_index_no_violation()
    test_constant_expression_index()
    test_multiple_violations_same_array()
    test_input_statement()
    test_read_statement()
    test_array_in_expression()
    test_array_in_if_condition()
    test_nested_array_subscripts()

    print("\n" + "="*70)
    print("All array bounds tests passed! ✓")
    print("="*70 + "\n")


if __name__ == '__main__':
    run_all_tests()
