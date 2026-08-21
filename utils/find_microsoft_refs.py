#!/usr/bin/env python3
"""
Find all Microsoft references in the codebase.

Categorizes references as:
- Links that can be updated to MBASIC_HISTORY.md
- Text that should be reworded
- External docs that should stay as-is
- PyPI/metadata that must stay generic
"""

import re
from pathlib import Path

# Directories to search
SEARCH_DIRS = [
    'src',
    'docs',
    'tests',
    '.',  # Root files
]

# Files to exclude
EXCLUDE_PATTERNS = [
    r'\.git',
    r'venv',
    r'__pycache__',
    r'\.pyc$',
]

# File patterns to include
INCLUDE_PATTERNS = [
    r'\.py$',
    r'\.md$',
    r'\.txt$',
    r'\.toml$',
]

def should_process(path):
    """Check if file should be processed."""
    path_str = str(path)

    # Exclude patterns
    for pattern in EXCLUDE_PATTERNS:
        if re.search(pattern, path_str):
            return False

    # Include patterns
    for pattern in INCLUDE_PATTERNS:
        if re.search(pattern, path_str):
            return True

    return False

def categorize_reference(file_path, line_num, line):
    """Categorize a Microsoft reference."""
    file_str = str(file_path)
    line_lower = line.lower()

    # PyPI metadata
    if 'pyproject.toml' in file_str or 'setup.py' in file_str:
        if 'description' in line_lower or 'summary' in line_lower:
            return 'METADATA', 'PyPI description - use generic "MBASIC"'

    # Links/URLs
    if 'http' in line_lower or 'www.' in line_lower:
        return 'URL', 'External URL - leave as-is if to Microsoft docs'

    # Common patterns to replace
    if re.search(r'microsoft\s+(?:mbasic|basic)', line_lower):
        return 'PHRASE', f'Replace "MBASIC" with "MBASIC (see docs/MBASIC_HISTORY.md)"'

    if re.search(r'microsoft.*interpreter', line_lower):
        return 'PHRASE', 'Replace with "MBASIC interpreter"'

    if re.search(r'microsoft.*implementation', line_lower):
        return 'PHRASE', 'Replace with "original MBASIC implementation"'

    # Generic mention
    return 'GENERIC', 'Review and reword to clarify this is independent'

def main():
    """Find and categorize all Microsoft references."""
    root = Path('.')
    results = {
        'METADATA': [],
        'URL': [],
        'PHRASE': [],
        'GENERIC': [],
    }

    # Search all files
    for search_dir in SEARCH_DIRS:
        dir_path = root / search_dir
        if not dir_path.exists():
            continue

        if dir_path.is_file():
            files = [dir_path]
        else:
            files = dir_path.rglob('*')

        for file_path in files:
            if not file_path.is_file():
                continue

            if not should_process(file_path):
                continue

            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        if 'microsoft' in line.lower():
                            category, advice = categorize_reference(file_path, line_num, line)
                            results[category].append({
                                'file': str(file_path),
                                'line': line_num,
                                'text': line.strip(),
                                'advice': advice
                            })
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

    # Print results
    total = sum(len(refs) for refs in results.values())
    print(f"Found {total} Microsoft references\n")

    for category in ['METADATA', 'URL', 'PHRASE', 'GENERIC']:
        refs = results[category]
        if not refs:
            continue

        print(f"\n{'='*80}")
        print(f"{category} ({len(refs)} references)")
        print('='*80)

        for ref in refs:
            print(f"\nFile: {ref['file']}:{ref['line']}")
            print(f"Text: {ref['text'][:100]}...")
            print(f"Advice: {ref['advice']}")

    print(f"\n{'='*80}")
    print(f"TOTAL: {total} references")
    print('='*80)

if __name__ == '__main__':
    main()
