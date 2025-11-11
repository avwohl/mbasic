#!/usr/bin/env python3
"""Debug script to check how logical operators are parsed"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.lexer import tokenize
from src.parser import Parser

test_program = """
10 IF A = 1 AND B = 2 THEN LET C = 3
20 IF A = 1 OR B = 2 THEN LET D = 4
30 IF NOT A = 1 THEN LET E = 5
"""

print("Tokenizing...")
tokens = tokenize(test_program)
print(f"Tokens: {len(tokens)}")

print("\nParsing...")
parser = Parser(tokens)
ast = parser.parse()

print("\nAST structure:")
for line in ast.lines:
    print(f"Line {line.line_number}:")
    for stmt in line.statements:
        print(f"  Statement type: {type(stmt).__name__}")
        if hasattr(stmt, 'condition'):
            print(f"  Condition type: {type(stmt.condition).__name__}")
            if hasattr(stmt.condition, 'operator'):
                print(f"  Operator: {stmt.condition.operator}")
            if hasattr(stmt.condition, 'left'):
                print(f"  Left: {type(stmt.condition.left).__name__}")
            if hasattr(stmt.condition, 'right'):
                print(f"  Right: {type(stmt.condition.right).__name__}")