#!/usr/bin/env python3
"""Debug test for the 'e' (end) command."""

import sys
import time
import pexpect

print("="*60)
print("DEBUG TEST: END COMMAND")
print("="*60)

# Create test program
with open('test_end_debug.bas', 'w') as f:
    f.write("""10 PRINT "Line 10"
20 PRINT "Line 20 - BREAKPOINT"
30 PRINT "Line 30"
40 PRINT "Done!"
""")

print("\nTest program:")
print("  10 PRINT \"Line 10\"")
print("  20 PRINT \"Line 20 - BREAKPOINT\"  <- breakpoint here")
print("  30 PRINT \"Line 30\"")
print("  40 PRINT \"Done!\"")
print("\nExpected behavior:")
print("  - Hit breakpoint at line 20")
print("  - Press 'e' to end")
print("  - Should NOT see 'Done!' (lines 30, 40 should not execute)")
print()

child = pexpect.spawn('python3 mbasic --backend curses test_end_debug.bas',
                      encoding='utf-8', dimensions=(24, 80), timeout=10)

# Log stderr to see debug messages
import os
stderr_file = open('test_end_stderr.log', 'w')
child.logfile_send = sys.stdout  # Show what we send
child.logfile_read = sys.stdout  # Show what we receive

try:
    time.sleep(0.8)

    print("\n[1] Setting breakpoint on line 20...")
    child.send('\x1b[B')  # Down to line 20
    time.sleep(0.2)
    child.send('b')  # Set breakpoint
    time.sleep(0.3)

    print("\n[2] Running program...")
    child.send('\x12')  # Ctrl+R
    time.sleep(1.0)

    print("\n[3] Checking for breakpoint...")
    try:
        child.expect('BREAKPOINT', timeout=2)
        print("\n✓ Hit breakpoint at line 20")
    except pexpect.TIMEOUT:
        print("\n✗ Did not hit breakpoint")
        sys.exit(1)

    # Check what output we have so far
    print("\n[4] Current output (should have Line 10):")
    try:
        child.expect('Line 10', timeout=0.5)
        print("  ✓ Found 'Line 10'")
    except pexpect.TIMEOUT:
        print("  ? Did not find 'Line 10' yet")

    print("\n[5] Pressing 'e' to END execution...")
    print("    (This should stop the program completely)")
    child.send('e')
    time.sleep(1.5)

    print("\n[6] Checking if execution stopped...")
    print("    - Looking for 'Execution stopped by user' message")
    try:
        child.expect('stopped by user', timeout=1.0)
        print("    ✓ Found 'stopped by user' message")
    except pexpect.TIMEOUT:
        print("    ? Did not find 'stopped by user' message")

    print("\n[7] Checking that program did NOT continue...")
    print("    - Looking for 'Done!' (should NOT be found)")
    try:
        child.expect('Done!', timeout=1.0)
        print("    ✗ FAIL: Found 'Done!' - program continued when it shouldn't have!")
        print("\nThis means the 'e' command is not working correctly.")
    except pexpect.TIMEOUT:
        print("    ✓ PASS: Did not find 'Done!' - program stopped correctly!")
        print("\nThe 'e' command is working!")

    print("\n[8] Quitting...")
    child.send('\x11')  # Ctrl+Q
    time.sleep(0.5)

except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()

finally:
    stderr_file.close()
    child.close()

# Print stderr log
print("\n" + "="*60)
print("STDERR LOG:")
print("="*60)
try:
    with open('test_end_stderr.log', 'r') as f:
        stderr_content = f.read()
        if stderr_content:
            print(stderr_content)
        else:
            print("(empty)")
except:
    print("(no stderr log)")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)
