#!/usr/bin/env python3
"""
Convert all text files in docs/ to Unix-style LF line endings.

Skip:
- .pdf (binary)
- .mac (need CRLF for CP/M M80 assembler)

Convert:
- .md, .txt, .bas, .json, .sh, .py, .pl, .css
"""

import sys
from pathlib import Path


def convert_file_to_lf(file_path: Path) -> tuple[bool, str]:
    """
    Convert a file to LF line endings.

    Returns:
        (changed, description) - whether file was changed and what was done
    """
    try:
        # Read as binary to preserve exact bytes
        content = file_path.read_bytes()

        # Check what EOL style(s) exist
        has_crlf = b'\r\n' in content
        has_cr = b'\r' in content
        has_lf = b'\n' in content

        # Determine current EOL style
        if has_crlf:
            # CRLF found - convert to LF
            new_content = content.replace(b'\r\n', b'\n')
            if new_content != content:
                file_path.write_bytes(new_content)
                return True, "CRLF -> LF"
            else:
                return False, "already LF"
        elif has_cr and not has_lf:
            # Only CR (old Mac style) - convert to LF
            new_content = content.replace(b'\r', b'\n')
            file_path.write_bytes(new_content)
            return True, "CR -> LF"
        elif has_lf:
            # Already LF only
            return False, "already LF"
        else:
            # No line endings (single line file or empty)
            return False, "no EOL"

    except Exception as e:
        return False, f"ERROR: {e}"


def main():
    docs_dir = Path("docs")

    if not docs_dir.exists():
        print(f"ERROR: {docs_dir} does not exist")
        return 1

    # File extensions to convert (skip .pdf and .mac)
    convert_exts = {'.md', '.txt', '.bas', '.json', '.sh', '.py', '.pl', '.css'}

    # Find all files in docs/
    all_files = list(docs_dir.rglob("*"))
    files_to_convert = [f for f in all_files if f.is_file() and f.suffix.lower() in convert_exts]

    print(f"Found {len(files_to_convert)} text files to convert")
    print(f"(Skipping .pdf and .mac files)")
    print()

    # Track statistics
    stats = {
        "CRLF -> LF": 0,
        "CR -> LF": 0,
        "already LF": 0,
        "no EOL": 0,
        "ERROR": 0
    }

    # Convert each file
    for file_path in sorted(files_to_convert):
        changed, description = convert_file_to_lf(file_path)

        # Update stats
        for key in stats:
            if key in description:
                stats[key] += 1
                break

        # Print only changed files
        if changed:
            rel_path = file_path.relative_to(docs_dir)
            print(f"{description:15} {rel_path}")

    # Print summary
    print()
    print("Summary:")
    print(f"  Converted CRLF -> LF: {stats['CRLF -> LF']}")
    print(f"  Converted CR -> LF:   {stats['CR -> LF']}")
    print(f"  Already LF:           {stats['already LF']}")
    print(f"  No EOL:               {stats['no EOL']}")
    if stats['ERROR'] > 0:
        print(f"  Errors:               {stats['ERROR']}")
    print()
    print(f"Total changed: {stats['CRLF -> LF'] + stats['CR -> LF']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
