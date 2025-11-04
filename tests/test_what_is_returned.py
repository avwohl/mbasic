#!/usr/bin/env python3
"""Show what info is returned per variable"""

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
30 PI# = 3.14159
40 DIM A%(5, 3)
50 Y% = X% + 10
60 PRINT Y%
"""

# Parse and run
tokens = tokenize(code)
parser = Parser(tokens)
program = parser.parse()
runtime = Runtime(program)
interpreter = Interpreter(runtime)
interpreter.run()

print("=" * 70)
print("get_all_variables() - Complete variable information")
print("=" * 70)
all_vars = runtime.get_all_variables()
print(f"Type: {type(all_vars)}")
print(f"Returns: list of {len(all_vars)} dicts")

if all_vars:
    print(f"\nFirst scalar variable:")
    scalar = [v for v in all_vars if not v['is_array'] and v['name'] == 'x'][0]
    print(json.dumps(scalar, indent=2, default=str))

    print(f"\nFirst array variable:")
    array = [v for v in all_vars if v['is_array']][0]
    print(json.dumps(array, indent=2, default=str))

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print("""
get_all_variables():
  Returns: list [{'name': str, 'type_suffix': str, 'is_array': bool,
                  'value': ... (scalars),
                  'dimensions': [...], 'base': int (arrays),
                  'last_read': {...}, 'last_write': {...}}, ...]
  Use: Complete variable information with access tracking
  Note: line -1 in last_write indicates debugger/prompt set
  Note: UI can sort the list however it wants (by name, type, recent access, etc.)
""")
