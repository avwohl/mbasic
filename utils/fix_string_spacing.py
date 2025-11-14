#!/usr/bin/env python3
"""
Fix extra spaces around keywords in BASIC string literals.

This script detects and fixes spacing issues caused by an earlier tokenizer
that added extra spaces around keywords even inside strings. Most commonly
affects two-character keywords like 'OR', 'IF', 'TO', 'ON', etc.

Examples:
  "NEVERM OR E" -> "NEVERMORE"
  "F OR TUNE" -> "FORTUNE"
  "C ON SIDER" -> "CONSIDER"

Usage:
  # Interactive mode - review each change:
  python3 utils/fix_string_spacing.py basic/games/poetry.bas

  # Dry-run mode - see what would change without modifying files:
  python3 utils/fix_string_spacing.py basic/games/*.bas --dry-run

  # Auto mode - automatically fix obvious cases (use with caution):
  python3 utils/fix_string_spacing.py basic/games/*.bas --auto

  # Recursive - process all .bas files in directory tree:
  python3 utils/fix_string_spacing.py basic/ --recursive

Note: This tool only fixes spacing inside string literals ("...") in BASIC code.
It detects patterns like "NEVERM OR E" which should be "NEVERMORE".
Some matches may be false positives (legitimate phrases), so review carefully!
"""

import re
import sys
import argparse
from pathlib import Path
from typing import List, Tuple, Optional

# Two-character BASIC keywords that commonly appear in strings
TWO_CHAR_KEYWORDS = [
    'OR', 'IF', 'TO', 'ON', 'GO', 'AS',
]

# Three-character keywords (less common but possible)
THREE_CHAR_KEYWORDS = [
    'FOR', 'AND', 'NOT', 'MOD', 'XOR', 'IMP', 'EQV',
    'DIM', 'DEF', 'END', 'LET', 'REM', 'RUN', 'NEW',
]

def find_strings_in_line(line: str) -> List[Tuple[int, int, str]]:
    """
    Find all string literals in a BASIC line.

    Returns list of (start_pos, end_pos, string_content) tuples.
    """
    strings = []
    in_string = False
    start_pos = 0
    i = 0

    while i < len(line):
        if line[i] == '"':
            if not in_string:
                # Start of string
                in_string = True
                start_pos = i
            else:
                # End of string
                strings.append((start_pos, i + 1, line[start_pos:i + 1]))
                in_string = False
        i += 1

    return strings

def detect_keyword_spacing_issues(text: str) -> List[Tuple[str, str, str]]:
    """
    Detect likely spacing issues around keywords in a string.

    Returns list of (pattern, before, after) tuples where:
      - pattern: the problematic pattern found
      - before: text before the fix
      - after: text after the fix
    """
    issues = []

    # Check for two-character keywords with spaces on both sides
    # Pattern: word fragment + space + keyword + space + word fragment
    # Example: "NEVERM OR E" where OR breaks up NEVERMORE

    for keyword in TWO_CHAR_KEYWORDS:
        # Look for pattern: [A-Z] KEYWORD [A-Z]
        # This suggests the keyword is breaking up a word
        pattern = rf'(\b\w+)(\s+{keyword}\s+)(\w+\b)'

        def check_match(match):
            before_word = match.group(1)
            keyword_with_spaces = match.group(2)
            after_word = match.group(3)

            # Pattern for tokenization artifacts:
            # Most reliable indicator: one side is VERY short (1-2 chars) finishing a longer word
            # Examples: "NEVERM OR E" (6+2+1), "...EVERM OR E" (8+2+1)
            #
            # Less reliable (causes false positives):
            # - "F OR TUNE" (1+2+4) - could be "F OR TUNE" or "FORTUNE"
            # - "ARRAYS TO BE" (6+2+2) - these are real words not fragments
            #
            # Strategy: Only auto-fix the most obvious cases (1-2 char endings)
            # For longer fragments, require interactive confirmation

            # Both sides are single letters - definitely not a broken word (e.g., "Y OR N")
            if len(before_word) <= 1 and len(after_word) <= 1:
                return None

            # If both parts are 3+ characters, likely real words not fragments
            # This avoids "ARRAYS TO BE", "FORGOTTEN TO USE", etc.
            if len(before_word) >= 3 and len(after_word) >= 3:
                return None

            # One side should be very short (1-2 chars) and the other longer (5+ chars)
            # This is the most reliable pattern for tokenization artifacts
            short_side = min(len(before_word), len(after_word))
            long_side = max(len(before_word), len(after_word))

            if not (1 <= short_side <= 2 and long_side >= 5):
                return None

            # If both sides are uppercase letters, likely a broken word
            if before_word[-1].isupper() and after_word[0].isupper():
                # Reconstruct without spaces - keep original case of keyword
                fixed = before_word + keyword + after_word
                original = before_word + keyword_with_spaces + after_word

                # Check if the fixed version looks like a real word
                # (all letters, no weird patterns)
                if fixed.replace(keyword, '').isalpha():
                    return (original.strip(), fixed)
            return None

        for match in re.finditer(pattern, text):
            result = check_match(match)
            if result:
                original, fixed = result
                issues.append((keyword, original, fixed))

    # Also check for three-character keywords if they appear suspicious
    for keyword in THREE_CHAR_KEYWORDS:
        pattern = rf'(\b\w+)(\s+{keyword}\s+)(\w+\b)'

        for match in re.finditer(pattern, text):
            before_word = match.group(1)
            keyword_with_spaces = match.group(2)
            after_word = match.group(3)

            # Only flag if it really looks like a broken word
            if (before_word[-1].isupper() and after_word[0].isupper() and
                len(before_word) <= 3 and len(after_word) <= 3):
                fixed = before_word + keyword + after_word
                original = before_word + keyword_with_spaces + after_word
                if fixed.replace(keyword, '').isalpha():
                    issues.append((keyword, original.strip(), fixed))

    return issues

