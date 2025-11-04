#!/usr/bin/env python3
"""Test that we can parse src/interactive.py without errors"""

import sys
import os
import json
import re

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path

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
    return None

# Test with the actual response format that was failing
test_response = '''```json
[
  {
    "type": "comment_outdated",
    "line": 18,
    "code_snippet": "try:\\n    import readline\\n    READLINE_AVAILABLE = True\\nexcept ImportError:\\n    READLINE_AVAILABLE = False",
    "comment": "Try to import readline for better line editing\\nThis enhances input() with:\\n- Backspace/Delete working properly\\n- Arrow keys for navigation\\n- Command history (up/down arrows)\\n- Ctrl+A (start of line), Ctrl+E (end of line)\\n- Emacs keybindings (Ctrl+K, Ctrl+U, etc.)",
    "explanation": "The comment mentions Ctrl+A as 'start of line', but looking at line 174, Ctrl+A is explicitly rebound to insert a literal character for edit mode, not for start of line functionality.",
    "suggested_fix": "Update comment to clarify that Ctrl+A behavior is overridden for edit mode later in the code"
  }
]
```'''

print("Testing JSON parsing with markdown-wrapped response...")
result = parse_json_response(test_response)

if result is not None:
    print(f"✓ SUCCESS!")
    print(f"Parsed {len(result)} conflict(s)")
    for i, conflict in enumerate(result, 1):
        print(f"\nConflict {i}:")
        print(f"  Type: {conflict.get('type')}")
        print(f"  Line: {conflict.get('line')}")
        print(f"  Explanation: {conflict.get('explanation')[:100]}...")
else:
    print("✗ FAILED: Could not parse")
    sys.exit(1)
