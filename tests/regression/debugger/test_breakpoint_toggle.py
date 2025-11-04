#!/usr/bin/env python3
"""
Test the breakpoint toggle functionality for the curses UI.
"""

import sys
import os

# Add project root to path (3 levels up from tests/regression/*/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, 'src')

def test_breakpoint_toggle():
    print("=== Breakpoint Toggle Test ===\n")

    # Import after adding src to path
    from src.ui.curses_ui import ProgramEditorWidget

    # Create editor
    editor = ProgramEditorWidget()

    print("Test 1: Toggle breakpoint on/off")
    line1 = " " + "   10" + " " + "PRINT \"hello\""
    text = line1
    editor.edit_widget.set_edit_text(text)
    editor.edit_widget.set_edit_pos(7)  # Position at start of code

    print(f"  Initial state: breakpoints={editor.breakpoints}")
    assert len(editor.breakpoints) == 0, "Should start with no breakpoints"

    # Simulate getting status for line 10
    status = editor._get_status_char(10, has_syntax_error=False)
    print(f"  Line 10 status: '{status}' (expected ' ')")
    assert status == ' ', f"Expected ' ', got '{status}'"

    # Add breakpoint
    editor.breakpoints.add(10)
    print(f"  After adding: breakpoints={editor.breakpoints}")
    assert 10 in editor.breakpoints, "Breakpoint should be set"

    # Get status again
    status = editor._get_status_char(10, has_syntax_error=False)
    print(f"  Line 10 status: '{status}' (expected '●')")
    assert status == '●', f"Expected '●', got '{status}'"

    # Remove breakpoint
    editor.breakpoints.remove(10)
    print(f"  After removing: breakpoints={editor.breakpoints}")
    assert 10 not in editor.breakpoints, "Breakpoint should be removed"

    # Get status again
    status = editor._get_status_char(10, has_syntax_error=False)
    print(f"  Line 10 status: '{status}' (expected ' ')")
    assert status == ' ', f"Expected ' ', got '{status}'"
    print()

    print("Test 2: Breakpoint with syntax error (priority)")
    # Set breakpoint
    editor.breakpoints.add(20)
    print(f"  Set breakpoint on line 20: breakpoints={editor.breakpoints}")

    # Check status without error
    status = editor._get_status_char(20, has_syntax_error=False)
    print(f"  Line 20 status (no error): '{status}' (expected '●')")
    assert status == '●', f"Expected '●', got '{status}'"

    # Check status with error (error should have priority)
    status = editor._get_status_char(20, has_syntax_error=True)
    print(f"  Line 20 status (with error): '{status}' (expected '?')")
    assert status == '?', f"Expected '?', got '{status}'"

    # Remove error (breakpoint should show)
    status = editor._get_status_char(20, has_syntax_error=False)
    print(f"  Line 20 status (error fixed): '{status}' (expected '●')")
    assert status == '●', f"Expected '●', got '{status}'"
    print()

    print("Test 3: Multiple breakpoints")
    editor.breakpoints.clear()
    editor.breakpoints.add(10)
    editor.breakpoints.add(20)
    editor.breakpoints.add(30)
    print(f"  Set breakpoints on 10, 20, 30: breakpoints={editor.breakpoints}")
    assert len(editor.breakpoints) == 3, "Should have 3 breakpoints"

    # Check each line
    for line_num in [10, 20, 30]:
        status = editor._get_status_char(line_num, has_syntax_error=False)
        print(f"  Line {line_num} status: '{status}' (expected '●')")
        assert status == '●', f"Expected '●' for line {line_num}, got '{status}'"

    # Remove one breakpoint
    editor.breakpoints.remove(20)
    print(f"  Removed breakpoint from line 20: breakpoints={editor.breakpoints}")
    assert 20 not in editor.breakpoints, "Line 20 should not have breakpoint"
    assert 10 in editor.breakpoints, "Line 10 should still have breakpoint"
    assert 30 in editor.breakpoints, "Line 30 should still have breakpoint"
    print()

    print("✅ All tests passed!")

if __name__ == '__main__':
    test_breakpoint_toggle()
