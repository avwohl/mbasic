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
```'''
]

def parse_json_response(response_text):
    """Robust JSON parsing that handles markdown code blocks."""
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

    # If still can't parse, show what we got
    print(f"Warning: Could not parse Claude's response")
    if len(response_text) < 200:
        print(f"  Response was: {response_text}")
    else:
        print(f"  Response started with: {response_text[:200]}...")
    return None

# Test all cases
for i, test_case in enumerate(test_cases, 1):
    print(f"\n=== Test Case {i} ===")
    print(f"Input: {test_case[:50]}..." if len(test_case) > 50 else f"Input: {test_case}")
    result = parse_json_response(test_case)
    if result is not None:
        print(f"✓ SUCCESS: Parsed as {result}")
    else:
        print(f"✗ FAILED: Could not parse")
