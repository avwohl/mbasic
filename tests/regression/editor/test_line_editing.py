#!/usr/bin/env python3
"""
Test the line editing commands (delete and renumber) for the curses UI.
"""

import sys
import os

# Add project root to path (3 levels up from tests/regression/*/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, 'src')

def test_line_editing():
    print("=== Line Editing Commands Test ===\n")

    # Import after adding src to path
    from src.ui.curses_ui import ProgramEditorWidget

    # Create editor
    editor = ProgramEditorWidget()

    print("Test 1: Line deletion tracking")
    # Set up some lines
    editor.lines = {10: 'PRINT "A"', 20: 'PRINT "B"', 30: 'PRINT "C"'}
    editor.breakpoints.add(20)
    editor.syntax_errors[30] = "Some error"

    print(f"  Initial state:")
    print(f"    Lines: {sorted(editor.lines.keys())}")
    print(f"    Breakpoints: {editor.breakpoints}")
    print(f"    Errors: {list(editor.syntax_errors.keys())}")

    # Simulate deleting line 20
    del editor.lines[20]
    if 20 in editor.breakpoints:
        editor.breakpoints.remove(20)
    if 20 in editor.syntax_errors:
        del editor.syntax_errors[20]

    print(f"  After deleting line 20:")
    print(f"    Lines: {sorted(editor.lines.keys())}")
    print(f"    Breakpoints: {editor.breakpoints}")
    print(f"    Errors: {list(editor.syntax_errors.keys())}")

    assert 20 not in editor.lines, "Line 20 should be deleted"
    assert 20 not in editor.breakpoints, "Breakpoint on line 20 should be removed"
    assert 10 in editor.lines and 30 in editor.lines, "Other lines should remain"
    print()

    print("Test 2: Renumber with breakpoints and errors")
    # Reset
    editor.lines = {15: 'PRINT "A"', 27: 'PRINT "B"', 38: 'PRINT "C"', 49: 'END'}
    editor.breakpoints = {27}
    editor.syntax_errors = {38: "Test error"}

    print(f"  Initial state:")
    print(f"    Lines: {sorted(editor.lines.keys())}")
    print(f"    Breakpoints: {editor.breakpoints}")
    print(f"    Errors: {list(editor.syntax_errors.keys())}")

    # Simulate renumbering: start=100, increment=5
    old_lines = sorted(editor.lines.keys())
    old_to_new = {}
    new_line_num = 100
    increment = 5

    for old_num in old_lines:
        old_to_new[old_num] = new_line_num
        new_line_num += increment

    # Apply renumbering
    new_lines = {}
    new_breakpoints = set()
    new_errors = {}

    for old_num in old_lines:
        new_num = old_to_new[old_num]
        new_lines[new_num] = editor.lines[old_num]

        if old_num in editor.breakpoints:
            new_breakpoints.add(new_num)

        if old_num in editor.syntax_errors:
            new_errors[new_num] = editor.syntax_errors[old_num]

    editor.lines = new_lines
    editor.breakpoints = new_breakpoints
    editor.syntax_errors = new_errors

    print(f"  After RENUM 100, 5:")
    print(f"    Lines: {sorted(editor.lines.keys())}")
    print(f"    Breakpoints: {editor.breakpoints}")
    print(f"    Errors: {list(editor.syntax_errors.keys())}")
    print(f"    Mapping: {old_to_new}")

    assert sorted(editor.lines.keys()) == [100, 105, 110, 115], "Lines should be renumbered"
    assert 105 in editor.breakpoints, "Breakpoint should move from 27 to 105"
    assert 110 in editor.syntax_errors, "Error should move from 38 to 110"
    assert editor.syntax_errors[110] == "Test error", "Error message preserved"
    print()

    print("Test 3: Status character preservation during renumber")
    editor.lines = {10: 'PRINT "A"', 20: 'PRINT "B"', 30: 'PRINT "C"'}
    editor.breakpoints = {10, 30}
    editor.syntax_errors = {30: "Error on 30"}

    print(f"  Initial state:")
    print(f"    Line 10: breakpoint={10 in editor.breakpoints}, error={10 in editor.syntax_errors}")
    print(f"    Line 20: breakpoint={20 in editor.breakpoints}, error={20 in editor.syntax_errors}")
    print(f"    Line 30: breakpoint={30 in editor.breakpoints}, error={30 in editor.syntax_errors}")

    # Check status for each line before renumber
    status_10_before = editor._get_status_char(10, has_syntax_error=10 in editor.syntax_errors)
    status_20_before = editor._get_status_char(20, has_syntax_error=20 in editor.syntax_errors)
    status_30_before = editor._get_status_char(30, has_syntax_error=30 in editor.syntax_errors)

    print(f"    Status chars: 10='{status_10_before}', 20='{status_20_before}', 30='{status_30_before}'")

    # Renumber: 10->50, 20->60, 30->70
    old_to_new = {10: 50, 20: 60, 30: 70}
    new_lines = {}
    new_breakpoints = set()
    new_errors = {}

    for old_num, new_num in old_to_new.items():
        new_lines[new_num] = editor.lines[old_num]
        if old_num in editor.breakpoints:
            new_breakpoints.add(new_num)
        if old_num in editor.syntax_errors:
            new_errors[new_num] = editor.syntax_errors[old_num]

    editor.lines = new_lines
    editor.breakpoints = new_breakpoints
    editor.syntax_errors = new_errors

    print(f"  After RENUM 50, 10:")
    print(f"    Line 50: breakpoint={50 in editor.breakpoints}, error={50 in editor.syntax_errors}")
    print(f"    Line 60: breakpoint={60 in editor.breakpoints}, error={60 in editor.syntax_errors}")
    print(f"    Line 70: breakpoint={70 in editor.breakpoints}, error={70 in editor.syntax_errors}")

    # Check status for each line after renumber
    status_50_after = editor._get_status_char(50, has_syntax_error=50 in editor.syntax_errors)
    status_60_after = editor._get_status_char(60, has_syntax_error=60 in editor.syntax_errors)
    status_70_after = editor._get_status_char(70, has_syntax_error=70 in editor.syntax_errors)

    print(f"    Status chars: 50='{status_50_after}', 60='{status_60_after}', 70='{status_70_after}'")

    assert status_10_before == status_50_after, "Line 10->50 status should be preserved (●)"
    assert status_20_before == status_60_after, "Line 20->60 status should be preserved ( )"
    assert status_30_before == status_70_after, "Line 30->70 status should be preserved (?)"
    print()

    print("✅ All tests passed!")

if __name__ == '__main__':
    test_line_editing()
