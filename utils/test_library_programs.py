#!/usr/bin/env python3
"""
Test all BASIC programs in the library categories.

Tests each program to ensure it:
1. Loads without parse errors
2. Starts execution
3. Either produces output or stops for input

Categories tested (excludes 'incompatible'):
- games
- utilities
- demos
- education
- business
- telecommunications
- electronics
- data_management
- ham_radio
"""

import subprocess
import sys
from pathlib import Path
import tempfile
import time

# Categories to test (all published categories, excluding incompatible)
CATEGORIES = [
    "games",
    "utilities",
    "demos",
    "education",
    "business",
    "telecommunications",
    "electronics",
    "data_management",
    "ham_radio"
]

# Root directory
ROOT = Path(__file__).parent.parent
BASIC_DIR = ROOT / "basic"

# Test results
results = {
    "success": [],      # Programs that loaded and ran
    "parse_error": [],  # Programs with syntax errors
    "runtime_error": [], # Programs that crashed during execution
    "timeout": [],      # Programs that didn't stop (infinite loop or waiting for input)
    "no_output": []     # Programs that loaded but produced no output
}


def test_program(filepath: Path, timeout_secs: int = 5) -> tuple[str, str]:
    """
    Test a single BASIC program.

    Returns:
        tuple[status, message] where status is one of:
        - "success": Program ran successfully
        - "parse_error": Program failed to parse
        - "runtime_error": Program crashed during execution
        - "timeout": Program timed out (likely waiting for input or infinite loop)
        - "no_output": Program loaded but produced no output
    """
    # Create a temporary input file with some default responses
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        # Provide some generic inputs that might help programs continue
        for _ in range(10):
            f.write("test\n")
            f.write("1\n")
            f.write("y\n")
            f.write("n\n")
        input_file = f.name

    try:
        # Run the program with timeout
        cmd = [sys.executable, str(ROOT / "mbasic"), str(filepath)]

        with open(input_file, 'r') as stdin:
            result = subprocess.run(
                cmd,
                stdin=stdin,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout_secs,
                text=True
            )

        # Check results
        stderr = result.stderr.strip()
        stdout = result.stdout.strip()

        # Parse errors show up in stderr
        if "Error" in stderr or "Traceback" in stderr:
            if "SyntaxError" in stderr or "ParseError" in stderr:
                return "parse_error", stderr[:200]
            else:
                return "runtime_error", stderr[:200]

        # Success if we got output
        if stdout:
            return "success", f"Output: {stdout[:100]}"

        # Loaded but no output
        return "no_output", "No output produced"

    except subprocess.TimeoutExpired:
        # Program timed out - likely waiting for input or infinite loop
        return "timeout", f"Timed out after {timeout_secs}s (likely waiting for INPUT)"

    except Exception as e:
        return "runtime_error", f"Exception: {str(e)[:200]}"

    finally:
        # Cleanup temp file
        Path(input_file).unlink(missing_ok=True)


def main():
    """Test all programs in all published categories."""

    print("=" * 80)
    print("MBASIC Library Program Test Suite")
    print("=" * 80)
    print()
    print(f"Testing categories: {', '.join(CATEGORIES)}")
    print(f"Root directory: {ROOT}")
    print(f"Basic directory: {BASIC_DIR}")
    print()

    total_programs = 0

    # Test each category
    for category in CATEGORIES:
        category_dir = BASIC_DIR / category

        if not category_dir.exists():
            print(f"⚠️  Category directory not found: {category_dir}")
            continue

        # Get all .bas files in category
        bas_files = sorted(category_dir.glob("*.bas"))

        if not bas_files:
            print(f"⚠️  No .bas files found in {category}")
            continue

        print(f"\n{'=' * 80}")
        print(f"Testing category: {category.upper()} ({len(bas_files)} programs)")
        print(f"{'=' * 80}")

        for bas_file in bas_files:
            total_programs += 1
            print(f"\nTesting: {bas_file.name}...", end=" ", flush=True)

            status, message = test_program(bas_file)
            results[status].append((category, bas_file.name, message))

            # Print result with emoji
            status_emoji = {
                "success": "✅",
                "parse_error": "❌",
                "runtime_error": "💥",
                "timeout": "⏱️",
                "no_output": "📭"
            }

            print(f"{status_emoji[status]} {status}")
            if status != "success" and status != "timeout":
                print(f"    → {message}")

    # Print summary
    print("\n")
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print(f"Total programs tested: {total_programs}")
    print()
    print(f"✅ Success:        {len(results['success']):3d} programs")
    print(f"⏱️  Timeout:        {len(results['timeout']):3d} programs (likely INPUT or loops)")
    print(f"📭 No output:      {len(results['no_output']):3d} programs")
    print(f"❌ Parse errors:   {len(results['parse_error']):3d} programs")
    print(f"💥 Runtime errors: {len(results['runtime_error']):3d} programs")

    # Detailed breakdown
    if results['parse_error']:
        print("\n" + "=" * 80)
        print("PARSE ERRORS")
        print("=" * 80)
        for category, filename, message in results['parse_error']:
            print(f"\n{category}/{filename}")
            print(f"  {message}")

    if results['runtime_error']:
        print("\n" + "=" * 80)
        print("RUNTIME ERRORS")
        print("=" * 80)
        for category, filename, message in results['runtime_error']:
            print(f"\n{category}/{filename}")
            print(f"  {message}")

    if results['timeout']:
        print("\n" + "=" * 80)
        print("TIMEOUTS (Likely waiting for INPUT)")
        print("=" * 80)
        for category, filename, message in results['timeout']:
            print(f"  {category}/{filename}")

    if results['no_output']:
        print("\n" + "=" * 80)
        print("NO OUTPUT")
        print("=" * 80)
        for category, filename, message in results['no_output']:
            print(f"  {category}/{filename}")

    # Exit code based on results
    if results['parse_error'] or results['runtime_error']:
        print("\n❌ Some programs failed with errors")
        return 1
    else:
        print("\n✅ All programs loaded successfully")
        return 0


if __name__ == "__main__":
    sys.exit(main())
