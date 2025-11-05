#!/usr/bin/env python3
"""
Test utility for check_docs_consistency2.py - single file mode.

This allows you to test the consistency checker on a single file without
running the full hours-long scan.

Usage:
    python3 utils/test_consistency_single_file.py <file_path>

Example:
    python3 utils/test_consistency_single_file.py src/pc.py
"""

import os
import sys
import json
from pathlib import Path

# Add utils to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from json_extractor import extract_json_from_markdown

try:
    import anthropic
except ImportError:
    print("Error: anthropic package not installed")
    print("Run: pip install anthropic")
    sys.exit(1)


def test_single_file(filepath: str):
    """Test the consistency checker on a single file."""

    # Check API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        sys.exit(1)

    # Verify file exists
    file_path = Path(filepath)
    if not file_path.exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    # Read file content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    print(f"Testing consistency checker on: {filepath}")
    print(f"File size: {len(content)} bytes")
    print("="*60)

    # Prepare prompt (same as in check_docs_consistency2.py)
    prompt = f"""Analyze this Python file for conflicts between code and comments.
Look for:
1. Comments that describe behavior different from what the code actually does
2. Outdated comments from refactoring where code changed but comments didn't
3. Comments that are correct but the code has a bug
4. Docstrings that don't match function/class behavior
5. TODO/FIXME comments that may have been addressed but not removed

File: {filepath}

```python
{content}
```

For each conflict found, return a JSON object with:
- "type": "code_bug" or "comment_outdated" or "unclear" (if you can't determine which)
- "line": approximate line number
- "code_snippet": the relevant code (escape newlines as \\n, tabs as \\t, quotes as \\")
- "comment": the conflicting comment/docstring (escape newlines as \\n)
- "explanation": why they conflict
- "suggested_fix": your recommendation (or "NEEDS_HUMAN_REVIEW" if unclear)

Return a JSON array of conflicts. Return empty array [] if no conflicts found.
IMPORTANT: If you cannot determine whether the code or comment is correct, mark type as "unclear" and suggested_fix as "NEEDS_HUMAN_REVIEW".

CRITICAL JSON FORMAT REQUIREMENTS:
- Return ONLY valid JSON - test it before returning
- In string values: escape newlines as \\n, tabs as \\t, quotes as \\"
- Example: "code_snippet": "if x:\\n    print(\\"hello\\")"
- Return ONLY the raw JSON array starting with [ and ending with ]
- DO NOT wrap the JSON in markdown code blocks (no ``` or ```json)
- No markdown formatting whatsoever
- No explanatory text before or after the JSON
- Just the pure, valid JSON array text"""

    # Make API call
    print("\nSending request to Claude API...")
    try:
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=4000,
            temperature=0,
            messages=[{"role": "user", "content": prompt}]
        )
        response_text = response.content[0].text.strip()
    except Exception as e:
        print(f"Error calling API: {e}")
        sys.exit(1)

    print("\nReceived response from Claude API")
    print("="*60)
    print("RAW RESPONSE:")
    print(response_text)
    print("="*60)

    # Try to parse JSON using the robust extractor
    print("\nAttempting to extract JSON...")
    result = extract_json_from_markdown(response_text, verbose=True)

    if result is not None:
        print("\n✓ Successfully extracted JSON!")
        print("="*60)
        print("PARSED RESULT:")
        print(json.dumps(result, indent=2))

        if isinstance(result, list):
            print(f"\nFound {len(result)} conflict(s)")
            if len(result) > 0:
                print("\nConflicts:")
                for i, conflict in enumerate(result, 1):
                    print(f"\n  {i}. {conflict.get('type', 'unknown')}")
                    print(f"     Line: {conflict.get('line', 'N/A')}")
                    print(f"     {conflict.get('explanation', 'No explanation')}")
    else:
        print("\n✗ Failed to extract valid JSON from response")
        print("\nThis is the problem that needs to be fixed!")

    print("\n" + "="*60)
    print("Test complete")


def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python3 utils/test_consistency_single_file.py <file_path>")
        print("\nExample:")
        print("  python3 utils/test_consistency_single_file.py src/pc.py")
        sys.exit(1)

    test_single_file(sys.argv[1])


if __name__ == "__main__":
    main()
