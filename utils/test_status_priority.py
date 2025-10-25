#!/usr/bin/env python3
"""
Test the status column priority system for the curses UI.
"""

import sys
sys.path.insert(0, 'src')

# Create a mock for SimpleFocusListWalker
class MockWalker:
    def __init__(self):
        self.lines = []

    def clear(self):
        self.lines = []

    def append(self, item):
        self.lines.append(item)

    def set_focus(self, index):
        pass

    def __len__(self):
        return len(self.lines)

# Test the status priority behavior
def test_status_priority():
    print("=== Status Column Priority Test ===\n")

    # Import after adding src to path
    from ui.curses_ui import ProgramEditorWidget

    # Create editor
    editor = ProgramEditorWidget()
    editor._output_walker = MockWalker()

    print("Priority order: Error (?) > Breakpoint (●) > Normal ( )\n")

    print("Test 1: _get_status_char() returns correct priority")
    print("  Normal (no error, no breakpoint):")
    status = editor._get_status_char(10, has_syntax_error=False)
    print(f"    Line 10: '{status}' (expected ' ')")
    assert status == ' ', f"Expected ' ', got '{status}'"

    print("  Breakpoint (no error, has breakpoint):")
    editor.breakpoints.add(20)
    status = editor._get_status_char(20, has_syntax_error=False)
    print(f"    Line 20: '{status}' (expected '●')")
    assert status == '●', f"Expected '●', got '{status}'"

    print("  Error only (has error, no breakpoint):")
    status = editor._get_status_char(30, has_syntax_error=True)
    print(f"    Line 30: '{status}' (expected '?')")
    assert status == '?', f"Expected '?', got '{status}'"

    print("  Error + Breakpoint (has both - error wins):")
    editor.breakpoints.add(40)
    status = editor._get_status_char(40, has_syntax_error=True)
    print(f"    Line 40: '{status}' (expected '?')")
    assert status == '?', f"Expected '?', got '{status}'"
    print()

    print("Test 2: Breakpoint preserved when error is fixed")
    # Format: "SNNNNN CODE"
    # Line 10 has error, line 20 has error + breakpoint
    editor.breakpoints.clear()
    editor.breakpoints.add(20)

    line1 = " " + "   10" + " " + "foo"        # Error only
    line2 = " " + "   20" + " " + "bar"        # Error + breakpoint (starts as space)
    text = line1 + "\n" + line2

    print("  Initial state:")
    print(f"    Line 10: 'foo' (error, no breakpoint)")
    print(f"    Line 20: 'bar' (error + breakpoint)")

    # Run syntax check - should mark both as errors
    new_text = editor._update_syntax_errors(text)
    lines = new_text.split('\n')

    print("  After first syntax check:")
    print(f"    Line 10 status: '{lines[0][0]}' (expected '?')")
    print(f"    Line 20 status: '{lines[1][0]}' (expected '?')")
    assert lines[0][0] == '?', f"Line 10 should have error status"
    assert lines[1][0] == '?', f"Line 20 should have error status"

    # Fix line 20 to valid code
    line1 = "?" + "   10" + " " + "foo"        # Still error
    line2 = "?" + "   20" + " " + "PRINT \"ok\""  # Fixed, but had error status
    text = line1 + "\n" + line2

    print("  Fixed line 20 to 'PRINT \"ok\"'")

    # Run syntax check again - line 20 should show breakpoint
    new_text = editor._update_syntax_errors(text)
    lines = new_text.split('\n')

    print("  After second syntax check:")
    print(f"    Line 10 status: '{lines[0][0]}' (expected '?' - still error)")
    print(f"    Line 20 status: '{lines[1][0]}' (expected '●' - breakpoint shown)")
    assert lines[0][0] == '?', f"Line 10 should still have error status"
    assert lines[1][0] == '●', f"Line 20 should show breakpoint after error fixed"
    print()

    print("Test 3: Breakpoint preserved when empty line")
    editor.breakpoints.clear()
    editor.breakpoints.add(10)

    line1 = " " + "   10" + " " + "PRINT \"test\""  # Valid code with breakpoint
    text = line1

    # Run syntax check - should show breakpoint
    new_text = editor._update_syntax_errors(text)
    print(f"  Line 10 with code: status='{new_text[0]}' (expected '●')")
    assert new_text[0] == '●', f"Line 10 should show breakpoint"

    # Clear the code (make it empty)
    line1 = "●" + "   10" + " "  # Empty code, but has breakpoint status
    text = line1

    # Run syntax check on empty line - should preserve breakpoint
    new_text = editor._update_syntax_errors(text)
    print(f"  Line 10 now empty: status='{new_text[0]}' (expected '●' - breakpoint preserved)")
    assert new_text[0] == '●', f"Line 10 should preserve breakpoint when empty"
    print()

    print("✅ All tests passed!")

if __name__ == '__main__':
    test_status_priority()
