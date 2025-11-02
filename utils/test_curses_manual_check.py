#!/usr/bin/env python3
"""
Manual check - creates backend, loads file, and prints editor state.
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

def test_editor_state():
    """Test that editor state is correct after loading from command line."""
    print("Testing editor state after file load via ProgramManager...")
    print("="*70)

    # Simulate what happens when you run: mbasic test_simple.bas --ui curses

    # 1. Create components (like main script does)
    def_type_map = {letter: TypeInfo.SINGLE for letter in 'abcdefghijklmnopqrstuvwxyz'}
    io_handler = ConsoleIOHandler(debug_enabled=False)
    program_manager = ProgramManager(def_type_map)

    # 2. Load file into ProgramManager (like run_file() does)
    test_file = "test_simple.bas"
    print(f"\n1. Loading {test_file} into ProgramManager...")
    success, errors = program_manager.load_from_file(test_file)
    print(f"   Success: {success}, Errors: {errors}")
    print(f"   Program has {len(program_manager.lines)} lines")

    # 3. Create backend (like main script does)
    print(f"\n2. Creating CursesBackend...")
    backend = CursesBackend(io_handler, program_manager)
    print(f"   Backend created")
    print(f"   Backend.program has {len(backend.program.lines)} lines")
    print(f"   Backend.editor_lines has {len(backend.editor_lines)} lines")

    # 4. Simulate calling start() which should sync the program
    print(f"\n3. Simulating start() sync...")
    if backend.program.has_lines() and not backend.editor_lines:
        print(f"   Calling _sync_program_to_editor()...")
        backend._sync_program_to_editor()
    else:
        print(f"   Sync not needed (editor_lines={len(backend.editor_lines)})")

    # 5. Check final state
    print(f"\n4. Final state:")
    print(f"   Backend.program has {len(backend.program.lines)} lines")
    print(f"   Backend.editor_lines has {len(backend.editor_lines)} lines")
    print(f"   Editor text length: {len(backend.editor.get_edit_text())} chars")

    print(f"\n5. Editor content:")
    editor_text = backend.editor.get_edit_text()
    for i, line in enumerate(editor_text.split('\n')[:10]):
        print(f"   {line}")

    print(f"\n6. editor_lines dict:")
    for line_num in sorted(backend.editor_lines.keys())[:10]:
        print(f"   {line_num}: {backend.editor_lines[line_num]}")

    # Verify
    if len(backend.editor_lines) > 0 and len(editor_text) > 0:
        print(f"\n✓ SUCCESS: Editor properly populated!")
        return True
    else:
        print(f"\n✗ FAILED: Editor not populated")
        return False

if __name__ == '__main__':
    success = test_editor_state()
    sys.exit(0 if success else 1)
