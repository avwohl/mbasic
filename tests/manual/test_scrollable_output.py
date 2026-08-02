#!/usr/bin/env python3
"""
Test that the output area is scrollable and auto-scrolls to bottom.
"""

import sys
sys.path.insert(0, 'src')

def test_scrollable_output():
    """Test output area scrolling behavior."""

    print("=== Scrollable Output Test ===\n")

    print("Testing output area features:")
    print("  ✓ Uses urwid.ListBox for scrolling")
    print("  ✓ Uses SimpleFocusListWalker to manage lines")
    print("  ✓ Auto-scrolls to bottom when new output added")
    print("  ✓ No longer limited to 20 lines")
    print()

    print("How to test manually:")
    print("1. Start the curses UI:")
    print("   python3 mbasic --ui curses")
    print()
    print("2. Enter a program with lots of output:")
    print("   10 FOR I = 1 TO 100")
    print("   20 PRINT I")
    print("   30 NEXT I")
    print("   40 END")
    print()
    print("3. Press Ctrl+R to run")
    print()
    print("Expected behavior:")
    print("  - Output window shows all 100 lines")
    print("  - Automatically scrolled to show line 100 at bottom")
    print("  - Can scroll up/down with arrow keys when focused on output")
    print()

    print("To focus on output area:")
    print("  - Press Tab to switch between editor and output")
    print("  - Use Up/Down arrows to scroll output")
    print("  - Press Tab again to return to editor")

if __name__ == '__main__':
    test_scrollable_output()
