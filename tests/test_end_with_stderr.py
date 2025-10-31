#!/usr/bin/env python3
"""Test end command with stderr logging to file."""

import sys
import time
import pexpect
import os

print("="*60)
print("END COMMAND TEST WITH STDERR LOGGING")
print("="*60)

# Create test program
with open('test_end_stderr.bas', 'w') as f:
    f.write("""10 PRINT "Line 10"
20 PRINT "Line 20 - BREAKPOINT"
30 PRINT "Line 30"
40 PRINT "Done!"
""")

# Redirect stderr to a file before spawning
stderr_file = 'mbasic_stderr.log'
if os.path.exists(stderr_file):
    os.remove(stderr_file)

# Create a wrapper script that redirects stderr
wrapper_script = 'run_with_stderr.sh'
with open(wrapper_script, 'w') as f:
    f.write(f'''#!/bin/bash
exec 2>{stderr_file}
python3 mbasic --backend curses test_end_stderr.bas
''')
os.chmod(wrapper_script, 0o755)

print("\n[1] Starting mbasic with stderr redirected to file...")
child = pexpect.spawn(f'bash {wrapper_script}',
                      encoding='utf-8',
                      dimensions=(24, 80),
                      timeout=10)

try:
    time.sleep(1.0)

    print("[2] Setting breakpoint on line 20...")
    child.send('\x1b[B')  # Down
    time.sleep(0.2)
    child.send('b')
    time.sleep(0.3)

    print("[3] Running program...")
    child.send('\x12')  # Ctrl+R
    time.sleep(1.5)

    print("[4] Pressing 'e' to end...")
    child.send('e')
    time.sleep(1.5)

    print("[5] Quitting...")
    child.send('\x11')  # Ctrl+Q
    time.sleep(0.5)

finally:
    child.close()

# Read and display stderr
print("\n" + "="*60)
print("STDERR DEBUG OUTPUT:")
print("="*60)
time.sleep(0.5)  # Give file time to flush
if os.path.exists(stderr_file):
    with open(stderr_file, 'r') as f:
        stderr_content = f.read()
    if stderr_content:
        print(stderr_content)
    else:
        print("(stderr file is empty)")
else:
    print("(stderr file not created)")

print("\n" + "="*60)
print("ANALYSIS:")
print("="*60)
print("Look for these debug messages:")
print("  - 'DEBUG: h_breakpoint_key called' - shows 'e' key was received")
print("  - 'DEBUG: Calling _handle_breakpoint_end' - shows handler was called")
print("  - 'DEBUG: _handle_breakpoint_end called' - shows handler executed")
print("  - 'DEBUG: _execution_timer called' - shows if timer continues running")
print("="*60)
