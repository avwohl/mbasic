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
    print("Variables with access tracking:")
    print("="*60)

    all_vars = runtime.get_all_variables()

    # Sort by most recent access (like the old get_variables_by_recent_access)
    def get_most_recent_timestamp(var):
        read_ts = var['last_read']['timestamp'] if var['last_read'] else 0
        write_ts = var['last_write']['timestamp'] if var['last_write'] else 0
        return max(read_ts, write_ts)

    vars_sorted = sorted(all_vars, key=get_most_recent_timestamp, reverse=True)

    for var in vars_sorted:
        if var['is_array']:
            continue  # Skip arrays

        var_name = var['name'] + var['type_suffix']
        value = var['value']

        print(f"\n{var_name} = {value}")

        if var['last_read']:
            print(f"  Last READ:  line {var['last_read']['line']}, "
                  f"pos {var['last_read']['position']}, "
                  f"timestamp {var['last_read']['timestamp']:.6f}")
        else:
            print(f"  Last READ:  None")

        if var['last_write']:
            print(f"  Last WRITE: line {var['last_write']['line']}, "
                  f"pos {var['last_write']['position']}, "
                  f"timestamp {var['last_write']['timestamp']:.6f}")
        else:
            print(f"  Last WRITE: None")

        debugger_set = var['last_write'] and var['last_write']['line'] == -1
        print(f"  Debugger set: {debugger_set}")

    # Test debugger get (should not update tracking)
    print("\n" + "="*60)
    print("Testing debugger get (should not update tracking)...")
    print("="*60)

    # Get current tracking for x!
    x_var_before = [v for v in runtime.get_all_variables() if v['name'] == 'x'][0]
    last_read_before = x_var_before['last_read']

    # Use debugger get
    x_value = runtime.get_variable_for_debugger('x', '!')
    print(f"Got x! = {x_value} using get_variable_for_debugger()")

    # Check tracking hasn't changed
    x_var_after = [v for v in runtime.get_all_variables() if v['name'] == 'x'][0]
    last_read_after = x_var_after['last_read']

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

    test_var = [v for v in runtime.get_all_variables() if v['name'] == 'test'][0]
    debugger_set = test_var['last_write'] and test_var['last_write']['line'] == -1
    print(f"test% last_write line: {test_var['last_write']['line']}")

    if debugger_set:
        print("✓ Debugger set flag is correct (line -1)")
    else:
        print("✗ Debugger set flag is wrong")

    print("\n" + "="*60)
    print("All tests completed!")
    print("="*60)


if __name__ == '__main__':
    test_variable_tracking()
