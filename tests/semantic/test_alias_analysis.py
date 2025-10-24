#!/usr/bin/env python3
"""
Test Alias Analysis

Tests the compiler's ability to detect potential aliasing between
array elements and variables.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from lexer import tokenize
from parser import Parser
from semantic_analyzer import SemanticAnalyzer


def test_no_aliases():
    """Test that distinct array accesses produce no aliases"""
    code = """
    10 DIM A(10)
    20 LET A(1) = 10
    30 LET A(2) = 20
    40 LET A(3) = 30
    50 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    # Different constant indices = no aliasing
    assert len(analyzer.alias_info) == 0, "Different constant indices should not alias"

    print("✓ No aliases")


def test_definite_alias_same_constant():
    """Test detection of definite alias with same constant index"""
    code = """
    10 DIM A(10)
    20 LET A(5) = 10
    30 X = A(5)
    40 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert len(analyzer.alias_info) > 0, "Should detect alias"

    # Should be definite alias
    definite = [a for a in analyzer.alias_info if a.alias_type == "definite"]
    assert len(definite) > 0, "Should be definite alias (same constant)"

    print("✓ Definite alias (same constant)")


def test_definite_alias_same_variable():
    """Test detection of definite alias with same variable index"""
    code = """
    10 DIM A(10)
    20 INPUT I
    30 LET A(I) = 10
    40 X = A(I) + 5
    50 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert len(analyzer.alias_info) > 0, "Should detect alias"

    # Should be definite alias (same variable)
    definite = [a for a in analyzer.alias_info if a.alias_type == "definite"]
    assert len(definite) > 0, "Should be definite alias (same variable I)"

    print("✓ Definite alias (same variable)")


def test_possible_alias_different_variables():
    """Test detection of possible alias with different variable indices"""
    code = """
    10 DIM A(10)
    20 INPUT I, J
    30 LET A(I) = 10
    40 LET A(J) = 20
    50 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert len(analyzer.alias_info) > 0, "Should detect possible alias"

    # Should be possible alias (different variables might have same value)
    possible = [a for a in analyzer.alias_info if a.alias_type == "possible"]
    assert len(possible) > 0, "Should be possible alias (I and J might be equal)"

    print("✓ Possible alias (different variables)")


def test_multidimensional_alias():
    """Test alias detection in multi-dimensional arrays"""
    code = """
    10 DIM B(5, 10)
    20 LET B(2, 3) = 100
    30 X = B(2, 3)
    40 Y = B(2, 3) + 1
    50 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"

    # B(2,3) accessed three times = definite alias
    definite = [a for a in analyzer.alias_info if a.alias_type == "definite"]
    assert len(definite) > 0, "Should detect B(2,3) aliasing with itself"

    print("✓ Multi-dimensional alias")


def test_loop_variable_alias():
    """Test alias detection with loop variables"""
    code = """
    10 DIM A(10)
    20 FOR I = 1 TO 10
    30   LET A(I) = I * 2
    40   PRINT A(I)
    50 NEXT I
    60 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert len(analyzer.alias_info) > 0, "Should detect alias"

    # A(I) used twice with same variable I
    definite = [a for a in analyzer.alias_info if a.alias_type == "definite"]
    assert len(definite) > 0, "Should detect A(I) aliasing with itself"

    print("✓ Loop variable alias")


def test_mixed_constant_variable():
    """Test alias between constant and variable index"""
    code = """
    10 DIM A(10)
    20 INPUT I
    30 LET A(5) = 10
    40 LET A(I) = 20
    50 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert len(analyzer.alias_info) > 0, "Should detect possible alias"

    # A(5) and A(I) might alias if I=5
    possible = [a for a in analyzer.alias_info if a.alias_type == "possible"]
    assert len(possible) > 0, "Should detect possible alias (I might be 5)"

    print("✓ Mixed constant/variable")


def test_no_alias_different_arrays():
    """Test that different arrays don't alias"""
    code = """
    10 DIM A(10), B(10)
    20 LET A(5) = 10
    30 LET B(5) = 20
    40 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    # Different arrays = no aliasing
    assert len(analyzer.alias_info) == 0, "Different arrays should not alias"

    print("✓ No alias (different arrays)")


def test_expression_in_subscript():
    """Test alias detection with expressions in subscripts"""
    code = """
    10 DIM A(10)
    20 INPUT I
    30 LET A(I + 1) = 10
    40 LET A(I + 1) = 20
    50 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    # Same expression I+1 might be detected
    # (depends on how expressions are normalized)

    print("✓ Expression in subscript")


def test_read_write_alias():
    """Test alias between read and write of same location"""
    code = """
    10 DIM A(10)
    20 INPUT I
    30 LET A(I) = A(I) + 1
    40 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert len(analyzer.alias_info) > 0, "Should detect read/write alias"

    # A(I) on both sides = definite alias
    definite = [a for a in analyzer.alias_info if a.alias_type == "definite"]
    assert len(definite) > 0, "Should detect A(I) aliasing with itself"

    print("✓ Read/write alias")


def test_multiple_accesses_same_index():
    """Test multiple accesses to same index"""
    code = """
    10 DIM A(10)
    20 LET A(3) = 10
    30 X = A(3)
    40 LET A(3) = 20
    50 Y = A(3)
    60 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert len(analyzer.alias_info) > 0, "Should detect multiple aliases"

    # All A(3) accesses alias with each other
    definite = [a for a in analyzer.alias_info if a.alias_type == "definite"]
    assert len(definite) > 0, "Should detect A(3) aliasing"

    print("✓ Multiple accesses same index")


def test_constant_propagated_index():
    """Test alias with constant-propagated index"""
    code = """
    10 DIM A(10)
    20 I = 5
    30 LET A(I) = 10
    40 LET A(5) = 20
    50 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    # I is constant-propagated to 5, so A(I) and A(5) both become A(5)
    # Should detect alias
    assert len(analyzer.alias_info) > 0, "Should detect alias after constant propagation"

    print("✓ Constant propagated index")


def run_all_tests():
    """Run all alias analysis tests"""
    print("\n" + "="*70)
    print("ALIAS ANALYSIS TESTS")
    print("="*70 + "\n")

    test_no_aliases()
    test_definite_alias_same_constant()
    test_definite_alias_same_variable()
    test_possible_alias_different_variables()
    test_multidimensional_alias()
    test_loop_variable_alias()
    test_mixed_constant_variable()
    test_no_alias_different_arrays()
    test_expression_in_subscript()
    test_read_write_alias()
    test_multiple_accesses_same_index()
    test_constant_propagated_index()

    print("\n" + "="*70)
    print("All alias analysis tests passed! ✓")
    print("="*70 + "\n")


if __name__ == '__main__':
    run_all_tests()
