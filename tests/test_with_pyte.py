#!/usr/bin/env python3
"""Automated testing with screen scraping using pyte."""

import pexpect
import pyte
import time

def test_ui_with_screen():
    print("Starting mbasic with curses backend...")

    # Create terminal emulator
    screen = pyte.Screen(80, 24)
    stream = pyte.ByteStream(screen)

    # Start process
    child = pexpect.spawn('python3 mbasic --backend curses test_program.bas',
                          encoding='utf-8',
                          timeout=10,
                          dimensions=(24, 80))

    def capture_screen():
        """Capture and display current screen state."""
        # Feed output to pyte
        if child.before:
            stream.feed(child.before.encode('utf-8'))

        # Get screen as text
        lines = []
        for i in range(screen.lines):
            line = ''.join(screen.buffer[i]).rstrip()
            lines.append(f"{i:2d}: {line}")
        return '\n'.join(lines)

    try:
        # Wait for UI to load
        print("Waiting for UI to load...")
        time.sleep(3)
        child.expect('.+', timeout=1)

        print("\n=== Initial screen ===")
        print(capture_screen())

        # Try menu approach first (ESC then x to open menu)
        print("\n\nOpening menu with Ctrl+X...")
        child.send('\x18')  # Ctrl+X for npyscreen menu
        time.sleep(1)
        child.expect('.+', timeout=1)

        print("\n=== After Ctrl+X ===")
        print(capture_screen())

        # Try Ctrl+R
        print("\n\nSending Ctrl+R...")
        child.send('\x12')  # Ctrl+R
        time.sleep(2)
        child.expect('.+', timeout=1)

        print("\n=== After Ctrl+R ===")
        print(capture_screen())

        # Check output window area (lines 16-22 based on layout)
        print("\n\n=== Output window content ===")
        for i in range(16, 23):
            line = ''.join(screen.buffer[i]).rstrip()
            print(f"Line {i}: '{line}'")

        # Exit
        child.send('\x03')  # Ctrl+C
        time.sleep(1)

    except pexpect.TIMEOUT:
        print("Timeout")
    except pexpect.EOF:
        print("Process ended")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if child.isalive():
            child.close()

if __name__ == '__main__':
    test_ui_with_screen()
