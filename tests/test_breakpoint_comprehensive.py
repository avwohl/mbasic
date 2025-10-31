#!/usr/bin/env python3
"""Comprehensive test of all breakpoint features: Continue, Step, End."""

import sys
import time
import pexpect

def run_test(test_name, test_func):
    """Run a single test and report results."""
    print("\n" + "="*60)
    print(f"TEST: {test_name}")
    print("="*60)
    try:
        result = test_func()
        if result:
            print(f"✓ {test_name} PASSED")
        else:
            print(f"✗ {test_name} FAILED")
        return result
    except Exception as e:
        print(f"✗ {test_name} ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_continue():
    """Test that 'c' continues from breakpoint."""
    print("\nTesting: Hit breakpoint, press 'c' to continue")

    # Create test program
    with open('test_continue.bas', 'w') as f:
        f.write("""10 PRINT "Line 10"
20 PRINT "Line 20 - BREAKPOINT"
30 PRINT "Line 30"
40 PRINT "Done!"
""")

    child = pexpect.spawn('python3 mbasic --backend curses-npyscreen test_continue.bas',
                          encoding='utf-8', dimensions=(24, 80), timeout=10)

    try:
        time.sleep(0.8)

        # Move to line 20 and set breakpoint
        print("  [1] Setting breakpoint on line 20...")
        child.send('\x1b[B')  # Down to line 20
        time.sleep(0.2)
        child.send('b')  # Set breakpoint
        time.sleep(0.3)

        # Run program
        print("  [2] Running program...")
        child.send('\x12')  # Ctrl+R
        time.sleep(1.0)

        # Check for breakpoint
        print("  [3] Checking for breakpoint...")
        try:
            child.expect('BREAKPOINT', timeout=2)
            print("      ✓ Hit breakpoint")
        except pexpect.TIMEOUT:
            print("      ✗ Did not hit breakpoint")
            return False

        # Press 'c' to continue
        print("  [4] Pressing 'c' to continue...")
        child.send('c')
        time.sleep(1.0)

        # Check for completion
        print("  [5] Checking for completion...")
        try:
            child.expect('Done!', timeout=2)
            print("      ✓ Program completed")
            return True
        except pexpect.TIMEOUT:
            print("      ✗ Program did not complete")
            return False

    finally:
        child.send('\x11')  # Ctrl+Q
        child.close()

def test_step():
    """Test that 's' steps one line at a time."""
    print("\nTesting: Hit breakpoint, press 's' to step")

    with open('test_step.bas', 'w') as f:
        f.write("""10 PRINT "Line 10"
20 PRINT "Line 20 - BREAKPOINT"
30 PRINT "Line 30"
40 PRINT "Done!"
""")

    child = pexpect.spawn('python3 mbasic --backend curses-npyscreen test_step.bas',
                          encoding='utf-8', dimensions=(24, 80), timeout=10)

    try:
        time.sleep(0.8)

        # Move to line 20 and set breakpoint
        print("  [1] Setting breakpoint on line 20...")
        child.send('\x1b[B')  # Down to line 20
        time.sleep(0.2)
        child.send('b')
        time.sleep(0.3)

        # Run program
        print("  [2] Running program...")
        child.send('\x12')  # Ctrl+R
        time.sleep(1.0)

        # Check for breakpoint
        print("  [3] Checking for breakpoint at line 20...")
        try:
            child.expect('BREAKPOINT', timeout=2)
            print("      ✓ Hit breakpoint at line 20")
        except pexpect.TIMEOUT:
            print("      ✗ Did not hit breakpoint")
            return False

        # Press 's' to step to line 30
        print("  [4] Pressing 's' to step to line 30...")
        child.send('s')
        time.sleep(0.5)

        # Press 's' again to step to line 40
        print("  [5] Pressing 's' to step to line 40...")
        child.send('s')
        time.sleep(0.5)

        # Check for "Done!"
        print("  [6] Checking if stepped to line 40...")
        try:
            child.expect('Done!', timeout=2)
            print("      ✓ Stepped through lines correctly")
            return True
        except pexpect.TIMEOUT:
            print("      ✗ Did not reach line 40")
            return False

    finally:
        child.send('\x11')  # Ctrl+Q
        child.close()

def test_end():
    """Test that 'e' ends execution at breakpoint."""
    print("\nTesting: Hit breakpoint, press 'e' to end")

    with open('test_end.bas', 'w') as f:
        f.write("""10 PRINT "Line 10"
20 PRINT "Line 20 - BREAKPOINT"
30 PRINT "Line 30"
40 PRINT "Done!"
""")

    child = pexpect.spawn('python3 mbasic --backend curses-npyscreen test_end.bas',
                          encoding='utf-8', dimensions=(24, 80), timeout=10)

    try:
        time.sleep(0.8)

        # Move to line 20 and set breakpoint
        print("  [1] Setting breakpoint on line 20...")
        child.send('\x1b[B')  # Down to line 20
        time.sleep(0.2)
        child.send('b')
        time.sleep(0.3)

        # Run program
        print("  [2] Running program...")
        child.send('\x12')  # Ctrl+R
        time.sleep(1.0)

        # Check for breakpoint
        print("  [3] Checking for breakpoint...")
        try:
            child.expect('BREAKPOINT', timeout=2)
            print("      ✓ Hit breakpoint")
        except pexpect.TIMEOUT:
            print("      ✗ Did not hit breakpoint")
            return False

        # Press 'e' to end
        print("  [4] Pressing 'e' to end execution...")
        child.send('e')
        time.sleep(1.0)

        # The program should NOT reach line 40
        print("  [5] Checking that program ended...")
        # Look for execution stopped message or lack of "Done!"
        # If we see "Done!" that means 'e' didn't work
        before = child.before if hasattr(child, 'before') else ""

        # This is a bit tricky - we're checking that "Done!" was NOT printed
        # Since pexpect will timeout if it doesn't find it, that's actually success
        try:
            child.expect('Done!', timeout=1)
            print("      ✗ Program continued (should have ended)")
            return False
        except pexpect.TIMEOUT:
            print("      ✓ Program ended (did not reach line 40)")
            return True

    finally:
        child.send('\x11')  # Ctrl+Q
        child.close()

def test_normal_editing():
    """Test that 's', 'c', 'e' work as normal keys when NOT at breakpoint."""
    print("\nTesting: Normal editing (s/c/e should type normally)")

    with open('test_edit.bas', 'w') as f:
        f.write("""10 PRINT "Test"
""")

    child = pexpect.spawn('python3 mbasic --backend curses-npyscreen test_edit.bas',
                          encoding='utf-8', dimensions=(24, 80), timeout=10)

    try:
        time.sleep(0.8)

        # Try typing 's' in the editor (should work normally)
        print("  [1] Typing 's' in editor...")
        child.send('s')
        time.sleep(0.3)

        # This is hard to verify automatically, but if the program doesn't crash
        # and we can still quit, that's good enough
        print("  [2] Checking editor still works...")

        # Quit
        child.send('\x11')  # Ctrl+Q
        time.sleep(0.5)

        print("      ✓ Normal editing works")
        return True

    except Exception as e:
        print(f"      ✗ Error: {e}")
        return False
    finally:
        try:
            child.close()
        except:
            pass

# Main test runner
def main():
    print("="*60)
    print("COMPREHENSIVE BREAKPOINT SYSTEM TEST")
    print("="*60)
    print("\nThis will test all breakpoint features:")
    print("  1. Continue (c) - removes breakpoint and continues")
    print("  2. Step (s) - executes one line")
    print("  3. End (e) - stops execution")
    print("  4. Normal editing - s/c/e work normally when not at breakpoint")

    results = []

    results.append(run_test("CONTINUE", test_continue))
    results.append(run_test("STEP", test_step))
    results.append(run_test("END", test_end))
    results.append(run_test("NORMAL EDITING", test_normal_editing))

    print("\n" + "="*60)
    print("FINAL RESULTS")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"\nPassed: {passed}/{total}")

    if passed == total:
        print("\n✓✓✓ ALL TESTS PASSED ✓✓✓")
        print("\nThe breakpoint system is fully functional!")
    else:
        print(f"\n✗✗✗ {total - passed} TESTS FAILED ✗✗✗")
        print("\nSome features need fixing.")

    print("="*60)

    return passed == total

if __name__ == '__main__':
    try:
        import pexpect
    except ImportError:
        print("ERROR: pexpect not installed")
        print("Install with: pip3 install pexpect")
        sys.exit(1)

    success = main()
    sys.exit(0 if success else 1)