def fix_line(line: str, auto: bool = False, dry_run: bool = False) -> Tuple[str, List[str]]:
    """
    Fix spacing issues in a BASIC line.

    Returns (fixed_line, changes_made) where changes_made is a list of descriptions.
    """
    changes = []

    # Find all strings in the line
    strings = find_strings_in_line(line)

    if not strings:
        return line, changes

    # Process each string
    result = line
    offset = 0  # Track position changes as we modify the line

    for start_pos, end_pos, string_literal in strings:
        # Get the content inside the quotes
        string_content = string_literal[1:-1]

        # Detect issues
        issues = detect_keyword_spacing_issues(string_content)

        if not issues:
            continue

        # Fix each issue
        fixed_content = string_content
        for keyword, original, fixed in issues:
            if auto or dry_run:
                # Auto-fix (or just report for dry run)
                fixed_content = fixed_content.replace(original, fixed)
                changes.append(f'  "{original}" -> "{fixed}" (keyword: {keyword})')
            else:
                # Ask user
                print(f'\nFound potential issue:')
                print(f'  Original: "{original}"')
                print(f'  Fixed:    "{fixed}"')
                print(f'  Keyword:  {keyword}')
                print(f'  Context:  {line.strip()}')

                try:
                    response = input('Fix this? [y/n/q] (q=quit): ').strip().lower()
                except EOFError:
                    response = 'n'

                if response == 'q':
                    return line, []
                elif response == 'y':
                    fixed_content = fixed_content.replace(original, fixed)
                    changes.append(f'  "{original}" -> "{fixed}" (keyword: {keyword})')

        if fixed_content != string_content:
            # Rebuild the string literal
            new_string = '"' + fixed_content + '"'

            # Replace in the result line
            adjusted_start = start_pos + offset
            adjusted_end = end_pos + offset
            result = result[:adjusted_start] + new_string + result[adjusted_end:]

            # Update offset for next iteration
            offset += len(new_string) - len(string_literal)

    return result, changes

def process_file(filepath: Path, auto: bool = False, dry_run: bool = False) -> int:
    """
    Process a single BASIC file.

    Returns the number of lines changed.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f'Error reading {filepath}: {e}', file=sys.stderr)
        return 0

    changes_made = 0
    new_lines = []

    for line_num, line in enumerate(lines, 1):
        fixed_line, changes = fix_line(line.rstrip('\n'), auto=auto, dry_run=dry_run)

        if changes:
            print(f'\n{filepath}:{line_num}')
            print(f'  Before: {line.rstrip()}')
            print(f'  After:  {fixed_line}')
            for change in changes:
                print(change)
            changes_made += 1

        new_lines.append(fixed_line + '\n')

    if changes_made > 0 and not dry_run:
        # Write back to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f'\n✓ Fixed {changes_made} line(s) in {filepath}')
    elif changes_made > 0:
        print(f'\n[DRY RUN] Would fix {changes_made} line(s) in {filepath}')

    return changes_made

def main():
    parser = argparse.ArgumentParser(
        description='Fix extra spaces around keywords in BASIC string literals',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('paths', nargs='+', help='BASIC file(s) or directory to process')
    parser.add_argument('--auto', action='store_true',
                       help='Automatically fix obvious issues without prompting')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be changed without modifying files')
    parser.add_argument('--recursive', '-r', action='store_true',
                       help='Process directories recursively')

    args = parser.parse_args()

    # Collect all files to process
    files = []
    for path_str in args.paths:
        path = Path(path_str)

        if path.is_file():
            if path.suffix.lower() in ['.bas', '.BAS']:
                files.append(path)
            else:
                print(f'Skipping non-BASIC file: {path}', file=sys.stderr)
        elif path.is_dir():
            if args.recursive:
                files.extend(path.rglob('*.bas'))
                files.extend(path.rglob('*.BAS'))
            else:
                files.extend(path.glob('*.bas'))
                files.extend(path.glob('*.BAS'))
        else:
            print(f'Path not found: {path}', file=sys.stderr)

    if not files:
        print('No BASIC files found to process', file=sys.stderr)
        return 1

    print(f'Processing {len(files)} file(s)...\n')

    total_changes = 0
    for filepath in sorted(files):
        changes = process_file(filepath, auto=args.auto, dry_run=args.dry_run)
        total_changes += changes

    print(f'\n{"[DRY RUN] " if args.dry_run else ""}Total: {total_changes} line(s) changed across {len(files)} file(s)')

    return 0

if __name__ == '__main__':
    sys.exit(main())
