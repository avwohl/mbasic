#!/usr/bin/env python3
"""
Robust JSON extractor that handles markdown-wrapped responses from Claude API.

This module provides functions to extract valid JSON from text that may contain:
- Markdown code blocks (```json ... ```)
- Explanatory text before/after JSON
- Mixed content with embedded JSON
"""

import json
import re
from typing import Optional, Any


def extract_json_from_markdown(text: str, verbose: bool = False) -> Optional[Any]:
    """
    Extract and parse JSON from text that may contain markdown or other content.

    Tries multiple strategies in order:
    1. Direct JSON parsing (if already clean)
    2. Extract from markdown code blocks (```json ... ```)
    3. Extract from plain code blocks (``` ... ```)
    4. Find JSON array/object anywhere in text
    5. Strip common prefixes/suffixes and retry

    Args:
        text: Text that may contain JSON (possibly with markdown)
        verbose: If True, print debug information

    Returns:
        Parsed JSON object/array, or None if extraction failed
    """
    if not text:
        return None

    original_text = text
    text = text.strip()

    # Strategy 1: Try direct parsing first
    try:
        result = json.loads(text)
        if verbose:
            print("✓ Direct JSON parsing succeeded")
        return result
    except json.JSONDecodeError:
        pass

    # Strategy 2: Extract from markdown code blocks with language tag
    # Pattern: ```json\n ... \n```
    markdown_json_pattern = r'^```json\s*\n(.*?)\n```\s*$'
    match = re.search(markdown_json_pattern, text, re.DOTALL | re.MULTILINE)
    if match:
        json_text = match.group(1).strip()
        try:
            result = json.loads(json_text)
            if verbose:
                print("✓ Extracted from ```json block")
            return result
        except json.JSONDecodeError as e:
            if verbose:
                print(f"  Failed to parse JSON from ```json block: {e}")

    # Strategy 3: Extract from plain markdown code blocks
    # Pattern: ```\n ... \n```
    markdown_plain_pattern = r'^```\s*\n(.*?)\n```\s*$'
    match = re.search(markdown_plain_pattern, text, re.DOTALL | re.MULTILINE)
    if match:
        json_text = match.group(1).strip()
        try:
            result = json.loads(json_text)
            if verbose:
                print("✓ Extracted from ``` block")
            return result
        except json.JSONDecodeError as e:
            if verbose:
                print(f"  Failed to parse JSON from ``` block: {e}")

    # Strategy 4: Look for markdown blocks anywhere in text (not just start/end)
    # This handles cases where there's explanatory text before/after
    all_json_blocks = re.findall(r'```(?:json)?\s*\n(.*?)\n```', text, re.DOTALL)
    for block in all_json_blocks:
        block = block.strip()
        try:
            result = json.loads(block)
            if verbose:
                print("✓ Extracted from embedded markdown block")
            return result
        except json.JSONDecodeError:
            continue

    # Strategy 5: Find JSON array/object patterns anywhere in text
    # Look for [ ... ] or { ... }
    # This is more aggressive and handles "Here are the results: [...]"

    # Try to find array first
    array_pattern = r'(\[[\s\S]*\])'
    array_matches = re.findall(array_pattern, text)
    for json_candidate in array_matches:
        json_candidate = json_candidate.strip()
        try:
            result = json.loads(json_candidate)
            # Verify it's actually a list or dict (not just valid JSON like a number)
            if isinstance(result, (list, dict)):
                if verbose:
                    print("✓ Extracted JSON array from text")
                return result
        except json.JSONDecodeError:
            continue

    # Try to find object
    object_pattern = r'(\{[\s\S]*\})'
    object_matches = re.findall(object_pattern, text)
    for json_candidate in object_matches:
        json_candidate = json_candidate.strip()
        try:
            result = json.loads(json_candidate)
            if isinstance(result, (list, dict)):
                if verbose:
                    print("✓ Extracted JSON object from text")
                return result
        except json.JSONDecodeError:
            continue

    # Strategy 6: Remove common markdown/text prefixes and try again
    # Remove lines that don't look like JSON
    lines = text.split('\n')

    # Find first line that looks like JSON start
    start_idx = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('[') or stripped.startswith('{'):
            start_idx = i
            break

    # Find last line that looks like JSON end
    end_idx = None
    for i in range(len(lines) - 1, -1, -1):
        stripped = lines[i].strip()
        if stripped.endswith(']') or stripped.endswith('}'):
            end_idx = i
            break

    if start_idx is not None and end_idx is not None and start_idx <= end_idx:
        json_text = '\n'.join(lines[start_idx:end_idx+1])
        try:
            result = json.loads(json_text)
            if isinstance(result, (list, dict)):
                if verbose:
                    print("✓ Extracted by trimming non-JSON lines")
                return result
        except json.JSONDecodeError:
            pass

    # All strategies failed
    if verbose:
        print("✗ All extraction strategies failed")
        print(f"Text preview: {original_text[:300]}...")

    return None


def test_extractor():
    """Test the JSON extractor with various inputs."""

    test_cases = [
        # Case 1: Clean JSON
        ('[]', []),

        # Case 2: JSON with markdown block
        ('```json\n[{"foo": "bar"}]\n```', [{"foo": "bar"}]),

        # Case 3: JSON with plain markdown block
        ('```\n[{"test": 123}]\n```', [{"test": 123}]),

        # Case 4: JSON with explanatory text
        ('Here are the results:\n```json\n[{"id": 1}]\n```\nHope this helps!',
         [{"id": 1}]),

        # Case 5: JSON embedded in text without markdown
        ('The analysis found: [{"type": "error", "line": 42}] in the code.',
         [{"type": "error", "line": 42}]),

        # Case 6: Multiple JSON blocks (should get first valid one)
        ('Invalid: [broken\nValid: ```json\n[{"ok": true}]\n```',
         [{"ok": True}]),

        # Case 7: Markdown with extra whitespace
        ('```json\n\n  [{"x": 1}]  \n\n```', [{"x": 1}]),

        # Case 8: Text that starts with ```json
        ('```json\n[{"bug": "code_bug"}]', [{"bug": "code_bug"}]),
    ]

    print("Testing JSON extractor...")
    passed = 0
    failed = 0

    for i, (input_text, expected) in enumerate(test_cases, 1):
        print(f"\nTest {i}:")
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

    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    success = test_extractor()
    exit(0 if success else 1)
