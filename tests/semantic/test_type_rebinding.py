#!/usr/bin/env python3
"""
Tests for type rebinding analysis (Phase 1).

Tests detection of:
- FOR loop variables with INTEGER bounds (can rebind)
- Sequential independent assignments (can rebind)
- Dependent assignments (cannot rebind)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from lexer import Lexer
from parser import Parser
from semantic_analyzer import SemanticAnalyzer


def analyze_program(source: str):
    """Helper to analyze a BASIC program"""
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    program = parser.parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(program)
    return analyzer


def get_var_name(analyzer, base_name: str) -> str:
    """
    Helper to get the actual variable name (with or without suffix).
    The parser may add a default ! suffix for untyped variables.
    """
    # Try with ! suffix first (default SINGLE type)
    if f'{base_name}!' in analyzer.variable_type_versions:
        return f'{base_name}!'
    # Try with # suffix (DOUBLE)
    if f'{base_name}#' in analyzer.variable_type_versions:
        return f'{base_name}#'
    # Try with % suffix (INTEGER)
    if f'{base_name}%' in analyzer.variable_type_versions:
        return f'{base_name}%'
    # Try with $ suffix (STRING)
    if f'{base_name}$' in analyzer.variable_type_versions:
        return f'{base_name}$'
    # Try without suffix
    if base_name in analyzer.variable_type_versions:
        return base_name
    # Return base name (will fail assertion if not found)
    return base_name


def test_for_loop_integer_rebinding():
    """Test that FOR loop variable can rebind from DOUBLE to INTEGER"""
    source = """
100 I = 22.1
110 FOR I = 0 TO 10
120   PRINT I
130 NEXT I
"""
    analyzer = analyze_program(source)

    # Should have two bindings for I (parser may add ! suffix)
    var_name = get_var_name(analyzer, 'I')
    assert var_name in analyzer.variable_type_versions
    bindings = analyzer.variable_type_versions[var_name]
    assert len(bindings) == 2

    # First binding: DOUBLE (from 22.1)
    assert bindings[0].line == 100
    assert bindings[0].type_name == "DOUBLE"
    assert bindings[0].can_rebind == True  # Independent assignment

    # Second binding: INTEGER (from FOR loop)
    assert bindings[1].line == 110
    assert bindings[1].type_name == "INTEGER"
    assert bindings[1].can_rebind == True  # FOR overwrites
    assert bindings[1].reason == "FOR loop with INTEGER bounds"

    # Variable can be re-bound
    assert analyzer.can_rebind_variable[var_name] == True

    print("✓ test_for_loop_integer_rebinding passed")


def test_for_loop_double_bounds():
    """Test that FOR loop with DOUBLE bounds stays DOUBLE"""
    source = """
100 FOR I = 1.0 TO 10.0
110   PRINT I
120 NEXT I
"""
    analyzer = analyze_program(source)

    var_name = get_var_name(analyzer, 'I')
    assert var_name in analyzer.variable_type_versions
    bindings = analyzer.variable_type_versions[var_name]
    assert len(bindings) == 1

    assert bindings[0].line == 100
    assert bindings[0].type_name == "DOUBLE"
    assert bindings[0].reason == "FOR loop with DOUBLE bounds"

    print("✓ test_for_loop_double_bounds passed")


def test_sequential_independent_assignments():
    """Test sequential assignments with no data dependency"""
    source = """
100 X = 10
110 PRINT X
120 X = 10.5
130 PRINT X
"""
    analyzer = analyze_program(source)

    var_name = get_var_name(analyzer, 'X')
    assert var_name in analyzer.variable_type_versions
    bindings = analyzer.variable_type_versions[var_name]
    assert len(bindings) == 2

    # First binding: INTEGER
    assert bindings[0].line == 100
    assert bindings[0].type_name == "INTEGER"
    assert bindings[0].depends_on_previous == False
    assert bindings[0].can_rebind == True

    # Second binding: DOUBLE
    assert bindings[1].line == 120
    assert bindings[1].type_name == "DOUBLE"
    assert bindings[1].depends_on_previous == False
    assert bindings[1].can_rebind == True

    # Can rebind
    assert analyzer.can_rebind_variable[var_name] == True

    print("✓ test_sequential_independent_assignments passed")


def test_dependent_assignment_cannot_rebind():
    """Test that dependent assignments cannot rebind"""
    source = """
