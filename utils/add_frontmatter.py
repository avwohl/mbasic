#!/usr/bin/env python3
"""
Add YAML front matter to existing help files.

This script analyzes markdown files and adds appropriate front matter
based on file location, content, and manual categorization.
"""

import frontmatter
import re
from pathlib import Path
from typing import Dict, Optional


# Categorization mapping
STATEMENT_CATEGORIES = {
    # Input/Output
    'input': 'input-output',
    'print': 'input-output',
    'print-using': 'input-output',
    'write': 'input-output',
    'writei': 'input-output',
    'lprint': 'input-output',
    'lprint-using': 'input-output',

    # Control flow
    'if-then-else-if-goto': 'control-flow',
    'for-next': 'control-flow',
    'while-wend': 'control-flow',
    'goto': 'control-flow',
    'gosub-return': 'control-flow',
    'on-gosub-on-goto': 'control-flow',
    'on-error-goto': 'error-handling',

    # File I/O
    'open': 'file-io',
    'close': 'file-io',
    'field': 'file-io',
    'get': 'file-io',
    'put': 'file-io',
    'inputi': 'file-io',
    'line-inputi': 'file-io',
    'printi-printi-using': 'file-io',

    # File management
    'load': 'file-management',
    'save': 'file-management',
    'merge': 'file-management',
    'kill': 'file-management',
    'name': 'file-management',
    'run': 'file-management',
    'chain': 'program-control',

    # Data
    'data': 'data',
    'read': 'data',
    'restore': 'data',

    # Arrays
    'dim': 'arrays',
    'erase': 'arrays',
    'option-base': 'arrays',

    # Variables
    'let': 'variables',
    'swap': 'variables',
    'defint-defsng-defdbl-defstr': 'variables',

    # Functions
    'def-fn': 'functions',

    # Error handling
    'error': 'error-handling',
    'resume': 'error-handling',
    'err-erl': 'error-handling',

    # Strings
    'mid_dollar': 'strings',

    # Hardware
    'poke': 'hardware',
    'out': 'hardware',
    'call': 'hardware',
    'wait': 'hardware',

    # Program control
    'clear': 'program-control',
    'common': 'program-control',
    'cont': 'program-control',
    'end': 'program-control',
    'new': 'program-control',
    'stop': 'program-control',

    # Editing
    'auto': 'editing',
    'delete': 'editing',
    'edit': 'editing',
    'list': 'editing',
    'llist': 'editing',
    'renum': 'editing',

    # System
    'null': 'system',
    'randomize': 'system',
    'rem': 'system',
    'tron-troff': 'system',
    'width': 'system',
}

FUNCTION_CATEGORIES = {
    # Mathematical
    'abs': 'mathematical',
    'atn': 'mathematical',
    'cos': 'mathematical',
    'exp': 'mathematical',
    'fix': 'mathematical',
    'int': 'mathematical',
    'log': 'mathematical',
    'rnd': 'mathematical',
    'sgn': 'mathematical',
    'sin': 'mathematical',
    'sqr': 'mathematical',
    'tan': 'mathematical',

    # String
    'asc': 'string',
    'chr_dollar': 'string',
    'hex_dollar': 'string',
    'instr': 'string',
    'left_dollar': 'string',
    'len': 'string',
    'mid_dollar': 'string',
    'right_dollar': 'string',
    'space_dollar': 'string',
    'spc': 'string',
    'str_dollar': 'string',
    'string_dollar': 'string',
    'val': 'string',

    # Type conversion
    'cdbl': 'type-conversion',
    'cint': 'type-conversion',
    'cvd': 'type-conversion',
    'cvi': 'type-conversion',
    'cvs': 'type-conversion',
    'mkd_dollar': 'type-conversion',
    'mki_dollar': 'type-conversion',
    'mks_dollar': 'type-conversion',

    # File I/O
    'eof': 'file-io',
    'input_dollar': 'file-io',
    'loc': 'file-io',
    'lof': 'file-io',
    'lpos': 'file-io',
    'pos': 'file-io',

    # System
    'fre': 'system',
    'inkey_dollar': 'system',
    'inp': 'system',
    'peek': 'system',
    'usr': 'system',
    'varptr': 'system',
}


