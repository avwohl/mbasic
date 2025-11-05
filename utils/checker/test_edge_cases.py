#!/usr/bin/env python3
"""
Test edge cases for the JSON extractor to ensure robustness.
"""

import sys
from pathlib import Path

# Add utils to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from json_extractor import extract_json_from_markdown


def test_edge_cases():
    """Test various edge cases that might occur with Claude API responses."""

    test_cases = [
        # Case 1: Response with metadata prefix
        (
            "Here's what I found:\n```json\n[{\"issue\": \"test\"}]\n```",
            [{"issue": "test"}],
            "Metadata prefix with markdown"
        ),

        # Case 2: Response with trailing comma
        (
            '[{"a": 1, "b": 2,}]',
            [{"a": 1, "b": 2}],
            "Trailing comma in JSON"
        ),

        # Case 3: Response that says "no issues"
        (
            "I analyzed the code and found no conflicts or issues.",
            None,
            "Plain text saying no issues"
        ),

        # Case 4: Markdown without closing backticks
        (
            '```json\n[{"incomplete": "markdown"}]',
            [{"incomplete": "markdown"}],
            "Missing closing backticks"
        ),

        # Case 5: Multiple JSON blocks (should get first)
        (
            'First: ```json\n[{"first": 1}]\n```\nSecond: ```json\n[{"second": 2}]\n```',
            [{"first": 1}],
            "Multiple JSON blocks"
        ),

        # Case 6: JSON with escaped characters
        (
            '[{"text": "Line 1\\nLine 2\\tTabbed", "quote": "\\"quoted\\""}]',
            [{"text": "Line 1\nLine 2\tTabbed", "quote": "\"quoted\""}],
            "Escaped characters in JSON"
        ),

        # Case 7: Empty array
        (
            "[]",
            [],
            "Empty JSON array"
        ),

        # Case 8: Markdown with extra spaces
        (
            "```json  \n  [  {  \"spaced\"  :  true  }  ]  \n  ```",
            [{"spaced": True}],
            "Extra spaces in JSON"
        ),

        # Case 9: Response with explanation after JSON
        (
            '```json\n[{"found": "issue"}]\n```\nThis means there is a problem.',
            [{"found": "issue"}],
            "Explanation after JSON"
        ),

        # Case 10: Mixed content with embedded JSON
        (
            'The analysis found the following: [{"embedded": true}] in the code.',
            [{"embedded": True}],
            "JSON embedded in sentence"
        ),
    ]

    print("Testing edge cases for JSON extractor...")
    print("=" * 60)

    passed = 0
    failed = 0

    for i, (input_text, expected, description) in enumerate(test_cases, 1):
        print(f"\nTest {i}: {description}")
        print(f"  Input: {input_text[:60]}...")

        result = extract_json_from_markdown(input_text, verbose=False)

        if result == expected:
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
    success = test_edge_cases()
    if not success:
        sys.exit(1)
    print("\n✅ All edge case tests passed!")