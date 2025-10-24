#!/usr/bin/env python3
"""Test variable access tracking functionality."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from runtime import Runtime
from editing.manager import ProgramManager
from interpreter import Interpreter
from iohandler.console import ConsoleIOHandler
import time


def test_variable_tracking():
    """Test that variable tracking records read/write timestamps and locations."""

    print("Testing variable access tracking...")

    # Create a simple BASIC program
    program_text = """
10 X = 5
20 Y = X + 3
30 PRINT Y
40 Z = X * Y
50 PRINT Z
"""

    # Parse the program
    program = ProgramManager({})  # Empty def_type_map
    for line in program_text.strip().split('\n'):
        line = line.strip()
        if line:
            # Extract line number
            parts = line.split(None, 1)
            if parts:
                line_num = int(parts[0])
                program.add_line(line_num, line)

    # Create runtime and interpreter
    io_handler = ConsoleIOHandler(debug_enabled=False)
    program_ast = program.get_program_ast()
    runtime = Runtime(program_ast).setup()
    interpreter = Interpreter(runtime, io_handler)

    # Run the program
    print("\nRunning program...")
    interpreter.run()

    # Check variable tracking
    print("\n" + "="*60)
    print("Variables sorted by recent access:")
    print("="*60)

    vars_sorted = runtime.get_variables_by_recent_access(include_metadata=True)

    for var_name, value, metadata in vars_sorted:
        print(f"\n{var_name} = {value}")

        if metadata['last_read']:
            print(f"  Last READ:  line {metadata['last_read']['line']}, "
                  f"pos {metadata['last_read']['position']}, "
                  f"timestamp {metadata['last_read']['timestamp']:.6f}")
        else:
            print(f"  Last READ:  None")

        if metadata['last_write']:
            print(f"  Last WRITE: line {metadata['last_write']['line']}, "
                  f"pos {metadata['last_write']['position']}, "
                  f"timestamp {metadata['last_write']['timestamp']:.6f}")
        else:
            print(f"  Last WRITE: None")

        print(f"  Debugger set: {metadata['debugger_set']}")

    # Test debugger get (should not update tracking)
    print("\n" + "="*60)
    print("Testing debugger get (should not update tracking)...")
    print("="*60)

    # Get current metadata for x!
    x_meta_before = runtime._variable_metadata.get('x!', {})
    last_read_before = x_meta_before.get('last_read')

    # Use debugger get
    x_value = runtime.get_variable_for_debugger('x', '!')
    print(f"Got x! = {x_value} using get_variable_for_debugger()")

    # Check metadata hasn't changed
    x_meta_after = runtime._variable_metadata.get('x!', {})
    last_read_after = x_meta_after.get('last_read')

    if last_read_before == last_read_after:
        print("✓ Debugger get did NOT update tracking (correct)")
    else:
        print("✗ Debugger get DID update tracking (wrong!)")

    # Test debugger set
    print("\n" + "="*60)
    print("Testing debugger set...")
    print("="*60)

    runtime.set_variable('test', '%', 999, debugger_set=True)
    print("Set test% = 999 using debugger_set=True")

    test_meta = runtime._variable_metadata.get('test%', {})
    print(f"test% debugger_set flag: {test_meta.get('debugger_set')}")

    if test_meta.get('debugger_set'):
        print("✓ Debugger set flag is True (correct)")
    else:
        print("✗ Debugger set flag is False (wrong!)")

    print("\n" + "="*60)
    print("All tests completed!")
    print("="*60)


if __name__ == '__main__':
    test_variable_tracking()
