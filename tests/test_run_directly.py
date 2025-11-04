#!/usr/bin/env python3
"""Test running a program directly without UI."""

import sys
sys.path.insert(0, 'src')

from editing import ProgramManager
from ui.curses_ui import CursesBackend
from iohandler.base import IOHandler

# Create minimal IO handler
class DummyIO(IOHandler):
    def input(self, prompt=""):
        return ""

    def print(self, *args, **kwargs):
        pass

    def error(self, message):
        pass

    def output(self, text):
        pass

    def input_line(self, prompt=""):
        return ""

    def input_char(self):
        return ""

    def clear_screen(self):
        pass

    def debug(self, message):
        pass

# Create program manager with empty type map
def_type_map = {}
program = ProgramManager(def_type_map)

# Create backend
io = DummyIO()
backend = CursesBackend(io, program)

# Load test program
backend.editor_lines = {
    10: "PRINT \"HELLO WORLD\"",
    20: "FOR I = 1 TO 5",
    30: "PRINT I",
    40: "NEXT I",
    50: "END"
}

# Try to run it
print("Testing program execution...")
print("Editor lines:", backend.editor_lines)

try:
    output = backend._run_program_capture()
    print("\n=== OUTPUT ===")
    print(output)
    print("=== END OUTPUT ===")
except Exception as e:
    import traceback
    print("\n=== ERROR ===")
    print(traceback.format_exc())
    print("=== END ERROR ===")
