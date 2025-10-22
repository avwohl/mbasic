#!/usr/bin/env python3
"""
Test the lexer against all .bas files in the project
"""
import os
import sys
from pathlib import Path
from lexer import tokenize, LexerError


def is_tokenized_basic(filepath):
    """Check if file is tokenized BASIC (starts with 0xFF)"""
    try:
        with open(filepath, 'rb') as f:
            first_byte = f.read(1)
            return len(first_byte) > 0 and first_byte[0] == 0xFF
    except:
        return False


def test_bas_file(filepath):
    """Test if lexer can parse a BASIC file"""
    # Skip tokenized BASIC files
    if is_tokenized_basic(filepath):
        return 'TOKENIZED', None, 0

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            source = f.read()

        # Skip empty files
        if not source.strip():
            return 'EMPTY', None, 0

        # Try to tokenize
        tokens = tokenize(source)
        return 'SUCCESS', None, len(tokens)

    except LexerError as e:
        return 'LEXER_ERROR', str(e), 0
    except UnicodeDecodeError as e:
        return 'ENCODING_ERROR', str(e), 0
    except Exception as e:
        return 'ERROR', str(type(e).__name__ + ': ' + str(e)), 0


def main():
    # Find all .bas files in bas_tests1/ directory
    bas_dir = Path('bas_tests1')
    if not bas_dir.exists():
        print("Error: bas_tests1/ directory not found")
        return 1

    bas_files = []
    for ext in ['*.bas', '*.BAS']:
        bas_files.extend(bas_dir.glob(ext))

    # Sort by name
    bas_files = sorted(bas_files)

    print(f"Found {len(bas_files)} BASIC files\n")
    print("=" * 80)

    # Statistics
    stats = {
        'SUCCESS': [],
        'TOKENIZED': [],
        'EMPTY': [],
        'LEXER_ERROR': [],
        'ENCODING_ERROR': [],
        'ERROR': []
    }

    # Test each file
    for filepath in bas_files:
        status, error, token_count = test_bas_file(filepath)
        stats[status].append(filepath)

        if status == 'SUCCESS':
            print(f"✓ {filepath.name:30} {token_count:5} tokens")
        elif status == 'TOKENIZED':
            print(f"⊗ {filepath.name:30} (tokenized, skipped)")
        elif status == 'EMPTY':
            print(f"○ {filepath.name:30} (empty)")
        elif status == 'LEXER_ERROR':
            print(f"✗ {filepath.name:30} LEXER ERROR")
            print(f"  {error}")
        elif status == 'ENCODING_ERROR':
            print(f"⚠ {filepath.name:30} (encoding issue)")
        else:
            print(f"✗ {filepath.name:30} ERROR")
            print(f"  {error}")

    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total files:          {len(bas_files)}")
    print(f"Successfully parsed:  {len(stats['SUCCESS'])}")
    print(f"Tokenized (skipped):  {len(stats['TOKENIZED'])}")
    print(f"Empty files:          {len(stats['EMPTY'])}")
    print(f"Lexer errors:         {len(stats['LEXER_ERROR'])}")
    print(f"Encoding errors:      {len(stats['ENCODING_ERROR'])}")
    print(f"Other errors:         {len(stats['ERROR'])}")

    success_rate = len(stats['SUCCESS']) / (len(bas_files) - len(stats['TOKENIZED']) - len(stats['EMPTY'])) * 100 if (len(bas_files) - len(stats['TOKENIZED']) - len(stats['EMPTY'])) > 0 else 0
    print(f"\nSuccess rate:         {success_rate:.1f}% (excluding tokenized and empty files)")

    # Show first few errors in detail
    if stats['LEXER_ERROR']:
        print("\n" + "=" * 80)
        print("FIRST 5 LEXER ERRORS (for debugging)")
        print("=" * 80)
        for filepath in stats['LEXER_ERROR'][:5]:
            print(f"\n{filepath}:")
            status, error, _ = test_bas_file(filepath)
            print(f"  {error}")

            # Show first few lines of the file
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()[:10]
                print("  First 10 lines:")
                for i, line in enumerate(lines, 1):
                    print(f"    {i:3}: {line.rstrip()}")
            except:
                pass

    return 0 if not stats['LEXER_ERROR'] else 1


if __name__ == "__main__":
    sys.exit(main())
