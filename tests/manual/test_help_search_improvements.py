#!/usr/bin/env python3
"""
Manual test for help system search improvements.

Tests:
1. Search ranking (exact title > keyword > description)
2. Fuzzy matching (typos like "PRNT" finds "PRINT")
3. In-page search (Ctrl+F functionality)

Usage:
    python3 tests/manual/test_help_search_improvements.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import tkinter as tk
from src.ui.tk_help_browser import TkHelpBrowser


def test_search_improvements():
    """Test the help search improvements."""
    print("Testing Help Search Improvements")
    print("=" * 60)
    print()
    print("This test opens the TK help browser.")
    print()
    print("TEST 1: Search Ranking")
    print("  1. Search for 'print' in the search box")
    print("  2. Verify 'PRINT' statement appears first (exact title match)")
    print("  3. Other print-related topics should follow")
    print()
    print("TEST 2: Fuzzy Matching")
    print("  1. Search for 'prnt' (typo)")
    print("  2. Should still find 'PRINT' statement (fuzzy match)")
    print("  3. Search for 'inpt' (typo)")
    print("  4. Should find 'INPUT' statement (fuzzy match)")
    print()
    print("TEST 3: In-Page Search")
    print("  1. Open any help page (e.g., click on PRINT)")
    print("  2. Press Ctrl+F")
    print("  3. Search bar should appear at top")
    print("  4. Type a word (e.g., 'statement')")
    print("  5. All matches should be highlighted in yellow")
    print("  6. Current match should be orange")
    print("  7. Click 'Next' / 'Prev' to navigate")
    print("  8. Press Escape or click 'Close' to close search")
    print()
    print("=" * 60)
    print()

    # Create root window
    root = tk.Tk()
    root.withdraw()  # Hide main window

    # Get help root
    help_root = Path(__file__).parent.parent.parent / 'docs' / 'help'

    # Create help browser
    browser = TkHelpBrowser(root, str(help_root))

    # Run
    root.mainloop()

    print("\nTest complete!")


if __name__ == '__main__':
    test_search_improvements()
