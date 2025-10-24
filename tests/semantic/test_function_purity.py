#!/usr/bin/env python3
"""
Test Built-in Function Purity Analysis

Tests the compiler's ability to classify built-in functions as pure or impure
and provide optimization guidance based on purity.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from lexer import tokenize
from parser import Parser
from semantic_analyzer import SemanticAnalyzer


def test_pure_math_functions():
    """Test that math functions are classified as pure"""
    code = """
    10 X = SIN(1.0)
    20 Y = COS(2.0)
    30 Z = TAN(3.0)
    40 A = ABS(-5.0)
    50 B = SQR(16.0)
    60 C = INT(3.7)
    70 D = SGN(-10.0)
    80 E = ATN(1.0)
    90 F = EXP(2.0)
    100 G = LOG(10.0)
    110 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert len(analyzer.builtin_function_calls) == 10, "Should detect 10 function calls"
    assert len(analyzer.impure_function_calls) == 0, "Math functions should be pure"

    # Verify all are pure
    for func_name in analyzer.builtin_function_calls.keys():
        is_pure, reason = analyzer._is_pure_builtin_function(func_name)
        assert is_pure, f"{func_name} should be pure"

    print("✓ Pure math functions")


def test_pure_string_functions():
    """Test that string functions are classified as pure"""
    code = """
    10 A$ = "HELLO"
    20 B = LEN(A$)
    30 C = ASC(A$)
    40 K = INSTR(A$, "L")
    50 X = VAL("123")
    60 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert len(analyzer.impure_function_calls) == 0, f"String functions should be pure, but found: {analyzer.impure_function_calls}"

    # Verify specific functions
    assert "LEN" in analyzer.builtin_function_calls
    assert "ASC" in analyzer.builtin_function_calls
    assert "INSTR" in analyzer.builtin_function_calls
    assert "VAL" in analyzer.builtin_function_calls

    print("✓ Pure string functions")


def test_impure_rnd():
    """Test that RND is classified as impure"""
    code = """
    10 X = RND
    20 Y = RND(1)
    30 Z = RND * 100
    40 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert "RND" in analyzer.builtin_function_calls
    assert len(analyzer.impure_function_calls) == 3, "RND should be detected 3 times as impure"

    # Check all impure calls are RND
    for line, func, reason in analyzer.impure_function_calls:
        assert func == "RND"
        assert "non-deterministic" in reason.lower() or "state" in reason.lower()

    print("✓ Impure RND")


def test_impure_io_functions():
    """Test that I/O functions are classified as impure"""
    code = """
    10 OPEN "FILE.DAT" FOR INPUT AS #1
    20 X = EOF(1)
    30 Y = LOC(1)
    40 Z = LOF(1)
    50 A$ = INKEY$
    60 CLOSE #1
    70 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"

    # Should detect impure calls
    impure_funcs = {func for _, func, _ in analyzer.impure_function_calls}
    assert "EOF" in impure_funcs, "EOF should be impure"
    assert "LOC" in impure_funcs, "LOC should be impure"
    assert "LOF" in impure_funcs, "LOF should be impure"
    assert "INKEY" in impure_funcs, "INKEY should be impure"

    print("✓ Impure I/O functions")


def test_mixed_pure_impure():
    """Test program with both pure and impure functions"""
    code = """
    10 X = SIN(1.0)
    20 Y = RND
    30 Z = COS(X)
    40 A = RND * 100
    50 B = ABS(Y)
    60 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"

    total_calls = sum(len(calls) for calls in analyzer.builtin_function_calls.values())
    assert total_calls == 5, "Should detect 5 function calls"

    # RND appears twice, should be impure
    assert len(analyzer.impure_function_calls) == 2

    # SIN, COS, ABS should be pure
    for func in ["SIN", "COS", "ABS"]:
        is_pure, _ = analyzer._is_pure_builtin_function(func)
        assert is_pure

    print("✓ Mixed pure and impure")


