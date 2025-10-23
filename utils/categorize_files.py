#!/usr/bin/env python3
"""Categorize BASIC files in basic/ root directory"""

import os
import subprocess
import re
from pathlib import Path

def test_file(filepath):
    """Test if a file parses correctly"""
    try:
        result = subprocess.run(
            ['python3', 'mbasic.py', filepath],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=5,
            text=True
        )
        output = result.stdout

        # Check for various error conditions
        has_ready = 'Ready' in output
        has_syntax_error = '?Syntax error' in output
        has_undef_statement = '?Undef\'d statement' in output
        has_other_error = '?Error' in output or 'Error:' in output

        return {
            'success': has_ready and not has_syntax_error,
            'has_ready': has_ready,
            'has_syntax_error': has_syntax_error,
            'has_undef_statement': has_undef_statement,
            'has_other_error': has_other_error,
            'output': output
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'timeout': True,
            'output': 'TIMEOUT'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'output': f'ERROR: {e}'
        }

def read_file_sample(filepath, lines=10):
    """Read first few lines of file"""
    try:
        with open(filepath, 'r', encoding='latin-1', errors='ignore') as f:
            content = f.read()
            lines_list = content.split('\n')[:lines]
            return '\n'.join(lines_list)
    except:
        return None

def categorize_file(filepath):
    """Determine the appropriate category for a file"""
    basename = os.path.basename(filepath).lower()

    # Test if it parses
    test_result = test_file(filepath)

    # Read first few lines for context
    sample = read_file_sample(filepath)

    # Determine category
    category = None
    reason = ""

    if not test_result['success']:
        if test_result.get('timeout'):
            category = 'bad_syntax'
            reason = "File times out during execution"
        elif test_result.get('has_syntax_error'):
            category = 'bad_syntax'
            reason = "Syntax error"
        elif test_result.get('has_undef_statement'):
            category = 'bad_syntax'
            reason = "Undefined statement error"
        elif test_result.get('has_other_error'):
            category = 'bad_syntax'
            reason = "Other error during parsing"
        else:
            category = 'bad_syntax'
            reason = "Failed to parse"
    else:
        # File parses successfully - determine if it's a test
        if 'test' in basename:
            category = 'bas_tests'
            reason = "Filename contains 'test'"
        elif sample and any(marker in sample.lower() for marker in ['rem test', 'rem * test', '10 rem test']):
            category = 'bas_tests'
            reason = "Contains test marker in comments"
        else:
            # Keep in root - it's a working program
            category = None
            reason = "Working BASIC program"

    return {
        'category': category,
        'reason': reason,
        'test_result': test_result
    }

def main():
    # Get all .bas/.BAS files in basic/ root
    files = []
    for ext in ['*.bas', '*.BAS']:
        files.extend(Path('basic').glob(ext))

    files = sorted([str(f) for f in files])

    print(f"Found {len(files)} files in basic/ root directory")
    print("=" * 70)
    print()

    # Categorize each file
    categorized = {
        'bad_syntax': [],
        'bas_tests': [],
        'keep_root': []
    }

    for i, filepath in enumerate(files, 1):
        print(f"[{i}/{len(files)}] Analyzing {os.path.basename(filepath)}...", end=' ')

        result = categorize_file(filepath)
        category = result['category']

        if category is None:
            categorized['keep_root'].append((filepath, result['reason']))
            print(f"KEEP - {result['reason']}")
        else:
            categorized[category].append((filepath, result['reason']))
            print(f"MOVE to {category}/ - {result['reason']}")

    print()
    print("=" * 70)
    print("CATEGORIZATION SUMMARY")
    print("=" * 70)
    print(f"Keep in basic/: {len(categorized['keep_root'])} files")
    print(f"Move to basic/bas_tests/: {len(categorized['bas_tests'])} files")
    print(f"Move to basic/bad_syntax/: {len(categorized['bad_syntax'])} files")
    print()

    # Show details
    if categorized['bas_tests']:
        print("Files to move to bas_tests/:")
        for filepath, reason in categorized['bas_tests']:
            print(f"  - {os.path.basename(filepath)}: {reason}")
        print()

    if categorized['bad_syntax']:
        print("Files to move to bad_syntax/:")
        for filepath, reason in categorized['bad_syntax']:
            print(f"  - {os.path.basename(filepath)}: {reason}")
        print()

    # Ask for confirmation to move
    print("=" * 70)
    response = input("Move files to appropriate directories? (yes/no): ")

    if response.lower() in ['yes', 'y']:
        moved_count = 0

        for category in ['bas_tests', 'bad_syntax']:
            for filepath, reason in categorized[category]:
                dest_dir = f'basic/{category}'
                dest_path = os.path.join(dest_dir, os.path.basename(filepath))

                try:
                    # Check if destination already exists
                    if os.path.exists(dest_path):
                        print(f"  WARNING: {dest_path} already exists, skipping")
                        continue

                    os.rename(filepath, dest_path)
                    print(f"  Moved {os.path.basename(filepath)} -> {category}/")
                    moved_count += 1
                except Exception as e:
                    print(f"  ERROR moving {filepath}: {e}")

        print()
        print(f"Successfully moved {moved_count} files")
        print(f"{len(categorized['keep_root'])} files remain in basic/ root")
    else:
        print("No files moved")

if __name__ == '__main__':
    main()
