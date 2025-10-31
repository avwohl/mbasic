#!/usr/bin/env python3
"""Test end command with various timings."""

import sys
import time
import pexpect

def test_with_timing(delay_after_breakpoint, delay_after_e):
    """Test with specific timing delays."""
    print(f"\n{'='*60}")
    print(f"Testing with delays: after_bp={delay_after_breakpoint}s, after_e={delay_after_e}s")
    print('='*60)

    with open('test_end_timing.bas', 'w') as f:
        f.write("""10 PRINT "Line 10"
20 PRINT "Line 20 - BREAKPOINT"
30 PRINT "Line 30"
40 PRINT "Done!"
""")

    child = pexpect.spawn('python3 mbasic --backend curses test_end_timing.bas',
                          encoding='utf-8', dimensions=(24, 80), timeout=10)

    try:
        time.sleep(0.8)

        # Set breakpoint
        child.send('\x1b[B')  # Down to line 20
        time.sleep(0.2)
        child.send('b')
        time.sleep(0.3)

        # Run
        child.send('\x12')
        time.sleep(delay_after_breakpoint)

        # Check for breakpoint
        try:
            child.expect('BREAKPOINT', timeout=2)
            print("  ✓ Hit breakpoint")
        except pexpect.TIMEOUT:
            print("  ✗ No breakpoint")
            return False

        # Press 'e'
        child.send('e')
        time.sleep(delay_after_e)

        # Check if program completed
        try:
            child.expect('Done!', timeout=0.5)
            print("  ✗ Found 'Done!' - program continued")
            return False
        except pexpect.TIMEOUT:
            print("  ✓ Did not find 'Done!' - program stopped")
            return True

    finally:
        child.send('\x11')
        child.close()

print("="*60)
print("END COMMAND TIMING TEST")
print("="*60)
print("\nTesting different timing delays to see if there's a race condition...")

results = []

# Test with various delays
test_cases = [
    (0.5, 0.5),
    (1.0, 1.0),
    (1.0, 2.0),
    (2.0, 1.0),
    (2.0, 2.0),
]

for after_bp, after_e in test_cases:
    result = test_with_timing(after_bp, after_e)
    results.append((after_bp, after_e, result))
    time.sleep(0.5)  # Brief pause between tests

print("\n" + "="*60)
print("RESULTS SUMMARY")
print("="*60)
for after_bp, after_e, result in results:
    status = "PASS" if result else "FAIL"
    print(f"  Delays ({after_bp}s, {after_e}s): {status}")

if all(r[2] for r in results):
    print("\n✓ ALL timing tests passed - no race condition")
elif any(r[2] for r in results):
    print("\n⚠ SOME timing tests passed - possible race condition")
else:
    print("\n✗ ALL timing tests failed - 'e' command not working")
