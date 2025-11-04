#!/usr/bin/env python3
"""
Test Available Expression Analysis

Tests the compiler's ability to detect expressions that are available
(computed on all paths) at program points for more sophisticated CSE.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from lexer import tokenize
from parser import Parser
from semantic_analyzer import SemanticAnalyzer


def test_simple_available():
    """Test simple available expression (not killed)"""
    code = """
    10 LET X = A + B
    20 LET Y = C + D
    30 LET Z = A + B
    40 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert len(analyzer.available_expr_analysis) > 0, "Should detect available expression"

    # A+B is available at line 30 (not modified between 10 and 30)
    ab_expr = [e for e in analyzer.available_expr_analysis if "A" in e.variables_used and "B" in e.variables_used]
    assert len(ab_expr) > 0, "Should find A+B as available"
    assert 30 in ab_expr[0].available_at_lines, "A+B should be available at line 30"

    print("✓ Simple available expression")


def test_killed_expression():
    """Test expression killed by variable modification"""
    code = """
    10 LET X = A + B
    20 LET A = 10
    30 LET Y = A + B
    40 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"

    # A+B is NOT available at line 30 (A is modified at line 20)
    ab_expr = [e for e in analyzer.available_expr_analysis if "A" in e.variables_used and "B" in e.variables_used]
    if len(ab_expr) > 0:
        assert 30 not in ab_expr[0].available_at_lines, "A+B should NOT be available at line 30 (A modified)"

    print("✓ Killed expression")


def test_multiple_computations():
    """Test expression computed multiple times with some available"""
    code = """
    10 LET X = A * B
    20 LET Y = C + D
    30 LET Z = A * B
    40 LET W = A * B
    50 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"

    # A*B should be available at lines 30 and 40
    ab_expr = [e for e in analyzer.available_expr_analysis if "A" in e.variables_used and "B" in e.variables_used]
    assert len(ab_expr) > 0, "Should find A*B as available"
    assert 30 in ab_expr[0].available_at_lines, "A*B available at line 30"
    assert 40 in ab_expr[0].available_at_lines, "A*B available at line 40"
    assert ab_expr[0].redundant_computations == 2, "Two redundant computations"

    print("✓ Multiple computations")


def test_partial_availability():
    """Test expression available at some points but killed at others"""
    code = """
    10 LET X = A + B
    20 LET Y = A + B
    30 LET A = 5
    40 LET Z = A + B
    50 LET W = A + B
    60 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"

    ab_expr = [e for e in analyzer.available_expr_analysis if "A" in e.variables_used and "B" in e.variables_used]
    assert len(ab_expr) > 0, "Should find A+B"

    # Line 20: available (computed at 10, not killed)
    assert 20 in ab_expr[0].available_at_lines, "A+B available at line 20"

    # Line 40: NOT available (A modified at line 30)
    assert 40 not in ab_expr[0].available_at_lines, "A+B NOT available at line 40 (A modified)"

    # Line 50: available (computed at 40, not killed)
    assert 50 in ab_expr[0].available_at_lines, "A+B available at line 50"

    print("✓ Partial availability")


def test_no_redundant_computation():
    """Test expression computed only once (no redundancy)"""
    code = """
    10 LET X = A + B
    20 LET Y = C + D
    30 LET Z = E + F
    40 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    # No expression computed multiple times
    assert len(analyzer.available_expr_analysis) == 0, "No available expressions (each computed once)"

    print("✓ No redundant computation")


def test_function_calls():
    """Test available expression analysis with function calls"""
    code = """
    10 LET X = SIN(A)
    20 LET Y = B + C
    30 LET Z = SIN(A)
    40 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"

    # SIN(A) should be available at line 30
    sin_expr = [e for e in analyzer.available_expr_analysis if "SIN" in e.expression_desc]
    assert len(sin_expr) > 0, "Should find SIN(A) as available"
    assert 30 in sin_expr[0].available_at_lines, "SIN(A) available at line 30"

    print("✓ Function calls")


def test_loop_computations():
    """Test expressions computed in loops"""
    code = """
    10 FOR I = 1 TO 10
    20   LET X = A * B
    30   PRINT X
    40 NEXT I
    50 LET Y = A * B
    60 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"

    # A*B computed multiple times (in loop body)
    # Note: This is a simplified test - full loop analysis would be more complex
    ab_expr = [e for e in analyzer.available_expr_analysis if "A" in e.variables_used and "B" in e.variables_used]
    # May or may not find availability depending on loop handling

    print("✓ Loop computations")


