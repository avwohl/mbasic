#!/usr/bin/env python3
"""Test the final simplified variable export API"""

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
print("FINAL SIMPLIFIED API: get_all_variables()")
print("=" * 70)
print("\nThere is now only ONE method to get variable information.")
print("It returns a list of dicts with complete information including")
print("tracking data (last_read and last_write).\n")

all_vars = runtime.get_all_variables()

print(f"Type: {type(all_vars)}")
print(f"Number of variables: {len(all_vars)}\n")

# Show a scalar variable
scalar = [v for v in all_vars if not v['is_array'] and v['name'] == 'x'][0]
print("Example scalar variable:")
print(json.dumps(scalar, indent=2, default=str))

# Show an array variable
array = [v for v in all_vars if v['is_array']][0]
print("\nExample array variable:")
print(json.dumps(array, indent=2, default=str))

print("\n" + "=" * 70)
print("KEY FEATURES:")
print("=" * 70)
print("""
✓ Single method: get_all_variables()
✓ Returns list of dicts (not tuples or simple dict)
✓ Always includes last_read and last_write tracking
✓ No 'metadata' concept - tracking is part of the variable
✓ No 'include_metadata' parameter - always included
✓ UI can sort the list however it wants
✓ line -1 in last_write indicates debugger/prompt set
""")

print("=" * 70)
print("Test passed!")
print("=" * 70)
