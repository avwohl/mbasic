#!/usr/bin/env python3
"""Integration test for variable case conflict with runtime and variable window"""

import sys
sys.path.insert(0, 'src')

from runtime import Runtime
from src.settings import SettingsManager
from parser import Parser
from lexer import Lexer

def test_case_conflict_in_program():
    """Test case conflict detection in a real program"""
    print("Testing case conflict in full program...")

    # Create a program with case conflicts
    program = """
10 REM Test case conflict
20 TargetAngle = 45
30 PRINT "First: "; TargetAngle
40 targetangle = 90
50 PRINT "Second: "; targetangle
60 PRINT "Are same?"; TargetAngle = targetangle
70 END
"""

    # Parse the program
    lexer = Lexer(program)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()

    # Create runtime with line table
    line_table = {line.line_number: line for line in ast.lines}
    runtime = Runtime(line_table)
    runtime.setup()

    # Test with different policies
    policies = ['first_wins', 'prefer_upper', 'prefer_lower']

    for policy in policies:
        print(f"\n  Testing policy: {policy}")

        # Reset runtime
        runtime = Runtime(line_table)
        runtime.setup()

        # Create settings with policy
        settings = SettingsManager()
        settings.set("variables.case_conflict", policy)

        # Create interpreter
        from src.interpreter import Interpreter
        interp = Interpreter(runtime, settings_manager=settings)

        # Execute lines 20 and 40 (the assignments)
        try:
            # Line 20: TargetAngle = 45
            line20 = runtime.line_table[20]
            runtime.current_line = line20
            for stmt in line20.statements:
                interp.execute_statement(stmt)

            # Line 40: targetangle = 90
            line40 = runtime.line_table[40]
            runtime.current_line = line40
            for stmt in line40.statements:
                interp.execute_statement(stmt)

            # Check which case was stored
            variables = runtime.get_all_variables()
            target_var = [v for v in variables if v['name'].lower() == 'targetangle'][0]
            stored_case = target_var.get('original_case', target_var['name'])
            value = target_var['value']

            print(f"    Stored case: {stored_case}")
            print(f"    Value: {value}")

            # Verify expectations
            if policy == 'first_wins':
                assert stored_case == 'TargetAngle', f"Expected 'TargetAngle', got '{stored_case}'"
                assert value == 90, f"Expected value 90, got {value}"
                print(f"    ✓ first_wins: {stored_case} with value {value}")

            elif policy == 'prefer_upper':
                # Both have same number of uppercase, so first should win initially
                # But targetangle (all lower) should NOT replace TargetAngle
                # Actually both have 1 uppercase letter in TargetAngle, and 0 in targetangle
                # So prefer_upper should choose TargetAngle
                assert stored_case == 'TargetAngle', f"Expected 'TargetAngle', got '{stored_case}'"
                print(f"    ✓ prefer_upper: {stored_case}")

            elif policy == 'prefer_lower':
                # targetangle has more lowercase letters
                assert stored_case == 'targetangle', f"Expected 'targetangle', got '{stored_case}'"
                print(f"    ✓ prefer_lower: {stored_case}")

        except Exception as e:
            print(f"    ✗ Error: {e}")
            return False

    return True

def test_variable_window_display():
    """Test that get_all_variables returns original_case"""
    print("\nTesting variable window display...")

    # Create simple runtime
    runtime = Runtime({})
    settings = SettingsManager()
    settings.set("variables.case_conflict", "prefer_upper")

    # Create token class for testing
    class TestToken:
        def __init__(self, line, column):
            self.line = line
            self.column = column

    # Set variables with different cases
    token1 = TestToken(10, 5)
    token2 = TestToken(20, 5)
    token3 = TestToken(30, 5)

    runtime.set_variable('myvar', '!', 10, token=token1, original_case='MyVar', settings_manager=settings)
    runtime.set_variable('myvar', '!', 20, token=token2, original_case='myvar', settings_manager=settings)
    runtime.set_variable('myvar', '!', 30, token=token3, original_case='MYVAR', settings_manager=settings)

    # Get all variables
    variables = runtime.get_all_variables()

    # Find myvar
    myvar = [v for v in variables if v['name'].lower() == 'myvar'][0]

    # Check original_case is present and correct
    assert 'original_case' in myvar, "original_case not in variable info"
    stored_case = myvar['original_case']

    print(f"  Stored case: {stored_case}")
    assert stored_case == 'MYVAR', f"Expected 'MYVAR' (prefer_upper), got '{stored_case}'"
    print(f"  ✓ Variable window will display: {stored_case}!")

    return True

if __name__ == "__main__":
    print("Running variable case conflict integration tests\n")
    print("="*50)

    results = []
    results.append(("Full program test", test_case_conflict_in_program()))
    results.append(("Variable window display", test_variable_window_display()))

    print("\n" + "="*50)
    print("Test Results:")
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {name}")

    all_passed = all(r[1] for r in results)
    print("="*50)
    if all_passed:
        print("\nAll integration tests passed!")
        sys.exit(0)
    else:
        print("\nSome tests failed!")
        sys.exit(1)
