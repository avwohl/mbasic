#!/usr/bin/env python3
"""
Test curses UI using pyte terminal emulator.

Uses pyte to emulate a terminal and capture screen state.
"""

import pyte
import subprocess
import sys
import os
sys.path.insert(0, 'src')
import time
import select
from threading import Thread
from src.ui.keybindings import HELP_CHAR

class TerminalEmulator:
    """Terminal emulator for testing curses applications."""

    def __init__(self, rows=24, cols=80):
        self.screen = pyte.Screen(cols, rows)
        self.stream = pyte.Stream(self.screen)
        self.process = None

    def start_process(self, cmd):
        """Start a subprocess with a pseudo-terminal."""
        import pty
        master, slave = pty.openpty()

        self.process = subprocess.Popen(
            cmd,
            stdin=slave,
            stdout=slave,
            stderr=slave,
            close_fds=True,
            preexec_fn=os.setsid
        )

        os.close(slave)
        self.master = master

        # Set non-blocking
        import fcntl
        fl = fcntl.fcntl(self.master, fcntl.F_GETFL)
        fcntl.fcntl(self.master, fcntl.F_SETFL, fl | os.O_NONBLOCK)

        return self

    def read_output(self, timeout=0.5):
        """Read output from process and feed to terminal emulator."""
        start = time.time()
        while time.time() - start < timeout:
            ready, _, _ = select.select([self.master], [], [], 0.1)
            if ready:
                try:
                    data = os.read(self.master, 4096)
                    if data:
                        self.stream.feed(data.decode('utf-8', errors='replace'))
                except OSError:
                    break
            else:
                time.sleep(0.01)

    def send_input(self, text):
        """Send input to the process."""
        os.write(self.master, text.encode('utf-8'))

    def get_screen_text(self):
        """Get current screen content as text."""
        return '\n'.join(self.screen.display)

    def get_screen_lines(self):
        """Get screen lines."""
        return self.screen.display

    def terminate(self):
        """Terminate the process."""
        if self.process:
            self.process.terminate()
            self.process.wait(timeout=2)
        if hasattr(self, 'master'):
            os.close(self.master)

def test_curses_with_pyte():
    """Test curses UI using pyte terminal emulator."""
    print("=== Testing curses UI with pyte ===\n")

    term = TerminalEmulator(rows=24, cols=80)

    try:
        # Start the curses UI
        print("Starting curses UI...")
        term.start_process(['python3', 'mbasic', '--backend', 'curses'])

        # Wait for startup
        print("Waiting for UI to initialize...")
        time.sleep(1)
        term.read_output(timeout=1)

        # Display initial screen
        print("\n=== Initial screen state ===")
        screen_text = term.get_screen_text()
        print(screen_text)
        print("="*80)

        # Send help key
        print(f"\nSending {HELP_CHAR!r} (help)...")
        term.send_input(HELP_CHAR)
        time.sleep(0.5)
        term.read_output(timeout=0.5)

        print(f"\n=== After {HELP_CHAR!r} ===")
        print(term.get_screen_text())
        print("="*80)

        # Press ESC or Q to close help
        print("\nSending 'q' to close help...")
        term.send_input('q')
        time.sleep(0.5)
        term.read_output(timeout=0.5)

        # Try typing a program line
        print("\nTyping program line...")
        term.send_input('10 PRINT "HELLO"\r')
        time.sleep(0.5)
        term.read_output(timeout=0.5)

        print("\n=== After typing line ===")
        print(term.get_screen_text())
        print("="*80)

        # Try Ctrl+R to run
        print("\nSending Ctrl+R (run)...")
        term.send_input('\x12')
        time.sleep(1)
        term.read_output(timeout=1)

        print("\n=== After Ctrl+R ===")
        print(term.get_screen_text())
        print("="*80)

        # Quit with Ctrl+Q
        print("\nSending Ctrl+Q (quit)...")
        term.send_input('\x11')
        time.sleep(0.5)

        print("\nTest completed successfully!")
        return True

    except Exception as e:
        print(f"\nException: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        term.terminate()

if __name__ == '__main__':
    print("Curses UI Testing with pyte\n")
    success = test_curses_with_pyte()
    print(f"\n{'='*60}")
    print(f"Result: {'PASS' if success else 'FAIL'}")
    print(f"{'='*60}")
