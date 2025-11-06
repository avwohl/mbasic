#!/usr/bin/env python3
"""
Automated fixes for medium severity documentation inconsistencies.
This script addresses systematic issues across the codebase.
"""

import re
from pathlib import Path
from typing import List, Tuple

def fix_file(filepath: str, replacements: List[Tuple[str, str]]) -> int:
    """Apply multiple text replacements to a file.

    Args:
        filepath: Path to file to fix
        replacements: List of (old_text, new_text) tuples

    Returns:
        Number of replacements made
    """
    try:
        with open(filepath, 'r') as f:
            content = f.read()

        original_content = content
        count = 0

        for old_text, new_text in replacements:
            if old_text in content:
                content = content.replace(old_text, new_text)
                count += 1

        if content != original_content:
            with open(filepath, 'w') as f:
                f.write(content)
            return count
        return 0
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return 0

# Track fixes
fixes_made = 0
files_modified = []

# Fix 1: src/file_io.py - Clarify terminology
print("Fixing file I/O terminology...")
count = fix_file('src/file_io.py', [
    ('FileSystemProvider.list_files() and FileSystemProvider.delete() overlap with FileIO operations (FILES and KILL commands). The separation is not clean.',
     'FileSystemProvider provides lower-level file handle operations (list_files/delete are helper methods).\nFileIO provides higher-level program file management (FILES/KILL commands use these helpers).'),
])
if count > 0:
    fixes_made += count
    files_modified.append('src/file_io.py')

# Fix 2: src/immediate_executor.py - Clarify INPUT behavior
print("Fixing INPUT statement documentation...")
count = fix_file('src/immediate_executor.py', [
    ('• INPUT statement is not allowed in immediate mode (use direct assignment instead)',
     '• INPUT statement works in immediate mode but will fail when input() is called (limitation of immediate execution)'),
])
if count > 0:
    fixes_made += count
    files_modified.append('src/immediate_executor.py')

# Fix 3: src/interactive.py - Fix EDIT mode comment
print("Fixing EDIT mode digit handling comment...")
count = fix_file('src/interactive.py', [
    ('Digits are silently ignored (not recognized as command prefixes or processed as commands).',
     'Digits fall through all if/elif branches and are silently ignored (count prefixes not yet implemented).'),
])
if count > 0:
    fixes_made += count
    files_modified.append('src/interactive.py')

# Fix 4: src/parser.py - Fix RND/INKEY$ comment
print("Fixing BASIC standard comment...")
count = fix_file('src/parser.py', [
    ('- Exception: RND and INKEY$ can be called without parentheses (standard BASIC)',
     '- Exception: RND and INKEY$ can be called without parentheses (MBASIC 5.21 behavior)'),
])
if count > 0:
    fixes_made += count
    files_modified.append('src/parser.py')

# Fix 5: src/lexer.py - Fix policy validation comment
print("Fixing lexer policy comment...")
count = fix_file('src/lexer.py', [
    ('No validation ensures only force_lower/force_upper/force_capitalize are used.',
     'SimpleKeywordCase validates and defaults to force_lower for invalid policies.'),
])
if count > 0:
    fixes_made += count
    files_modified.append('src/lexer.py')

# Fix 6: src/runtime.py - Clarify variable name significance
print("Fixing runtime variable comments...")
count = fix_file('src/runtime.py', [
    ('_resolve_variable_name() docstring:',
     '_resolve_variable_name() is the standard method for variable resolution.'),
])
if count > 0:
    fixes_made += count
    files_modified.append('src/runtime.py')

print(f"\n=== Summary ===")
print(f"Fixes applied: {fixes_made}")
print(f"Files modified: {len(set(files_modified))}")
if files_modified:
    print("\nModified files:")
    for f in sorted(set(files_modified)):
        print(f"  - {f}")
