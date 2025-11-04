#!/usr/bin/env python3
"""
Test String Constant Pooling Optimization

Tests the compiler's ability to detect duplicate string constants and
suggest pooling them to save memory.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from lexer import tokenize
from parser import Parser
from semantic_analyzer import SemanticAnalyzer


def test_no_duplicate_strings():
    """Test that unique strings are not pooled"""
    code = """
    10 PRINT "Hello"
    20 PRINT "World"
    30 PRINT "BASIC"
    40 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert len(analyzer.string_pool) == 0, "Unique strings should not be pooled"

    print("✓ No duplicate strings")


def test_simple_duplicate_string():
    """Test detection of a simple duplicate string"""
    code = """
    10 PRINT "Hello"
    20 PRINT "World"
    30 PRINT "Hello"
    40 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert len(analyzer.string_pool) == 1, f"Should detect 1 duplicate string, found {len(analyzer.string_pool)}"
    assert "Hello" in analyzer.string_pool
    assert len(analyzer.string_pool["Hello"].occurrences) == 2
    assert 10 in analyzer.string_pool["Hello"].occurrences
    assert 30 in analyzer.string_pool["Hello"].occurrences

    print("✓ Simple duplicate string")


def test_multiple_duplicate_strings():
    """Test detection of multiple different duplicate strings"""
    code = """
    10 PRINT "Error"
    20 PRINT "Success"
    30 PRINT "Error"
    40 PRINT "Warning"
    50 PRINT "Success"
    60 PRINT "Error"
    70 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert len(analyzer.string_pool) == 2, f"Should detect 2 duplicate strings, found {len(analyzer.string_pool)}"

    assert "Error" in analyzer.string_pool
    assert len(analyzer.string_pool["Error"].occurrences) == 3

    assert "Success" in analyzer.string_pool
    assert len(analyzer.string_pool["Success"].occurrences) == 2

    print("✓ Multiple duplicate strings")


def test_string_in_expression():
    """Test that strings in expressions are detected"""
    code = """
    10 MSG$ = "Hello"
    20 PRINT "Hello"
    30 IF X$ = "Hello" THEN PRINT "Match"
    40 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert len(analyzer.string_pool) == 1, "Should detect duplicate string in expressions"
    assert "Hello" in analyzer.string_pool
    assert len(analyzer.string_pool["Hello"].occurrences) == 3

    print("✓ String in expression")


def test_string_concatenation():
    """Test strings in concatenation operations"""
    code = """
    10 A$ = "Hello" + " " + "World"
    20 B$ = "Hello" + " there"
    30 PRINT "World"
    40 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    # "Hello" appears twice, "World" appears twice
    assert len(analyzer.string_pool) == 2
    assert "Hello" in analyzer.string_pool
    assert "World" in analyzer.string_pool

    print("✓ String concatenation")


def test_string_in_data_statement():
    """Test strings in DATA statements"""
    code = """
    10 DATA "Apple", "Banana", "Apple"
    20 READ A$, B$, C$
    30 PRINT "Apple"
    40 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert "Apple" in analyzer.string_pool
    assert len(analyzer.string_pool["Apple"].occurrences) == 3  # 2 in DATA, 1 in PRINT

    print("✓ String in DATA statement")


def test_pool_id_generation():
    """Test that pool IDs are generated correctly"""
    code = """
    10 PRINT "First"
    20 PRINT "Second"
    30 PRINT "First"
    40 PRINT "Second"
    50 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert len(analyzer.string_pool) == 2

    # Check that pool IDs are unique
    pool_ids = {entry.pool_id for entry in analyzer.string_pool.values()}
    assert len(pool_ids) == 2, "Pool IDs should be unique"

    # Check format
    for pool_id in pool_ids:
        assert pool_id.startswith("STR"), "Pool ID should start with STR"
        assert pool_id.endswith("$"), "Pool ID should end with $"

    print("✓ Pool ID generation")


def test_string_size_calculation():
    """Test that string sizes are calculated correctly"""
    code = """
    10 PRINT "Short"
    20 PRINT "A longer string message"
    30 PRINT "Short"
    40 PRINT "A longer string message"
    50 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"

    assert "Short" in analyzer.string_pool
    assert analyzer.string_pool["Short"].size == 5

    assert "A longer string message" in analyzer.string_pool
    assert analyzer.string_pool["A longer string message"].size == 23

    print("✓ String size calculation")


def test_empty_string():
    """Test handling of empty strings"""
    code = """
    10 A$ = ""
    20 B$ = ""
    30 PRINT ""
    40 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert "" in analyzer.string_pool
    assert len(analyzer.string_pool[""]. occurrences) == 3
    assert analyzer.string_pool[""].size == 0

    print("✓ Empty string")


def test_string_in_for_loop():
    """Test strings used in FOR loop expressions"""
    code = """
    10 FOR I = 1 TO 10
    20   PRINT "Iteration"
    30 NEXT I
    40 PRINT "Iteration"
    50 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert "Iteration" in analyzer.string_pool
    # Appears in loop (line 20) and after (line 40)
    assert len(analyzer.string_pool["Iteration"].occurrences) == 2

    print("✓ String in FOR loop")


def test_string_in_if_statement():
    """Test strings in IF THEN ELSE statements"""
    code = """
    10 IF X > 0 THEN PRINT "Positive" ELSE PRINT "Negative"
    20 PRINT "Positive"
    30 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert "Positive" in analyzer.string_pool
    assert len(analyzer.string_pool["Positive"].occurrences) == 2

    print("✓ String in IF statement")


def test_many_duplicates():
    """Test a string that appears many times"""
    code = """
    10 PRINT "LOG"
    20 PRINT "Processing"
    30 PRINT "LOG"
    40 PRINT "LOG"
    50 PRINT "LOG"
    60 PRINT "LOG"
    70 PRINT "Done"
    80 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert "LOG" in analyzer.string_pool
    assert len(analyzer.string_pool["LOG"].occurrences) == 5

    # Calculate expected savings
    # "LOG" is 3 bytes, appears 5 times, saves 3 * (5-1) = 12 bytes
    expected_savings = 3 * 4  # size * (occurrences - 1)

    # This would be checked in the report output

    print("✓ Many duplicates")


def test_case_sensitive_strings():
    """Test that string pooling is case-sensitive"""
    code = """
    10 PRINT "hello"
    20 PRINT "Hello"
    30 PRINT "HELLO"
    40 PRINT "hello"
    50 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    # Only "hello" (lowercase) appears twice
    assert len(analyzer.string_pool) == 1
    assert "hello" in analyzer.string_pool
    assert len(analyzer.string_pool["hello"].occurrences) == 2

    print("✓ Case-sensitive strings")


def run_all_tests():
    """Run all string pooling tests"""
    print("\n" + "="*70)
    print("STRING CONSTANT POOLING TESTS")
    print("="*70 + "\n")

    test_no_duplicate_strings()
    test_simple_duplicate_string()
    test_multiple_duplicate_strings()
    test_string_in_expression()
    test_string_concatenation()
    test_string_in_data_statement()
    test_pool_id_generation()
    test_string_size_calculation()
    test_empty_string()
    test_string_in_for_loop()
    test_string_in_if_statement()
    test_many_duplicates()
    test_case_sensitive_strings()

    print("\n" + "="*70)
    print("All string pooling tests passed! ✓")
    print("="*70 + "\n")


if __name__ == '__main__':
    run_all_tests()