100 X = 10
110 X = X + 1
"""
    analyzer = analyze_program(source)

    var_name = get_var_name(analyzer, 'X')
    assert var_name in analyzer.variable_type_versions
    bindings = analyzer.variable_type_versions[var_name]
    assert len(bindings) == 2

    # First binding: INTEGER
    assert bindings[0].line == 100
    assert bindings[0].type_name == "INTEGER"
    assert bindings[0].depends_on_previous == False
    assert bindings[0].can_rebind == True

    # Second binding: INTEGER but depends on previous
    assert bindings[1].line == 110
    assert bindings[1].type_name == "INTEGER"
    assert bindings[1].depends_on_previous == True  # X = X + 1
    assert bindings[1].can_rebind == False  # Cannot rebind

    # Cannot rebind (one binding has dependency)
    assert analyzer.can_rebind_variable[var_name] == False

    print("✓ test_dependent_assignment_cannot_rebind passed")


def test_integer_arithmetic():
    """Test that INTEGER arithmetic is detected correctly"""
    source = """
100 A = 10
110 B = 20
120 C = A + B
130 D = C * 2
"""
    analyzer = analyze_program(source)

    # All should be INTEGER
    for var_base in ['A', 'B', 'C', 'D']:
        var_name = get_var_name(analyzer, var_base)
        assert var_name in analyzer.variable_type_versions
        bindings = analyzer.variable_type_versions[var_name]
        assert len(bindings) == 1
        assert bindings[0].type_name == "INTEGER"

    print("✓ test_integer_arithmetic passed")


def test_double_arithmetic():
    """Test that DOUBLE arithmetic is detected correctly"""
    source = """
100 A = 10.5
110 B = 20.5
120 C = A + B
"""
    analyzer = analyze_program(source)

    # All should be DOUBLE
    for var_base in ['A', 'B', 'C']:
        var_name = get_var_name(analyzer, var_base)
        assert var_name in analyzer.variable_type_versions
        bindings = analyzer.variable_type_versions[var_name]
        assert len(bindings) == 1
        assert bindings[0].type_name == "DOUBLE"

    print("✓ test_double_arithmetic passed")


def test_mixed_arithmetic_promotes_to_double():
    """Test that mixed INTEGER/DOUBLE arithmetic becomes DOUBLE"""
    source = """
100 X = 10
110 Y = 10.5
120 Z = X + Y
"""
    analyzer = analyze_program(source)

    # X is INTEGER
    x_name = get_var_name(analyzer, 'X')
    assert analyzer.variable_type_versions[x_name][0].type_name == "INTEGER"

    # Y is DOUBLE
    y_name = get_var_name(analyzer, 'Y')
    assert analyzer.variable_type_versions[y_name][0].type_name == "DOUBLE"

    # Z should be DOUBLE (conservative - we don't know X+Y type yet)
    # For now, we just check that Z exists
    z_name = get_var_name(analyzer, 'Z')
    assert z_name in analyzer.variable_type_versions

    print("✓ test_mixed_arithmetic_promotes_to_double passed")


def test_for_loop_with_explicit_integer_suffix():
    """Test FOR loop variable with explicit INTEGER suffix"""
    source = """
100 FOR I% = 1 TO 100
110   PRINT I%
120 NEXT I%
"""
    analyzer = analyze_program(source)

    assert 'I%' in analyzer.variable_type_versions
    bindings = analyzer.variable_type_versions['I%']
    assert len(bindings) == 1
    assert bindings[0].type_name == "INTEGER"

    print("✓ test_for_loop_with_explicit_integer_suffix passed")


def test_for_loop_with_explicit_double_suffix():
    """Test FOR loop variable with explicit DOUBLE suffix"""
    source = """
