#!/usr/bin/env python3
"""Test with a realistic truncated response."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from json_extractor import extract_json_from_markdown

# Test the actual truncated JSON that was failing
truncated = '''```json
[
  {
    "type": "comment_outdated",
    "line": 19,
    "code_snippet": "try:\\n    import readline\\n    READLINE_AVAILABLE = True\\nexcept ImportError:\\n    READLINE_AVAILABLE = False",
    "comment": "# Try to import readline for better line editing\\n# This enhances input() with:\\n# - Backspace/Delete working properly\\n# - Arrow keys for navigation\\n# - Command history (up/down arrows)\\n# - Ctrl+A (start of line), Ctrl+E (end of line)\\n# - Emacs keybindings (Ctrl+K, Ctrl+U, etc.)",
    "explanation": "Comment describes features but code just imports"
  },
  {
    "type": "code_bug",
    "line": 143,
    "code_snippet": "# incomplete due to truncation'''

print("Testing realistic truncated JSON in markdown...")
result = extract_json_from_markdown(truncated, verbose=True)
print(f"\nResult: {result}")

# Also test clean JSON
clean = '''```json
[
  {
    "type": "comment_outdated",
    "line": 19,
    "explanation": "Test"
  }
]
```'''

print("\n" + "="*60)
print("Testing clean JSON in markdown...")
result2 = extract_json_from_markdown(clean, verbose=False)
print(f"Result: {result2}")