def test_pure_type_conversion():
    """Test that type conversion functions are pure"""
    code = """
    10 A = CINT(3.7)
    20 B = CSNG(5)
    30 C = CDBL(10)
    40 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert len(analyzer.impure_function_calls) == 0, "Type conversion should be pure"

    print("✓ Pure type conversion")


def test_pure_binary_conversion():
    """Test that binary conversion functions are pure"""
    code = """
    10 A$ = "XX"
    20 B = CVI(A$)
    30 C = CVS(A$)
    40 D = CVD(A$)
    50 E$ = MKI$(100)
    60 F$ = MKS$(3.14)
    70 G$ = MKD$(2.718)
    80 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert len(analyzer.impure_function_calls) == 0, "Binary conversion should be pure"

    print("✓ Pure binary conversion")


def test_function_in_expression():
    """Test function calls within complex expressions"""
    code = """
    10 X = SIN(1.0) + COS(2.0)
    20 Y = RND * 10 + RND * 20
    30 Z = ABS(SIN(X))
    40 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"

    # Should detect nested and multiple calls
    assert "SIN" in analyzer.builtin_function_calls
    assert "COS" in analyzer.builtin_function_calls
    assert "ABS" in analyzer.builtin_function_calls
    assert "RND" in analyzer.builtin_function_calls

    # Only RND should be impure
    impure_funcs = {func for _, func, _ in analyzer.impure_function_calls}
    assert impure_funcs == {"RND"}

    print("✓ Function in expression")


def test_function_in_if():
    """Test function calls in IF conditions"""
    code = """
    10 IF RND > 0.5 THEN PRINT "High"
    20 IF ABS(X) < 10 THEN Y = SIN(X)
    30 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"

    assert "RND" in analyzer.builtin_function_calls
    assert "ABS" in analyzer.builtin_function_calls
    assert "SIN" in analyzer.builtin_function_calls

    # Only RND should be impure
    impure_funcs = {func for _, func, _ in analyzer.impure_function_calls}
    assert impure_funcs == {"RND"}

    print("✓ Function in IF")


def test_function_in_loop():
    """Test function calls in loop"""
    code = """
    10 FOR I = 1 TO 10
    20   X = SIN(I)
    30   Y = RND
    40 NEXT I
    50 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"

    assert "SIN" in analyzer.builtin_function_calls
    assert "RND" in analyzer.builtin_function_calls

    # Only RND should be impure
    impure_funcs = {func for _, func, _ in analyzer.impure_function_calls}
    assert impure_funcs == {"RND"}

    print("✓ Function in loop")


def test_val_function():
    """Test VAL string-to-number function"""
    code = """
    10 A$ = "123"
    20 B = VAL(A$)
    30 C = VAL("456")
    40 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert "VAL" in analyzer.builtin_function_calls
    assert len(analyzer.impure_function_calls) == 0, "VAL should be pure"

    print("✓ VAL function")


def test_pos_function():
    """Test POS cursor position function (impure)"""
    code = """
    10 X = POS(0)
    20 PRINT X
    30 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert "POS" in analyzer.builtin_function_calls

    # POS should be impure (stateful)
    impure_funcs = {func for _, func, _ in analyzer.impure_function_calls}
    assert "POS" in impure_funcs

    print("✓ POS function (impure)")


def test_multiple_same_function():
    """Test same function called multiple times"""
    code = """
    10 A = SIN(1)
    20 B = SIN(2)
    30 C = SIN(3)
    40 D = SIN(1)
    50 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert len(analyzer.builtin_function_calls["SIN"]) == 4, "Should detect 4 SIN calls"
    assert len(analyzer.impure_function_calls) == 0

    print("✓ Multiple same function")


def run_all_tests():
    """Run all function purity tests"""
    print("\n" + "="*70)
    print("BUILT-IN FUNCTION PURITY ANALYSIS TESTS")
    print("="*70 + "\n")

    test_pure_math_functions()
    test_pure_string_functions()
    test_impure_rnd()
    test_impure_io_functions()
    test_mixed_pure_impure()
    test_pure_type_conversion()
    test_pure_binary_conversion()
    test_function_in_expression()
    test_function_in_if()
    test_function_in_loop()
    test_val_function()
    test_pos_function()
    test_multiple_same_function()

    print("\n" + "="*70)
    print("All function purity tests passed! ✓")
    print("="*70 + "\n")


if __name__ == '__main__':
    run_all_tests()
