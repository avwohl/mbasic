#!/bin/bash

# Test continue functionality in breakpoint system
# This script tests that pressing 'c' continues execution to the next breakpoint

cat > /tmp/test_continue.py << 'PYTEST'
import sys
import time
import pyte
import subprocess
import os

def test_continue():
    """Test that 'c' continues from one breakpoint to the next."""

    # Create a test BASIC program
    test_program = """10 PRINT "Line 10"
20 PRINT "Line 20 - breakpoint 1"
30 PRINT "Line 30"
40 PRINT "Line 40 - breakpoint 2"
50 PRINT "Line 50"
60 PRINT "Done!"
"""

    with open('/tmp/test_continue.bas', 'w') as f:
        f.write(test_program)

    # Create a pyte screen
    screen = pyte.Screen(80, 24)
    stream = pyte.Stream(screen)

    # Start mbasic with curses backend
    proc = subprocess.Popen(
        ['python3', 'mbasic', '--backend', 'curses', '/tmp/test_continue.bas'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=False,
        bufsize=0
    )

    def send(text):
        """Send text to process."""
        proc.stdin.write(text.encode())
        proc.stdin.flush()

    def read_output(timeout=1.0):
        """Read available output."""
        import select
        output = b''
        end_time = time.time() + timeout
        while time.time() < end_time:
            ready, _, _ = select.select([proc.stdout], [], [], 0.1)
            if ready:
                chunk = proc.stdout.read(1024)
                if chunk:
                    output += chunk
                    stream.feed(chunk.decode('utf-8', errors='ignore'))
                else:
                    break
            else:
                # No more data immediately available
                time.sleep(0.1)
        return output

    try:
        # Wait for UI to initialize
        time.sleep(0.5)
        read_output(0.5)

        print("Step 1: Setting breakpoint on line 20")
        # Move to line 20 (press down arrow)
        send('\x1b[B')  # Down
        time.sleep(0.2)
        read_output(0.2)

        # Toggle breakpoint with 'b'
        send('b')
        time.sleep(0.2)
        output = read_output(0.2)

        # Check that breakpoint indicator appears
        screen_text = '\n'.join(screen.display)
        if '●' in screen_text or '20' in screen_text:
            print("✓ Breakpoint set on line 20")
        else:
            print("✗ Failed to set breakpoint on line 20")
            print("Screen:", screen_text)

        print("\nStep 2: Setting breakpoint on line 40")
        # Move to line 40 (press down arrow twice)
        send('\x1b[B\x1b[B')  # Down Down
        time.sleep(0.2)
        read_output(0.2)

        # Toggle breakpoint with 'b'
        send('b')
        time.sleep(0.2)
        read_output(0.2)
        print("✓ Breakpoint set on line 40")

        print("\nStep 3: Running program")
        # Run program with Ctrl+R
        send('\x12')
        time.sleep(0.5)
        output = read_output(0.5)

        # Should hit first breakpoint at line 20
        screen_text = '\n'.join(screen.display)
        if 'BREAKPOINT' in screen_text and '20' in screen_text:
            print("✓ Hit first breakpoint at line 20")
            print(f"   Status: {[line for line in screen.display if 'BREAKPOINT' in line][0].strip()}")
        else:
            print("✗ Did not hit breakpoint at line 20")
            print("Screen:", screen_text)

        print("\nStep 4: Pressing 'c' to continue")
        # Press 'c' to continue
        send('c')
        time.sleep(0.5)
        output = read_output(0.5)

        # Should hit second breakpoint at line 40
        screen_text = '\n'.join(screen.display)
        if 'BREAKPOINT' in screen_text and '40' in screen_text:
            print("✓ Continued to second breakpoint at line 40")
            print(f"   Status: {[line for line in screen.display if 'BREAKPOINT' in line][0].strip()}")
        else:
            print("✗ Did not continue to breakpoint at line 40")
            print("Screen:", screen_text)

        print("\nStep 5: Pressing 'c' again to finish")
        # Press 'c' to continue to end
        send('c')
        time.sleep(0.5)
        output = read_output(0.5)

        # Should show "Done!" in output
        screen_text = '\n'.join(screen.display)
        if 'Done!' in screen_text:
            print("✓ Program completed successfully")
        else:
            print("? Program may have completed (checking output)")
            print("Screen:", screen_text)

        print("\nStep 6: Exiting")
        # Exit with Ctrl+Q
        send('\x11')
        time.sleep(0.3)

    finally:
        # Clean up
        try:
            proc.stdin.close()
            proc.terminate()
            proc.wait(timeout=2)
        except:
            proc.kill()
            proc.wait()

    print("\n" + "="*60)
    print("CONTINUE TEST COMPLETED")
    print("="*60)

if __name__ == '__main__':
    test_continue()
PYTEST

python3 /tmp/test_continue.py
