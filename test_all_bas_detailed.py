"""
Comprehensive test of all .bas files with detailed reporting
"""

import sys
from pathlib import Path
from lexer import tokenize, LexerError
from parser import parse, ParseError
from ast_nodes import *


def test_file(filepath):
    """Test lexer and parser on a single file"""
    try:
        # Read file
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            code = f.read()

        file_size = len(code)

        # Tokenize
        try:
            tokens = tokenize(code)
            token_count = len(tokens)
        except LexerError as e:
            return {
                'status': 'lexer_error',
                'error': str(e),
                'file_size': file_size
            }
        except Exception as e:
            return {
                'status': 'lexer_exception',
                'error': str(e),
                'file_size': file_size
            }

        # Parse
        try:
            ast = parse(tokens)

            # Count statements by type
            stmt_counts = {}
            total_stmts = 0
            for line in ast.lines:
                for stmt in line.statements:
                    stmt_type = type(stmt).__name__
                    stmt_counts[stmt_type] = stmt_counts.get(stmt_type, 0) + 1
                    total_stmts += 1

            return {
                'status': 'success',
                'file_size': file_size,
                'lines': len(ast.lines),
                'statements': total_stmts,
                'tokens': token_count,
                'stmt_types': stmt_counts,
                'has_def_types': len([v for v in ast.def_type_statements.values() if v != 'SINGLE']) > 0
            }
        except ParseError as e:
            return {
                'status': 'parser_error',
                'error': str(e),
                'file_size': file_size,
                'tokens': token_count
            }
        except Exception as e:
            return {
                'status': 'parser_exception',
                'error': str(e),
                'file_size': file_size,
                'tokens': token_count
            }

    except Exception as e:
        return {
            'status': 'file_error',
            'error': str(e)
        }


