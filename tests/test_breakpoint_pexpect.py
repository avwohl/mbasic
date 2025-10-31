#!/usr/bin/env python3
"""Test the curses UI with breakpoints using pexpect."""

import sys
import time
import pexpect

def test_breakpoint_ui():
    """Test the full curses UI with breakpoint functionality."""

    print("="*60)
    print("CURSES UI BREAKPOINT TEST (pexpect)")
    print("="*60)
    print()

    # Create test program if it doesn't exist
    test_program = """10 PRINT "Line 10"
20 PRINT "Line 20 - BREAKPOINT"
30 PRINT "Line 30"
40 PRINT "Line 40"
50 PRINT "Done!"
"""

    with open('test_continue.bas', 'w') as f:
        f.write(test_program)

    print("Test program created: test_continue.bas")
    print()

    # Start mbasic with curses backend
    print("Starting mbasic with curses backend...")
    child = pexpect.spawn('python3 mbasic --backend curses-npyscreen test_continue.bas',
                          encoding='utf-8',
                          dimensions=(24, 80),
                          timeout=10)

    # Enable logging
    child.logfile_read = sys.stdout

    try:
        # Wait for UI to start
        print("\n[1] Waiting for UI to initialize...")
        time.sleep(1.0)

        # Move to line 20 (press down arrow multiple times)
        print("\n[2] Moving cursor to line 20...")
        child.send('\x1b[B')  # Down arrow
        time.sleep(0.2)

        # Set breakpoint on line 20
        print("\n[3] Setting breakpoint with 'b' key...")
        child.send('b')
        time.sleep(0.5)

        # Run the program with Ctrl+R
        print("\n[4] Running program with Ctrl+R...")
        child.send('\x12')  # Ctrl+R
        time.sleep(1.5)

        # At this point, we should be paused at the breakpoint
        print("\n[5] Should be paused at breakpoint now...")
        print("    Looking for BREAKPOINT message in output...")

        # Try to find breakpoint indicator
        try:
            child.expect('BREAKPOINT', timeout=2)
            print("    ✓ Found BREAKPOINT message!")
        except pexpect.TIMEOUT:
            print("    ✗ Did not see BREAKPOINT message")

        # Press 'c' to continue
        print("\n[6] Pressing 'c' to continue...")
        child.send('c')
        time.sleep(1.5)

        # Program should complete
        print("\n[7] Program should have completed...")

        # Check for output
        try:
            child.expect('Done!', timeout=2)
            print("    ✓ Program completed successfully!")
        except pexpect.TIMEOUT:
            print("    ? Did not see 'Done!' message")

        # Quit with Ctrl+Q
        print("\n[8] Quitting with Ctrl+Q...")
        child.send('\x11')  # Ctrl+Q
        time.sleep(0.5)

        print("\n" + "="*60)
        print("TEST RESULTS:")
        print("="*60)
        print("If you saw:")
        print("  ✓ 'BREAKPOINT' message - breakpoint was hit")
        print("  ✓ 'Done!' message - continue worked")
        print("Then the breakpoint system is working!")
        print()

    except Exception as e:
        print(f"\n✗ Error during test: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Clean up
        try:
            child.close()
        except:
            pass

        if child.isalive():
            child.terminate(force=True)

    print("="*60)
    print("TEST COMPLETE")
    print("="*60)

if __name__ == '__main__':
    try:
        import pexpect
    except ImportError:
        print("ERROR: pexpect not installed")
        print("Install with: pip3 install pexpect")
        sys.exit(1)

    test_breakpoint_ui()
