#!/usr/bin/env python3
"""
Test that curses UI actually displays program output.
"""

import sys
sys.path.insert(0, 'src')

from ui.curses_ui import CursesBackend
from iohandler.console import ConsoleIOHandler
from editing import ProgramManager
from parser import TypeInfo

def test_output_display():
    """Test that program output is captured and displayed."""

    # Create components
    def_type_map = {letter: TypeInfo.SINGLE for letter in 'abcdefghijklmnopqrstuvwxyz'}
    io_handler = ConsoleIOHandler(debug_enabled=False)
    program_manager = ProgramManager(def_type_map)
    backend = CursesBackend(io_handler, program_manager)
    backend._create_ui()

    # Set a program with multiple PRINT statements
    program_text = '''10 PRINT "Hello, World!"
20 PRINT "The answer is"; 42
30 FOR I = 1 TO 3
40   PRINT "Loop iteration"; I
50 NEXT I
60 PRINT "Done!"
70 END'''

    backend.editor.set_edit_text(program_text)

    print("=== Testing Output Display ===\n")
    print("Program:")
    print(program_text)
    print("\n" + "="*60)

    # Run the program
    backend._run_program()

    # Check output buffer
    print("\nOutput buffer contents:")
    for i, line in enumerate(backend.output_buffer):
        print(f"  {i}: {line}")

    print("\n" + "="*60)

    # Verify output
    expected_outputs = [
        "Hello, World!",
        "42",  # Part of "The answer is 42"
        "Loop iteration",
        "Done!",
        "Ok"
    ]

    success = True
    for expected in expected_outputs:
        found = any(expected in line for line in backend.output_buffer)
        status = "✓" if found else "✗"
        print(f"{status} Expected '{expected}': {'FOUND' if found else 'NOT FOUND'}")
        if not found:
            success = False

    print("\n" + "="*60)
    print(f"Result: {'PASS' if success else 'FAIL'}")
    print("="*60)

    return success

if __name__ == '__main__':
    success = test_output_display()
    sys.exit(0 if success else 1)
