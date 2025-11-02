#!/usr/bin/env python3
"""
Test curses UI file loading functionality.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.ui.curses_ui import CursesBackend
from src.iohandler.console import ConsoleIOHandler
from src.editing import ProgramManager
from src.parser import TypeInfo

def test_file_loading():
    """Test loading a BASIC file into curses UI."""
    print("Testing file loading in curses UI...")

    # Create components
    def_type_map = {letter: TypeInfo.SINGLE for letter in 'abcdefghijklmnopqrstuvwxyz'}
    io_handler = ConsoleIOHandler(debug_enabled=False)
    program_manager = ProgramManager(def_type_map)
    backend = CursesBackend(io_handler, program_manager)
    backend._create_ui()

    # Test loading a file
    test_file = "test_simple.bas"

    try:
        print(f"Loading {test_file}...")
        backend._load_program_file(test_file)

        print(f"✓ File loaded successfully")
        print(f"  Editor lines: {len(backend.editor_lines)}")
        print(f"  Program lines: {len(backend.program.lines)}")
        print(f"  Current filename: {backend.current_filename}")

        # Check editor content
        editor_text = backend.editor.get_edit_text()
        print(f"  Editor text length: {len(editor_text)}")

        if len(backend.editor_lines) > 0:
            print(f"  ✓ Editor has {len(backend.editor_lines)} lines")
            for line_num in sorted(backend.editor_lines.keys())[:5]:
                print(f"    Line {line_num}: {backend.editor_lines[line_num][:50]}")
        else:
            print(f"  ✗ ERROR: No lines in editor_lines!")

        if len(editor_text) > 0:
            print(f"  ✓ Editor text populated")
            print(f"    First 100 chars: {editor_text[:100]}")
        else:
            print(f"  ✗ ERROR: Editor text is empty!")

        # Try with a real test program
        test_file2 = "basic/dev/bas_tests/prime1.bas"
        if Path(test_file2).exists():
            print(f"\nLoading {test_file2}...")
            backend._load_program_file(test_file2)

            print(f"✓ File loaded successfully")
            print(f"  Editor lines: {len(backend.editor_lines)}")
            print(f"  Program lines: {len(backend.program.lines)}")

            editor_text = backend.editor.get_edit_text()
            if len(editor_text) > 0:
                print(f"  ✓ Editor text populated ({len(editor_text)} chars)")
                lines = editor_text.split('\n')
                print(f"  First 3 lines:")
                for line in lines[:3]:
                    print(f"    {line[:70]}")
            else:
                print(f"  ✗ ERROR: Editor text is empty!")

        return True

    except Exception as e:
        print(f"✗ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_file_loading()
    sys.exit(0 if success else 1)