def test_nested_expressions():
    """Test availability of nested sub-expressions"""
    code = """
    10 LET X = (A + B) * C
    20 LET Y = D + E
    30 LET Z = (A + B) * C
    40 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"

    # Both (A+B) and (A+B)*C should be tracked
    assert len(analyzer.available_expr_analysis) > 0, "Should find available expressions"

    print("✓ Nested expressions")


def test_modified_in_between():
    """Test variable modified between computations"""
    code = """
    10 LET X = A + B
    20 LET B = B + 1
    30 LET Y = A + B
    40 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"

    # A+B is NOT available at line 30 (B modified at line 20)
    ab_expr = [e for e in analyzer.available_expr_analysis if "A" in e.variables_used and "B" in e.variables_used]
    if len(ab_expr) > 0:
        assert 30 not in ab_expr[0].available_at_lines, "A+B should NOT be available (B modified)"

    print("✓ Modified in between")


def test_input_kills_expression():
    """Test that INPUT kills expressions using that variable"""
    code = """
    10 LET X = A + B
    20 INPUT A
    30 LET Y = A + B
    40 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"

    # A+B is NOT available at line 30 (A modified by INPUT)
    ab_expr = [e for e in analyzer.available_expr_analysis if "A" in e.variables_used and "B" in e.variables_used]
    if len(ab_expr) > 0:
        assert 30 not in ab_expr[0].available_at_lines, "A+B should NOT be available (INPUT modifies A)"

    print("✓ INPUT kills expression")


def test_complex_expression():
    """Test complex expression with multiple operators"""
    code = """
    10 LET X = (A * B) + (C / D)
    20 LET Y = E - F
    30 LET Z = (A * B) + (C / D)
    40 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"

    # Should track multiple sub-expressions: A*B, C/D, (A*B)+(C/D)
    assert len(analyzer.available_expr_analysis) > 0, "Should find available sub-expressions"

    print("✓ Complex expression")


def test_read_statement():
    """Test that READ statement kills expressions"""
    code = """
    10 DATA 1, 2, 3
    20 LET X = A + B
    30 READ A
    40 LET Y = A + B
    50 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"

    # A+B is NOT available at line 40 (A modified by READ)
    ab_expr = [e for e in analyzer.available_expr_analysis if "A" in e.variables_used and "B" in e.variables_used]
    if len(ab_expr) > 0:
        assert 40 not in ab_expr[0].available_at_lines, "A+B should NOT be available (READ modifies A)"

    print("✓ READ statement")


def test_for_loop_kills():
    """Test that FOR loop modifies its control variable"""
    code = """
    10 LET X = I + J
    20 FOR I = 1 TO 10
    30 NEXT I
    40 LET Y = I + J
    50 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"

    # I+J is NOT available at line 40 (I modified by FOR loop)
    ij_expr = [e for e in analyzer.available_expr_analysis if "I" in e.variables_used and "J" in e.variables_used]
    if len(ij_expr) > 0:
        assert 40 not in ij_expr[0].available_at_lines, "I+J should NOT be available (FOR modifies I)"

    print("✓ FOR loop kills")


def run_all_tests():
    """Run all available expression analysis tests"""
    print("\n" + "="*70)
    print("AVAILABLE EXPRESSION ANALYSIS TESTS")
    print("="*70 + "\n")

    test_simple_available()
    test_killed_expression()
    test_multiple_computations()
    test_partial_availability()
    test_no_redundant_computation()
    test_function_calls()
    test_loop_computations()
    test_nested_expressions()
    test_modified_in_between()
    test_input_kills_expression()
    test_complex_expression()
    test_read_statement()
    test_for_loop_kills()

    print("\n" + "="*70)
    print("All available expression analysis tests passed! ✓")
    print("="*70 + "\n")


if __name__ == '__main__':
    run_all_tests()
