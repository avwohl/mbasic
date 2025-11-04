#!/usr/bin/env python3
"""Test CSE with function calls"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from lexer import tokenize
from parser import Parser
from semantic_analyzer import SemanticAnalyzer

test_program = """
10 X = 5
20 F1 = SQR(X)
30 F2 = SQR(X) + 1
40 F3 = SQR(X) - 1
50 END
"""

print("Testing CSE with function calls...")
tokens = tokenize(test_program)
parser = Parser(tokens)
program = parser.parse()

analyzer = SemanticAnalyzer()
success = analyzer.analyze(program)

print(analyzer.get_report())
