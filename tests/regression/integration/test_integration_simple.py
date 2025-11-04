#!/usr/bin/env python3
"""Simple integration test - tests basic parsing, runtime, and interpreter"""

import sys
import os

# Add project root to path (3 levels up from tests/regression/integration/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.runtime import Runtime
from src.settings import SettingsManager
from src.parser import Parser
from src.lexer import Lexer
from src.interpreter import Interpreter

program = """
10 X = 5
20 Y = X + 10
30 PRINT Y
"""

# Parse
print("Parsing program...")
lexer = Lexer(program)
tokens = lexer.tokenize()
parser = Parser(tokens)
ast = parser.parse()

print(f"  Parsed {len(ast.lines)} lines")

# Create runtime
line_table = {line.line_number: line for line in ast.lines}
runtime = Runtime(line_table)
runtime.setup()
print("  Runtime initialized")

# Create interpreter
interp = Interpreter(runtime)
print("  Interpreter created")

# Execute the program
print("\nExecuting program...")
interp.run()

# Check results
variables = runtime.get_all_variables()
print(f"\nFinal variables:")
for var in variables:
    print(f"  {var['name']} = {var['value']}")

# Verify
x_var = [v for v in variables if v['name'].lower() == 'x']
y_var = [v for v in variables if v['name'].lower() == 'y']

if x_var and y_var:
    if x_var[0]['value'] == 5 and y_var[0]['value'] == 15:
        print("\n✅ SUCCESS: Variables computed correctly")
        sys.exit(0)
    else:
        print(f"\n❌ FAIL: Expected X=5, Y=15, got X={x_var[0]['value']}, Y={y_var[0]['value']}")
        sys.exit(1)
else:
    print("\n❌ FAIL: Variables not found")
    sys.exit(1)
