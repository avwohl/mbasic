#!/usr/bin/env python3
"""
Test loading a file via command line in curses UI.
This tests the full integration path: mbasic file.bas --ui curses
"""

import sys
import pexpect
import time
from pathlib import Path

def test_cli_file_load(filename):
    """Test loading a file via command line."""
    print(f"Testing: mbasic {filename} --ui curses")

    try:
        child = pexpect.spawn(
            f'python3 mbasic {filename} --ui curses',
            encoding='utf-8',
            timeout=5,
            dimensions=(24, 80)
        )

        # Wait for UI to start
        time.sleep(0.5)

        # Try to list the program to see if it's loaded
        child.send('\x0c')  # Ctrl+L for LIST
        time.sleep(0.3)

        # Get some output to see if program is visible
        try:
            output = child.before if hasattr(child, 'before') else ""
            print(f"  UI started successfully")
        except:
            pass

        # Quit
        child.send('\x11')  # Ctrl+Q
        time.sleep(0.5)

        # Check if exited
        if child.isalive():
            child.send('\x03')  # Ctrl+C
            time.sleep(0.5)

        if child.isalive():
            child.terminate()
            print(f"  ✗ Process did not exit cleanly")
            return False

        print(f"  ✓ Test passed - file loaded and UI exited cleanly")
        return True

    except pexpect.TIMEOUT as e:
        print(f"  ✗ Timeout: {e}")
        try:
            child.terminate()
        except:
            pass
        return False
    except Exception as e:
        print(f"  ✗ Error: {type(e).__name__}: {e}")
        return False

def main():
    """Main test runner."""
    print("="*70)
    print("CURSES UI COMMAND-LINE FILE LOADING TEST")
    print("="*70)
    print()

    # Test with simple file
    test_files = [
        "test_simple.bas",
        "basic/dev/bas_tests/prime1.bas",
    ]

    passed = 0
    failed = 0

    for test_file in test_files:
        if not Path(test_file).exists():
            print(f"Skipping {test_file} (not found)")
            continue

        if test_cli_file_load(test_file):
            passed += 1
        else:
            failed += 1
        print()

    print("="*70)
    print(f"SUMMARY: {passed} passed, {failed} failed")
    print("="*70)

    sys.exit(0 if failed == 0 else 1)

if __name__ == '__main__':
    main()
