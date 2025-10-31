#!/usr/bin/env python3
"""Comprehensive breakpoint tests - FIXED VERSION."""

import sys
import time
import pexpect
import os

def test_continue():
    """Test that 'c' continues from breakpoint."""
    print("\n" + "="*60)
    print("TEST: CONTINUE")
    print("="*60)

    # Create test program
    with open('test_cont.bas', 'w') as f:
        f.write("""10 PRINT "Line 10 - BREAKPOINT"
20 PRINT "Line 20"
30 PRINT "Done!"
""")

    child = pexpect.spawn('python3 mbasic --backend curses-npyscreen test_cont.bas',
                          encoding='utf-8', dimensions=(24, 80), timeout=10)

    try:
        time.sleep(1.0)

        # Set breakpoint on line 10 (cursor starts there)
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

        # Press 'c' to continue
        child.send('c')
        time.sleep(1.5)

        # Check debug log - should have 2+ calls to _execution_timer
        # (one for initial run, one+ for continue)
        if os.path.exists('/tmp/mbasic_debug.log'):
            with open('/tmp/mbasic_debug.log', 'r') as f:
                log = f.read()
                timer_calls = log.count('_execution_timer called')
                if timer_calls >= 2:
                    print(f"  ✓ Continue worked (timer called {timer_calls} times)")
                    return True
                else:
                    print(f"  ✗ Continue failed (timer only called {timer_calls} time)")
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

        # Press 's' to step
        child.send('s')
        time.sleep(0.5)

        # Press 's' again
        child.send('s')
        time.sleep(0.5)

        # Check debug log - step_once should be called for each line
        if os.path.exists('/tmp/mbasic_debug.log'):
            with open('/tmp/mbasic_debug.log', 'r') as f:
                log = f.read()
                step_calls = log.count('step_once returned')
                if step_calls >= 3:  # Initial + 2 steps
                    print(f"  ✓ Step worked ({step_calls} steps executed)")
                    return True
                else:
                    print(f"  ✗ Step failed (only {step_calls} steps)")
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

        # Press 'e' to end
        child.send('e')
        time.sleep(1.5)

        # Check debug log - timer should only be called once
        if os.path.exists('/tmp/mbasic_debug.log'):
            with open('/tmp/mbasic_debug.log', 'r') as f:
                log = f.read()
                timer_calls = log.count('_execution_timer called')
                if timer_calls == 1:
                    print(f"  ✓ End worked (execution stopped)")
                    return True
                else:
                    print(f"  ✗ End failed (timer called {timer_calls} times)")
                    return False

        return False

    finally:
        child.send('\x11')
        child.close()

# Main
print("="*60)
print("COMPREHENSIVE BREAKPOINT TESTS (FIXED)")
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
