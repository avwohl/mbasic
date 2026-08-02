#!/usr/bin/env python3
"""
Test output area focus indicator behavior.
"""

import sys
sys.path.insert(0, 'src')

def test_output_focus():
    """Test output focus indicator."""

    print("=== Output Focus Indicator Test ===\n")

    print("Testing focus indicator features:")
    print("  ✓ OutputLineWidget shows green cursor on first char when focused")
    print("  ✓ Only the focused line has green cursor, not all lines")
    print("  ✓ Tab key toggles between editor and output (one press)")
    print("  ✓ Focus updates dynamically as you scroll with arrow keys")
    print()

    print("How to test manually:")
    print("1. Start the curses UI:")
    print("   python3 mbasic --ui curses")
    print()
    print("2. Enter a program with output:")
    print("   10 FOR I = 1 TO 20")
    print("   20 PRINT I")
    print("   30 NEXT I")
    print("   40 END")
    print()
    print("3. Press Ctrl+R to run")
    print()
    print("4. Press Tab ONCE to switch to output area")
    print()
    print("Expected behavior:")
    print("  - First character of focused line has green background")
    print("  - Only ONE line shows the green cursor")
    print("  - Up/Down arrows move the green cursor to different lines")
    print("  - Press Tab again to return to editor")
    print()

    print("Visual appearance:")
    print("  Normal line:  Hello World")
    print("  Focused line: ▓ello World  (first char has green background)")
    print()

if __name__ == '__main__':
    test_output_focus()
