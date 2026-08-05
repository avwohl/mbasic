#!/usr/bin/env python3
"""
Test position-based serialization

Tests that code can be parsed and re-serialized without errors.
Note: Current serializer may normalize spacing (add spaces around operators).
"""

import sys
import os

# Add project root to path (3 levels up from tests/regression/serializer/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.lexer import Lexer
from src.parser import Parser
from src.position_serializer import serialize_line_with_positions


def test_spacing_preservation():
    """Test that code can be serialized without errors"""

    test_cases = [
        # (input, description)
        ("10 X=Y+3", "Compact spacing"),
        ("10 X = Y + 3", "Spacious spacing"),
        ("10 X= Y +3", "Mixed spacing"),
        ("10 X=Y", "Simple assignment"),
        ("20 PRINT X", "PRINT statement"),
        ("30 FOR I=1 TO 10", "FOR loop"),
        ("40 IF X>5 THEN PRINT X", "IF statement"),
    ]

    print("Testing Position-Based Serialization")
    print("=" * 60)

    passed = 0
    failed = 0

    for input_text, description in test_cases:
        print(f"\nTest: {description}")
        print(f"Input:    '{input_text}'")

        # Tokenize and parse the line
        try:
            lexer = Lexer(input_text)
            tokens = lexer.tokenize()
            parser = Parser(tokens, source=input_text)
            line_node = parser.parse_line()
        except Exception as e:
            print(f"❌ PARSE FAILED: {e}")
            failed += 1
            continue

        # Serialize - just verify it doesn't crash
        try:
            output, conflicts = serialize_line_with_positions(line_node, debug=False)
            print(f"Output:   '{output}'")

            # Verify output is valid by re-parsing it
            lexer2 = Lexer(output)
            tokens2 = lexer2.tokenize()
            parser2 = Parser(tokens2)
            line_node2 = parser2.parse_line()

            print("✅ PASS - Serialized code is valid")
            passed += 1

        except Exception as e:
            print(f"❌ FAIL - Serialization error: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")

    return failed == 0


def test_conflict_detection():
    """Test that position conflicts are detected and reported"""

    print("\n\nTesting Position Conflict Detection")
    print("=" * 60)

    # Create a case where position conflict should occur
    # This is tricky - we need to manually construct AST with wrong positions
    # For now, just test that the mechanism works

    input_text = "10 X=Y+3"
    try:
        lexer = Lexer(input_text)
        tokens = lexer.tokenize()
        parser = Parser(tokens, source=input_text)
        line_node = parser.parse_line()
    except Exception as e:
        print(f"❌ Parse failed: {e}")
        return False

    # Serialize with debug enabled
    output, conflicts = serialize_line_with_positions(line_node, debug=True)

    print(f"Input:  '{input_text}'")
    print(f"Output: '{output}'")
    print(f"Conflicts detected: {len(conflicts)}")

    if conflicts:
        print("Conflicts:")
        for conflict in conflicts:
            print(f"  {conflict}")
    else:
        print("No conflicts detected (expected for valid parse)")

    return True


