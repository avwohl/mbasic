#!/usr/bin/env python3
"""Debug test for first_wins policy"""

import sys
sys.path.insert(0, 'src')

from runtime import Runtime
from src.settings import SettingsManager

class TestToken:
    def __init__(self, line, column):
        self.line = line
        self.column = column

# Create runtime
runtime = Runtime({})
settings = SettingsManager()
settings.set("variables.case_conflict", "first_wins")

print("Setting variable 'targetangle' with case 'TargetAngle' at line 20")
token1 = TestToken(20, 5)
runtime.set_variable('targetangle', '!', 45, token=token1, original_case='TargetAngle', settings_manager=settings)

print(f"Variants after line 20: {runtime._variable_case_variants.get('targetangle', [])}")
print(f"Stored original_case: {runtime._variables['targetangle!'].get('original_case')}")
print(f"Value: {runtime._variables['targetangle!']['value']}")

print("\nSetting variable 'targetangle' with case 'targetangle' at line 40")
token2 = TestToken(40, 5)
runtime.set_variable('targetangle', '!', 90, token=token2, original_case='targetangle', settings_manager=settings)

print(f"Variants after line 40: {runtime._variable_case_variants.get('targetangle', [])}")
print(f"Stored original_case: {runtime._variables['targetangle!'].get('original_case')}")
print(f"Value: {runtime._variables['targetangle!']['value']}")

# Check get_all_variables
variables = runtime.get_all_variables()
target_var = [v for v in variables if v['name'].lower() == 'targetangle'][0]
print(f"\nget_all_variables returned original_case: {target_var.get('original_case')}")
