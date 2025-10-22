"""
Test parser against entire BASIC corpus
"""

import sys
from pathlib import Path

# Add src directory to path so we can import compiler modules
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from lexer import tokenize, LexerError
from parser import parse, ParseError
from ast_nodes import *


def test_file(filepath):
    """Test lexer and parser on a single file"""
    try:
        # Read file
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            code = f.read()

        # Tokenize
        try:
            tokens = tokenize(code)
        except LexerError as e:
            return ('lexer_error', str(e))
        except Exception as e:
            return ('lexer_exception', str(e))

        # Parse
        try:
            ast = parse(tokens)

            # Count statements
            stmt_count = 0
            for line in ast.lines:
                stmt_count += len(line.statements)

            return ('success', {
                'lines': len(ast.lines),
                'statements': stmt_count,
                'tokens': len(tokens)
            })
        except ParseError as e:
            return ('parser_error', str(e))
        except Exception as e:
            return ('parser_exception', str(e))

    except Exception as e:
        return ('file_error', str(e))


def main():
    """Run parser tests on all .bas files"""

    # Find all .bas files in bas_tests1 directory
    test_dir = Path('bas_tests1')
    if not test_dir.exists():
        print(f"Error: {test_dir} directory not found")
        return 1

    bas_files = sorted(test_dir.glob('*.bas'))

    if not bas_files:
        print(f"No .bas files found in {test_dir}")
        return 1

    print("=" * 80)
    print(f"Testing Parser on {len(bas_files)} BASIC files")
    print("=" * 80)
    print()

    results = {
        'success': [],
        'lexer_error': [],
        'lexer_exception': [],
        'parser_error': [],
        'parser_exception': [],
        'file_error': []
    }

    # Test each file
    for i, filepath in enumerate(bas_files, 1):
        if i % 10 == 0:
            print(f"Progress: {i}/{len(bas_files)} files tested...", file=sys.stderr)

        result_type, result_data = test_file(filepath)
        results[result_type].append((filepath.name, result_data))

    # Print results
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)
    print()

    # Success
    success_count = len(results['success'])
    print(f"✓ Successfully parsed: {success_count}/{len(bas_files)} ({100*success_count/len(bas_files):.1f}%)")

    if results['success']:
        total_lines = sum(r[1]['lines'] for r in results['success'])
        total_stmts = sum(r[1]['statements'] for r in results['success'])
        total_tokens = sum(r[1]['tokens'] for r in results['success'])
        print(f"  Total: {total_lines:,} lines, {total_stmts:,} statements, {total_tokens:,} tokens")

    # Lexer failures
    lexer_fail = len(results['lexer_error']) + len(results['lexer_exception'])
    if lexer_fail > 0:
        print(f"\n✗ Lexer failures: {lexer_fail} ({100*lexer_fail/len(bas_files):.1f}%)")
        print(f"  - Lexer errors: {len(results['lexer_error'])}")
        print(f"  - Lexer exceptions: {len(results['lexer_exception'])}")

    # Parser failures
    parser_fail = len(results['parser_error']) + len(results['parser_exception'])
    if parser_fail > 0:
        print(f"\n✗ Parser failures: {parser_fail} ({100*parser_fail/len(bas_files):.1f}%)")
        print(f"  - Parser errors: {len(results['parser_error'])}")
        print(f"  - Parser exceptions: {len(results['parser_exception'])}")

    # File errors
    if results['file_error']:
        print(f"\n✗ File errors: {len(results['file_error'])}")

    # Detailed breakdown of parser errors
    if results['parser_error']:
        print("\n" + "=" * 80)
        print("PARSER ERROR BREAKDOWN")
        print("=" * 80)

        error_types = {}
        for filename, error_msg in results['parser_error']:
            # Extract error type from message
            if 'Expected' in error_msg:
                error_type = error_msg.split(':')[-1].strip().split('\n')[0]
            elif 'Unexpected' in error_msg:
                error_type = error_msg.split(':')[-1].strip().split('\n')[0]
            elif 'not yet implemented' in error_msg:
                error_type = error_msg.split(':')[-1].strip()
            else:
                error_type = error_msg[:80]

            if error_type not in error_types:
                error_types[error_type] = []
            error_types[error_type].append(filename)

        print()
        for error_type, files in sorted(error_types.items(), key=lambda x: -len(x[1])):
            print(f"{len(files):3} files: {error_type}")
            if len(files) <= 5:
                for f in files:
                    print(f"       - {f}")

    # Sample of successful files
    if results['success']:
        print("\n" + "=" * 80)
        print("SAMPLE SUCCESSFUL PARSES (largest files)")
        print("=" * 80)
        print()

        # Sort by number of statements
        sorted_success = sorted(results['success'], key=lambda x: x[1]['statements'], reverse=True)

        for filename, data in sorted_success[:10]:
            print(f"  {filename:30} {data['lines']:4} lines, {data['statements']:5} statements")

    # Files that need attention
    if results['parser_error']:
        print("\n" + "=" * 80)
        print("SAMPLE FILES NEEDING ATTENTION")
        print("=" * 80)
        print()

        for filename, error_msg in results['parser_error'][:10]:
            error_line = error_msg.split('\n')[0][:70]
            print(f"  {filename:30} {error_line}")

    print("\n" + "=" * 80)
    print(f"SUMMARY: {success_count}/{len(bas_files)} files parsed successfully")
    print("=" * 80)

    return 0 if success_count == len(bas_files) else 1


if __name__ == '__main__':
    sys.exit(main())
