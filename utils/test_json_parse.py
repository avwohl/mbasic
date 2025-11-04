#!/usr/bin/env python3
"""Test JSON parsing with different Claude response formats"""

import json
import re

# Test cases: various ways Claude might return JSON
test_cases = [
    # Case 1: Clean JSON (what we want)
    '''[
  {
    "type": "comment_outdated",
    "line": 18
  }
]''',

    # Case 2: Wrapped in ```json (the problem case)
    '''```json
[
  {
    "type": "comment_outdated",
    "line": 18
  }
]
```''',

    # Case 3: Just ``` without json
    '''```
[
  {
    "type": "comment_outdated",
    "line": 18
  }
]
```''',

    # Case 4: Extra text before
    '''Here is the JSON:
```json
[
  {
    "type": "comment_outdated",
    "line": 18
  }
]
```''',

    # Case 5: Empty array
    '[]',

    # Case 6: Empty array with markdown
    '''```json
[]
```''',

    # Case 7: JSON with ESCAPED newlines (correct)
    '''```json
[
  {
    "type": "comment_outdated",
    "line": 18,
    "code_snippet": "try:\\n    import readline\\n    READLINE_AVAILABLE = True\\nexcept ImportError:\\n    READLINE_AVAILABLE = False",
    "comment": "# Try to import readline for better line editing",
    "explanation": "The comment says it's for better line editing but doesn't explain what happens if readline is not available"
  }
]
```''',

    # Case 8: JSON with ACTUAL newlines (INCORRECT - malformed JSON)
    '''```json
[
  {
    "type": "comment_outdated",
    "line": 18,
    "code_snippet": "try:
    import readline
    READLINE_AVAILABLE = True
except ImportError:
    READLINE_AVAILABLE = False",
    "comment": "# Try to import readline for better line editing"
  }
]
```''',

    # Case 9: Real-world complex case with multiple fields
    '''```json
[
  {
    "type": "comment_outdated",
    "line": 23,
    "code_snippet": "try:\\n    import readline\\n    READLINE_AVAILABLE = True\\nexcept ImportError:\\n    READLINE_AVAILABLE = False",
    "comment": "# This enhances input() with:\\n# - Backspace/Delete working properly\\n# - Arrow keys for navigation",
    "explanation": "Comment explains features but code doesn't show those features",
    "suggested_fix": "NEEDS_HUMAN_REVIEW"
  },
  {
    "type": "code_bug",
    "line": 45,
    "code_snippet": "if runtime.pc and runtime.pc.line_num:",
    "comment": "Check if we have a program counter",
    "explanation": "Code checks both pc and line_num but comment only mentions pc"
  }
]
```'''
]

def parse_json_response_old(response_text):
    """OLD VERSION - may fail on complex cases"""
    cleaned_text = response_text.strip()

    # Try direct parsing first
    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError:
        pass

    # Try to find JSON array in the text using regex
    # Look for [ ... ] pattern, allowing for markdown blocks
    json_match = re.search(r'(\[[\s\S]*\])', cleaned_text)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    return None

def parse_json_response_new(response_text):
    """NEW VERSION - strips markdown code blocks first"""
    cleaned_text = response_text.strip()

    # Try direct parsing first
    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError:
        pass

    # Strip markdown code blocks first (```json ... ``` or ``` ... ```)
    # Match from start of line to handle multiline blocks
    markdown_stripped = re.sub(r'^```(?:json)?\s*\n', '', cleaned_text, flags=re.MULTILINE)
    markdown_stripped = re.sub(r'\n```\s*$', '', markdown_stripped)

    # Try parsing the stripped version
    try:
        return json.loads(markdown_stripped)
    except json.JSONDecodeError:
        pass

    # Last resort: Look for JSON array in the cleaned (non-markdown) text
    # This handles cases like "Here are the results: [...]"
    json_match = re.search(r'(\[[\s\S]*\])', markdown_stripped)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    return None

# Test all cases with BOTH versions
print("=" * 70)
print("TESTING OLD VERSION (current implementation)")
print("=" * 70)
for i, test_case in enumerate(test_cases, 1):
    print(f"\n=== Test Case {i} ===")
    first_line = test_case.split('\n')[0]
    print(f"Input starts: {first_line[:60]}..." if len(first_line) > 60 else f"Input: {first_line}")
    result = parse_json_response_old(test_case)
    if result is not None:
        print(f"✓ SUCCESS: Parsed {len(result)} item(s)")
    else:
        print(f"✗ FAILED: Could not parse")

print("\n\n" + "=" * 70)
print("TESTING NEW VERSION (proposed fix)")
print("=" * 70)
for i, test_case in enumerate(test_cases, 1):
    print(f"\n=== Test Case {i} ===")
    first_line = test_case.split('\n')[0]
    print(f"Input starts: {first_line[:60]}..." if len(first_line) > 60 else f"Input: {first_line}")
    result = parse_json_response_new(test_case)
    if result is not None:
        print(f"✓ SUCCESS: Parsed {len(result)} item(s)")
    else:
        print(f"✗ FAILED: Could not parse")

print("\n\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print("Test Case 8 intentionally contains malformed JSON (actual newlines")
print("instead of \\n escapes). Both parsers should fail on this case.")
print("This represents Claude returning invalid JSON, which we can't fix.")
