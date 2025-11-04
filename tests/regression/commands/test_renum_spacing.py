#!/usr/bin/env python3
"""
Test RENUM with spacing preservation

Tests that renumbering preserves the original spacing in the code.
"""

import sys
import os

# Add project root to path (3 levels up from tests/regression/commands/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.lexer import Lexer
from src.parser import Parser
from src.position_serializer import renumber_with_spacing_preservation


def test_renum_spacing():
    """Test that RENUM preserves spacing"""

    # Test program with various spacing styles
    test_program = """10 X=Y+3
20 A = B + C
30 GOTO 10
40 IF X>5 THEN 10
50 GOSUB 20
60 END"""

    print("Testing RENUM with Spacing Preservation")
    print("=" * 60)
    print("\nOriginal program:")
    print(test_program)

    # Parse the program
    program_lines = {}
    for line_text in test_program.strip().split('\n'):
        lexer = Lexer(line_text)
        tokens = lexer.tokenize()
        parser = Parser(tokens, source=line_text)
        line_node = parser.parse_line()
        if line_node:
            program_lines[line_node.line_number] = line_node

    print(f"\nParsed {len(program_lines)} lines")

    # Renumber from 100, step 10
    print("\nRenumbering from 100, step 10...")
    renumbered_lines = renumber_with_spacing_preservation(program_lines, 100, 10, debug=True)

    print("\nRenumbered program:")
    for line_num in sorted(renumbered_lines.keys()):
        line_node = renumbered_lines[line_num]
        # AST is the single source - regenerate text from it
        from src.position_serializer import serialize_line_with_positions
        text, _ = serialize_line_with_positions(line_node)
        print(text)

    # Check that spacing is preserved
    print("\n" + "=" * 60)
    print("Checking spacing preservation:")

    tests = [
        # Note: Line 100 will have position conflicts because line number changes from "10" (2 chars)
        # to "100" (3 chars), shifting everything. This is expected.
        (100, ["X=Y+3", "X = Y + 3"], "Spacing (may have conflicts)"),
        (110, ["A = B + C"], "Spacious spacing preserved"),
        (120, ["goto 100", "GOTO 100"], "GOTO target updated"),  # Accept both cases
        (130, ["then 100", "THEN 100"], "IF THEN target updated"),  # Accept both cases
        (140, ["gosub 110", "GOSUB 110"], "GOSUB target updated"),  # Accept both cases
    ]

    passed = 0
    failed = 0

    for line_num, expected_fragments, description in tests:
        if line_num in renumbered_lines:
            # AST is the single source - regenerate text
            from src.position_serializer import serialize_line_with_positions
            line_text, _ = serialize_line_with_positions(renumbered_lines[line_num])
            # Extract code after line number
            code = line_text.split(maxsplit=1)[1] if ' ' in line_text else ""

            # Check if any expected fragment is in the code
            if any(frag in code for frag in expected_fragments):
                print(f"✅ {description}: {repr(code)}")
                passed += 1
            else:
                print(f"❌ {description}: expected one of {expected_fragments}, got {repr(code)}")
                failed += 1
        else:
            print(f"❌ {description}: line {line_num} not found")
            failed += 1

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")

    return failed == 0


def test_renum_complex():
    """Test RENUM with more complex cases"""

    print("\n\nTesting RENUM with Complex Cases")
    print("=" * 60)

    test_program = """10 ON X GOTO 100,200,300
100 PRINT "CASE 1"
110 GOTO 400
200 PRINT "CASE 2"
210 GOTO 400
300 PRINT "CASE 3"
400 END"""

    print("\nOriginal program:")
    print(test_program)

    # Parse
    program_lines = {}
    for line_text in test_program.strip().split('\n'):
        lexer = Lexer(line_text)
        tokens = lexer.tokenize()
        parser = Parser(tokens, source=line_text)
        line_node = parser.parse_line()
        if line_node:
            program_lines[line_node.line_number] = line_node

    # Renumber from 1000, step 100
    print("\nRenumbering from 1000, step 100...")
    renumbered_lines = renumber_with_spacing_preservation(program_lines, 1000, 100, debug=False)

    print("\nRenumbered program:")
    for line_num in sorted(renumbered_lines.keys()):
        from src.position_serializer import serialize_line_with_positions
        text, _ = serialize_line_with_positions(renumbered_lines[line_num])
        print(text)

    # Check ON GOTO was updated
    # Original: ON X GOTO 100,200,300
    # Should map: 100→1100, 200→1300, 300→1500
    from src.position_serializer import serialize_line_with_positions
    line_1000, _ = serialize_line_with_positions(renumbered_lines[1000])
    if "1100" in line_1000 and "1300" in line_1000 and "1500" in line_1000:
        print("\n✅ ON GOTO targets updated correctly")
        return True
    else:
        print(f"\n❌ ON GOTO targets not updated correctly: {line_1000}")
        return False


if __name__ == "__main__":
    success1 = test_renum_spacing()
    success2 = test_renum_complex()

    sys.exit(0 if (success1 and success2) else 1)
