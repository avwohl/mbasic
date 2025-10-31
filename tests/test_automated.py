#!/usr/bin/env python3
"""Automated testing of the npyscreen UI using pexpect."""

import pexpect
import time
import sys

def test_ui():
    print("Starting mbasic with curses backend...")

    # Start the process
    child = pexpect.spawn('python3 mbasic --backend curses test_program.bas',
                          encoding='utf-8',
                          timeout=10)

    # Set up logging
    child.logfile = open('/tmp/mbasic_pexpect.log', 'w')

    try:
        # Wait for UI to load
        time.sleep(2)

        print("UI should be loaded. Sending Ctrl+R to run program...")
        child.send('\x12')  # Ctrl+R
        time.sleep(2)

        print("Taking screenshot of terminal state...")
        # Get the current screen content
        child.send('\x03')  # Ctrl+C to exit

        # Wait for exit
        child.expect(pexpect.EOF, timeout=5)

    except pexpect.TIMEOUT:
        print("Timeout waiting for response")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        if child.isalive():
            child.close()

    print("\nLog saved to /tmp/mbasic_pexpect.log")

    # Read and display log
    with open('/tmp/mbasic_pexpect.log', 'r') as f:
        content = f.read()
        print("\n=== Terminal output ===")
        print(content)
        print("=== End output ===")

if __name__ == '__main__':
    test_ui()
