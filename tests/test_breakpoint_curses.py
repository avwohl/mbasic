#!/usr/bin/env python3
"""Test the curses UI with breakpoints using pyte terminal emulator."""

import sys
import time
import subprocess
import pyte

def test_breakpoint_ui():
    """Test the full curses UI with breakpoint functionality."""

    print("="*60)
    print("CURSES UI BREAKPOINT TEST")
    print("="*60)
    print()

    # Create a pyte screen to capture output
    screen = pyte.Screen(80, 24)
    stream = pyte.Stream(screen)

    # Start mbasic with curses backend using a PTY
    print("Starting mbasic with curses backend...")
    import pty
    import os

    # Create a pseudo-terminal
    master, slave = pty.openpty()

    proc = subprocess.Popen(
        ['python3', 'mbasic', '--backend', 'curses', 'test_continue.bas'],
        stdin=slave,
        stdout=slave,
        stderr=subprocess.PIPE,
        bufsize=0
    )

    # Close slave in parent process
    os.close(slave)

    def send_keys(keys, delay=0.1):
        """Send keys to the process."""
        for key in keys:
            if isinstance(key, str):
                os.write(master, key.encode())
            else:
                os.write(master, bytes([key]))
            time.sleep(delay)

    def read_output(timeout=1.0):
        """Read available output."""
        import select
        output = b''
        end_time = time.time() + timeout
        while time.time() < end_time:
            ready, _, _ = select.select([master], [], [], 0.1)
            if ready:
                try:
                    chunk = os.read(master, 4096)
                    if chunk:
                        output += chunk
                        stream.feed(chunk.decode('utf-8', errors='ignore'))
                    else:
                        break
                except OSError:
                    break
            else:
                time.sleep(0.05)
        return output

    try:
        # Wait for UI to start
        print("Waiting for UI to initialize...")
        time.sleep(1.0)
        read_output(1.0)

        # Check if UI started
        screen_text = '\n'.join(screen.display)
        if 'test_continue.bas' in screen_text or 'MBASIC' in screen_text or '10' in screen_text:
            print("✓ UI started successfully")
        else:
            print("✗ UI may not have started")
            print("Screen content:")
            print(screen_text[:500])

        # Step 1: Set breakpoint on line 20
        print("\nStep 1: Setting breakpoint on line 20...")
        send_keys('\x1b[B', 0.2)  # Down arrow to line 20
        time.sleep(0.2)
        read_output(0.2)

        send_keys('b', 0.2)  # Press 'b' to toggle breakpoint
        time.sleep(0.3)
        read_output(0.3)

        screen_text = '\n'.join(screen.display)
        if '●' in screen_text or '20' in screen_text:
            print("✓ Breakpoint appears to be set")
        else:
            print("? Could not confirm breakpoint marker")

        # Step 2: Run the program
        print("\nStep 2: Running program with Ctrl+R...")
        send_keys('\x12', 0.2)  # Ctrl+R
        time.sleep(1.0)
        read_output(1.0)

        screen_text = '\n'.join(screen.display)

        # Check for breakpoint message
        if 'BREAKPOINT' in screen_text and '20' in screen_text:
            print("✓ Breakpoint hit! Status shown at bottom")
            print(f"  Status line contains: {[line for line in screen.display if 'BREAKPOINT' in line][0].strip()}")
        else:
            print("✗ Breakpoint status not visible")
            print("Screen content:")
            for i, line in enumerate(screen.display):
                if line.strip():
                    print(f"  Line {i}: {line}")

        # Check if output was captured
        if 'Line 10' in screen_text:
            print("✓ Program output visible (Line 10 executed)")

        # Step 3: Press 'c' to continue
        print("\nStep 3: Pressing 'c' to continue...")
        send_keys('c', 0.3)
        time.sleep(1.0)
        read_output(1.0)

        screen_text = '\n'.join(screen.display)

        # Check if program completed
        if 'Done!' in screen_text or 'completed' in screen_text.lower():
            print("✓ Program continued and completed")
        else:
            print("? Program may have completed")

        # Check all output lines
        output_lines = []
        for line in screen.display:
            if 'Line ' in line:
                output_lines.append(line.strip())

        print(f"\nOutput captured: {len(output_lines)} lines")
        for line in output_lines:
            print(f"  {line}")

        # Step 4: Quit
        print("\nStep 4: Quitting with Ctrl+Q...")
        send_keys('\x11', 0.2)
        time.sleep(0.5)

    except Exception as e:
        print(f"\n✗ Error during test: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Clean up
        try:
            os.close(master)
            proc.terminate()
            proc.wait(timeout=2)
        except:
            try:
                proc.kill()
                proc.wait()
            except:
                pass

        # Check stderr for errors
        try:
            stderr_output = proc.stderr.read().decode('utf-8', errors='ignore')
            if stderr_output:
                print("\nStderr output:")
                print(stderr_output[:1000])
        except:
            pass

    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)

if __name__ == '__main__':
    test_breakpoint_ui()
