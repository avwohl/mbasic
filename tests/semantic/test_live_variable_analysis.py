#!/usr/bin/env python3
"""
Test Live Variable Analysis Optimization

Tests the compiler's ability to track which variables are live (will be used later)
and identify dead writes (variables written but never read).
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from lexer import tokenize
from parser import Parser
from semantic_analyzer import SemanticAnalyzer


def test_simple_dead_write():
    """Test detection of a simple dead write"""
    code = """
    10 X = 10
    20 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert len(analyzer.dead_writes) == 1, f"Should detect 1 dead write, found {len(analyzer.dead_writes)}"
    assert analyzer.dead_writes[0].variable == "X"
    assert analyzer.dead_writes[0].line == 10

    print("✓ Simple dead write")


def test_variable_used_no_dead_write():
    """Test that used variables are not flagged as dead"""
    code = """
    10 X = 10
    20 PRINT X
    30 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    # X is used in PRINT, so no dead write
    x_dead = [dw for dw in analyzer.dead_writes if dw.variable == "X"]
    assert len(x_dead) == 0, "X should not be flagged as dead (it's used in PRINT)"

    print("✓ Variable used, no dead write")


def test_overwritten_before_use():
    """Test detection when variable is written twice without reading"""
    code = """
    10 X = 10
    20 X = 20
    30 PRINT X
    40 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    # First write to X at line 10 is dead (overwritten at line 20 without reading)
    x_dead = [dw for dw in analyzer.dead_writes if dw.variable == "X" and dw.line == 10]
    assert len(x_dead) == 1, "First write to X should be dead"

    print("✓ Overwritten before use")


def test_multiple_dead_writes():
    """Test detection of multiple dead writes"""
    code = """
    10 X = 10
    20 Y = 20
    30 Z = 30
    40 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    assert len(analyzer.dead_writes) == 3, f"Should detect 3 dead writes, found {len(analyzer.dead_writes)}"

    dead_vars = {dw.variable for dw in analyzer.dead_writes}
    assert dead_vars == {"X", "Y", "Z"}, "Should detect all three dead writes"

    print("✓ Multiple dead writes")


def test_dead_write_in_expression():
    """Test that variables used in expressions are live"""
    code = """
    10 X = 10
    20 Y = X + 5
    30 PRINT Y
    40 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    # X is used in the expression for Y, so not dead
    # Y is used in PRINT, so not dead
    x_dead = [dw for dw in analyzer.dead_writes if dw.variable == "X"]
    y_dead = [dw for dw in analyzer.dead_writes if dw.variable == "Y"]
    assert len(x_dead) == 0, "X should not be dead (used in Y's expression)"
    assert len(y_dead) == 0, "Y should not be dead (used in PRINT)"

    print("✓ Dead write in expression")


def test_dead_write_with_conditional():
    """Test live variable analysis with conditional statements"""
    code = """
    10 X = 10
    20 IF X > 5 THEN Y = 20
    30 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    # X is used in condition, so not dead
    # Y is written but never read, so it's dead
    x_dead = [dw for dw in analyzer.dead_writes if dw.variable == "X"]
    y_dead = [dw for dw in analyzer.dead_writes if dw.variable == "Y"]
    assert len(x_dead) == 0, "X should not be dead (used in condition)"
    assert len(y_dead) == 1, "Y should be dead (never read)"

    print("✓ Dead write with conditional")


def test_live_across_goto():
    """Test that variables live across GOTO"""
    code = """
    10 X = 10
    20 GOTO 40
    30 PRINT "SKIPPED"
    40 PRINT X
    50 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    # X is used at line 40, so not dead
    x_dead = [dw for dw in analyzer.dead_writes if dw.variable == "X"]
    assert len(x_dead) == 0, "X should not be dead (used after GOTO)"

    print("✓ Live across GOTO")


