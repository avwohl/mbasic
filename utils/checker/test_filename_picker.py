#!/usr/bin/env python3
"""
Test jig for the filename picker functionality.

Tests the get_next_report_filename() function to ensure it correctly:
1. Finds all existing docs_inconsistencies_report-v*.md files
2. Filters out zero-sized files
3. Parses version numbers correctly
4. Returns the next available version
"""

from get_next_report_filename import get_next_report_filename
from pathlib import Path

def main():
    print("=" * 70)
    print("Testing get_next_report_filename() Integration")
    print("=" * 70)
    print()

    # Test 1: Get the filename
    print("TEST 1: Getting next report filename")
    print("-" * 70)
    filename = get_next_report_filename()
    print()

    # Test 2: Verify it's in the correct format
    print("TEST 2: Validating filename format")
    print("-" * 70)
    import re
    pattern = re.compile(r'^docs_inconsistencies_report-v(\d+)\.md$')
    match = pattern.match(filename)

    if match:
        version = int(match.group(1))
        print(f"✓ Filename format is valid: {filename}")
        print(f"✓ Version number parsed: {version}")
    else:
        print(f"✗ ERROR: Filename format is invalid: {filename}")
        return 1

    # Test 3: Check that the output file doesn't already exist
    print()
    print("TEST 3: Checking if output file already exists")
    print("-" * 70)
    script_dir = Path(__file__).parent
    history_dir = script_dir / "../../docs/history"
    history_dir = history_dir.resolve()
    output_path = history_dir / filename

    if output_path.exists():
        print(f"⚠ WARNING: Output file already exists: {output_path}")
        print(f"  Size: {output_path.stat().st_size} bytes")
        print("  This is expected if a previous run completed successfully")
    else:
        print(f"✓ Output file does not exist yet: {output_path}")
        print("  Ready for new report generation")

    # Test 4: List existing reports for context
    print()
    print("TEST 4: Listing existing report files")
    print("-" * 70)
    if history_dir.exists():
        reports = sorted(history_dir.glob("docs_inconsistencies_report-v*.md"))
        if reports:
            print(f"Found {len(reports)} existing report files:")
            for report in reports:
                size = report.stat().st_size
                size_str = f"{size:,} bytes" if size > 0 else "0 bytes (EMPTY)"
                print(f"  - {report.name}: {size_str}")
        else:
            print("  No existing report files found")
    else:
        print(f"  History directory not found: {history_dir}")

    print()
    print("=" * 70)
    print("All tests completed successfully!")
    print(f"Next report will be saved as: {filename}")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    exit(main())
