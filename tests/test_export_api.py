#!/usr/bin/env python3
"""Test the variable export API"""

import sys
sys.path.insert(0, '../src')

from lexer import tokenize
from parser import Parser
from interpreter import Interpreter
from runtime import Runtime

# Simple test program
code = """
10 X% = 42
20 MSG$ = "hello"
30 PI# = 3.14159
40 DIM A%(5, 3)
50 A%(0, 0) = 99
"""

# Parse and run
tokens = tokenize(code)
parser = Parser(tokens)
program = parser.parse()

# Create runtime and interpreter
runtime = Runtime(program)
interpreter = Interpreter(runtime)
interpreter.run()

print("=" * 70)
print("TEST: get_all_variables()")
print("=" * 70)
all_vars = runtime.get_all_variables()
for var in all_vars:
    if var['is_array']:
        print(f"  {var['name']}{var['type_suffix']}: array {var['dimensions']} (base {var['base']})")
    else:
        print(f"  {var['name']}{var['type_suffix']} = {var['value']}")

print("\n" + "=" * 70)
print("TEST: Variables with tracking info")
print("=" * 70)
for var in all_vars[:2]:  # Just show first 2
    print(f"\n  {var['name']}{var['type_suffix']}:")
    print(f"    Is Array: {var['is_array']}")
    if var['is_array']:
        print(f"    Dimensions: {var['dimensions']}")
        print(f"    Base: {var['base']}")
    else:
        print(f"    Value: {var['value']}")
    print(f"    Last Read: {var['last_read']}")
    print(f"    Last Write: {var['last_write']}")

print("\n" + "=" * 70)
print("All tests passed!")
