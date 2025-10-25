#!/usr/bin/env python3
"""
Test output area scrolling with cursor visibility.
"""

import sys
sys.path.insert(0, 'src')

def test_output_scrolling():
    """Test that output scrolling works and cursor follows."""

    print("=== Output Scrolling Test ===\n")

    print("Manual test procedure:")
    print()
    print("1. Start curses UI:")
    print("   python3 mbasic.py")
    print()
    print("2. Enter test program:")
    print("   10 FOR I = 1 TO 30")
    print("   20 PRINT \"Line\"; I")
    print("   30 NEXT I")
    print("   40 END")
    print()
    print("3. Run with Ctrl+R")
    print()
    print("4. Press Tab to switch to output area")
    print()
    print("5. Test scrolling:")
    print("   - Press Up arrow")
    print("   - Watch for green cursor on first character")
    print("   - Cursor should move UP to previous line")
    print("   - Green highlight should be visible")
    print()
    print("   - Press Down arrow")
    print("   - Cursor should move DOWN to next line")
    print("   - Green highlight should follow")
    print()
    print("Expected behavior:")
    print("  ✓ Green cursor on first char of bottom line initially")
    print("  ✓ Up arrow moves cursor up one line")
    print("  ✓ Down arrow moves cursor down one line")
    print("  ✓ Only ONE line has green cursor at a time")
    print("  ✓ Cursor stays visible as you scroll")
    print()
    print("If cursor doesn't move:")
    print("  ✗ Problem: Focus not changing in ListBox")
    print("  ✗ Problem: Keypresses not reaching ListBox")
    print("  ✗ Problem: render() not called with focus changes")
    print()

if __name__ == '__main__':
    test_output_scrolling()
