#!/usr/bin/env python3
"""Unit test for variable case conflict detection"""

import sys
sys.path.insert(0, 'src')

from runtime import Runtime
from src.settings import SettingsManager, SettingScope
from ast_nodes import LineNode

# Create a simple token class for testing
class TestToken:
    def __init__(self, line, column):
        self.line = line
        self.column = column

def test_first_wins():
    """Test first_wins policy - first case seen wins"""
    print("Testing first_wins policy...")

    # Create runtime and settings
    runtime = Runtime({})
    settings = SettingsManager()
    settings.set("variables.case_conflict", "first_wins")

    token1 = TestToken(10, 5)
    token2 = TestToken(20, 5)

    # Set variable with first case
    runtime.set_variable('x', '!', 10, token=token1, original_case='TargetAngle', settings_manager=settings)

    # Set variable with different case
    runtime.set_variable('x', '!', 20, token=token2, original_case='targetangle', settings_manager=settings)

    # Check that original_case is the first one
    if 'original_case' in runtime._variables['x!']:
        stored_case = runtime._variables['x!']['original_case']
        print(f"  Stored case: {stored_case}")
        assert stored_case == 'TargetAngle', f"Expected 'TargetAngle', got '{stored_case}'"
        print("  ✓ first_wins working correctly")
    else:
        print("  ✗ original_case not stored")
        return False

    return True

def test_prefer_upper():
    """Test prefer_upper policy - choose most uppercase version"""
    print("Testing prefer_upper policy...")

    # Create runtime and settings
    runtime = Runtime({})
    settings = SettingsManager()
    settings.set("variables.case_conflict", "prefer_upper")

    token1 = TestToken(10, 5)
    token2 = TestToken(20, 5)
    token3 = TestToken(30, 5)

    # Set variable with mixed case
    runtime.set_variable('x', '!', 10, token=token1, original_case='TargetAngle', settings_manager=settings)

    # Set variable with all lowercase
    runtime.set_variable('x', '!', 20, token=token2, original_case='targetangle', settings_manager=settings)

    # Set variable with all uppercase (should win)
    runtime.set_variable('x', '!', 30, token=token3, original_case='TARGETANGLE', settings_manager=settings)

    # Check that original_case is the all uppercase one
    if 'original_case' in runtime._variables['x!']:
        stored_case = runtime._variables['x!']['original_case']
        print(f"  Stored case: {stored_case}")
        assert stored_case == 'TARGETANGLE', f"Expected 'TARGETANGLE', got '{stored_case}'"
        print("  ✓ prefer_upper working correctly")
    else:
        print("  ✗ original_case not stored")
        return False

    return True

def test_error_policy():
    """Test error policy - should raise error on conflict"""
    print("Testing error policy...")

    # Create runtime and settings
    runtime = Runtime({})
    settings = SettingsManager()
    settings.set("variables.case_conflict", "error")

    token1 = TestToken(10, 5)
    token2 = TestToken(20, 5)

    # Set variable with first case
    runtime.set_variable('x', '!', 10, token=token1, original_case='TargetAngle', settings_manager=settings)

    # Try to set variable with different case - should raise error
    try:
        runtime.set_variable('x', '!', 20, token=token2, original_case='targetangle', settings_manager=settings)
        print("  ✗ Error policy did not raise exception")
        return False
    except RuntimeError as e:
        print(f"  ✓ Error raised as expected: {e}")
        return True

if __name__ == "__main__":
    print("Running variable case conflict unit tests\n")

    results = []
    results.append(("first_wins", test_first_wins()))
    results.append(("prefer_upper", test_prefer_upper()))
    results.append(("error", test_error_policy()))

    print("\n" + "="*50)
    print("Test Results:")
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {name}")

    all_passed = all(r[1] for r in results)
    print("="*50)
    if all_passed:
        print("\nAll tests passed!")
        sys.exit(0)
    else:
        print("\nSome tests failed!")
        sys.exit(1)
