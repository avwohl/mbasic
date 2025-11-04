#!/usr/bin/env python3
"""Test CONTINUE command to verify key handling works."""

import sys
import time
import pexpect
import os

print("="*60)
print("CONTINUE COMMAND TEST (should work)")
print("="*60)

# Clear debug log
debug_log = '/tmp/mbasic_debug.log'
if os.path.exists(debug_log):
    os.remove(debug_log)

# Create test program
with open('test_continue_log.bas', 'w') as f:
    f.write("""10 PRINT "Line 10"
20 PRINT "Line 20 - BREAKPOINT"
30 PRINT "Line 30"
40 PRINT "Done!"
""")

print("\n[1] Starting mbasic...")
child = pexpect.spawn('python3 mbasic --ui curses test_continue_log.bas',
                      encoding='utf-8',
                      dimensions=(24, 80),
                      timeout=10)

try:
    time.sleep(1.0)

    print("[2] Moving to line 20...")
    child.send('\x1bOB')  # Down arrow
    time.sleep(0.3)

    print("[3] Setting breakpoint...")
    child.send('b')
    time.sleep(0.5)

    print("[4] Running program...")
    child.send('\x12')  # Ctrl+R

    # Wait for breakpoint to be hit
    try:
        child.expect('BREAKPOINT', timeout=3)
        print("     ✓ Breakpoint hit, UI is ready")
    except pexpect.TIMEOUT:
        print("     ✗ Did not see BREAKPOINT message")

    print("[5] Pressing 'c' to CONTINUE...")
    child.send('c')
    time.sleep(2.0)  # Wait for program to complete

    print("[6] Quitting...")
    child.send('\x11')  # Ctrl+Q
    time.sleep(0.5)

finally:
    child.close()

# Read and analyze debug log
print("\n" + "="*60)
print("DEBUG LOG (last 20 lines):")
print("="*60)
if os.path.exists(debug_log):
    with open(debug_log, 'r') as f:
        log_lines = f.readlines()

    if log_lines:
        for line in log_lines[-20:]:
            print(line.rstrip())

        print("\n" + "="*60)
        print("KEY ANALYSIS:")
        print("="*60)

        c_key_received = any("input_char=99 ('c')" in line for line in log_lines)
        continue_handler_called = any('_handle_breakpoint_continue called' in line for line in log_lines)

        print(f"✓ 'c' key received: {c_key_received}")
        print(f"✓ Continue handler called: {continue_handler_called}")

        if c_key_received and continue_handler_called:
            print("\n✓ Continue command works - key handling is functional!")
        else:
            print("\n✗ Continue command broken - key handling not working!")
    else:
        print("(debug log is empty)")
else:
    print("(debug log not created)")

print("="*60)
