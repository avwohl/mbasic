#!/usr/bin/env python3
"""
Convert BASIC files to CP/M format (CRLF line endings + EOF marker).

Usage:
    python3 utils/convert_to_cpm.py input.bas [output.bas]

If output filename is not specified, overwrites the input file.
"""

import sys
from pathlib import Path


def convert_to_cpm(input_file: Path, output_file: Path = None) -> None:
    """
    Convert a file to CP/M format:
    - LF (\n) -> CRLF (\r\n)
    - Add CP/M EOF marker (\x1a) at end if not present

    Args:
        input_file: Input file path
        output_file: Output file path (defaults to input_file)
    """
    if output_file is None:
        output_file = input_file

    # Read file as binary
    content = input_file.read_bytes()

    # Normalize to LF first (in case already has mixed CRLF/LF)
    content = content.replace(b'\r\n', b'\n')
    content = content.replace(b'\r', b'\n')

    # Convert LF to CRLF
    content = content.replace(b'\n', b'\r\n')

    # Add CP/M EOF marker if not present
    if not content.endswith(b'\x1a'):
        content += b'\x1a'

    # Write back
    output_file.write_bytes(content)

    if output_file == input_file:
        print(f"Converted {input_file} to CP/M format (CRLF + EOF marker)")
    else:
        print(f"Converted {input_file} -> {output_file} (CP/M format)")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nError: No input file specified")
        return 1

    input_path = Path(sys.argv[1])

    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        return 1

    # Output path is optional
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else input_path

    try:
        convert_to_cpm(input_path, output_path)
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
