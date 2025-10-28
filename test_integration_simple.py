#!/usr/bin/env python3
"""Simple integration test"""

import sys
sys.path.insert(0, 'src')

from runtime import Runtime
from src.settings import SettingsManager
from parser import Parser
from lexer import Lexer
from src.interpreter import Interpreter

program = """
20 TargetAngle = 45
40 targetangle = 90
"""

# Parse
lexer = Lexer(program)
tokens = lexer.tokenize()
parser = Parser(tokens)
ast = parser.parse()

# Create runtime
line_table = {line.line_number: line for line in ast.lines}
runtime = Runtime(line_table)
runtime.setup()

# Create settings
settings = SettingsManager()
settings.set("variables.case_conflict", "first_wins")

# Create interpreter
interp = Interpreter(runtime, settings_manager=settings)

# Execute line 20
print("Executing line 20: TargetAngle = 45")
line20 = runtime.line_table[20]
runtime.current_line = line20
for stmt in line20.statements:
    print(f"  Statement variable: name={stmt.variable.name}, original_case={stmt.variable.original_case}")
    interp.execute_statement(stmt)

variables = runtime.get_all_variables()
target_var = [v for v in variables if v['name'].lower() == 'targetangle'][0]
print(f"  After line 20: original_case={target_var['original_case']}, value={target_var['value']}")

# Execute line 40
print("\nExecuting line 40: targetangle = 90")
line40 = runtime.line_table[40]
runtime.current_line = line40
for stmt in line40.statements:
    print(f"  Statement variable: name={stmt.variable.name}, original_case={stmt.variable.original_case}")
    interp.execute_statement(stmt)

variables = runtime.get_all_variables()
target_var = [v for v in variables if v['name'].lower() == 'targetangle'][0]
print(f"  After line 40: original_case={target_var['original_case']}, value={target_var['value']}")

if target_var['original_case'] == 'TargetAngle':
    print("\n✓ SUCCESS: first_wins preserved 'TargetAngle'")
else:
    print(f"\n✗ FAIL: Expected 'TargetAngle', got '{target_var['original_case']}'")
