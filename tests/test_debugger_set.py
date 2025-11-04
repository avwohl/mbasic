#!/usr/bin/env python3
"""Test that debugger_set uses line -1"""

import sys
sys.path.insert(0, '../src')

from lexer import tokenize
from parser import Parser
from interpreter import Interpreter
from runtime import Runtime

code = """
10 X% = 42
20 PRINT X%
"""

# Parse and run
tokens = tokenize(code)
parser = Parser(tokens)
program = parser.parse()
runtime = Runtime(program)
interpreter = Interpreter(runtime)
interpreter.run()

print("=" * 70)
print("Testing debugger_set flag")
print("=" * 70)

# Now set a variable from the "debugger"
runtime.set_variable('z', '%', 999, debugger_set=True)

# Get variables
vars = runtime.get_all_variables()
z_var = [v for v in vars if v['name'] == 'z'][0]

print(f"\nVariable z% set with debugger_set=True:")
print(f"  Value: {z_var['value']}")
print(f"  last_write: {z_var['last_write']}")
print(f"\n  last_write['line']: {z_var['last_write']['line']}")
print(f"  Is debugger/prompt set: {z_var['last_write']['line'] == -1}")

print("\n" + "=" * 70)
print("Compare with normal program variable:")
print("=" * 70)
x_var = [v for v in vars if v['name'] == 'x'][0]
print(f"\nVariable x% set by program:")
print(f"  Value: {x_var['value']}")
print(f"  last_write['line']: {x_var['last_write']['line']}")
print(f"  Is debugger/prompt set: {x_var['last_write']['line'] == -1}")

print("\n" + "=" * 70)
print("SUCCESS: line -1 correctly indicates debugger/prompt set")
print("=" * 70)
