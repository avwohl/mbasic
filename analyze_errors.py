#!/usr/bin/env python3
"""
Analyze lexer errors to find patterns and common issues
"""
import re
from pathlib import Path
from collections import defaultdict
from lexer import tokenize, LexerError


def is_tokenized_basic(filepath):
    """Check if file is tokenized BASIC (starts with 0xFF)"""
    try:
        with open(filepath, 'rb') as f:
            first_byte = f.read(1)
            return len(first_byte) > 0 and first_byte[0] == 0xFF
    except:
        return False


def analyze_file(filepath):
    """Analyze a file and return error details"""
    if is_tokenized_basic(filepath):
        return None, None, None

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            source = f.read()

        if not source.strip():
            return None, None, None

        tokenize(source)
        return None, None, None  # Success

    except LexerError as e:
        # Extract error details
        match = re.search(r"Unexpected character: '(.*)' \((0x[0-9a-f]+)\)", str(e))
        if match:
            char = match.group(1)
            hex_code = match.group(2)
            return 'unexpected_char', (char, hex_code), str(e)

        if 'Unterminated string' in str(e):
            return 'unterminated_string', None, str(e)

        if 'Invalid' in str(e):
            return 'invalid_syntax', None, str(e)

        return 'other', None, str(e)
    except Exception as e:
        return 'exception', None, str(e)


def main():
    bas_dir = Path('bas_tests1')
    if not bas_dir.exists():
        print("Error: bas_tests1/ directory not found")
        return 1

    bas_files = sorted(list(bas_dir.glob('*.bas')) + list(bas_dir.glob('*.BAS')))

    print(f"Analyzing {len(bas_files)} files...\n")

    # Categorize errors
    error_categories = defaultdict(list)
    char_errors = defaultdict(list)
    success_count = 0

    for filepath in bas_files:
        category, details, message = analyze_file(filepath)

        if category is None:
            success_count += 1
        else:
            error_categories[category].append((filepath.name, message))
            if category == 'unexpected_char' and details:
                char, hex_code = details
                char_errors[hex_code].append(filepath.name)

    # Print summary
    print("=" * 80)
    print("ERROR ANALYSIS SUMMARY")
    print("=" * 80)
    print(f"Total files: {len(bas_files)}")
    print(f"Successfully parsed: {success_count}")
    print(f"Files with errors: {len(bas_files) - success_count}\n")

    # Unexpected character analysis
    if char_errors:
        print("=" * 80)
        print("UNEXPECTED CHARACTER ERRORS (by frequency)")
        print("=" * 80)

        sorted_chars = sorted(char_errors.items(), key=lambda x: len(x[1]), reverse=True)

        for hex_code, files in sorted_chars[:15]:  # Top 15
            # Determine character description
            code_int = int(hex_code, 16)
            if code_int == 0x2e:
                char_desc = ". (period/dot)"
            elif code_int == 0x5b:
                char_desc = "[ (left bracket)"
            elif code_int == 0x5d:
                char_desc = "] (right bracket)"
            elif code_int == 0x24:
                char_desc = "$ (dollar sign)"
            elif code_int == 0x26:
                char_desc = "& (ampersand)"
            elif code_int == 0x40:
                char_desc = "@ (at sign)"
            elif code_int < 32:
                char_desc = f"<control char>"
            else:
                try:
                    char_desc = f"{chr(code_int)}"
                except:
                    char_desc = "<unprintable>"

            print(f"{hex_code} {char_desc:30} {len(files):3} files")
            if len(files) <= 5:
                for fname in files:
                    print(f"    {fname}")

        print()

    # Other error categories
    for category, file_list in sorted(error_categories.items()):
        if category != 'unexpected_char':
            print("=" * 80)
            print(f"{category.upper().replace('_', ' ')}: {len(file_list)} files")
            print("=" * 80)
            for fname, msg in file_list[:5]:  # Show first 5
                print(f"{fname}: {msg[:100]}")
            if len(file_list) > 5:
                print(f"... and {len(file_list) - 5} more")
            print()

    # Detailed analysis of top issues
    print("=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)

    if 0x2e in [int(h, 16) for h in char_errors.keys()]:
        period_count = len(char_errors.get('0x2e', []))
        print(f"\n1. PERIOD (.) - {period_count} files affected")
        print("   Issue: Period appearing outside number context")
        print("   Common cases:")
        print("   - Commodore BASIC abbreviated commands (P. for PRINT)")
        print("   - Statement continuation")
        print("   - Non-MBASIC dialect")
        print("   Action: May need dialect-specific handling or skip these files")

    if 0x5b in [int(h, 16) for h in char_errors.keys()]:
        bracket_count = len(char_errors.get('0x5b', []))
        print(f"\n2. SQUARE BRACKETS [ ] - {bracket_count} files affected")
        print("   Issue: Square brackets used instead of parentheses")
        print("   Common cases:")
        print("   - Arrays: DIM A[10] instead of DIM A(10)")
        print("   - Function calls with []")
        print("   - Control sequences in strings")
        print("   Action: Add optional bracket support or mark as non-MBASIC")

    if 0x40 in [int(h, 16) for h in char_errors.keys()]:
        at_count = len(char_errors.get('0x40', []))
        print(f"\n3. AT SIGN (@) - {at_count} files affected")
        print("   Issue: @ used as operator or special character")
        print("   Common cases:")
        print("   - Cursor positioning: @(X,Y)")
        print("   - TRS-80 or other dialect-specific syntax")
        print("   Action: May need dialect detection")

    return 0


if __name__ == "__main__":
    exit(main())
