#!/usr/bin/env python3
"""Manual test for urwid UI - creates a simple program and runs it."""

import time
import pexpect

print("Testing urwid UI with a simple program...")
print()

# Create test program
with open('test_hello_urwid.bas', 'w') as f:
    f.write("""10 PRINT "Hello from urwid!"
20 PRINT "2 + 2 = "; 2 + 2
30 END
""")

print("Starting urwid UI...")
print("Instructions:")
print("  1. The program should be loaded in the editor")
print("  2. Press Ctrl+R to run it")
print("  3. Check the output window for results")
print("  4. Press F1 for help")
print("  5. Press Ctrl+Q to quit")
print()
print("Launching in 2 seconds...")
time.sleep(2)

# Start with the test program
import subprocess
subprocess.run(['python3', 'mbasic', '--backend', 'curses', 'test_hello_urwid.bas'])

print("\nTest complete!")
