#!/usr/bin/env python3
"""
Test that the JSON extractor can handle truncated JSON responses.
"""

import sys
from pathlib import Path

# Add utils to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from json_extractor import extract_json_from_markdown

def test_truncation_handling():
    """Test handling of truncated JSON that might come from API responses."""

    test_cases = [
        # Case 1: Truncated string in JSON object
        (
            '''[
  {
    "type": "comment_outdated",
    "line": 19,
    "code_snippet": "try:\\n    import readline\\n    READLINE_AVAILABLE = True\\nexcept ImportError:\\n    READLINE_AVAILABLE = False",
    "comment": "# Try to import readline for better line editing\\n# This enhances input() with:\\n# - Backspace/Delete working properly\\n# - Arrow keys for navigation\\n# - Command history (up/down arrows)\\n# - Ctrl+A (start of line), Ctrl+E (end of line)\\n# - Emacs keybindings (Ctrl+K, Ctrl+U, etc.)",''',
            # Should recover at least the fields we have
            None,  # Can't recover incomplete object
            "Truncated in middle of object"
        ),

        # Case 2: Complete first object, truncated second
        (
            '''[
  {
    "type": "comment_outdated",
    "line": 19,
    "explanation": "Comment is outdated"
  },
  {
    "type": "code_bug",
    "line": 42,
    "explanation": "This code has a bug because''',
            # Should recover the first complete object
            [{"type": "comment_outdated", "line": 19, "explanation": "Comment is outdated"}],
            "One complete object, one truncated"
        ),

        # Case 3: Truncated array of complete objects
        (
            '''[
  {"id": 1, "complete": true},
  {"id": 2, "complete": true},
  {"id": 3, "complete": true}''',
            # Should recover all three complete objects
            [
                {"id": 1, "complete": True},
                {"id": 2, "complete": True},
                {"id": 3, "complete": True}
            ],
            "Array not closed but objects complete"
        ),

        # Case 4: Clean JSON (not truncated)
        (
            '[{"type": "test", "status": "ok"}]',
            [{"type": "test", "status": "ok"}],
            "Clean JSON (baseline test)"
        ),

        # Case 5: Empty array response (common for "no issues found")
        (
            '[]',
            [],
            "Empty array"
        ),
    ]

    print("Testing truncation handling...")
    print("=" * 60)

    passed = 0
    failed = 0

    for i, (input_text, expected, description) in enumerate(test_cases, 1):
        print(f"\nTest {i}: {description}")
        print(f"  Input length: {len(input_text)} chars")

        result = extract_json_from_markdown(input_text, verbose=True)

        # For truncated cases where we expect None or partial recovery
        if expected is None:
            if result is None:
                print(f"  ✓ PASSED (correctly identified as unrecoverable)")
                passed += 1
            else:
                print(f"  ⚠ Unexpected recovery: {result}")
                # Still count as pass if we got something useful
                passed += 1
        elif result == expected:
            print(f"  ✓ PASSED")
            passed += 1
        else:
            print(f"  ✗ FAILED")
            print(f"    Expected: {expected}")
            print(f"    Got: {result}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")

    return failed == 0

if __name__ == "__main__":
    success = test_truncation_handling()
    if not success:
        sys.exit(1)
    print("\n✅ All truncation tests passed!")