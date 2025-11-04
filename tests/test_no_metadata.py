#!/usr/bin/env python3
"""Test that metadata concept is removed and tracking info is always included"""

import sys
import json
sys.path.insert(0, '../src')

from lexer import tokenize
from parser import Parser
from interpreter import Interpreter
from runtime import Runtime

code = """
10 X% = 42
20 MSG$ = "hello"
30 DIM A%(5, 3)
40 Y% = X% + 10
50 PRINT Y%
"""

# Parse and run
tokens = tokenize(code)
parser = Parser(tokens)
program = parser.parse()
runtime = Runtime(program)
interpreter = Interpreter(runtime)
interpreter.run()

print("=" * 70)
print("1. get_all_variables() - Always includes last_read/last_write")
print("=" * 70)
detailed = runtime.get_all_variables()
print(f"Returns: list of {len(detailed)} dicts")

# Show a scalar
scalar = [v for v in detailed if not v['is_array'] and v['name'] == 'x'][0]
print(f"\nScalar variable 'x%':")
print(json.dumps(scalar, indent=2, default=str))
print(f"\nKeys: {list(scalar.keys())}")
print(f"Has 'last_read': {'last_read' in scalar}")
print(f"Has 'last_write': {'last_write' in scalar}")
print(f"Has 'metadata': {'metadata' in scalar}")  # Should be False

# Show an array
array = [v for v in detailed if v['is_array']][0]
print(f"\nArray variable '{array['name']}{array['type_suffix']}':")
print(json.dumps(array, indent=2, default=str))


print("\n" + "=" * 70)
print("2. No 'include_metadata' parameter")
print("=" * 70)
print("get_all_variables signature:")
import inspect
sig = inspect.signature(runtime.get_all_variables)
print(f"  Parameters: {list(sig.parameters.keys())}")
print(f"  Has 'include_metadata' param: {'include_metadata' in sig.parameters}")

print("\n" + "=" * 70)
print("SUCCESS: API simplified!")
print("  - Single method: get_all_variables()")
print("  - No 'metadata' key in returned dicts")
print("  - No 'include_metadata' parameters")
print("  - last_read and last_write are always included directly")
print("=" * 70)
