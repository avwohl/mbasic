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


def _attempt_json_repair(json_text: str, verbose: bool = False) -> Optional[Any]:
    """
    Attempt to repair truncated JSON by closing open structures.
    This is a last-resort strategy for handling API responses that were cut off.

    Args:
        json_text: Potentially truncated JSON text
        verbose: If True, print debug information

    Returns:
        Parsed JSON if repair was successful, None otherwise
    """
    if not json_text:
        return None

    # Try to parse what we have first to understand where it failed
    try:
        # Find all complete JSON objects in the array
        # If it's an array of objects, try to extract complete ones
        if json_text.strip().startswith('['):
            # Count open braces to find complete objects
            complete_objects = []
            current_obj = ""
            brace_count = 0
            in_string = False
            escape_next = False

            # Skip the opening '['
            text_to_parse = json_text[1:] if json_text.startswith('[') else json_text

            for char in text_to_parse:
                if escape_next:
                    current_obj += char
                    escape_next = False
                    continue

                if char == '\\' and in_string:
                    current_obj += char
                    escape_next = True
                    continue

                if char == '"' and not escape_next:
                    in_string = not in_string
                    current_obj += char
                    continue

                if not in_string:
                    if char == '{':
                        if brace_count == 0:
                            current_obj = char
                        else:
                            current_obj += char
                        brace_count += 1
                    elif char == '}':
                        current_obj += char
                        brace_count -= 1
                        if brace_count == 0:
                            # Try to parse this complete object
                            try:
                                obj = json.loads(current_obj)
                                complete_objects.append(obj)
                                current_obj = ""
                            except:
                                pass  # This object is malformed, skip it
                    else:
                        if current_obj:  # Only add if we're inside an object
                            current_obj += char
                else:
                    current_obj += char

            # If we found any complete objects, return them
            if complete_objects:
                if verbose:
                    print(f"  ✓ Recovered {len(complete_objects)} complete objects from truncated JSON")
                return complete_objects

        # If not an array or couldn't extract objects, try simpler repairs
        # Try closing unclosed strings and structures
        repaired = json_text

        # Count unclosed quotes (rough approximation)
        quote_count = json_text.count('"') - json_text.count('\\"')
        if quote_count % 2 == 1:
            repaired += '"'

        # Close unclosed braces/brackets
        open_braces = json_text.count('{') - json_text.count('}')
        open_brackets = json_text.count('[') - json_text.count(']')

        repaired += '}' * open_braces
        repaired += ']' * open_brackets

        try:
            result = json.loads(repaired)
            if verbose:
                print(f"  ✓ Successfully repaired truncated JSON")
            return result
        except:
            pass

    except Exception as e:
        if verbose:
            print(f"  JSON repair failed: {e}")

    return None


