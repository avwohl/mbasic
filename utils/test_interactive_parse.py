#!/usr/bin/env python3
"""Test parsing interactive.py with Claude API"""

import os
import sys
import json

try:
    import anthropic
except ImportError:
    print("Error: anthropic package not installed")
    sys.exit(1)

api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    print("Error: ANTHROPIC_API_KEY not set")
    sys.exit(1)

client = anthropic.Anthropic(api_key=api_key)

# Read the file
with open('/home/wohl/cl/mbasic/src/interactive.py', 'r') as f:
    content = f.read()

prompt = f"""Analyze this Python source code file for documentation/comment inconsistencies.

File: src/interactive.py
Content:
{content}

Please identify any issues where:
1. Comments are outdated or incorrect
2. Docstrings don't match implementation
3. Code contradicts comments

Return your response as a JSON array of issue objects. Each issue should have:
- type: "comment_outdated", "docstring_mismatch", "code_comment_conflict", etc.
- line: line number
- code_snippet: relevant code
- comment: the problematic comment/docstring
- explanation: why it's inconsistent

If no issues found, return an empty array: []

IMPORTANT: Return ONLY valid JSON, no markdown formatting, no code blocks, no explanatory text.
"""

print("Sending request to Claude...")
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=4000,
    messages=[{"role": "user", "content": prompt}]
)

print("\n=== Raw Response ===")
raw_text = response.content[0].text
print(raw_text)

print("\n=== Attempting to parse JSON ===")
try:
    # Try to parse directly
    parsed = json.loads(raw_text)
    print("✓ Successfully parsed JSON directly")
    print(f"Found {len(parsed)} issues")
except json.JSONDecodeError as e:
    print(f"✗ Failed to parse: {e}")

    # Try to strip markdown code blocks
    if raw_text.strip().startswith("```"):
        print("\nTrying to strip markdown code blocks...")
        lines = raw_text.strip().split('\n')
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = '\n'.join(lines)

        try:
            parsed = json.loads(cleaned)
            print("✓ Successfully parsed after stripping markdown")
            print(f"Found {len(parsed)} issues")
        except json.JSONDecodeError as e2:
            print(f"✗ Still failed: {e2}")
            print("\nCleaned content:")
            print(cleaned[:200])
