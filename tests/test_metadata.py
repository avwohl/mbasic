#!/usr/bin/env python3
"""Test variable access metadata tracking"""

import sys
sys.path.insert(0, '../src')

from lexer import tokenize
from parser import Parser
from interpreter import Interpreter
from runtime import Runtime

# Program that accesses variables
code = """
10 X% = 42
20 Y% = X% + 10
30 PRINT Y%
40 X% = 99
"""

# Parse and run
tokens = tokenize(code)
parser = Parser(tokens)
program = parser.parse()

runtime = Runtime(program)
interpreter = Interpreter(runtime)
interpreter.run()

print("=" * 70)
print("Variable Access Tracking")
print("=" * 70)

all_vars = runtime.get_all_variables()

for var in all_vars:
    if var['name'] in ('x', 'y'):  # Only show our test variables
        print(f"\n{var['name']}{var['type_suffix']} = {var['value']}")

        if var['last_read']:
            print(f"  Last READ:")
            print(f"    Line: {var['last_read']['line']}")
            print(f"    Position: {var['last_read']['position']}")
            print(f"    Timestamp: {var['last_read']['timestamp']:.6f}")
        else:
            print(f"  Last READ: None")

        if var['last_write']:
            print(f"  Last WRITE:")
            print(f"    Line: {var['last_write']['line']}")
            print(f"    Position: {var['last_write']['position']}")
            print(f"    Timestamp: {var['last_write']['timestamp']:.6f}")
        else:
            print(f"  Last WRITE: None")

        debugger_set = var['last_write'] and var['last_write']['line'] == -1
        print(f"  Debugger/Prompt Set: {debugger_set}")

print("\n" + "=" * 70)
print("Variable Tracking Structure:")
print("=" * 70)
print("""
Each variable contains access tracking information:
  'last_read': {
      'line': <line number>,
      'position': <character position>,
      'timestamp': <high precision time.perf_counter()>
  }
  'last_write': {
      'line': <line number or -1 for debugger/prompt>,
      'position': <character position or None>,
      'timestamp': <high precision time.perf_counter()>
  }

Note: line -1 in last_write indicates variable was set from debugger or command prompt
""")
