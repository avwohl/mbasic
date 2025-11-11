#!/usr/bin/env python3
"""Debug script to check code generation for logical operators"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.lexer import tokenize
from src.parser import Parser
from src.semantic_analyzer import SemanticAnalyzer
from src.codegen_backend import Z88dkCBackend

test_program = """
10 IF A% < B% AND B% < C% THEN LET D% = 1 ELSE LET D% = 0
"""

print("Processing:", test_program.strip())
print()

# Tokenize
tokens = tokenize(test_program)

# Parse
parser = Parser(tokens)
ast = parser.parse()

# Semantic analysis
analyzer = SemanticAnalyzer()
analyzer.analyze(ast)

# Code generation
backend = Z88dkCBackend(analyzer.symbols)
output = backend.generate(ast)

print("Generated code:")
print(output)