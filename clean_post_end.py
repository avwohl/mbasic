#!/usr/bin/env python3
"""
Clean unreferenced code after END statements in BASIC files.
"""

import os
import re
import subprocess
from pathlib import Path

# Files identified with fully unreferenced post-END code
FILES_TO_CLEAN = [
    # From bad_not521
    ('basic/bad_not521/aut850.bas', 80, [90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200]),
    ('basic/bad_not521/checkers.bas', 950, [960]),
    ('basic/bad_not521/krakinst.bas', 810, [820]),
    ('basic/bad_not521/pcat.bas', 10000, [11000, 11100]),

    # From bad_syntax
    ('basic/bad_syntax/backgamm.bas', 2870, list(range(2880, 3501, 10))),
    ('basic/bad_syntax/lanes.bas', 9999, [12570, 9550]),
    ('basic/bad_syntax/speech.bas', 600, list(range(610, 881, 10))),
    ('basic/bad_syntax/trade.bas', 4660, [6682, 4600, 4610, 4620]),
]

def extract_line_number(line):
    """Extract line number from a BASIC line."""
    match = re.match(r'^\s*(\d+)', line)
    return int(match.group(1)) if match else None

def clean_file(filepath, end_line_num, lines_to_remove):
    """Remove unreferenced lines after END statement."""
    filepath = Path(filepath)

    if not filepath.exists():
        return False, "File not found"

    # Read all lines
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    # Build set of line numbers to remove
    remove_set = set(lines_to_remove)

    # Filter out lines after END that are in remove_set
    filtered_lines = []
    past_end = False
    end_line_found = False

    for line in lines:
        line_num = extract_line_number(line)

        if line_num is not None:
            if line_num == end_line_num:
                # Found the END line
                end_line_found = True
                past_end = True
                filtered_lines.append(line)
            elif past_end and line_num in remove_set:
                # Skip this line - it's after END and unreferenced
                continue
            else:
                filtered_lines.append(line)
        else:
            # Keep non-numbered lines (shouldn't be any in BASIC)
            if not past_end:
                filtered_lines.append(line)

    if not end_line_found:
        return False, f"END line {end_line_num} not found"

    # Create backup
    backup_path = filepath.with_suffix('.bas.bak')
    filepath.rename(backup_path)

    # Write cleaned file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(filtered_lines)

    return True, backup_path

def test_file(filepath):
    """Test if a BASIC file parses without errors."""
    try:
        result = subprocess.run(
            ['python3', 'mbasic.py', filepath],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=2,
            text=True
        )

        # Check for parse errors
        output = result.stdout + result.stderr

        if '?Syntax error' in output or 'Error' in output:
            return False, output

        # If it loads without errors, it parsed successfully
        return True, output

    except subprocess.TimeoutExpired:
        # Timeout is OK - means it started running
        return True, "Timeout (running)"
    except Exception as e:
        return False, str(e)

def main():
    """Clean all identified files and test results."""
    base_dir = Path('/home/wohl/cl/mbasic')
    os.chdir(base_dir)

    print("Cleaning BASIC files with unreferenced post-END code...")
    print("=" * 80)
    print()

    results = {
        'success': [],
        'failed': [],
        'no_change': []
    }

    for filepath, end_line, lines_to_remove in FILES_TO_CLEAN:
        print(f"\n{filepath}")
        print(f"  END line: {end_line}")
        print(f"  Removing {len(lines_to_remove)} unreferenced lines")

        # Clean the file
        success, backup_or_msg = clean_file(filepath, end_line, lines_to_remove)

        if not success:
            print(f"  ✗ Cleanup failed: {backup_or_msg}")
            results['failed'].append((filepath, backup_or_msg))
            continue

        backup_path = backup_or_msg

        # Get file sizes
        original_size = os.path.getsize(backup_path)
        new_size = os.path.getsize(filepath)
        removed_bytes = original_size - new_size

        print(f"  Reduced from {original_size} to {new_size} bytes ({removed_bytes} bytes removed)")

        # Test the cleaned file
        print(f"  Testing cleaned file...")
        test_success, output = test_file(filepath)

        if test_success:
            print(f"  ✓ NOW LEGAL - parses without errors!")
            results['success'].append(filepath)
            # Remove backup
            os.remove(backup_path)
        else:
            print(f"  ✗ Still has errors, restoring backup")
            if 'Syntax error' in output:
                # Show first error
                for line in output.split('\n'):
                    if '?' in line:
                        print(f"    {line}")
                        break
            # Restore backup
            os.remove(filepath)
            backup_path.rename(filepath)
            results['no_change'].append(filepath)

    # Summary
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"\n✓ Successfully cleaned and now legal: {len(results['success'])} files")
    for f in results['success']:
        print(f"  - {f}")

    if results['no_change']:
        print(f"\n✗ Still have errors (no change): {len(results['no_change'])} files")
        for f in results['no_change']:
            print(f"  - {f}")

    if results['failed']:
        print(f"\n✗ Failed to process: {len(results['failed'])} files")
        for f, msg in results['failed']:
            print(f"  - {f}: {msg}")

if __name__ == '__main__':
    main()