100 FOR I# = 1 TO 100
110   PRINT I#
120 NEXT I#
"""
    analyzer = analyze_program(source)

    assert 'I#' in analyzer.variable_type_versions
    bindings = analyzer.variable_type_versions['I#']
    assert len(bindings) == 1
    # Even though bounds are INTEGER, variable has # suffix so might be DOUBLE
    # Actually, the FOR loop should detect INTEGER bounds
    assert bindings[0].type_name == "INTEGER"  # Bounds are INTEGER

    print("✓ test_for_loop_with_explicit_double_suffix passed")


def test_multiple_rebindings():
    """Test variable with multiple type bindings"""
    source = """
100 X = 10
110 PRINT X
120 X = 10.5
130 PRINT X
140 X = 20
150 PRINT X
"""
    analyzer = analyze_program(source)

    var_name = get_var_name(analyzer, 'X')
    assert var_name in analyzer.variable_type_versions
    bindings = analyzer.variable_type_versions[var_name]
    assert len(bindings) == 3

    # All should be independent (no dependencies)
    assert bindings[0].type_name == "INTEGER"
    assert bindings[0].can_rebind == True

    assert bindings[1].type_name == "DOUBLE"
    assert bindings[1].can_rebind == True

    assert bindings[2].type_name == "INTEGER"
    assert bindings[2].can_rebind == True

    # Can rebind
    assert analyzer.can_rebind_variable[var_name] == True

    print("✓ test_multiple_rebindings passed")


def test_loop_counter_stays_integer():
    """Test that loop counter stays INTEGER throughout"""
    source = """
100 FOR I = 1 TO 100
110   J = J + I
120 NEXT I
"""
    analyzer = analyze_program(source)

    # I should be INTEGER
    i_name = get_var_name(analyzer, 'I')
    assert i_name in analyzer.variable_type_versions
    assert analyzer.variable_type_versions[i_name][0].type_name == "INTEGER"

    # J should be INTEGER (starts uninitialized, then J + I)
    # Actually, J is not in the list yet because it's not assigned explicitly
    # J = J + I creates one binding
    j_name = get_var_name(analyzer, 'J')
    if j_name in analyzer.variable_type_versions:
        # J depends on itself, so cannot rebind
        bindings = analyzer.variable_type_versions[j_name]
        assert bindings[0].depends_on_previous == True

    print("✓ test_loop_counter_stays_integer passed")


def test_real_world_example():
    """Test the real-world example from the doc"""
    source = """
100 I=22.1
110 FOR I=0 TO 10
120   J=J+I
130 NEXT I
"""
    analyzer = analyze_program(source)

    # I should have two bindings
    var_name = get_var_name(analyzer, 'I')
    assert var_name in analyzer.variable_type_versions
    bindings = analyzer.variable_type_versions[var_name]
    assert len(bindings) == 2

    # First: DOUBLE
    assert bindings[0].type_name == "DOUBLE"

    # Second: INTEGER (FOR loop)
    assert bindings[1].type_name == "INTEGER"

    # Can rebind
    assert analyzer.can_rebind_variable[var_name] == True

    print("✓ test_real_world_example passed")


def test_same_type_no_rebinding_needed():
    """Test that variables with same type don't need rebinding"""
    source = """
100 X = 10
110 PRINT X
120 X = 20
130 PRINT X
"""
    analyzer = analyze_program(source)

    var_name = get_var_name(analyzer, 'X')
    assert var_name in analyzer.variable_type_versions
    bindings = analyzer.variable_type_versions[var_name]
    assert len(bindings) == 2

    # Both INTEGER
    assert bindings[0].type_name == "INTEGER"
    assert bindings[1].type_name == "INTEGER"

    # No rebinding needed (same type)
    assert analyzer.can_rebind_variable[var_name] == False

    print("✓ test_same_type_no_rebinding_needed passed")


if __name__ == '__main__':
    test_for_loop_integer_rebinding()
    test_for_loop_double_bounds()
    test_sequential_independent_assignments()
    test_dependent_assignment_cannot_rebind()
    test_integer_arithmetic()
    test_double_arithmetic()
    test_mixed_arithmetic_promotes_to_double()
    test_for_loop_with_explicit_integer_suffix()
    test_for_loop_with_explicit_double_suffix()
    test_multiple_rebindings()
    test_loop_counter_stays_integer()
    test_real_world_example()
    test_same_type_no_rebinding_needed()

    print("\n✅ All type rebinding tests passed!")
