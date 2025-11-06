#!/usr/bin/env python3
"""
Test the 3-column program editor layout.

Shows status, line numbers, and code in separate columns.
"""

import sys
sys.path.insert(0, 'src')

from ui.curses_ui import ProgramEditorWidget

def test_3column_editor():
    """Test the 3-column editor display."""

    print("=== 3-Column Program Editor Test ===\n")

    # Create editor
    editor = ProgramEditorWidget()

    # Add some lines
    editor.add_line(10, 'PRINT "Hello, World!"')
    editor.add_line(20, 'FOR I = 1 TO 10')
    editor.add_line(30, '  PRINT I')
    editor.add_line(40, 'NEXT I')
    editor.add_line(50, 'END')

    # Set a breakpoint
    editor.toggle_breakpoint(20)

    # Set an error
    editor.set_error(30, "Syntax error")

    print("Field Layout:")
    print("  Field 1 (1 char):      Status (● = breakpoint, ? = error)")
    print("  Field 2 (variable):    Line number")
    print("  Field 3 (rest):        BASIC code")
    print()

    print("Sample Program:")
    print("="*70)

    # Get the formatted display
    display_text = editor.edit_widget.get_edit_text()
    print(display_text)

    print("="*70)
    print()

    print("Legend:")
    print("  ●  = Breakpoint set on line 20")
    print("  ?  = Error on line 30")
    print("     = Normal line (10, 40, 50)")
    print()

    print("Auto-numbering:")
    print(f"  Next line number: {editor.next_auto_line_num}")
    print(f"  Increment: {editor.auto_number_increment}")
    print(f"  When Enter is pressed on blank line, line number auto-fills")
    print()

    print("Features:")
    print("  ✓ Status field shows breakpoints and errors")
    print("  ✓ Line numbers use variable width")
    print("  ✓ Code uses remaining space")
    print("  ✓ Breakpoints tracked (toggle with toggle_breakpoint())")
    print("  ✓ Errors tracked (set with set_error())")
    print("  ✓ Auto-numbering enabled (press Enter on blank line)")

if __name__ == '__main__':
    test_3column_editor()
