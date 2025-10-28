#!/usr/bin/env python3
"""Test keyword case handling policies"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lexer import Lexer
from parser import Parser
from position_serializer import PositionSerializer

# Test program
test_code = """10 PRINT "Test"
20 FOR I = 1 TO 3
30   IF I = 2 THEN PRINT "Two"
40 NEXT I
50 END
"""

def test_policy(policy_name):
    print(f"\n=== Testing policy: {policy_name} ===")

    # Parse the code with keyword case policy
    lexer = Lexer(test_code)
    tokens = lexer.tokenize()
    parser = Parser(tokens, keyword_case_policy=policy_name)
    program = parser.parse_program()

    # Serialize using the parser's keyword case manager
    serializer = PositionSerializer(debug=False, keyword_case_manager=parser.keyword_case_manager)

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
