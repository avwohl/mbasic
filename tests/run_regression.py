#!/usr/bin/env python3
"""
MBASIC Regression Test Runner

Discovers and runs all regression tests in tests/regression/.
Exit code 0 if all pass, 1 if any fail.

Usage:
    python3 tests/run_regression.py                    # Run all tests
    python3 tests/run_regression.py --category lexer   # Run specific category
    python3 tests/run_regression.py --verbose          # Detailed output
"""

import sys
import os
import subprocess
from pathlib import Path
import argparse


class TestRunner:
    """Discovers and runs regression tests."""

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.passed = []
        self.failed = []
        self.errors = []
        # Tests that exited 2 to report they could not run (e.g. an optional
        # dependency such as urwid is absent). Reported separately so they are
        # never mistaken for passes.
        self.skipped = []

    def discover_tests(self, base_dir: Path, category=None):
        """
        Discover all test_*.py files in regression directory.

        Args:
            base_dir: Base tests/regression/ directory
            category: Optional category subdirectory (lexer, parser, etc.)

        Returns:
            List of test file paths
        """
        search_dir = base_dir / category if category else base_dir

        if not search_dir.exists():
            print(f"❌ Error: Directory not found: {search_dir}")
            return []

        # Find all test_*.py files recursively
        tests = list(search_dir.rglob("test_*.py"))
        return sorted(tests)

    def run_test(self, test_path: Path) -> bool:
        """
        Run a single test file.

        Args:
            test_path: Path to test file

        Returns:
            True if test passed, False if failed
        """
        try:
            # Get project root (tests/ parent directory)
            project_root = test_path.parent.parent.parent

            # Run the test as a subprocess from project root
            # Set PYTHONPATH to include project root so imports work
            env = os.environ.copy()
            env['PYTHONPATH'] = str(project_root) + os.pathsep + env.get('PYTHONPATH', '')

            result = subprocess.run(
                [sys.executable, str(test_path)],
                capture_output=True,
                text=True,
                # Long enough that a legitimately slow test is not killed, short
                # enough to catch a hang. It was 30s, which
                # regression/interpreter/test_error_messages.py sits right on:
                # it starts an interpreter per provocation, and on a two-core
                # machine that is ~25s, so it was being timed out on about half
                # of all runs. A timed-out test reports no output at all, so it
                # read as a mystery rather than as "this one needs longer".
                timeout=120,
                cwd=project_root,  # Run from project root
                env=env
            )

            if result.returncode == 2:
                # Exit code 2 means "could not run", not "passed". Counting it
                # as a pass would put a green tick on untested code.
                self.skipped.append((test_path, result.stdout.strip()))
                print(f"⊘ SKIP: {test_path.relative_to(test_path.parent.parent.parent)}")
                if result.stdout.strip():
                    print(f"  {result.stdout.strip()}")
                return True
            elif result.returncode == 0:
                self.passed.append(test_path)
                if self.verbose:
                    print(f"✓ PASS: {test_path.relative_to(test_path.parent.parent.parent)}")
                    if result.stdout.strip():
                        print(f"  Output: {result.stdout.strip()}")
                return True
            else:
                self.failed.append((test_path, result))
                print(f"✗ FAIL: {test_path.relative_to(test_path.parent.parent.parent)}")
                if result.stdout:
                    print(f"  stdout: {result.stdout}")
                if result.stderr:
                    print(f"  stderr: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            self.errors.append((test_path, "Timeout"))
            print(f"⏱ TIMEOUT: {test_path.relative_to(test_path.parent.parent.parent)}")
            return False
        except Exception as e:
            self.errors.append((test_path, str(e)))
            print(f"❌ ERROR: {test_path.relative_to(test_path.parent.parent.parent)}: {e}")
            return False

    def run_all(self, tests):
        """Run all discovered tests."""
        if not tests:
            print("No tests found.")
            return True

        print(f"\nRunning {len(tests)} regression tests...\n")
        print("=" * 60)

        for test in tests:
            self.run_test(test)

        # Print summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"✓ Passed:  {len(self.passed)}")
        print(f"✗ Failed:  {len(self.failed)}")
        print(f"⊘ Skipped: {len(self.skipped)}")
        print(f"❌ Errors:  {len(self.errors)}")
        print(f"Total:    {len(tests)}")

        if self.skipped:
            print("\nSkipped (not run - these verified nothing):")
            for test_path, reason in self.skipped:
                print(f"  {test_path.relative_to(test_path.parent.parent.parent)}"
                      f"{': ' + reason if reason else ''}")

        if self.failed or self.errors:
            print("\n❌ REGRESSION TESTS FAILED")
            return False
        else:
            print("\n✅ ALL REGRESSION TESTS PASSED")
            return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Run MBASIC regression tests'
    )
    parser.add_argument(
        '--category',
        help='Run only tests in specific category (lexer, parser, etc.)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed output for passing tests'
    )

    args = parser.parse_args()

    # Find tests/regression/ directory
    script_dir = Path(__file__).parent
    regression_dir = script_dir / 'regression'

    if not regression_dir.exists():
        print(f"Error: Regression test directory not found: {regression_dir}")
        return 1

    # Discover and run tests
    runner = TestRunner(verbose=args.verbose)
    tests = runner.discover_tests(regression_dir, args.category)

    if not tests:
        print(f"No tests found in {regression_dir}")
        if args.category:
            print(f"Category '{args.category}' may not exist.")
        return 1

    success = runner.run_all(tests)
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
