#!/usr/bin/env python3
"""
Test the syntax checking logic for the curses UI.
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

# Test the syntax checking behavior
def test_syntax_checking():
    print("=== Syntax Checking Behavior Test ===\n")

    # Import after adding src to path
    from ui.curses_ui import ProgramEditorWidget

    # Create editor
    editor = ProgramEditorWidget()
    editor._output_walker = MockWalker()

    print("Test 1: Check that incomplete line 'FOR I = 1' shows error when checked")
    text = " 10 FOR I = 1"
    result = editor._check_line_syntax("FOR I = 1")
    print(f"  Code: 'FOR I = 1'")
    print(f"  Valid: {result[0]}, Error: {result[1]}")
    print()

    print("Test 2: Check that bare identifier 'foo' shows error")
    result = editor._check_line_syntax("foo")
    print(f"  Code: 'foo'")
    print(f"  Valid: {result[0]}, Error: {result[1]}")
    print()

    print("Test 3: Check that valid statement 'PRINT \"hello\"' is valid")
    result = editor._check_line_syntax("PRINT \"hello\"")
    print(f"  Code: 'PRINT \"hello\"'")
    print(f"  Valid: {result[0]}, Error: {result[1]}")
    print()

    print("Test 4: Display errors, then fix them - should clear output")
    print("  Step 1: Add error line")
    editor.syntax_errors = {10: "Test error"}
    print(f"    syntax_errors: {editor.syntax_errors}")
    print(f"    _showing_syntax_errors before: {editor._showing_syntax_errors}")
    editor._display_syntax_errors()
    print(f"    _showing_syntax_errors after: {editor._showing_syntax_errors}")
    print(f"    Output lines: {len(editor._output_walker)}")

    print("  Step 2: Clear errors")
    editor.syntax_errors = {}
    print(f"    syntax_errors: {editor.syntax_errors}")
    print(f"    _showing_syntax_errors before: {editor._showing_syntax_errors}")
    editor._display_syntax_errors()
    print(f"    _showing_syntax_errors after: {editor._showing_syntax_errors}")
    print(f"    Output lines: {len(editor._output_walker)} (should be 0)")
    print()

    print("Test 5: Verify _update_syntax_errors marks errors correctly")
    # Format: "SNNNNN CODE" (S=status at col 0, NNNNN=line number at cols 1-5 right-aligned, space at col 6, code at col 7+)
    # Build correctly formatted lines
    line1 = " " + "   10" + " " + "foo"        # Status + line number (5 chars) + space + code
    line2 = " " + "   20" + " " + "PRINT \"hello\""
    line3 = " " + "   30" + " " + "bar"
    text = line1 + "\n" + line2 + "\n" + line3
    new_text = editor._update_syntax_errors(text)
    print(f"  Input lines:")
    for i, line in enumerate(text.split('\n'), 1):
        print(f"    Line {i}: '{line}' (status='{line[0]}', linenum='{line[1:6]}', code='{line[7:] if len(line) > 7 else ''}')")
    print(f"  Output lines:")
    for i, line in enumerate(new_text.split('\n'), 1):
        print(f"    Line {i}: '{line}' (status='{line[0]}', linenum='{line[1:6]}', code='{line[7:] if len(line) > 7 else ''}')")
    print(f"  syntax_errors: {editor.syntax_errors}")
    print(f"  Expected: Lines 10 and 30 marked with '?', line 20 unmarked")
    print()

    print("Test 6: Priority system - breakpoint preserved when error fixed")
    # Set breakpoint on line 20
    editor.breakpoints.add(20)

    # Create lines with error and breakpoint
    line1 = " " + "   10" + " " + "PRINT \"ok\""  # Valid, no breakpoint
    line2 = " " + "   20" + " " + "foo"           # Error + breakpoint
    text = line1 + "\n" + line2

    # First check - should show error
    new_text = editor._update_syntax_errors(text)
    lines = new_text.split('\n')
    print(f"  Line 20 with error + breakpoint: status='{lines[1][0]}' (expected '?' - error has priority)")

    # Fix the error
    line1 = " " + "   10" + " " + "PRINT \"ok\""
    line2 = "?" + "   20" + " " + "PRINT \"fixed\""  # Fixed code, had error status
    text = line1 + "\n" + line2

    # Second check - should show breakpoint
    new_text = editor._update_syntax_errors(text)
    lines = new_text.split('\n')
    print(f"  Line 20 after fix: status='{lines[1][0]}' (expected '●' - breakpoint shown)")
    print()

if __name__ == '__main__':
    test_syntax_checking()
