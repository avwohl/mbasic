#!/usr/bin/env python3
"""
Utility to determine the next available version number for docs inconsistencies reports.

Scans ../../docs/history/ for files matching docs_inconsistencies_report-v[0-9]*.md
and returns the next version number based on the highest numbered file with non-zero size.

Usage:
    from get_next_report_filename import get_next_report_filename
    filename = get_next_report_filename()
"""

import re
from pathlib import Path
from typing import Optional


def get_next_report_filename() -> str:
    """
    Find the highest version number from existing non-empty report files and return next filename.

    Returns:
        str: The next report filename (e.g., "docs_inconsistencies_report-v11.md")
    """
    # Get the history directory relative to this script
    script_dir = Path(__file__).parent
    history_dir = script_dir / "../../docs/history"
    history_dir = history_dir.resolve()

    if not history_dir.exists():
        print(f"Warning: History directory not found: {history_dir}")
        print("Defaulting to version 1")
        return "docs_inconsistencies_report-v1.md"

    # Pattern to match version numbers
    pattern = re.compile(r'docs_inconsistencies_report-v(\d+)\.md$')

    max_version = 0

    # Scan for existing report files
    for file_path in history_dir.glob("docs_inconsistencies_report-v*.md"):
        # Check if file has non-zero size
        if file_path.stat().st_size == 0:
            print(f"Skipping empty file: {file_path.name}")
            continue

        # Extract version number
        match = pattern.search(file_path.name)
        if match:
            version = int(match.group(1))
            if version > max_version:
                max_version = version
                print(f"Found version {version}: {file_path.name} (size: {file_path.stat().st_size} bytes)")

    # Next version is max + 1
    next_version = max_version + 1
    next_filename = f"docs_inconsistencies_report-v{next_version}.md"

    print(f"\nNext version number: {next_version}")
    print(f"Next filename: {next_filename}")

    return next_filename


if __name__ == "__main__":
    """Test jig for the filename picker."""
    print("=" * 60)
    print("Testing get_next_report_filename()")
    print("=" * 60)
    print()

    filename = get_next_report_filename()

    print()
    print("=" * 60)
    print(f"Result: {filename}")
    print("=" * 60)
