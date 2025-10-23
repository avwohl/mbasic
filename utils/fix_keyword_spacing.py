#!/usr/bin/env python3
"""
Fixes missing spaces after BASIC keywords like THEN and GOTO.

Some BASIC programs are missing spaces after keywords, which causes
syntax errors in MBASIC 5.21. This script adds the necessary spaces.

Examples of fixes:
  - THENK3=3 -> THEN K3=3
  - GOTO980 -> GOTO 980
  - GOSUB1000 -> GOSUB 1000
  - FORI=1TO9 -> FOR I=1 TO 9
  - IFK9>T9 -> IF K9>T9
  - NEXTI -> NEXT I
  - 9THEN -> 9 THEN
  - IGO TO -> I GO TO
  - GO TO -> GOTO (combines two-word form)
"""

import sys
import re
from pathlib import Path


def fix_keyword_spacing(line):
    """
    Fix missing spaces after keywords in a BASIC line.

    Args:
        line: A line of BASIC code

    Returns:
        The line with fixed spacing
    """
    # Fix THEN preceded by digit with no space (9THEN -> 9 THEN)
    line = re.sub(r'(\d)THEN\b', r'\1 THEN', line)

    # Fix THEN followed by letter or digit (but not already spaced)
    # Pattern: THEN + (letter/digit) with no space
    # Note: Can't use \b because "9THEN" has no word boundary between 9 and T
    line = re.sub(r'THEN([A-Z0-9])', r'THEN \1', line)

    # Fix GOTO followed by digit with no space
    line = re.sub(r'\bGOTO(\d)', r'GOTO \1', line)

    # Fix GOSUB followed by digit with no space
    line = re.sub(r'\bGOSUB(\d)', r'GOSUB \1', line)

    # Fix ON followed by letter/digit with no space (for ON...GOTO/GOSUB)
    line = re.sub(r'\bON([A-Z0-9])', r'ON \1', line)

    # Fix FOR followed by letter with no space (FORI=1TO9 -> FOR I=1TO9)
    # Only match FOR followed by a letter (variable name)
    line = re.sub(r'\bFOR([A-Z])', r'FOR \1', line)

    # Fix TO preceded by digit with no space (I=1TO9 -> I=1 TO 9)
    line = re.sub(r'(\d)TO(\d)', r'\1 TO \2', line)
    # Also fix TO preceded by letter/paren with no space (A)TO9 -> A) TO 9)
    line = re.sub(r'([A-Z)])TO(\d)', r'\1 TO \2', line)

    # Fix IF followed by letter/digit with no space (IFK9>T9 -> IF K9>T9)
    line = re.sub(r'\bIF([A-Z0-9])', r'IF \1', line)

    # Fix NEXT followed by letter with no space (NEXTI -> NEXT I, NEXTJ -> NEXT J)
    line = re.sub(r'\bNEXT([A-Z])', r'NEXT \1', line)

    # Fix OR preceded by letter/digit/paren with no space (Q1<1ORQ1 -> Q1<1 OR Q1)
    line = re.sub(r'([A-Z0-9)])OR([A-Z0-9])', r'\1 OR \2', line)

    # Fix AND preceded by letter/digit/paren with no space
    line = re.sub(r'([A-Z0-9)])AND([A-Z0-9])', r'\1 AND \2', line)

    # Fix GO preceded by letter/digit with no space (Z4GO -> Z4 GO, IGO -> I GO)
    # This handles cases like "ON IGO TO" which should be "ON I GO TO"
    line = re.sub(r'([A-Z0-9])GO\b', r'\1 GO', line)

    # Change " GO TO " to " GOTO " (combine two-word form to single keyword)
    line = re.sub(r'\bGO TO\b', r'GOTO', line)

    return line


def fix_file(filepath, dry_run=True):
    """
    Fix keyword spacing in a BASIC file.

    Args:
        filepath: Path to the BASIC file
        dry_run: If True, only report changes without modifying the file

    Returns:
        Number of lines changed
    """
    with open(filepath, 'r') as f:
        lines = f.readlines()

    changed_lines = []
    changes_made = 0

    for i, line in enumerate(lines, 1):
        fixed = fix_keyword_spacing(line)
        if fixed != line:
            changed_lines.append((i, line.rstrip(), fixed.rstrip()))
            changes_made += 1
            lines[i-1] = fixed

    if changed_lines:
        print(f"File: {filepath}")
        print(f"Lines changed: {changes_made}")
        if dry_run:
            print("Changes to be made (dry-run):")
            for line_num, old, new in changed_lines[:5]:  # Show first 5
                print(f"  Line {line_num}:")
                print(f"    OLD: {old}")
                print(f"    NEW: {new}")
            if len(changed_lines) > 5:
                print(f"  ... and {len(changed_lines) - 5} more lines")
        else:
            # Write the fixed file
            with open(filepath, 'w') as f:
                f.writelines(lines)
            print("✓ File updated")
        print()

    return changes_made


def main():
    if len(sys.argv) < 2:
        print("Usage: fix_keyword_spacing.py <file_or_directory> [--execute]")
        print()
        print("Fixes missing spaces after keywords like THEN and GOTO")
        print()
        print("Options:")
        print("  --execute    Actually modify files (default is dry-run)")
        print()
        print("Examples:")
        print("  python3 utils/fix_keyword_spacing.py bcg/superstartrek.bas")
        print("  python3 utils/fix_keyword_spacing.py bcg/ --execute")
        sys.exit(1)

    target = Path(sys.argv[1])
    dry_run = '--execute' not in sys.argv

    if dry_run:
        print("DRY-RUN MODE - No files will be modified")
        print("Use --execute to actually modify files")
        print()

    total_files = 0
    total_changes = 0

    if target.is_file():
        files = [target]
    elif target.is_dir():
        files = sorted(target.glob('*.bas'))
    else:
        print(f"Error: {target} not found")
        sys.exit(1)

    for filepath in files:
        changes = fix_file(filepath, dry_run=dry_run)
        if changes > 0:
            total_files += 1
            total_changes += changes

    print(f"Summary: {total_files} files with changes, {total_changes} total lines changed")

    if dry_run and total_changes > 0:
        print()
        print("Run with --execute to apply these changes")


if __name__ == '__main__':
    main()
