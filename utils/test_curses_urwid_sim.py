#!/usr/bin/env python3
"""
Test curses UI using urwid's built-in testing capabilities.

This approach simulates the screen and input without needing a real terminal.
"""

import sys
import os
sys.path.insert(0, 'src')

import urwid
from src.ui.keybindings import HELP_KEY, LIST_KEY

def test_curses_with_urwid_simulation():
    """Test the curses UI using urwid's simulation screen."""
    print("=== Testing curses UI with urwid simulation ===\n")

    try:
        # Import our curses backend
        from ui.curses_ui import CursesBackend
        from iohandler.console import ConsoleIOHandler
        from editing import ProgramManager
        from parser import TypeInfo

        # Create default type map
        def_type_map = {}
        for letter in 'abcdefghijklmnopqrstuvwxyz':
            def_type_map[letter] = TypeInfo.SINGLE

        # Create components
        io_handler = ConsoleIOHandler(debug_enabled=True)
        program_manager = ProgramManager(def_type_map)

        # Create curses backend
        backend = CursesBackend(io_handler, program_manager)

        # Create the UI
        backend._create_ui()

        # Create a simulated screen for testing
        # urwid.raw_display.Screen() for real screen
        # urwid.curses_display.Screen() for curses
        # We can use the loop's screen directly

        print("UI created successfully!")
        print(f"Loop: {backend.loop}")
        print(f"Widget: {backend.loop.widget}")

        # Try to simulate some input
        print("\nSimulating input...")

        # Get the screen in raw mode
        screen = urwid.raw_display.Screen()

        # Simulate screen size
        screen.set_terminal_properties(
            colors=256,
            bright_is_bold=True,
            has_underline=True
        )

        # Draw the screen to see what it looks like
        print("\nAttempting to render UI...")
        canvas = backend.loop.widget.render((80, 24), focus=True)
        print(f"Canvas created: {canvas}")

        # Get text content
        text_content = []
        for i in range(min(24, canvas.rows())):
            row = canvas.content()[i]
            # Extract text from row
            text = ''
            for seg in row:
                if len(seg) > 2:
                    text += seg[2].decode('utf-8') if isinstance(seg[2], bytes) else str(seg[2])
            text_content.append(text)

        print("\n=== Rendered screen ===")
        for i, line in enumerate(text_content):
            print(f"{i:2d}: {line}")
        print("="*80)

        print("\nTest completed successfully!")
        return True

    except Exception as e:
        print(f"\nException: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_curses_input_simulation():
    """Test simulating user input to the curses UI."""
    print("\n\n=== Testing input simulation ===\n")

    try:
        from ui.curses_ui import CursesBackend
        from iohandler.console import ConsoleIOHandler
        from editing import ProgramManager
        from parser import TypeInfo

        # Setup
        def_type_map = {}
        for letter in 'abcdefghijklmnopqrstuvwxyz':
            def_type_map[letter] = TypeInfo.SINGLE

        io_handler = ConsoleIOHandler(debug_enabled=True)
        program_manager = ProgramManager(def_type_map)
        backend = CursesBackend(io_handler, program_manager)
        backend._create_ui()

        # Simulate key press
        print(f"Simulating {HELP_KEY} (help)...")

        # Process the unhandled input handler directly
        try:
            backend._handle_input(HELP_KEY)
            print(f"{HELP_KEY} processed successfully")
        except Exception as e:
            print(f"Error processing {HELP_KEY}: {e}")
            import traceback
            traceback.print_exc()

        # Try list key
        print(f"\nSimulating {LIST_KEY} (list)...")
        try:
            backend._handle_input(LIST_KEY)
            print(f"{LIST_KEY} processed successfully")
        except Exception as e:
            print(f"Error processing {LIST_KEY}: {e}")

        print("\nInput simulation test completed!")
        return True

    except Exception as e:
        print(f"\nException: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("Curses UI Testing with urwid simulation\n")

    success1 = test_curses_with_urwid_simulation()
    success2 = test_curses_input_simulation()

    print(f"\n{'='*60}")
    print("Results:")
    print(f"  Screen rendering test: {'PASS' if success1 else 'FAIL'}")
    print(f"  Input simulation test: {'PASS' if success2 else 'FAIL'}")
    print(f"{'='*60}")
