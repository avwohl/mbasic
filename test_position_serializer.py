#!/usr/bin/env python3
"""
Test position-based serialization

Tests that spacing is preserved when serializing AST back to source.
"""

import sys
sys.path.insert(0, 'src')

from lexer import Lexer
from parser import Parser
from position_serializer import serialize_line_with_positions


def test_spacing_preservation():
    """Test that various spacing styles are preserved"""

    test_cases = [
        # (input, expected_output, description)
        ("10 X=Y+3", "10 X=Y+3", "Compact spacing"),
        ("10 X = Y + 3", "10 X = Y + 3", "Spacious spacing"),
        ("10 X= Y +3", "10 X= Y +3", "Mixed spacing"),
        ("10 X=Y", "10 X=Y", "Simple assignment"),
        ("20 PRINT X", "20 PRINT X", "PRINT statement"),
        ("30 FOR I=1 TO 10", "30 FOR I=1 TO 10", "FOR loop"),
        ("40 IF X>5 THEN PRINT X", "40 IF X>5 THEN PRINT X", "IF statement"),
    ]

    print("Testing Position-Based Serialization")
    print("=" * 60)

    passed = 0
    failed = 0

    for input_text, expected, description in test_cases:
        print(f"\nTest: {description}")
        print(f"Input:    '{input_text}'")

        # Tokenize and parse the line
        try:
            lexer = Lexer(input_text)
            tokens = lexer.tokenize()
            parser = Parser(tokens, source=input_text)  # Pass source for source_text preservation
            line_node = parser.parse_line()
        except Exception as e:
            print(f"❌ PARSE FAILED: {e}")
            failed += 1
            continue

        # Serialize with position preservation
        output, conflicts = serialize_line_with_positions(line_node, debug=True)

        print(f"Output:   '{output}'")
        print(f"Expected: '{expected}'")

        # Check if output matches expected
        if output == expected:
            print("✅ PASS")
            passed += 1
        else:
            print("❌ FAIL - Output doesn't match expected")
            failed += 1

        # Report any position conflicts
        if conflicts:
            print(f"⚠️  Position conflicts detected: {len(conflicts)}")
            for conflict in conflicts:
                print(f"   {conflict}")

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
    basic_dir = Path("basic")
    if not basic_dir.exists():
        print("❌ basic/ directory not found")
        return False

    bas_files = list(basic_dir.rglob("*.bas"))
    print(f"Found {len(bas_files)} .bas files")

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

    if unchanged_count == len(bas_files):
        print("\n🎉 Perfect! All files preserved exactly!")
        return True
    else:
        percent_unchanged = (unchanged_count / len(bas_files)) * 100 if bas_files else 0
        print(f"\n📈 {percent_unchanged:.1f}% of files preserved exactly")
        return False


if __name__ == "__main__":
    success1 = test_spacing_preservation()
    test_conflict_detection()
    success2 = test_all_games()

    sys.exit(0 if (success1 and success2) else 1)