def infer_metadata_from_file(file_path: Path, content: str) -> Dict:
    """
    Infer front matter metadata from file location and content.

    Args:
        file_path: Path to markdown file
        content: File content

    Returns:
        Dictionary of inferred metadata
    """
    metadata = {}

    # Get title from first heading
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        title = match.group(1).strip()
        # Clean up title (remove extra spaces, formatting)
        title = re.sub(r'\s+', ' ', title)
        metadata['title'] = title

    # Infer type from directory structure
    parts = file_path.parts
    if 'statements' in parts:
        metadata['type'] = 'statement'
    elif 'functions' in parts:
        metadata['type'] = 'function'
    elif 'appendices' in parts:
        metadata['type'] = 'reference'
    elif 'ui' in parts:
        metadata['type'] = 'guide'
    elif 'mbasic' in parts:
        metadata['type'] = 'guide'
    else:
        metadata['type'] = 'guide'

    # Infer category from filename and type
    filename = file_path.stem.lower()

    if metadata['type'] == 'statement':
        category = STATEMENT_CATEGORIES.get(filename, 'NEEDS_CATEGORIZATION')
        metadata['category'] = category
    elif metadata['type'] == 'function':
        category = FUNCTION_CATEGORIES.get(filename, 'NEEDS_CATEGORIZATION')
        metadata['category'] = category

    # Add description placeholder
    metadata['description'] = 'NEEDS_DESCRIPTION'

    # Add keywords placeholder
    metadata['keywords'] = ['NEEDS_KEYWORDS']

    return metadata


def add_frontmatter_to_file(file_path: Path, metadata: Optional[Dict] = None,
                             dry_run: bool = True, force: bool = False) -> bool:
    """
    Add front matter to a markdown file if it doesn't have it.

    Args:
        file_path: Path to markdown file
        metadata: Optional metadata to add/merge
        dry_run: If True, show what would be done without doing it
        force: If True, update existing front matter

    Returns:
        True if file was modified (or would be in dry run)
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        post = frontmatter.load(f)

    # If already has front matter and not forcing, skip
    if post.metadata and not force:
        if not dry_run:
            print(f"✓ {file_path.name} - already has front matter (use --force to update)")
        return False

    # Infer metadata from content
    inferred = infer_metadata_from_file(file_path, post.content)

    # Merge with provided metadata (provided takes precedence)
    final_metadata = {**inferred, **(metadata or {})}

    # Create or update post with front matter
    if post.metadata:
        # Merge with existing
        post.metadata.update(final_metadata)
    else:
        post.metadata = final_metadata

    if dry_run:
        print(f"\n{'='*60}")
        print(f"Would add to: {file_path}")
        print(f"{'='*60}")
        for key, value in final_metadata.items():
            print(f"  {key}: {value}")
        return True
    else:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))
        print(f"✓ Added front matter to {file_path.name}")
        return True


def process_directory(directory: Path, dry_run: bool = True,
                      force: bool = False, pattern: str = "*.md") -> None:
    """
    Process all markdown files in a directory.

    Args:
        directory: Directory to process
        dry_run: If True, show what would be done
        force: If True, update existing front matter
        pattern: File pattern to match
    """
    files = list(directory.rglob(pattern))

    # Skip index files
    files = [f for f in files if f.name.lower() != 'index.md']

    if not files:
        print(f"No matching files found in {directory}")
        return

    print(f"\nFound {len(files)} files to process")
    print("=" * 60)

    modified_count = 0
    for file_path in files:
        if add_frontmatter_to_file(file_path, dry_run=dry_run, force=force):
            modified_count += 1

    print(f"\n{'='*60}")
    if dry_run:
        print(f"Would modify {modified_count} files")
        print("Run without --dry-run to actually modify files")
    else:
        print(f"Modified {modified_count} files")


def main():
    """Command-line interface."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Add YAML front matter to help files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run - show what would be done
  %(prog)s docs/help/language/statements --dry-run

  # Actually add front matter
  %(prog)s docs/help/language/statements

  # Update existing front matter
  %(prog)s docs/help/language/statements --force

  # Single file
  %(prog)s docs/help/language/statements/print.md
        """
    )

    parser.add_argument('path', type=Path,
                       help='File or directory to process')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without doing it')
    parser.add_argument('--force', action='store_true',
                       help='Update existing front matter')
    parser.add_argument('--pattern', default='*.md',
                       help='File pattern to match (default: *.md)')

    args = parser.parse_args()

    if not args.path.exists():
        print(f"Error: {args.path} does not exist")
        return 1

    if args.path.is_file():
        # Process single file
        add_frontmatter_to_file(args.path, dry_run=args.dry_run,
                                force=args.force)
    else:
        # Process directory
        process_directory(args.path, dry_run=args.dry_run,
                         force=args.force, pattern=args.pattern)

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
