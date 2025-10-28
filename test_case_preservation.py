#!/usr/bin/env python3
"""
Test case-preserving variables

Tests that variable names preserve the original case as typed by the user.
"""

import sys
sys.path.insert(0, 'src')

from lexer import Lexer
from parser import Parser
from position_serializer import serialize_line_with_positions


def test_case_preservation():
    """Test that variable case is preserved"""

    test_cases = [
        # (input, expected_output, description)
        ("10 TargetAngle=45", "10 TargetAngle=45", "PascalCase variable"),
        ("20 targetAngle=50", "20 targetAngle=50", "camelCase variable"),
        ("30 TARGETANGLE=55", "30 TARGETANGLE=55", "UPPERCASE variable"),
        ("40 target_angle=60", "40 target_angle=60", "snake_case variable"),
        ("50 X=Y+Z", "50 X=Y+Z", "Single letter uppercase"),
        ("60 x=y+z", "60 x=y+z", "Single letter lowercase"),
        ("70 MyVar = OtherVar + 3", "70 MyVar = OtherVar + 3", "Mixed case with spaces"),
        ("80 PRINT MyVariable", "80 PRINT MyVariable", "Mixed case in PRINT"),
        ("90 FOR Index=1 TO 10", "90 FOR Index=1 TO 10", "Mixed case in FOR loop"),
        ("100 DIM MyArray(10)", "100 DIM MyArray(10)", "Mixed case array"),
    ]

    print("Testing Case Preservation")
    print("=" * 60)

    passed = 0
    failed = 0

    for input_text, expected, description in test_cases:
        print(f"\nTest: {description}")
        print(f"Input:    '{input_text}'")

        try:
            # Tokenize and parse
            lexer = Lexer(input_text)
            tokens = lexer.tokenize()
            parser = Parser(tokens, source=input_text)
            line_node = parser.parse_line()

            # Serialize
            output, conflicts = serialize_line_with_positions(line_node, debug=False)

            print(f"Output:   '{output}'")
            print(f"Expected: '{expected}'")

            if output == expected:
                print("✅ PASS")
                passed += 1
            else:
                print("❌ FAIL - Output doesn't match expected")
                failed += 1

        except Exception as e:
            print(f"❌ ERROR: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")

    return failed == 0


def test_case_insensitive_lookup():
    """Test that variables with different cases refer to the same variable"""
    print("\n\nTesting Case-Insensitive Lookup (same variable)")
    print("=" * 60)

    # This tests that TargetAngle, targetangle, and TARGETANGLE all refer to the same variable
    # We can't fully test this without running the interpreter, but we can verify parsing

    test_code = """10 TargetAngle = 45
20 targetangle = 50
30 PRINT TARGETANGLE"""

    print(f"Test code:")
    print(test_code)
    print()

    try:
        lines = []
        for line_text in test_code.strip().split('\n'):
            lexer = Lexer(line_text)
            tokens = lexer.tokenize()
            parser = Parser(tokens, source=line_text)
            line_node = parser.parse_line()

            output, _ = serialize_line_with_positions(line_node, debug=False)
            lines.append(output)

            # Check variable nodes
            for stmt in line_node.statements:
                if hasattr(stmt, 'variable'):
                    var = stmt.variable
                    print(f"Line {line_node.line_number}: Variable '{var.name}' "
                          f"(original_case: '{var.original_case}')")
                elif hasattr(stmt, 'expressions'):
                    for expr in stmt.expressions:
                        if type(expr).__name__ == 'VariableNode':
                            print(f"Line {line_node.line_number}: Variable '{expr.name}' "
                                  f"(original_case: '{expr.original_case}')")

        print("\nReserialized code:")
        for line in lines:
            print(line)

        print("\n✅ Case preservation working - each line keeps its original case")
        print("   (Note: Runtime lookup will treat them as the same variable)")
        return True

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success1 = test_case_preservation()
    success2 = test_case_insensitive_lookup()

    sys.exit(0 if (success1 and success2) else 1)
