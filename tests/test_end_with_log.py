#!/usr/bin/env python3
"""Test end command with file-based debug logging."""

import sys
import time
import pexpect
import os

print("="*60)
print("END COMMAND TEST WITH FILE LOGGING")
print("="*60)

# Clear debug log
debug_log = '/tmp/mbasic_debug.log'
if os.path.exists(debug_log):
    os.remove(debug_log)

# Create test program
with open('test_end_log.bas', 'w') as f:
    f.write("""10 PRINT "Line 10"
20 PRINT "Line 20 - BREAKPOINT"
30 PRINT "Line 30"
40 PRINT "Done!"
""")

print("\n[1] Starting mbasic...")
child = pexpect.spawn('python3 mbasic --backend curses test_end_log.bas',
                      encoding='utf-8',
                      dimensions=(24, 80),
                      timeout=10)

try:
    time.sleep(1.0)

    print("[2] Moving to line 20...")
    # Press down arrow to move from line 10 to line 20
    child.send('\x1bOB')  # Down arrow (VT100 sequence)
    time.sleep(0.3)

    print("[3] Setting breakpoint...")
    child.send('b')
    time.sleep(0.5)

    print("[4] Running program...")
    child.send('\x12')  # Ctrl+R
    time.sleep(1.5)

    print("[5] Pressing 'e' to end...")
    child.send('e')
    time.sleep(1.5)

    print("[6] Quitting...")
    child.send('\x11')  # Ctrl+Q
    time.sleep(0.5)

finally:
    child.close()

# Read and analyze debug log
print("\n" + "="*60)
print("DEBUG LOG:")
print("="*60)
if os.path.exists(debug_log):
    with open(debug_log, 'r') as f:
        log_lines = f.readlines()

    if log_lines:
        for line in log_lines:
            print(line.rstrip())

        print("\n" + "="*60)
        print("ANALYSIS:")
        print("="*60)

        # Check for key events
        breakpoint_hit = any('Hit breakpoint' in line for line in log_lines)
        e_key_received = any("input_char=101 ('e')" in line for line in log_lines)
        end_handler_called = any('_handle_breakpoint_end called' in line for line in log_lines)
        timer_after_end = False

        # Check if timer was called after end handler
        end_handler_index = -1
        for i, line in enumerate(log_lines):
            if '_handle_breakpoint_end called' in line:
                end_handler_index = i
                break

        if end_handler_index >= 0:
            for i in range(end_handler_index + 1, len(log_lines)):
                if '_execution_timer called' in log_lines[i]:
                    timer_after_end = True
                    break

        print(f"✓ Breakpoint hit: {breakpoint_hit}")
        print(f"✓ 'e' key received: {e_key_received}")
        print(f"✓ End handler called: {end_handler_called}")
        print(f"{'✗' if timer_after_end else '✓'} Execution timer after end: {timer_after_end}")

        if not e_key_received:
            print("\n⚠ PROBLEM: 'e' key was not received by handler!")
            print("  This means the key binding is not working.")
        elif not end_handler_called:
            print("\n⚠ PROBLEM: End handler was not called!")
            print("  This means paused_at_breakpoint was False when 'e' was pressed.")
        elif timer_after_end:
            print("\n⚠ PROBLEM: Execution continued after end!")
            print("  This means something is calling _execution_timer after end.")
        else:
            print("\n✓ Everything looks correct! The 'e' command should work.")
    else:
        print("(debug log is empty)")
else:
    print("(debug log not created)")

print("="*60)