def test_all_games():
    """Test loading all BASIC games and check how many change when reserialized"""
    import os
    import tempfile
    from pathlib import Path

    print("\n\nTesting All BASIC Games")
    print("=" * 60)

    # Find all .bas files
    # Get project root (3 levels up from tests/regression/serializer/)
    project_root = Path(__file__).parent.parent.parent.parent
    basic_dir = project_root / "basic"
    if not basic_dir.exists():
        print(f"❌ basic/ directory not found at {basic_dir}")
        return False

    # basic/dev/bad_syntax/ holds programs that are deliberately broken - the
    # project keeps them so the parser's error handling has something to chew
    # on (see CLAUDE.md: "basic/ (working), basic/bad_syntax/ (broken)").
    # Counting the parser's correct refusal of them as a serializer failure
    # made this number meaningless: 222 of the 229 remaining errors were files
    # that are supposed to fail. They are reported separately below.
    skipped_dirs = {'bad_syntax'}
    all_bas_files = list(basic_dir.rglob("*.bas"))
    bas_files = [f for f in all_bas_files
                 if not skipped_dirs.intersection(f.parts)]
    deliberately_broken = len(all_bas_files) - len(bas_files)
    print(f"Found {len(bas_files)} .bas files "
          f"({deliberately_broken} skipped as deliberately broken)")

    unchanged_count = 0
    changed_count = 0
    error_count = 0

    # Create temp directory for output
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "reserialized"
        output_dir.mkdir()

        for bas_file in bas_files:
            try:
                # Read original
                with open(bas_file, 'r') as f:
                    original_lines = f.readlines()

                # Parse each line
                reserialized_lines = []
                for line_text in original_lines:
                    line_text = line_text.rstrip('\n\r')
                    if not line_text.strip():
                        reserialized_lines.append("")
                        continue

                    lexer = Lexer(line_text)
                    tokens = lexer.tokenize()
                    parser = Parser(tokens, source=line_text)
                    line_node = parser.parse_line()

                    if line_node:
                        serialized, conflicts = serialize_line_with_positions(line_node, debug=False)
                        reserialized_lines.append(serialized)
                    else:
                        reserialized_lines.append(line_text)

                # Write to output
                rel_path = bas_file.relative_to(basic_dir)
                output_file = output_dir / rel_path
                output_file.parent.mkdir(parents=True, exist_ok=True)

                with open(output_file, 'w') as f:
                    # Add trailing newline if original had one
                    content = '\n'.join(reserialized_lines)
                    if original_lines and original_lines[-1].endswith(('\n', '\r')):
                        content += '\n'
                    f.write(content)

                # Compare
                with open(output_file, 'r') as f:
                    reserialized_content = f.read()
                with open(bas_file, 'r') as f:
                    original_content = f.read()

                if original_content == reserialized_content:
                    unchanged_count += 1
                else:
                    changed_count += 1
                    print(f"  ⚠️  CHANGED: {bas_file}")

            except Exception as e:
                error_count += 1
                print(f"  ❌ ERROR in {bas_file}: {e}")

    print("\n" + "=" * 60)
    print(f"Results:")
    print(f"  ✅ Unchanged: {unchanged_count}")
    print(f"  ⚠️  Changed:   {changed_count}")
    print(f"  ❌ Errors:    {error_count}")
    print(f"  📊 Total:     {len(bas_files)}")

    # Success if we can parse and serialize without major errors
    # Note: Spacing may change, which is expected with current serializer
    success_count = unchanged_count + changed_count
    success_rate = (success_count / len(bas_files)) * 100 if bas_files else 0

    if error_count == 0:
        print(f"\n✅ SUCCESS: All {len(bas_files)} files parsed and serialized without errors")
        return True
    elif success_rate >= 95:
        # Was 50%, which passed while 462 of 535 files failed to serialize at
        # all. With the deliberately-broken programs excluded and every
        # statement type serializable, anything below this is a real
        # regression rather than a known gap.
        print(f"\n⚠️  PARTIAL SUCCESS: {success_rate:.1f}% of files processed successfully")
        return True
    else:
        print(f"\n❌ FAIL: Only {success_rate:.1f}% success rate")
        return False



def test_parentheses_survive_serialization():
    """Brackets that change the meaning must come back.

    The AST does not record parentheses - the parser builds the tree they
    imply - so a serializer has to put them back wherever precedence would
    otherwise say something different. It did not, and RENUM wrote the result
    straight into the user's program:

        10 Y=(12*Y0+M)/12       became    10 Y = 12 * Y0 + M / 12

    which is different arithmetic. Silent, and in a documented command.
    """
    from src.ui.ui_helpers import serialize_statement

    print("Testing Parenthesis Preservation")
    print("=" * 60)

    cases = [
        # (source, expected serialization)
        ("10 Y=(12*Y0+M)/12", "Y = (12 * Y0 + M) / 12"),
        ("10 I=(J+K)*(L+M)", "I = (J + K) * (L + M)"),
        ("10 N=O+P*Q", "N = O + P * Q"),           # no brackets needed
        ("10 Q=A+(B+C)", "Q = A + B + C"),         # associative: droppable
        ("10 W=A-(B-C)", "W = A - (B - C)"),       # not associative
        ("10 X=(A-B)-C", "X = A - B - C"),
        ("10 Y=A/(B/C)", "Y = A / (B / C)"),
        ("10 Z=(A/B)/C", "Z = A / B / C"),
        # '^' is right-associative here (2^3^2 is 512), so at equal precedence
        # it is the LEFT operand that has to keep its brackets.
        ("10 R=(S^T)^U", "R = (S ^ T) ^ U"),
        ("10 V=S^(T^U)", "V = S ^ T ^ U"),
        ("10 C=(A<B)*(C>D)", "C = (A < B) * (C > D)"),
        ("10 F=(A OR B) AND C", "F = (A OR B) AND C"),
    ]

    all_passed = True
    for source, expected in cases:
        lexer = Lexer(source)
        parser = Parser(lexer.tokenize(), source=source)
        line_node = parser.parse_line()
        got = serialize_statement(line_node.statements[0])
        ok = got == expected
        if not ok:
            all_passed = False
        print(f"{'✓' if ok else '✗'} {source:24} -> {got}"
              + ("" if ok else f"   (expected: {expected})"))

    print()
    return all_passed


if __name__ == "__main__":
    success1 = test_spacing_preservation()
    test_conflict_detection()
    success2 = test_all_games()
    success3 = test_parentheses_survive_serialization()

    sys.exit(0 if (success1 and success2 and success3) else 1)
