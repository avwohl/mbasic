#!/usr/bin/env python3
"""Final comprehensive breakpoint tests."""

import sys
import time
import pexpect
import os

def test_continue():
    """Test that 'c' continues from breakpoint."""
    print("\n" + "="*60)
    print("TEST: CONTINUE")
    print("="*60)

    with open('test_cont.bas', 'w') as f:
        f.write("""10 PRINT "Line 10 - BREAKPOINT"
20 PRINT "Line 20"
30 PRINT "Done!"
""")

    child = pexpect.spawn('python3 mbasic --backend curses-npyscreen test_cont.bas',
                          encoding='utf-8', dimensions=(24, 80), timeout=10)

    try:
        time.sleep(1.0)

        # Set breakpoint on line 10
        child.send('b')
        time.sleep(0.5)

        # Run
        child.send('\x12')  # Ctrl+R
        try:
            child.expect('BREAKPOINT', timeout=3)
            print("  ✓ Hit breakpoint")
        except pexpect.TIMEOUT:
            print("  ✗ No breakpoint")
            return False

        # Wait a bit to ensure paused flag is set
        time.sleep(0.5)

        # Press 'c' to continue
        child.send('c')
        time.sleep(2.0)

        # Check debug log - should see continue handler and more execution
        if os.path.exists('/tmp/mbasic_debug.log'):
            with open('/tmp/mbasic_debug.log', 'r') as f:
                log = f.read()
                continue_called = '_handle_breakpoint_continue called' in log
                callback_calls = log.count('_execution_callback running')

                if continue_called and callback_calls >= 2:
                    print(f"  ✓ Continue worked (handler called, {callback_calls} callbacks)")
                    return True
                else:
                    print(f"  ✗ Continue failed (handler={continue_called}, callbacks={callback_calls})")
                    return False

        return False

    finally:
        child.send('\x11')
        child.close()

def test_step():
    """Test that 's' steps one line at a time."""
    print("\n" + "="*60)
    print("TEST: STEP")
    print("="*60)

    with open('test_step.bas', 'w') as f:
        f.write("""10 PRINT "Line 10 - BREAKPOINT"
20 PRINT "Line 20"
30 PRINT "Done!"
""")

    child = pexpect.spawn('python3 mbasic --backend curses-npyscreen test_step.bas',
                          encoding='utf-8', dimensions=(24, 80), timeout=10)

    try:
        time.sleep(1.0)

        # Set breakpoint
        child.send('b')
        time.sleep(0.5)

        # Run
        child.send('\x12')
        try:
            child.expect('BREAKPOINT', timeout=3)
            print("  ✓ Hit breakpoint")
        except pexpect.TIMEOUT:
            print("  ✗ No breakpoint")
            return False

        # Wait a bit to ensure paused flag is set
        time.sleep(0.5)

        # Press 's' twice
        child.send('s')
        time.sleep(0.5)
        child.send('s')
        time.sleep(0.5)

        # Check debug log
        if os.path.exists('/tmp/mbasic_debug.log'):
            with open('/tmp/mbasic_debug.log', 'r') as f:
                log = f.read()
                step_calls = log.count('_handle_breakpoint_step called')

                if step_calls >= 2:
                    print(f"  ✓ Step worked ({step_calls} step calls)")
                    return True
                else:
                    print(f"  ✗ Step failed ({step_calls} step calls)")
                    return False

        return False

    finally:
        child.send('\x11')
        child.close()

def test_end():
    """Test that 'e' ends execution."""
    print("\n" + "="*60)
    print("TEST: END")
    print("="*60)

    with open('test_end.bas', 'w') as f:
        f.write("""10 PRINT "Line 10 - BREAKPOINT"
20 PRINT "Line 20"
30 PRINT "Done!"
""")

    child = pexpect.spawn('python3 mbasic --backend curses-npyscreen test_end.bas',
                          encoding='utf-8', dimensions=(24, 80), timeout=10)

    try:
        time.sleep(1.0)

        # Set breakpoint
        child.send('b')
        time.sleep(0.5)

        # Run
        child.send('\x12')
        try:
            child.expect('BREAKPOINT', timeout=3)
            print("  ✓ Hit breakpoint")
        except pexpect.TIMEOUT:
            print("  ✗ No breakpoint")
            return False

        # Wait a bit to ensure paused flag is set
        time.sleep(0.5)

        # Press 'e' to end
        child.send('e')
        time.sleep(1.5)

        # Check debug log - should see end handler and no more execution
        if os.path.exists('/tmp/mbasic_debug.log'):
            with open('/tmp/mbasic_debug.log', 'r') as f:
                log = f.read()
                end_called = '_handle_breakpoint_end called' in log

                # Count callbacks AFTER the end handler
                if end_called:
                    end_pos = log.find('_handle_breakpoint_end called')
                    callbacks_after = log[end_pos:].count('_execution_callback running')

                    if callbacks_after == 0:
                        print(f"  ✓ End worked (handler called, no further execution)")
                        return True
                    else:
                        print(f"  ✗ End failed ({callbacks_after} callbacks after end)")
                        return False
                else:
                    print("  ✗ End handler not called")
                    return False

        return False

    finally:
        child.send('\x11')
        child.close()

# Main
print("="*60)
print("FINAL COMPREHENSIVE BREAKPOINT TESTS")
print("="*60)

results = []

os.system('rm -f /tmp/mbasic_debug.log')
results.append(("CONTINUE", test_continue()))

os.system('rm -f /tmp/mbasic_debug.log')
results.append(("STEP", test_step()))

os.system('rm -f /tmp/mbasic_debug.log')
results.append(("END", test_end()))

print("\n" + "="*60)
print("FINAL RESULTS")
print("="*60)
for name, result in results:
    status = "✓ PASS" if result else "✗ FAIL"
    print(f"  {name}: {status}")

passed = sum(1 for _, r in results if r)
total = len(results)
print(f"\nTotal: {passed}/{total} passed")

if passed == total:
    print("\n✓✓✓ ALL TESTS PASSED ✓✓✓")
    print("\nThe breakpoint system is fully functional!")
    sys.exit(0)
else:
    print(f"\n✗✗✗ {total - passed} TESTS FAILED ✗✗✗")
    sys.exit(1)
