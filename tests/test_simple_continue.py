#!/usr/bin/env python3
"""Simple test for continue command."""

import sys
import time
import pexpect
import os

print("=" * 60)
print("SIMPLE CONTINUE TEST")
print("=" * 60)

# Clear debug log
os.system('rm -f /tmp/mbasic_debug.log')

# Create test program
with open('test_cont.bas', 'w') as f:
    f.write("""10 PRINT "Line 10 - BREAKPOINT"
20 PRINT "Line 20"
30 PRINT "Done!"
""")

child = pexpect.spawn('python3 mbasic --backend curses-npyscreen test_cont.bas',
                      encoding='utf-8', dimensions=(24, 80), timeout=10)

try:
    time.sleep(1.0)
    print("[1] Setting breakpoint...")
    child.send('b')
    time.sleep(0.5)

    print("[2] Running...")
    child.send('\x12')  # Ctrl+R

    print("[3] Waiting for breakpoint...")
    try:
        child.expect('BREAKPOINT', timeout=3)
        print("    ✓ Breakpoint hit")
    except pexpect.TIMEOUT:
        print("    ✗ Timeout waiting for breakpoint")
        sys.exit(1)

    # Give extra time for the paused flag to be set
    print("[4] Waiting 1 second before sending 'c'...")
    time.sleep(1.0)

    print("[5] Sending 'c' to continue...")
    child.send('c')

    print("[6] Waiting 2 seconds for execution to continue...")
    time.sleep(2.0)

    print("[7] Quitting...")
    child.send('\x11')
    time.sleep(0.5)

finally:
    child.close()

# Check debug log
print("\n" + "=" * 60)
print("DEBUG LOG:")
print("=" * 60)
if os.path.exists('/tmp/mbasic_debug.log'):
    with open('/tmp/mbasic_debug.log', 'r') as f:
        log = f.read()
        print(log)

        # Check for continue handler
        if '_handle_breakpoint_continue called' in log:
            print("\n✓✓✓ CONTINUE HANDLER WAS CALLED ✓✓✓")
        else:
            print("\n✗✗✗ CONTINUE HANDLER NOT CALLED ✗✗✗")
else:
    print("(no debug log)")