def extract_json_from_markdown(text: str, verbose: bool = False) -> Optional[Any]:
    """
    Extract and parse JSON from text that may contain markdown or other content.

    Tries multiple strategies in order:
    1. Direct JSON parsing (if already clean)
    2. Extract from markdown code blocks (```json ... ```)
    3. Extract from plain code blocks (``` ... ```)
    4. Find JSON array/object anywhere in text
    5. Strip common prefixes/suffixes and retry
    6. Handle metadata prefixes from Claude API

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

    # Strategy 0: Handle common metadata/wrapper patterns from Claude API
    # Sometimes Claude returns metadata before the actual content
    # Look for patterns like "Here's the analysis:" or "I found these issues:"
    # followed by the actual JSON
    metadata_patterns = [
        r'^.*?(?:Here\'s|Here is|I found|Analysis|Results?).*?:\s*\n',
        r'^.*?(?:response|output|result).*?:\s*\n',
    ]

    for pattern in metadata_patterns:
        match = re.match(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            # Remove the metadata prefix and try parsing what's left
            cleaned = text[match.end():]
            if cleaned.strip().startswith('[') or cleaned.strip().startswith('{') or cleaned.strip().startswith('```'):
                if verbose:
                    print(f"  Removed metadata prefix: {match.group()[:50]}...")
                text = cleaned.strip()
                break

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
    # Try multiple patterns to catch various markdown formatting issues
    markdown_patterns = [
        r'```json\s*\n(.*?)\n```',  # Standard ```json block
        r'```json\s*\n(.*?)```',    # Missing newline before closing
        r'```json\s+(.*?)\n```',    # Space instead of newline after opening
        r'```json\s+(.*?)```',      # Space instead of newline, missing newline at close
        r'```\s*\n(.*?)\n```',      # Plain ``` block
        r'```\s*\n(.*?)```',        # Plain ``` block, missing newline at close
    ]

    for pattern in markdown_patterns:
        all_json_blocks = re.findall(pattern, text, re.DOTALL)
        for block in all_json_blocks:
            block = block.strip()
            try:
                result = json.loads(block)
                if isinstance(result, (list, dict)):
                    if verbose:
                        print(f"✓ Extracted from markdown block (pattern: {pattern})")
                    return result
            except json.JSONDecodeError:
                continue

    # Strategy 4b: Aggressive markdown stripping - handle malformed blocks
    # If we see ```json at the start, extract everything until ``` or end of text
    if text.strip().startswith('```json'):
        # Find the content after ```json
        content_start = text.find('```json') + 7  # len('```json') = 7
        # Skip any whitespace/newlines after ```json
        while content_start < len(text) and text[content_start] in ' \t\r\n':
            content_start += 1

        # Find the closing ``` if it exists
        closing_backticks = text.find('```', content_start)
        if closing_backticks != -1:
            json_candidate = text[content_start:closing_backticks].strip()
        else:
            # No closing backticks - take everything to the end
            json_candidate = text[content_start:].strip()

        try:
            result = json.loads(json_candidate)
            if isinstance(result, (list, dict)):
                if verbose:
                    print("✓ Extracted using aggressive markdown stripping")
                return result
        except json.JSONDecodeError as e:
            if verbose:
                print(f"  Aggressive markdown stripping found JSON-like content but parsing failed: {e}")
                print(f"  Candidate text (first 200 chars): {json_candidate[:200]}")

                # Check if it looks like the JSON was truncated
                if "Unterminated string" in str(e):
                    print(f"  WARNING: JSON appears to be truncated (incomplete response)")
                    # Try to salvage what we can by closing the JSON properly
                    # This is a last-resort attempt for truncated responses
                    return _attempt_json_repair(json_candidate, verbose)

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

    # Strategy 7: Try to fix common JSON formatting errors
    # Sometimes Claude might return slightly malformed JSON that can be fixed
    if verbose:
        print("  Attempting to fix common JSON formatting errors...")

    # Look for patterns that suggest JSON but might have issues
    # Try removing trailing commas (common error)
    cleaned_text = re.sub(r',(\s*[}\]])', r'\1', text)
    if cleaned_text != text:
        try:
            result = json.loads(cleaned_text)
            if isinstance(result, (list, dict)):
                if verbose:
                    print("✓ Fixed by removing trailing commas")
                return result
        except json.JSONDecodeError:
            pass

    # Try to close unclosed arrays/objects
    # This handles truncated JSON
    if text.strip().startswith('[') and not text.strip().endswith(']'):
        # Array not closed - try to close it
        fixed_text = text.strip()
        # Remove any trailing comma
        if fixed_text.endswith(','):
            fixed_text = fixed_text[:-1]
        fixed_text += ']'
        try:
            result = json.loads(fixed_text)
            if isinstance(result, list):
                if verbose:
                    print("✓ Fixed by closing unclosed array")
                return result
        except json.JSONDecodeError:
            pass

    # Try fixing unescaped quotes in strings (but be careful)
    # This is risky and should only be done as last resort
    # Look for patterns like: "key": "value with "quotes" inside"

    # All strategies failed
    if verbose:
        print("✗ All extraction strategies failed")
        if len(original_text) < 1000:
            print(f"Full text:\n{original_text}")
        else:
            print(f"Text preview (first 500 chars):\n{original_text[:500]}...")
            print(f"Text preview (last 200 chars):\n...{original_text[-200:]}")

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

        # Case 9: Text with metadata prefix
        ('Here\'s the analysis:\n```json\n[{"test": "metadata"}]\n```',
         [{"test": "metadata"}]),

        # Case 10: Trailing comma in JSON (common error)
        ('[{"a": 1, "b": 2,}]', [{"a": 1, "b": 2}]),
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
