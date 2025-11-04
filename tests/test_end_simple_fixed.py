#!/usr/bin/env python3
"""Test END command with breakpoint on line 10 (cursor starts there)."""

import sys
import time
import pexpect
import os

print("="*60)
print("END COMMAND TEST (FIXED)")
print("="*60)

# Clear debug log
debug_log = '/tmp/mbasic_debug.log'
if os.path.exists(debug_log):
    os.remove(debug_log)

# Create test program
with open('test_end_fixed.bas', 'w') as f:
    f.write("""10 PRINT "Line 10 - BREAKPOINT"
20 PRINT "Line 20"
30 PRINT "Line 30"
40 PRINT "Done!"
""")

print("\n[1] Starting mbasic...")
child = pexpect.spawn('python3 mbasic --ui curses test_end_fixed.bas',
                      encoding='utf-8',
                      dimensions=(24, 80),
                      timeout=10)

try:
    time.sleep(1.0)

    print("[2] Setting breakpoint on line 10 (cursor starts here)...")
    child.send('b')
    time.sleep(0.5)

    print("[3] Running program...")
    child.send('\x12')  # Ctrl+R

    # Wait for breakpoint
    try:
        child.expect('BREAKPOINT', timeout=3)
        print("    ✓ Breakpoint hit")
    except pexpect.TIMEOUT:
        print("    ✗ Breakpoint not hit")

    print("[4] Pressing 'e' to END...")
    child.send('e')
    time.sleep(2.0)

    # Get all output
    output = child.before + child.buffer

    # Check for the "stopped by user" message
    found_stopped_msg = 'Execution stopped by user' in output
    found_completed_msg = 'completed' in output.lower()

    print(f"    Found 'Execution stopped by user': {found_stopped_msg}")
    print(f"    Found 'completed': {found_completed_msg}")

    # Based on debug log - if program stopped at breakpoint and never resumed,
    # we should NOT see completion message
    if found_stopped_msg:
        print("    ✓ Program was stopped by 'e' command")
        result = True
    elif found_completed_msg:
        print("    ✗ Program completed (should have been stopped)")
        result = False
    else:
        print("    ? Could not determine if program stopped or completed")
        # Check debug log
        with open('/tmp/mbasic_debug.log', 'r') as f:
            log = f.read()
            timer_calls = log.count('_execution_timer called')
            print(f"      Debug log shows {timer_calls} calls to _execution_timer")
            if timer_calls == 1:
                print("      ✓ Timer only called once - execution likely stopped")
                result = True
            else:
                print("      ✗ Timer called multiple times - execution continued")
                result = False

    print("[5] Quitting...")
    child.send('\x11')  # Ctrl+Q
    time.sleep(0.5)

finally:
    child.close()

# Show debug log
print("\n" + "="*60)
print("DEBUG LOG:")
print("="*60)
if os.path.exists(debug_log):
    with open(debug_log, 'r') as f:
        for line in f:
            print(line.rstrip())
else:
    print("(no debug log)")

print("\n" + "="*60)
if result:
    print("✓✓✓ END COMMAND WORKS ✓✓✓")
else:
    print("✗✗✗ END COMMAND BROKEN ✗✗✗")
print("="*60)
