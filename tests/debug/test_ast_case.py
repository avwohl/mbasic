#!/usr/bin/env python3
"""Test AST preserves original_case"""

import sys
sys.path.insert(0, 'src')

from lexer import Lexer
from parser import Parser

program = """
20 TargetAngle = 45
40 targetangle = 90
"""

# Parse
lexer = Lexer(program)
tokens = lexer.tokenize()
parser = Parser(tokens)
ast = parser.parse()

# Check line 20
line20 = [line for line in ast.lines if line.line_number == 20][0]
stmt20 = line20.statements[0]
print(f"Line 20 variable node:")
print(f"  name: {stmt20.variable.name}")
print(f"  original_case: {stmt20.variable.original_case}")

# Check line 40
line40 = [line for line in ast.lines if line.line_number == 40][0]
stmt40 = line40.statements[0]
print(f"\nLine 40 variable node:")
print(f"  name: {stmt40.variable.name}")
print(f"  original_case: {stmt40.variable.original_case}")
