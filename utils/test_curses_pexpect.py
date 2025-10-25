#!/usr/bin/env python3
"""
Test curses UI using pexpect.

Spawns the curses UI in a subprocess and interacts with it.
"""

import pexpect
import sys
import time

def test_curses_basic():
    """Test basic curses UI startup and interaction."""
    print("=== Testing curses UI with pexpect ===")

    # Spawn the curses UI
    print("Spawning curses UI...")
    child = pexpect.spawn('python3 mbasic.py --backend curses',
                          encoding='utf-8',
                          timeout=5,
                          dimensions=(24, 80))

    try:
        # Log all output
        child.logfile = sys.stdout

        # Wait for UI to start
        print("\nWaiting for UI to initialize...")
        time.sleep(1)

        # Try to capture initial screen
        print("\n=== Initial screen ===")
        print(child.before if child.before else "(no output yet)")

        # Send Ctrl+H for help
        print("\n=== Sending Ctrl+H (help) ===")
        child.send('\x08')  # Ctrl+H
        time.sleep(0.5)

        # Send Ctrl+Q to quit
        print("\n=== Sending Ctrl+Q (quit) ===")
        child.send('\x11')  # Ctrl+Q
        time.sleep(0.5)

        # Check if it exited
        if child.isalive():
            print("\nProcess still alive, sending SIGTERM...")
            child.terminate()

        print("\nTest completed successfully")
        return True

    except pexpect.TIMEOUT:
        print(f"\nTIMEOUT: {child.before}")
        child.terminate()
        return False
    except pexpect.EOF:
        print(f"\nEOF (process ended): {child.before}")
        return True
    except Exception as e:
        print(f"\nException: {e}")
        import traceback
        traceback.print_exc()
        if child.isalive():
            child.terminate()
        return False

def test_curses_run_program():
    """Test running a program in curses UI."""
    print("\n\n=== Testing program execution in curses UI ===")

    child = pexpect.spawn('python3 mbasic.py --backend curses',
                          encoding='utf-8',
                          timeout=10,
                          dimensions=(24, 80))

    try:
        child.logfile = sys.stdout

        # Wait for startup
        time.sleep(1)

        # Type a simple program
        print("\n=== Typing program ===")
        child.send('10 PRINT "HELLO"\r')
        time.sleep(0.5)
        child.send('20 END\r')
        time.sleep(0.5)

        # Try to run it with Ctrl+R
        print("\n=== Sending Ctrl+R (run) ===")
        child.send('\x12')  # Ctrl+R
        time.sleep(1)

        # Quit
        print("\n=== Sending Ctrl+Q (quit) ===")
        child.send('\x11')
        time.sleep(0.5)

        if child.isalive():
            child.terminate()

        print("\nProgram execution test completed")
        return True

    except Exception as e:
        print(f"\nException during program test: {e}")
        import traceback
        traceback.print_exc()
        if child.isalive():
            child.terminate()
        return False

if __name__ == '__main__':
    print("Curses UI Testing with pexpect\n")

    success1 = test_curses_basic()
    success2 = test_curses_run_program()

    print("\n" + "="*60)
    print("Results:")
    print(f"  Basic test: {'PASS' if success1 else 'FAIL'}")
    print(f"  Program execution test: {'PASS' if success2 else 'FAIL'}")
    print("="*60)