def test_dead_write_with_for_loop():
    """Test live variable analysis with FOR loops"""
    code = """
    10 SUM = 0
    20 FOR I = 1 TO 10
    30   SUM = SUM + I
    40 NEXT I
    50 PRINT SUM
    60 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    # SUM is used, so not dead
    # I is loop variable, used in the loop
    sum_dead = [dw for dw in analyzer.dead_writes if dw.variable == "SUM"]
    i_dead = [dw for dw in analyzer.dead_writes if dw.variable == "I"]
    assert len(sum_dead) == 0, "SUM should not be dead"
    # Note: We may have dead writes for intermediate assignments to SUM

    print("✓ Dead write with FOR loop")


def test_input_not_dead():
    """Test that INPUT statements don't create dead writes"""
    code = """
    10 INPUT X
    20 PRINT X
    30 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    # INPUT defines X, and X is used in PRINT, so no dead write
    x_dead = [dw for dw in analyzer.dead_writes if dw.variable == "X"]
    assert len(x_dead) == 0, "INPUT variable should not be flagged as dead when used"

    print("✓ INPUT not dead")


def test_read_not_dead():
    """Test that READ statements don't create dead writes"""
    code = """
    10 DATA 1, 2, 3
    20 READ X
    30 PRINT X
    40 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    # READ defines X, and X is used in PRINT, so no dead write
    x_dead = [dw for dw in analyzer.dead_writes if dw.variable == "X"]
    assert len(x_dead) == 0, "READ variable should not be flagged as dead when used"

    print("✓ READ not dead")


def test_self_referential_assignment():
    """Test variables used in their own assignment"""
    code = """
    10 X = 0
    20 X = X + 1
    30 PRINT X
    40 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    # X at line 10 is used in line 20's RHS, so not dead
    # X at line 20 is used in PRINT, so not dead
    x_dead_10 = [dw for dw in analyzer.dead_writes if dw.variable == "X" and dw.line == 10]
    assert len(x_dead_10) == 0, "First X should not be dead (used in X = X + 1)"

    print("✓ Self-referential assignment")


def test_dead_write_complex_program():
    """Test live variable analysis on a complex program"""
    code = """
    10 A = 10
    20 B = 20
    30 C = A + B
    40 D = 40
    50 E = D * 2
    60 PRINT C, E
    70 F = 100
    80 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"

    # A, B used in C, C used in PRINT -> not dead
    # D used in E, E used in PRINT -> not dead
    # F never used -> dead
    f_dead = [dw for dw in analyzer.dead_writes if dw.variable == "F"]
    assert len(f_dead) == 1, "F should be dead (never read)"

    a_dead = [dw for dw in analyzer.dead_writes if dw.variable == "A"]
    b_dead = [dw for dw in analyzer.dead_writes if dw.variable == "B"]
    c_dead = [dw for dw in analyzer.dead_writes if dw.variable == "C"]
    assert len(a_dead) == 0, "A should not be dead"
    assert len(b_dead) == 0, "B should not be dead"
    assert len(c_dead) == 0, "C should not be dead"

    print("✓ Dead write complex program")


def test_no_dead_writes_in_perfect_program():
    """Test that a well-written program has no dead writes"""
    code = """
    10 X = 10
    20 Y = 20
    30 Z = X + Y
    40 PRINT Z
    50 END
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    assert success, f"Analysis failed: {analyzer.errors}"
    # All variables are used, no dead writes
    assert len(analyzer.dead_writes) == 0, "Well-written program should have no dead writes"

    print("✓ No dead writes in perfect program")


def run_all_tests():
    """Run all live variable analysis tests"""
    print("\n" + "="*70)
    print("LIVE VARIABLE ANALYSIS TESTS")
    print("="*70 + "\n")

    test_simple_dead_write()
    test_variable_used_no_dead_write()
    test_overwritten_before_use()
    test_multiple_dead_writes()
    test_dead_write_in_expression()
    test_dead_write_with_conditional()
    test_live_across_goto()
    test_dead_write_with_for_loop()
    test_input_not_dead()
    test_read_not_dead()
    test_self_referential_assignment()
    test_dead_write_complex_program()
    test_no_dead_writes_in_perfect_program()

    print("\n" + "="*70)
    print("All live variable analysis tests passed! ✓")
    print("="*70 + "\n")


if __name__ == '__main__':
    run_all_tests()
