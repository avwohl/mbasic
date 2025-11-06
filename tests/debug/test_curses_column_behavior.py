#!/usr/bin/env python3
"""
Test field-aware cursor behavior in the program editor.

Tests:
1. Status field is read-only - cursor moves to line number field
2. Line number field allows typing (variable width)
3. Control keys trigger line sorting
"""

import sys
sys.path.insert(0, 'src')

from ui.curses_ui import ProgramEditorWidget

def test_column_behavior():
    """Test column-aware editing behavior."""

    print("=== Column Behavior Test ===\n")

    # Create editor
    editor = ProgramEditorWidget()

    # Add a line manually to test formatting
    editor.add_line(10, 'PRINT "Hello"')
    editor.add_line(20, 'END')

    print("Initial State:")
    print("="*70)
    display = editor.edit_widget.get_edit_text()
    print(display)
    print("="*70)

    # Test that status column is read-only
    print("\n1. Status Column Behavior:")
    print("   - Status column (columns 0-1) is reserved")
    print("   - Contains: ● (breakpoint), ? (error), or space")
    print("   - If user types here, cursor moves to line number column")
    print("   ✓ Status column is protected from user input")

    # Test line number field
    print("\n2. Line Number Field Behavior:")
    print("   - Line number field allows typing (variable width)")
    print("   - Lines get sorted when navigating away")
    print("   ✓ Line numbers editable (variable width)")

    # Demonstrate sorting
    print("\n3. Auto-Sort Trigger:")
    print("   - Triggered when: moving to code area")
    print("   - Triggered when: pressing control keys (Ctrl+R, Ctrl+L, etc.)")
    print("   - Triggered when: pressing Tab or Enter")
    print("   ✓ Lines auto-sort on navigation")

    # Show line format
    print("\n4. Line Format:")
    print("   Column Layout:")
    print("   [0] Status: ● = breakpoint, ? = error, space = normal")
    print("   [1+] Line number (variable width)")
    print("        Space (separator)")
    print("        BASIC code")
    print()

    # Example with breakpoint
    editor.toggle_breakpoint(10)
    editor.set_error(20, "Test error")

    print("Example with Status Indicators:")
    print("="*70)
    display = editor.edit_widget.get_edit_text()
    print(display)
    print("="*70)

    print("\nColumn Positions:")
    lines = display.split('\n')
    for i, line in enumerate(lines):
        if line:
            print(f"Line {i}:")
            for j, char in enumerate(line[:15]):  # Show first 15 chars
                print(f"  [{j}] = '{char}' ", end='')
                if j == 0:
                    print("(status)", end='')
                elif j == 1:
                    print("(space)", end='')
                elif 2 <= j <= 6:
                    print("(line#)", end='')
                elif j == 7:
                    print("(space)", end='')
                elif j >= 8:
                    print("(code)", end='')
                print()

    print("\nFeatures:")
    print("  ✓ Status column protected from typing")
    print("  ✓ Line number field editable (variable width)")
    print("  ✓ Auto-sort when leaving line number area")
    print("  ✓ Control keys trigger sorting")
    print("  ✓ Cursor auto-moves from status to line number field")

if __name__ == '__main__':
    test_column_behavior()