def main():
    """Run comprehensive tests on all .bas files"""

    # Find all .bas files
    test_dir = Path('bas_tests1')
    if not test_dir.exists():
        print(f"Error: {test_dir} directory not found")
        return 1

    bas_files = sorted(test_dir.glob('*.bas'))

    if not bas_files:
        print(f"No .bas files found in {test_dir}")
        return 1

    print("=" * 100)
    print(f"COMPREHENSIVE TEST: {len(bas_files)} BASIC FILES")
    print("=" * 100)
    print()

    # Test all files
    results = {}
    for i, filepath in enumerate(bas_files, 1):
        if i % 50 == 0:
            print(f"Testing: {i}/{len(bas_files)}...", file=sys.stderr)

        result = test_file(filepath)
        results[filepath.name] = result

    print("\n" + "=" * 100)
    print("DETAILED RESULTS BY CATEGORY")
    print("=" * 100)

    # Categorize results
    success = {k: v for k, v in results.items() if v['status'] == 'success'}
    lexer_error = {k: v for k, v in results.items() if v['status'] == 'lexer_error'}
    lexer_exception = {k: v for k, v in results.items() if v['status'] == 'lexer_exception'}
    parser_error = {k: v for k, v in results.items() if v['status'] == 'parser_error'}
    parser_exception = {k: v for k, v in results.items() if v['status'] == 'parser_exception'}
    file_error = {k: v for k, v in results.items() if v['status'] == 'file_error'}

    # Print summary
    print(f"\n1. SUCCESSFULLY PARSED: {len(success)} files ({100*len(success)/len(bas_files):.1f}%)")
    print(f"2. LEXER ERRORS: {len(lexer_error)} files ({100*len(lexer_error)/len(bas_files):.1f}%)")
    print(f"3. LEXER EXCEPTIONS: {len(lexer_exception)} files ({100*len(lexer_exception)/len(bas_files):.1f}%)")
    print(f"4. PARSER ERRORS: {len(parser_error)} files ({100*len(parser_error)/len(bas_files):.1f}%)")
    print(f"5. PARSER EXCEPTIONS: {len(parser_exception)} files ({100*len(parser_exception)/len(bas_files):.1f}%)")
    print(f"6. FILE ERRORS: {len(file_error)} files ({100*len(file_error)/len(bas_files):.1f}%)")

    # Detailed success list
    if success:
        print("\n" + "=" * 100)
        print(f"SUCCESSFULLY PARSED FILES ({len(success)} files)")
        print("=" * 100)
        print(f"\n{'Filename':<30} {'Size':<8} {'Lines':<6} {'Stmts':<6} {'Tokens':<7} {'Stmt Types':<10}")
        print("-" * 100)

        # Sort by statement count
        sorted_success = sorted(success.items(), key=lambda x: x[1]['statements'], reverse=True)

        for filename, data in sorted_success:
            stmt_type_count = len(data['stmt_types'])
            print(f"{filename:<30} {data['file_size']:>7} {data['lines']:>6} {data['statements']:>6} "
                  f"{data['tokens']:>7} {stmt_type_count:>10}")

        # Statistics
        total_lines = sum(d['lines'] for d in success.values())
        total_stmts = sum(d['statements'] for d in success.values())
        total_tokens = sum(d['tokens'] for d in success.values())
        total_size = sum(d['file_size'] for d in success.values())

        print("-" * 100)
        print(f"{'TOTALS':<30} {total_size:>7} {total_lines:>6} {total_stmts:>6} {total_tokens:>7}")
        print(f"{'AVERAGES':<30} {total_size//len(success):>7} {total_lines//len(success):>6} "
              f"{total_stmts//len(success):>6} {total_tokens//len(success):>7}")

        # Statement type distribution
        print("\n" + "=" * 100)
        print("STATEMENT TYPE DISTRIBUTION (across all successful parses)")
        print("=" * 100)

        all_stmt_types = {}
        for data in success.values():
            for stmt_type, count in data['stmt_types'].items():
                all_stmt_types[stmt_type] = all_stmt_types.get(stmt_type, 0) + count

        print(f"\n{'Statement Type':<40} {'Count':<8} {'% of Total':<10}")
        print("-" * 100)

        total_stmt_count = sum(all_stmt_types.values())
        for stmt_type, count in sorted(all_stmt_types.items(), key=lambda x: -x[1]):
            pct = 100 * count / total_stmt_count
            print(f"{stmt_type:<40} {count:>7} {pct:>9.1f}%")

    # Lexer errors
    if lexer_error:
        print("\n" + "=" * 100)
        print(f"LEXER ERRORS ({len(lexer_error)} files)")
        print("=" * 100)

        error_types = {}
        for filename, data in lexer_error.items():
            error_msg = data['error'].split('\n')[0][:80]
            if error_msg not in error_types:
                error_types[error_msg] = []
            error_types[error_msg].append(filename)

        print(f"\n{'Error Type':<80} {'Count':<6}")
        print("-" * 100)

        for error_type, files in sorted(error_types.items(), key=lambda x: -len(x[1])):
            print(f"{error_type:<80} {len(files):>5}")
            if len(files) <= 3:
                for f in files:
                    print(f"  → {f}")

    # Parser errors
    if parser_error:
        print("\n" + "=" * 100)
        print(f"PARSER ERRORS ({len(parser_error)} files)")
        print("=" * 100)

        error_types = {}
        for filename, data in parser_error.items():
            # Extract error type
            error_msg = data['error']
            if 'Parse error' in error_msg:
                error_line = error_msg.split(':')[-1].strip().split('\n')[0][:60]
            else:
                error_line = error_msg[:60]

            if error_line not in error_types:
                error_types[error_line] = []
            error_types[error_line].append(filename)

        print(f"\n{'Error Type':<65} {'Count':<6}")
        print("-" * 100)

        for error_type, files in sorted(error_types.items(), key=lambda x: -len(x[1])):
            print(f"{error_type:<65} {len(files):>5}")
            if len(files) <= 3:
                for f in files:
                    print(f"  → {f}")

    # Parser exceptions
    if parser_exception:
        print("\n" + "=" * 100)
        print(f"PARSER EXCEPTIONS ({len(parser_exception)} files)")
        print("=" * 100)

        for filename, data in sorted(parser_exception.items())[:20]:
            error_msg = data['error'].split('\n')[0][:80]
            print(f"  {filename:<30} {error_msg}")

    # Write detailed results to files
    print("\n" + "=" * 100)
    print("WRITING DETAILED RESULTS TO FILES")
    print("=" * 100)

    with open('test_results_success.txt', 'w') as f:
        f.write(f"Successfully Parsed Files ({len(success)})\n")
        f.write("=" * 80 + "\n\n")
        for filename in sorted(success.keys()):
            f.write(f"{filename}\n")
    print(f"✓ Wrote test_results_success.txt ({len(success)} files)")

    with open('test_results_lexer_fail.txt', 'w') as f:
        f.write(f"Lexer Failures ({len(lexer_error) + len(lexer_exception)})\n")
        f.write("=" * 80 + "\n\n")
        for filename in sorted(list(lexer_error.keys()) + list(lexer_exception.keys())):
            f.write(f"{filename}\n")
    print(f"✓ Wrote test_results_lexer_fail.txt ({len(lexer_error) + len(lexer_exception)} files)")

    with open('test_results_parser_fail.txt', 'w') as f:
        f.write(f"Parser Failures ({len(parser_error) + len(parser_exception)})\n")
        f.write("=" * 80 + "\n\n")
        for filename in sorted(list(parser_error.keys()) + list(parser_exception.keys())):
            data = results[filename]
            error = data.get('error', 'Unknown error')[:200]
            f.write(f"{filename}\n  {error}\n\n")
    print(f"✓ Wrote test_results_parser_fail.txt ({len(parser_error) + len(parser_exception)} files)")

    # Final summary
    print("\n" + "=" * 100)
    print("FINAL SUMMARY")
    print("=" * 100)
    print(f"\nTotal files tested: {len(bas_files)}")
    print(f"Successfully parsed: {len(success)} ({100*len(success)/len(bas_files):.1f}%)")
    print(f"Lexer failures: {len(lexer_error) + len(lexer_exception)} ({100*(len(lexer_error) + len(lexer_exception))/len(bas_files):.1f}%)")
    print(f"Parser failures: {len(parser_error) + len(parser_exception)} ({100*(len(parser_error) + len(parser_exception))/len(bas_files):.1f}%)")

    if success:
        print(f"\nSuccessfully parsed programs contain:")
        print(f"  - {sum(d['lines'] for d in success.values()):,} lines of code")
        print(f"  - {sum(d['statements'] for d in success.values()):,} statements")
        print(f"  - {sum(d['tokens'] for d in success.values()):,} tokens")

    print("\n" + "=" * 100)

    return 0


if __name__ == '__main__':
    sys.exit(main())
