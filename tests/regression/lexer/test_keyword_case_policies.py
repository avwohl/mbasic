#!/usr/bin/env python3
"""Test keyword case handling policies"""

import sys
import os

# Add src directory to path (go up 3 levels: lexer -> regression -> tests -> root)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.lexer import Lexer
from src.parser import Parser
from src.position_serializer import PositionSerializer
from src.keyword_case_manager import KeywordCaseManager

# Test program
test_code = """10 PRINT "Test"
20 FOR I = 1 TO 3
30   IF I = 2 THEN PRINT "Two"
40 NEXT I
50 END
"""

def test_policy(policy_name):
    print(f"\n=== Testing policy: {policy_name} ===")

    # Create keyword case manager with policy
    keyword_case_manager = KeywordCaseManager(policy=policy_name)

    # Lexer builds keyword case table during tokenization
    lexer = Lexer(test_code, keyword_case_manager=keyword_case_manager)
    tokens = lexer.tokenize()

    # Parser uses the keyword case manager from lexer
    parser = Parser(tokens, keyword_case_manager=keyword_case_manager)
    program = parser.parse_program()

    # Serialize using the keyword case manager
    serializer = PositionSerializer(debug=False, keyword_case_manager=keyword_case_manager)

    # Print each line
    for line_node in program.lines:
        serialized, conflicts = serializer.serialize_line(line_node)
        print(serialized)
        serializer.reset()  # Reset for next line

# Test all policies
policies = [
    "force_lower",
    "force_upper",
    "force_capitalize",
    "first_wins",
    "preserve"
]

for policy in policies:
    test_policy(policy)

print("\n=== Test Complete ===")
