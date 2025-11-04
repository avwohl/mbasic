#!/usr/bin/env python3
"""Test for cursor positioning issue."""

import sys
import time
import pexpect

print("Testing cursor positioning issue...")
print("This will simulate typing two lines:")
print('  10 PRINT "a"')
print('  20 PRINT "b"')
print()

child = pexpect.spawn('python3 mbasic --ui curses',
                      encoding='utf-8', dimensions=(24, 80), timeout=10)

try:
    time.sleep(1.0)

    # Type first line
    print("[1] Typing: 10 PRINT \"a\"")
    child.send('10 PRINT "a"\r')
    time.sleep(0.5)

    # Type second line
    print("[2] Typing: 20 PRINT \"b\"")
    child.send('20 PRINT "b"\r')
    time.sleep(0.5)

    # List the program
    print("[3] Sending LIST command")
    child.send('LIST\r')
    time.sleep(1.0)

    # Get output
    output = (child.before or '') + (child.buffer or '')
    print("\n[4] Output captured:")
    print(output)

    # Check if both lines are present
    if '10 PRINT "a"' in output and '20 PRINT "b"' in output:
        print("\n✓✓✓ SUCCESS: Both lines preserved ✓✓✓")
        result = True
    else:
        print("\n✗✗✗ FAILURE: Lines not preserved ✗✗✗")
        result = False

    # Quit
    print("\n[5] Quitting...")
    child.send('\x11')  # Ctrl+Q
    time.sleep(0.5)

finally:
    child.close()

sys.exit(0 if result else 1)
