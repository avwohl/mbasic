#!/usr/bin/env python3
"""Test that update_variables() preserves original_case during CHAIN ALL"""

import sys
import os

# Add project root to path (3 levels up from tests/regression/integration/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.runtime import Runtime
from src.settings import SettingsManager

def test_update_variables_preserves_case():
    """Test that update_variables() preserves original_case"""
    print("Testing update_variables() case preservation...")

    # Create first runtime with variables
    runtime1 = Runtime({})
    settings = SettingsManager()
    settings.set("variables.case_conflict", "first_wins")

    # Simulate setting variables with specific cases
    class TestToken:
        def __init__(self, line, column):
            self.line = line
            self.column = column

    token1 = TestToken(10, 5)
    token2 = TestToken(20, 5)
    token3 = TestToken(30, 5)

    # Set variables with mixed case
    runtime1.set_variable('myvar', '!', 100, token=token1, original_case='MyVar', settings_manager=settings)
    runtime1.set_variable('counter', '%', 42, token=token2, original_case='Counter', settings_manager=settings)
    runtime1.set_variable('message', '$', 'Hello', token=token3, original_case='MESSAGE', settings_manager=settings)

    print(f"  Original runtime variables:")
    for name, var_entry in runtime1._variables.items():
        print(f"    {name}: value={var_entry['value']}, original_case={var_entry.get('original_case')}")

    # Get all variables (simulating CHAIN ALL)
    variables = runtime1.get_all_variables()

    print(f"\n  Exported variables:")
    for var in variables:
        print(f"    {var['name']}{var['type_suffix']}: value={var['value']}, original_case={var.get('original_case')}")

    # Create second runtime (simulating chained program)
    runtime2 = Runtime({})

    # Update variables (this is what CHAIN ALL does)
    runtime2.update_variables(variables)

    print(f"\n  Restored runtime variables:")
    for name, var_entry in runtime2._variables.items():
        print(f"    {name}: value={var_entry['value']}, original_case={var_entry.get('original_case')}")

    # Verify original_case was preserved
    assert 'myvar!' in runtime2._variables, "myvar! not found"
    assert runtime2._variables['myvar!']['original_case'] == 'MyVar', \
        f"Expected 'MyVar', got '{runtime2._variables['myvar!']['original_case']}'"

    assert 'counter%' in runtime2._variables, "counter% not found"
    assert runtime2._variables['counter%']['original_case'] == 'Counter', \
        f"Expected 'Counter', got '{runtime2._variables['counter%']['original_case']}'"

    assert 'message$' in runtime2._variables, "message$ not found"
    assert runtime2._variables['message$']['original_case'] == 'MESSAGE', \
        f"Expected 'MESSAGE', got '{runtime2._variables['message$']['original_case']}'"

    # Verify values were preserved
    assert runtime2._variables['myvar!']['value'] == 100
    assert runtime2._variables['counter%']['value'] == 42
    assert runtime2._variables['message$']['value'] == 'Hello'

    print("\n  ✓ All original_case values preserved correctly!")
    print("  ✓ All variable values preserved correctly!")
    return True

if __name__ == "__main__":
    print("Testing CHAIN ALL case preservation fix\n")
    print("="*50)

    try:
        success = test_update_variables_preserves_case()
        print("="*50)
        if success:
            print("\n✅ TEST PASSED: update_variables() preserves original_case")
            sys.exit(0)
    except AssertionError as e:
        print("="*50)
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print("="*50)
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
