#!/usr/bin/env python3
"""
Move tokenized BASIC files (starting with 0xFF) to bas_tok directory
"""
import os
import shutil
from pathlib import Path


def is_tokenized_basic(filepath):
    """Check if file is tokenized BASIC (starts with 0xFF)"""
    try:
        with open(filepath, 'rb') as f:
            first_byte = f.read(1)
            return len(first_byte) > 0 and first_byte[0] == 0xFF
    except:
        return False


def main():
    bas_dir = Path('bas')
    tok_dir = Path('bas_tok')

    if not bas_dir.exists():
        print("Error: bas/ directory not found")
        return 1

    # Ensure bas_tok directory exists
    tok_dir.mkdir(exist_ok=True)

    # Find all .bas files
    bas_files = list(bas_dir.glob('*.bas')) + list(bas_dir.glob('*.BAS'))

    moved_count = 0

    for filepath in sorted(bas_files):
        if is_tokenized_basic(filepath):
            dest = tok_dir / filepath.name
            print(f"Moving {filepath.name} -> bas_tok/")
            shutil.move(str(filepath), str(dest))
            moved_count += 1

    print(f"\nMoved {moved_count} tokenized files to bas_tok/")
    return 0


if __name__ == "__main__":
    exit(main())
