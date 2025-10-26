#!/usr/bin/env python3
"""
Fix formatting issues in function documentation files.

Common issues from OCR:
- Excessive leading spaces in example output
- Multiple consecutive spaces in text
- Hyphenated words like "the-natural"
- "ASClI" instead of "ASCII"
- Page headers like "BASIC-SO FUNCTIONS                                      Page 3-3"
"""

import re
from pathlib import Path

def fix_file(file_path: Path) -> bool:
    """Fix formatting issues in a single file. Returns True if changes were made."""
    with open(file_path, 'r') as f:
        content = f.read()

    original = content
    lines = content.split('\n')
    fixed_lines = []
    in_code_block = False

    for line in lines:
        # Track code blocks
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            fixed_lines.append(line)
            continue

        # Skip YAML front matter
        if line.strip() == '---':
            fixed_lines.append(line)
            continue

        # Remove page headers (BASIC-80/SO FUNCTIONS ... Page X-X)
        if re.match(r'^BASIC-[0-9SO]+\s+FUNCTIONS\s+Page\s+\d+-\d+\s*$', line):
            continue

        # In code blocks, fix excessive leading spaces in output lines
        if in_code_block:
            # Remove page headers even in code blocks
            if re.match(r'^BASIC-[0-9SO]+\s+FUNCTIONS\s+Page\s+\d+-\d+\s*$', line.strip()):
                continue

            # Fix common OCR errors even in code blocks
            line = line.replace('ASClI', 'ASCII')

            # If line has 10+ leading spaces, reduce to 1 space
            if re.match(r'^\s{10,}', line):
                line = ' ' + line.lstrip()

            # Fix multiple spaces in code block text
            if not line.strip().startswith('PRINT') and not line.strip().startswith('RUN'):
                line = re.sub(r'([^\s])\s{3,}([^\s])', r'\1 \2', line)

            fixed_lines.append(line)
            continue

        # Outside code blocks, fix text issues
        # Fix multiple consecutive spaces (but preserve single leading spaces)
        line = re.sub(r'([^\s])\s{2,}([^\s])', r'\1 \2', line)

        # Fix common OCR errors
        line = line.replace('ASClI', 'ASCII')
        line = line.replace('the-natural', 'the natural')
        line = line.replace('the-ASCII', 'the ASCII')
        line = line.replace('the-integer', 'the integer')
        line = line.replace('the-double', 'the double')
        line = line.replace('the-single', 'the single')
        line = line.replace('the-fractional', 'the fractional')

        fixed_lines.append(line)

    fixed_content = '\n'.join(fixed_lines)

    if fixed_content != original:
        with open(file_path, 'w') as f:
            f.write(fixed_content)
        return True
    return False

def main():
    """Fix all function documentation files."""
    func_dir = Path('/home/wohl/cl/mbasic/docs/help/common/language/functions')

    if not func_dir.exists():
        print(f"Error: {func_dir} does not exist")
        return 1

    fixed_count = 0
    total_count = 0

    for file_path in sorted(func_dir.glob('*.md')):
        if file_path.name == 'index.md':
            continue

        total_count += 1
        if fix_file(file_path):
            print(f"Fixed: {file_path.name}")
            fixed_count += 1

    print(f"\nFixed {fixed_count} out of {total_count} files")
    return 0

if __name__ == '__main__':
    exit(main())
