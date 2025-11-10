#!/usr/bin/env python3
"""
Run all tests in basic/dev/tests_with_results/ and compare outputs.
"""

import subprocess
import sys
from pathlib import Path

def run_test(test_file):
    """Run a single test and return output."""
    cmd = ['python3', 'mbasic', '--ui', 'cli', str(test_file)]
    # Send RUN command to execute the program and SYSTEM to exit
    result = subprocess.run(cmd, input="RUN\nSYSTEM\n", capture_output=True, text=True, timeout=10)

    # Filter out the interactive prompt lines
    lines = result.stdout.split('\n')
    filtered_lines = []
    for line in lines:
        if line.startswith('MBASIC-'):
            continue
        if line.startswith('100%'):
            continue
        if line.startswith('(Tip:'):
            continue
        if line.startswith('Type HELP'):
            continue
        if line == 'Ready':
            continue
        if line == 'Goodbye':
            continue
        filtered_lines.append(line)

    return '\n'.join(filtered_lines)

def main():
    test_dir = Path('basic/dev/tests_with_results')

    if not test_dir.exists():
        print(f"Error: {test_dir} does not exist")
        return 1

    # Find all .bas files
    test_files = sorted(test_dir.glob('*.bas'))

    if not test_files:
        print("No test files found")
        return 1

    print(f"Running {len(test_files)} tests...\n")

    passed = 0
    failed = 0
    skipped = 0

    for test_file in test_files:
        test_name = test_file.stem
        expected_file = test_dir / f"{test_name}.txt"

        print(f"Testing {test_name}...", end=' ')

        if not expected_file.exists():
            print("? No expected output file")
            skipped += 1
            continue

        try:
            # Run the test
            actual_output = run_test(test_file)

            # Read expected output
            expected_output = expected_file.read_text()

            # Compare
            if actual_output.strip() == expected_output.strip():
                print("✓ PASS")
                passed += 1
            else:
                print("✗ FAIL - Output differs")
                failed += 1

                # Show diff
                print(f"\n  Expected output file: {expected_file}")
                print("  First difference:")
                actual_lines = actual_output.strip().split('\n')
                expected_lines = expected_output.strip().split('\n')
                for i, (actual, expected) in enumerate(zip(actual_lines, expected_lines)):
                    if actual != expected:
                        print(f"    Line {i+1}:")
                        print(f"      Expected: {repr(expected)}")
                        print(f"      Got:      {repr(actual)}")
                        break
                if len(actual_lines) != len(expected_lines):
                    print(f"    Line count: expected {len(expected_lines)}, got {len(actual_lines)}")
                print()

        except subprocess.TimeoutExpired:
            print("✗ TIMEOUT")
            failed += 1
        except Exception as e:
            print(f"✗ ERROR: {e}")
            failed += 1

    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed, {skipped} skipped")
    print(f"{'='*60}")

    return 0 if failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
