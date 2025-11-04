#!/usr/bin/env python3
"""
Test String Concatenation in Loops

Tests the compiler's ability to detect inefficient string concatenation
patterns inside loops.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from lexer import tokenize
from parser import Parser
from semantic_analyzer import SemanticAnalyzer


def test_simple_concat_in_for_loop():
    """Test simple string concatenation in FOR loop"""
    code = """
    10 S$ = ""
    20 FOR I = 1 TO 10
    30   LET S$ = S$ + "X"
    40 NEXT I
    50 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert len(analyzer.string_concat_in_loops) > 0, "Should detect string concatenation in loop"

    concat = analyzer.string_concat_in_loops[0]
    assert concat.string_var == "S$", "Should track S$"
    assert concat.loop_type == "FOR", "Should be FOR loop"
    assert 30 in concat.concat_lines, "Should find concatenation at line 30"
    assert concat.iteration_count == 10, "Should know iteration count"
    assert concat.estimated_allocations == 10, "Should estimate 10 allocations"

    print("✓ Simple concat in FOR loop")


def test_multiple_concats_in_loop():
    """Test multiple concatenations in same loop"""
    code = """
    10 S$ = ""
    20 FOR I = 1 TO 5
    30   LET S$ = S$ + "A"
    40   LET S$ = S$ + "B"
    50 NEXT I
    60 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert len(analyzer.string_concat_in_loops) > 0, "Should detect string concatenation"

    concat = analyzer.string_concat_in_loops[0]
    assert len(concat.concat_lines) == 2, "Should find 2 concatenation points"
    assert 30 in concat.concat_lines and 40 in concat.concat_lines
    assert concat.estimated_allocations == 10, "Should estimate 2 * 5 = 10 allocations"

    print("✓ Multiple concats in loop")


def test_no_concat_outside_loop():
    """Test that concatenation outside loops is not flagged"""
    code = """
    10 S$ = ""
    20 LET S$ = S$ + "X"
    30 LET S$ = S$ + "Y"
    40 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert len(analyzer.string_concat_in_loops) == 0, "Should NOT detect (not in loop)"

    print("✓ No concat outside loop")


def test_concat_in_while_loop():
    """Test string concatenation in WHILE loop"""
    code = """
    10 S$ = ""
    20 I = 1
    30 WHILE I <= 10
    40   LET S$ = S$ + STR$(I)
    50   I = I + 1
    60 WEND
    70 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert len(analyzer.string_concat_in_loops) > 0, "Should detect string concatenation in WHILE"

    concat = analyzer.string_concat_in_loops[0]
    assert concat.string_var == "S$"
    assert concat.loop_type == "WHILE"
    assert 40 in concat.concat_lines

    print("✓ Concat in WHILE loop")


def test_large_iteration_count():
    """Test high impact warning for large loops"""
    code = """
    10 S$ = ""
    20 FOR I = 1 TO 1000
    30   LET S$ = S$ + "*"
    40 NEXT I
    50 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert len(analyzer.string_concat_in_loops) > 0

    concat = analyzer.string_concat_in_loops[0]
    assert concat.iteration_count == 1000
    assert "HIGH IMPACT" in concat.impact, "Should warn about high impact"

    print("✓ Large iteration count")


def test_medium_iteration_count():
    """Test medium impact for moderate loops"""
    code = """
    10 S$ = ""
    20 FOR I = 1 TO 50
    30   LET S$ = S$ + "."
    40 NEXT I
    50 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    concat = analyzer.string_concat_in_loops[0]
    assert "Medium impact" in concat.impact or "medium impact" in concat.impact.lower()

    print("✓ Medium iteration count")


def test_small_iteration_count():
    """Test low impact for small loops"""
    code = """
    10 S$ = ""
    20 FOR I = 1 TO 5
    30   LET S$ = S$ + CHR$(65 + I)
    40 NEXT I
    50 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    concat = analyzer.string_concat_in_loops[0]
    assert "Low impact" in concat.impact or "low impact" in concat.impact.lower()

    print("✓ Small iteration count")


def test_multiple_string_vars():
    """Test multiple different string variables in loop"""
    code = """
    10 A$ = ""
    20 B$ = ""
    30 FOR I = 1 TO 10
    40   LET A$ = A$ + "X"
    50   LET B$ = B$ + "Y"
    60 NEXT I
    70 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert len(analyzer.string_concat_in_loops) == 2, "Should detect both A$ and B$"

    vars_found = {c.string_var for c in analyzer.string_concat_in_loops}
    assert "A$" in vars_found and "B$" in vars_found

    print("✓ Multiple string vars")


def test_nested_loops():
    """Test string concatenation in nested loops"""
    code = """
    10 S$ = ""
    20 FOR I = 1 TO 10
    30   FOR J = 1 TO 5
    40     LET S$ = S$ + "*"
    50   NEXT J
    60 NEXT I
    70 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    # Should detect in at least one loop (inner or outer)
    assert len(analyzer.string_concat_in_loops) > 0

    print("✓ Nested loops")


def test_concat_right_side():
    """Test concatenation with variable on right side"""
    code = """
    10 S$ = ""
    20 FOR I = 1 TO 10
    30   LET S$ = "Prefix: " + S$
    40 NEXT I
    50 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert len(analyzer.string_concat_in_loops) > 0, "Should detect S$ on right side"

    print("✓ Concat right side")


def test_non_string_variable():
    """Test that non-string variables are not flagged"""
    code = """
    10 X = 0
    20 FOR I = 1 TO 10
    30   LET X = X + 1
    40 NEXT I
    50 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert len(analyzer.string_concat_in_loops) == 0, "Should NOT flag numeric variable"

    print("✓ Non-string variable")


def test_string_assignment_no_concat():
    """Test string assignment without concatenation"""
    code = """
    10 S$ = ""
    20 FOR I = 1 TO 10
    30   LET S$ = "FIXED"
    40 NEXT I
    50 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert len(analyzer.string_concat_in_loops) == 0, "Should NOT flag (no self-concatenation)"

    print("✓ String assignment no concat")


def test_concat_with_function():
    """Test concatenation using string functions"""
    code = """
    10 S$ = ""
    20 FOR I = 1 TO 10
    30   LET S$ = S$ + LEFT$("ABC", 2)
    40 NEXT I
    50 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert len(analyzer.string_concat_in_loops) > 0, "Should detect concatenation with function"

    print("✓ Concat with function")


def run_all_tests():
    """Run all string concatenation in loops tests"""
    print("\n" + "="*70)
    print("STRING CONCATENATION IN LOOPS TESTS")
    print("="*70 + "\n")

    test_simple_concat_in_for_loop()
    test_multiple_concats_in_loop()
    test_no_concat_outside_loop()
    test_concat_in_while_loop()
    test_large_iteration_count()
    test_medium_iteration_count()
    test_small_iteration_count()
    test_multiple_string_vars()
    test_nested_loops()
    test_concat_right_side()
    test_non_string_variable()
    test_string_assignment_no_concat()
    test_concat_with_function()

    print("\n" + "="*70)
    print("All string concatenation in loops tests passed! ✓")
    print("="*70 + "\n")


if __name__ == '__main__':
    run_all_tests()
