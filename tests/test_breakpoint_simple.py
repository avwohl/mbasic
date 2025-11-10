#!/usr/bin/env python3
"""Simple test to verify breakpoint functionality"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Create a test program
with open('/tmp/test_bp.bas', 'w') as f:
    f.write("10 PRINT \"Line 10\"\n")
    f.write("20 PRINT \"Line 20\"\n")
    f.write("30 PRINT \"Line 30\"\n")

# Test breakpoint system
from src.ui.curses_ui import CursesBackend
from src.editing.manager import ProgramManager
from src.iohandler.curses_io import CursesIOHandler

# Create program manager and load program
pm = ProgramManager()
pm.load_from_file('/tmp/test_bp.bas')

# Create backend
io = CursesIOHandler(None, debug_enabled=False)
backend = CursesBackend(io, pm)

# Load program to editor
backend._load_program_to_editor()

# Add a breakpoint at line 20
backend.breakpoints.add(20)

print("Editor lines:", backend.editor_lines)
print("Breakpoints:", backend.breakpoints)
print("Editor text with breakpoints:")
print(backend._get_editor_text())

# Verify breakpoint indicator appears
editor_text = backend._get_editor_text()
assert '●20' in editor_text or '● 20' in editor_text, f"Breakpoint indicator not found in: {editor_text}"

print("\n✓ Breakpoint indicator is present")
print("✓ Breakpoint system basic test passed!")
