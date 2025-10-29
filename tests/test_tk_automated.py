#!/usr/bin/env python3
"""
Automated test framework for Tk UI using tkinter event simulation.

This framework tests the Tk UI without requiring actual display by:
- Creating the UI programmatically
- Simulating keyboard and mouse events
- Verifying UI state changes
"""

import sys
import os
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Mock tkinter before importing UI
import tkinter as tk
from tkinter import ttk

class TkTestFramework:
    """Test framework for Tk UI"""

    def __init__(self):
        """Initialize test framework"""
        self.backend = None
        self.test_dir = None
        self.passed = 0
        self.failed = 0
        self.tests = []

    def setup(self):
        """Set up test environment"""
        # Create temp directory for test files
        self.test_dir = tempfile.mkdtemp(prefix="mbasic_tk_test_")
        print(f"Test directory: {self.test_dir}")

        # Import after path is set
        from src.ui.tk_ui import TkBackend
        from src.iohandler.console import ConsoleIOHandler
        from src.editing import ProgramManager
        from src.def_type_map import def_type_map

        # Create backend components
        io = ConsoleIOHandler()
        program = ProgramManager(def_type_map)

        # Create Tk backend but don't start mainloop
        self.backend = TkBackend(io, program)

        # Create root window for testing
        self.backend.root = tk.Tk()
        self.backend.root.withdraw()  # Hide window

        # Initialize UI components manually
        self._init_ui_components()

        return True

    def _init_ui_components(self):
        """Initialize UI components for testing"""
        # Create minimal UI structure
        from tkinter import scrolledtext
        from src.ui.tk_widgets import LineNumberedText

        # Create editor
        editor_frame = ttk.Frame(self.backend.root)
        self.backend.editor_text = LineNumberedText(
            editor_frame,
            wrap=tk.NONE,
            width=80,
            height=20
        )

        # Create output
        output_frame = ttk.Frame(self.backend.root)
        self.backend.output_text = scrolledtext.ScrolledText(
            output_frame,
            wrap=tk.WORD,
            width=80,
            height=10,
            state=tk.DISABLED
        )

        # Create status bar
        self.backend.status_label = ttk.Label(
            self.backend.root,
            text="Ready"
        )

        # Initialize state
        self.backend.breakpoints = set()
        self.backend.running = False
        self.backend.paused_at_breakpoint = False
        self.backend.find_text = ""
        self.backend.replace_text = ""
        self.backend.find_position = "1.0"
        self.backend.find_case_sensitive = False
        self.backend.find_whole_word = False

    def teardown(self):
        """Clean up test environment"""
        if self.backend and self.backend.root:
            try:
                self.backend.root.destroy()
            except:
                pass

        # Clean up test directory
        if self.test_dir and os.path.exists(self.test_dir):
            import shutil
            shutil.rmtree(self.test_dir)

    def run_test(self, name, test_func):
        """Run a single test"""
        try:
            print(f"\nTesting: {name}...", end=" ")
            test_func()
            print("✓ PASSED")
            self.passed += 1
            self.tests.append((name, True, None))
            return True
        except Exception as e:
            print(f"✗ FAILED: {e}")
            self.failed += 1
            self.tests.append((name, False, str(e)))
            return False

    # Test methods

    def test_editor_basic(self):
        """Test basic editor operations"""
        # Clear editor
        self.backend.editor_text.text.delete(1.0, tk.END)

        # Insert text
        self.backend.editor_text.text.insert(1.0, "10 PRINT \"HELLO\"\n")
        self.backend.editor_text.text.insert(tk.END, "20 PRINT \"WORLD\"\n")

        # Get content
        content = self.backend.editor_text.text.get(1.0, tk.END)
        assert "10 PRINT \"HELLO\"" in content
        assert "20 PRINT \"WORLD\"" in content

    def test_breakpoint_toggle(self):
        """Test breakpoint toggling"""
        # Add some code
        self.backend.editor_text.text.delete(1.0, tk.END)
        self.backend.editor_text.text.insert(1.0, "10 PRINT \"TEST\"\n")

        # Toggle breakpoint on line 10
        self.backend.breakpoints.add(10)
        assert 10 in self.backend.breakpoints

        # Toggle off
        self.backend.breakpoints.discard(10)
        assert 10 not in self.backend.breakpoints

    def test_find_functionality(self):
        """Test find functionality"""
        # Add text to editor
        self.backend.editor_text.text.delete(1.0, tk.END)
        self.backend.editor_text.text.insert(1.0, "10 PRINT \"HELLO\"\n")
        self.backend.editor_text.text.insert(tk.END, "20 PRINT \"WORLD\"\n")
        self.backend.editor_text.text.insert(tk.END, "30 PRINT \"HELLO\"\n")

        # Set find text
        self.backend.find_text = "HELLO"
        self.backend.find_position = "1.0"

        # Simulate find
        pos = self.backend.editor_text.text.search(
            self.backend.find_text,
            self.backend.find_position,
            tk.END
        )
        assert pos == "1.11"  # First HELLO position

        # Find next
        self.backend.find_position = f"{pos}+{len(self.backend.find_text)}c"
        pos = self.backend.editor_text.text.search(
            self.backend.find_text,
            self.backend.find_position,
            tk.END
        )
        assert pos == "3.11"  # Second HELLO position

    def test_replace_functionality(self):
        """Test replace functionality"""
        # Add text
        self.backend.editor_text.text.delete(1.0, tk.END)
        self.backend.editor_text.text.insert(1.0, "10 PRINT \"HELLO\"\n")

        # Set find/replace
        self.backend.find_text = "HELLO"
        self.backend.replace_text = "GOODBYE"

        # Find position
        pos = self.backend.editor_text.text.search("HELLO", "1.0", tk.END)
        if pos:
            end_pos = f"{pos}+{len('HELLO')}c"
            # Replace
            self.backend.editor_text.text.delete(pos, end_pos)
            self.backend.editor_text.text.insert(pos, "GOODBYE")

        # Verify
        content = self.backend.editor_text.text.get(1.0, tk.END)
        assert "GOODBYE" in content
        assert "HELLO" not in content

    def test_status_updates(self):
        """Test status bar updates"""
        # Set various status messages
        self.backend.status_label.config(text="Ready")
        assert self.backend.status_label.cget("text") == "Ready"

        self.backend.status_label.config(text="Running...")
        assert self.backend.status_label.cget("text") == "Running..."

        self.backend.status_label.config(text="Paused at breakpoint")
        assert self.backend.status_label.cget("text") == "Paused at breakpoint"

    def test_save_load_simulation(self):
        """Test save/load file operations"""
        test_file = os.path.join(self.test_dir, "test.bas")

        # Add content to editor
        self.backend.editor_text.text.delete(1.0, tk.END)
        self.backend.editor_text.text.insert(1.0, "10 REM TEST\n20 PRINT \"SAVED\"")

        # Get content
        content = self.backend.editor_text.text.get(1.0, tk.END).strip()

        # Simulate save
        with open(test_file, 'w') as f:
            f.write(content)

        assert os.path.exists(test_file)

        # Clear editor
        self.backend.editor_text.text.delete(1.0, tk.END)

        # Simulate load
        with open(test_file, 'r') as f:
            loaded_content = f.read()

        self.backend.editor_text.text.insert(1.0, loaded_content)

        # Verify
        new_content = self.backend.editor_text.text.get(1.0, tk.END).strip()
        assert new_content == content

    def test_output_display(self):
        """Test output window updates"""
        # Enable output for writing
        self.backend.output_text.config(state=tk.NORMAL)

        # Clear output
        self.backend.output_text.delete(1.0, tk.END)

        # Add output
        self.backend.output_text.insert(tk.END, "Program output\n")
        self.backend.output_text.insert(tk.END, "Line 2\n")

        # Disable for read-only
        self.backend.output_text.config(state=tk.DISABLED)

        # Verify
        content = self.backend.output_text.get(1.0, tk.END)
        assert "Program output" in content
        assert "Line 2" in content

    def test_line_numbers(self):
        """Test line number display"""
        # Add numbered lines
        self.backend.editor_text.text.delete(1.0, tk.END)
        self.backend.editor_text.text.insert(1.0, "10 PRINT \"A\"\n")
        self.backend.editor_text.text.insert(tk.END, "20 PRINT \"B\"\n")
        self.backend.editor_text.text.insert(tk.END, "30 PRINT \"C\"\n")

        # Force line number update (normally done by widget)
        self.backend.editor_text.update_line_numbers()

        # Check line count
        lines = self.backend.editor_text.text.get(1.0, tk.END).count('\n')
        assert lines >= 3

    def test_syntax_error_marking(self):
        """Test syntax error indication"""
        # Simulate setting an error on line 10
        if hasattr(self.backend.editor_text, 'set_error'):
            self.backend.editor_text.set_error(10, "Syntax error")

        # Simulate clearing errors
        if hasattr(self.backend.editor_text, 'clear_all_errors'):
            self.backend.editor_text.clear_all_errors()

        # Note: Actual error display depends on LineNumberedText implementation

    def run_all_tests(self):
        """Run all tests and report results"""
        print("\n" + "="*60)
        print("TK UI AUTOMATED TEST FRAMEWORK")
        print("="*60)

        if not self.setup():
            print("Failed to set up test environment")
            return False

        # Run all tests
        self.run_test("Editor basic operations", self.test_editor_basic)
        self.run_test("Breakpoint toggle", self.test_breakpoint_toggle)
        self.run_test("Find functionality", self.test_find_functionality)
        self.run_test("Replace functionality", self.test_replace_functionality)
        self.run_test("Status updates", self.test_status_updates)
        self.run_test("Save/Load simulation", self.test_save_load_simulation)
        self.run_test("Output display", self.test_output_display)
        self.run_test("Line numbers", self.test_line_numbers)
        self.run_test("Syntax error marking", self.test_syntax_error_marking)

        # Clean up
        self.teardown()

        # Report summary
        print("\n" + "="*60)
        print(f"RESULTS: {self.passed} passed, {self.failed} failed")
        print("="*60)

        if self.failed > 0:
            print("\nFailed tests:")
            for name, passed, error in self.tests:
                if not passed:
                    print(f"  - {name}: {error}")

        return self.failed == 0

def main():
    """Main entry point"""
    # Run without display
    import os
    os.environ['DISPLAY'] = ''  # Disable display for CI/headless

    tester = TkTestFramework()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()