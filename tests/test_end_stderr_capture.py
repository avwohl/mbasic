#!/usr/bin/env python3
"""Test end command with proper stderr capture."""

import sys
import time
import subprocess
import os
import pty
import select

print("="*60)
print("END COMMAND TEST WITH STDERR")
print("="*60)

# Create test program
with open('test_end_stderr.bas', 'w') as f:
    f.write("""10 PRINT "Line 10"
20 PRINT "Line 20 - BREAKPOINT"
30 PRINT "Line 30"
40 PRINT "Done!"
""")

# Create PTY
master, slave = pty.openpty()

# Start process
proc = subprocess.Popen(
    ['python3', 'mbasic', '--backend', 'curses', 'test_end_stderr.bas'],
    stdin=slave,
    stdout=slave,
    stderr=subprocess.PIPE,  # Capture stderr separately
    bufsize=0
)

os.close(slave)

def send_keys(keys_str, delay=0.2):
    """Send keys to PTY."""
    for ch in keys_str:
        if ch == '\r':
            os.write(master, b'\r')
        elif ch == '^':
            # Next char is control
            continue
        else:
            os.write(master, ch.encode())
        time.sleep(delay)

def read_output(timeout=1.0):
    """Read available output from PTY."""
    output = b''
    end_time = time.time() + timeout
    while time.time() < end_time:
        ready, _, _ = select.select([master], [], [], 0.1)
        if ready:
            try:
                chunk = os.read(master, 4096)
                if chunk:
                    output += chunk
                else:
                    break
            except OSError:
                break
    return output

try:
    print("\n[1] Waiting for UI to start...")
    time.sleep(1.0)
    read_output(0.5)

    print("[2] Moving to line 20 and setting breakpoint...")
    send_keys('\x1b[B', 0.2)  # Down arrow
    time.sleep(0.2)
    send_keys('b', 0.2)
    time.sleep(0.3)

    print("[3] Running program...")
    send_keys('\x12', 0.2)  # Ctrl+R
    time.sleep(1.5)
    output = read_output(0.5)

    if b'BREAKPOINT' in output:
        print("    ✓ Hit breakpoint")
    else:
        print("    ? Did not see BREAKPOINT in output")

    print("[4] Pressing 'e' to end...")
    send_keys('e', 0.2)
    time.sleep(1.5)
    output = read_output(0.5)

    if b'Done!' in output:
        print("    ✗ Found 'Done!' - program continued")
    else:
        print("    ✓ Did not find 'Done!' - program stopped")

    print("[5] Quitting...")
    send_keys('\x11', 0.2)  # Ctrl+Q
    time.sleep(0.5)

finally:
    # Read stderr
    proc.terminate()
    try:
        stderr_output = proc.stderr.read().decode('utf-8', errors='ignore')
    except:
        stderr_output = ""

    try:
        os.close(master)
    except:
        pass

    try:
        proc.wait(timeout=2)
    except:
        proc.kill()

print("\n" + "="*60)
print("STDERR OUTPUT:")
print("="*60)
if stderr_output:
    for line in stderr_output.split('\n'):
        if line.strip():
            print(line)
else:
    print("(no stderr output)")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)
