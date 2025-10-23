#!/usr/bin/env python3
"""
Analyze BASIC files for unreferenced code after END statements.

Similar to the Control-Z cleanup, this finds code after END statements
that isn't referenced by GOTO, GOSUB, or ON ERROR statements.
"""

import os
import re
from pathlib import Path

def extract_line_number(line):
    """Extract line number from a BASIC line."""
    match = re.match(r'^\s*(\d+)', line)
    return int(match.group(1)) if match else None

def find_end_statements(lines):
    """Find all END statement line numbers."""
    end_lines = []
    for i, line in enumerate(lines):
        line_num = extract_line_number(line)
        if line_num is not None:
            # Check if line contains END statement (as whole word or start of statement)
            # Match: END or END: or END ' or END REM but not WEND, APPEND, etc.
            if re.search(r'\bEND\s*($|:|\'|REM\b)', line, re.IGNORECASE):
                end_lines.append((i, line_num))
    return end_lines

def find_referenced_lines(lines):
    """Find all line numbers referenced by GOTO, GOSUB, or ON ERROR."""
    referenced = set()

    for line in lines:
        # GOTO targets: GOTO 100, THEN 100, ELSE 100
        for match in re.finditer(r'\b(?:GOTO|THEN|ELSE)\s+(\d+)', line, re.IGNORECASE):
            referenced.add(int(match.group(1)))

        # GOSUB targets: GOSUB 100
        for match in re.finditer(r'\bGOSUB\s+(\d+)', line, re.IGNORECASE):
            referenced.add(int(match.group(1)))

        # ON GOTO/GOSUB targets: ON X GOTO 100,200,300
        for match in re.finditer(r'\bON\s+.+?\s+(?:GOTO|GOSUB)\s+([\d,\s]+)', line, re.IGNORECASE):
            targets = match.group(1)
            for num in re.findall(r'\d+', targets):
                referenced.add(int(num))

        # ON ERROR targets: ON ERROR GOTO 100, ON ERROR GOSUB 100
        for match in re.finditer(r'\bON\s+ERROR\s+(?:GOTO|GOSUB)\s+(\d+)', line, re.IGNORECASE):
            referenced.add(int(match.group(1)))

    return referenced

def analyze_file(filepath):
    """Analyze a single BASIC file for unreferenced post-END code."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        return None

    if not lines:
        return None

    # Find END statements
    end_statements = find_end_statements(lines)
    if not end_statements:
        return None

    # Find all referenced line numbers
    referenced = find_referenced_lines(lines)

    # For each END statement, check if there are unreferenced lines after it
    results = []
    for line_idx, end_line_num in end_statements:
        # Get all lines after this END
        post_end_lines = []
        for i in range(line_idx + 1, len(lines)):
            line_num = extract_line_number(lines[i])
            if line_num is not None:
                post_end_lines.append(line_num)

        if not post_end_lines:
            continue

        # Check if any post-END lines are referenced
        unreferenced = [ln for ln in post_end_lines if ln not in referenced]

        if unreferenced and len(unreferenced) == len(post_end_lines):
            # All post-END lines are unreferenced
            results.append({
                'end_line': end_line_num,
                'post_end_lines': post_end_lines,
                'all_unreferenced': True
            })
        elif unreferenced:
            # Some post-END lines are unreferenced
            results.append({
                'end_line': end_line_num,
                'post_end_lines': post_end_lines,
                'unreferenced_lines': unreferenced,
                'referenced_lines': [ln for ln in post_end_lines if ln in referenced],
                'all_unreferenced': False
            })

    return results if results else None

def main():
    """Analyze all BASIC files in bad_not521 and bad_syntax directories."""
    base_dir = Path('/home/wohl/cl/mbasic/basic')

    dirs_to_check = [
        base_dir / 'bad_not521',
        base_dir / 'bad_syntax'
    ]

    print("Analyzing BASIC files for unreferenced code after END statements...")
    print("=" * 80)
    print()

    candidates = []

    for dir_path in dirs_to_check:
        if not dir_path.exists():
            print(f"Directory not found: {dir_path}")
            continue

        print(f"Checking {dir_path.name}/")
        print("-" * 80)

        for filepath in sorted(dir_path.glob('*.bas')):
            result = analyze_file(filepath)
            if result:
                print(f"\n{filepath.name}:")
                for item in result:
                    if item['all_unreferenced']:
                        print(f"  END at line {item['end_line']}")
                        print(f"  Unreferenced lines after END: {item['post_end_lines']}")
                        print(f"  → All {len(item['post_end_lines'])} lines are unreferenced (can be removed)")
                        candidates.append((filepath, item['end_line'], item['post_end_lines']))
                    else:
                        print(f"  END at line {item['end_line']}")
                        print(f"  Post-END lines: {item['post_end_lines']}")
                        print(f"  Unreferenced: {item['unreferenced_lines']}")
                        print(f"  Referenced: {item['referenced_lines']}")
                        print(f"  → Mixed: some lines are referenced, careful removal needed")

        print()

    print()
    print("=" * 80)
    print(f"SUMMARY: Found {len(candidates)} files with fully unreferenced post-END code")
    print("=" * 80)

    if candidates:
        print("\nFiles that can be cleaned (all post-END lines unreferenced):")
        for filepath, end_line, post_end_lines in candidates:
            print(f"  {filepath.name}: END at {end_line}, remove lines {post_end_lines}")

if __name__ == '__main__':
    main()
