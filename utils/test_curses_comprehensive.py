#!/usr/bin/env python3
"""
Comprehensive curses UI testing framework.

Combines multiple approaches for robust testing:
1. Direct method testing (fastest, catches most errors)
2. pexpect for integration testing (spawns real process)
3. Exception capture and reporting
"""

import sys
import os
sys.path.insert(0, 'src')

import pexpect
import time
import traceback as tb
from io import StringIO
from src.ui.keybindings import (
    HELP_KEY, LIST_KEY, NEW_KEY, RUN_KEY
)

class TestResult:
    """Store test results."""
    def __init__(self, name):
        self.name = name
        self.passed = False
        self.error = None
        self.output = ""

    def success(self, output=""):
        self.passed = True
        self.output = output

    def fail(self, error):
        self.passed = False
        self.error = error

    def __str__(self):
        status = "✓ PASS" if self.passed else "✗ FAIL"
        result = f"{status}: {self.name}"
        if self.error:
            result += f"\n  Error: {self.error}"
        if self.output:
            result += f"\n  Output: {self.output[:100]}"
        return result

class CursesUITester:
    """Test harness for curses UI."""

    def __init__(self):
        self.results = []

    def test_ui_creation(self):
        """Test that UI can be created without errors."""
        result = TestResult("UI Creation")

        try:
            from ui.curses_ui import CursesBackend
            from iohandler.console import ConsoleIOHandler
            from editing import ProgramManager
            from parser import TypeInfo

            # Create components
            def_type_map = {letter: TypeInfo.SINGLE for letter in 'abcdefghijklmnopqrstuvwxyz'}
            io_handler = ConsoleIOHandler(debug_enabled=False)
            program_manager = ProgramManager(def_type_map)

            # Create backend
            backend = CursesBackend(io_handler, program_manager)
            backend._create_ui()

            result.success(f"Loop created: {type(backend.loop)}")

        except Exception as e:
            result.fail(f"{type(e).__name__}: {str(e)}")

        self.results.append(result)
        return result.passed

    def test_input_handlers(self):
        """Test that input handlers work."""
        result = TestResult("Input Handlers")

        try:
            from ui.curses_ui import CursesBackend
            from iohandler.console import ConsoleIOHandler
            from editing import ProgramManager
            from parser import TypeInfo

            def_type_map = {letter: TypeInfo.SINGLE for letter in 'abcdefghijklmnopqrstuvwxyz'}
            io_handler = ConsoleIOHandler(debug_enabled=False)
            program_manager = ProgramManager(def_type_map)
            backend = CursesBackend(io_handler, program_manager)
            backend._create_ui()

            # Test various input handlers
            handlers_tested = []

            # Help key - should not raise
            try:
                backend._handle_input(HELP_KEY)
                handlers_tested.append(HELP_KEY)
            except Exception as e:
                raise Exception(f"{HELP_KEY} failed: {e}")

            # List key
            try:
                backend._handle_input(LIST_KEY)
                handlers_tested.append(LIST_KEY)
            except Exception as e:
                raise Exception(f"{LIST_KEY} failed: {e}")

            # New key
            try:
                backend._handle_input(NEW_KEY)
                handlers_tested.append(NEW_KEY)
            except Exception as e:
                raise Exception(f"{NEW_KEY} failed: {e}")

            result.success(f"Tested: {', '.join(handlers_tested)}")

        except Exception as e:
            result.fail(f"{type(e).__name__}: {str(e)}")

        self.results.append(result)
        return result.passed

    def test_program_parsing(self):
        """Test that program can be parsed from editor."""
        result = TestResult("Program Parsing")

        try:
            from ui.curses_ui import CursesBackend
            from iohandler.console import ConsoleIOHandler
            from editing import ProgramManager
            from parser import TypeInfo

            def_type_map = {letter: TypeInfo.SINGLE for letter in 'abcdefghijklmnopqrstuvwxyz'}
            io_handler = ConsoleIOHandler(debug_enabled=False)
            program_manager = ProgramManager(def_type_map)
            backend = CursesBackend(io_handler, program_manager)
            backend._create_ui()

            # Set editor text
            backend.editor.set_edit_text('10 PRINT "HELLO"\n20 END')

            # Parse it
            backend._parse_editor_content()

            if 10 in backend.editor_lines and 20 in backend.editor_lines:
                result.success(f"Parsed {len(backend.editor_lines)} lines")
            else:
                result.fail("Lines not parsed correctly")

        except Exception as e:
            result.fail(f"{type(e).__name__}: {str(e)}")

        self.results.append(result)
        return result.passed

    def test_run_program_method(self):
        """Test the _run_program method for errors."""
        result = TestResult("Run Program Method")

        try:
            from ui.curses_ui import CursesBackend
            from iohandler.console import ConsoleIOHandler
            from editing import ProgramManager
            from parser import TypeInfo

            def_type_map = {letter: TypeInfo.SINGLE for letter in 'abcdefghijklmnopqrstuvwxyz'}
            io_handler = ConsoleIOHandler(debug_enabled=False)
            program_manager = ProgramManager(def_type_map)
            backend = CursesBackend(io_handler, program_manager)
            backend._create_ui()

            # Set a simple program
            backend.editor.set_edit_text('10 PRINT "HELLO"\n20 END')

            # Capture any errors
            error_caught = None
            try:
                backend._run_program()
            except Exception as e:
                error_caught = e

            if error_caught:
                result.fail(f"Exception during _run_program: {type(error_caught).__name__}: {error_caught}")
            else:
                # Check output buffer for errors
                output_text = '\n'.join(backend.output_buffer)
                if 'error' in output_text.lower() or 'exception' in output_text.lower():
                    result.fail(f"Error in output: {output_text[:200]}")
                else:
                    result.success(f"Program ran, output lines: {len(backend.output_buffer)}")

        except Exception as e:
            result.fail(f"{type(e).__name__}: {str(e)}\n{tb.format_exc()}")

        self.results.append(result)
        return result.passed

    def test_with_pexpect(self):
        """Test with real subprocess using pexpect."""
        result = TestResult("pexpect Integration")

        try:
            child = pexpect.spawn(
                'python3 mbasic.py --backend curses',
                encoding='utf-8',
                timeout=5,
                dimensions=(24, 80)
            )

            # Capture stderr to catch errors
            errors = []

            try:
                # Wait for startup
                time.sleep(1)

                # Type a program
                child.send('10 PRINT "HELLO"\r')
                time.sleep(0.3)
                child.send('20 END\r')
                time.sleep(0.3)

                # Try to run
                child.send('\x12')  # Ctrl+R
                time.sleep(1)

                # Quit with Ctrl+Q
                child.send('\x11')  # Ctrl+Q
                time.sleep(1)

                # Check if process exited cleanly
                if child.isalive():
                    # Try Ctrl+C as well
                    child.send('\x03')  # Ctrl+C
                    time.sleep(1)

                if child.isalive():
                    child.terminate()
                    result.fail("Process did not exit cleanly")
                else:
                    result.success("Process started and stopped cleanly")

            except pexpect.TIMEOUT as e:
                result.fail(f"Timeout: {e}")
                child.terminate()
            except Exception as e:
                result.fail(f"{type(e).__name__}: {e}")
                if child.isalive():
                    child.terminate()

        except Exception as e:
            result.fail(f"Failed to spawn: {type(e).__name__}: {e}")

        self.results.append(result)
        return result.passed

    def run_all_tests(self):
        """Run all tests and return summary."""
        print("="*70)
        print("CURSES UI COMPREHENSIVE TEST SUITE")
        print("="*70)

        tests = [
            ("UI Creation", self.test_ui_creation),
            ("Input Handlers", self.test_input_handlers),
            ("Program Parsing", self.test_program_parsing),
            ("Run Program Method", self.test_run_program_method),
            ("pexpect Integration", self.test_with_pexpect),
        ]

        for name, test_func in tests:
            print(f"\nRunning: {name}...")
            try:
                test_func()
            except Exception as e:
                print(f"  Unexpected error in test runner: {e}")

        # Print results
        print("\n" + "="*70)
        print("RESULTS")
        print("="*70)

        for result in self.results:
            print(result)

        # Summary
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)

        print("\n" + "="*70)
        print(f"SUMMARY: {passed}/{total} tests passed")
        print("="*70)

        return passed == total

if __name__ == '__main__':
    tester = CursesUITester()
    all_passed = tester.run_all_tests()
    sys.exit(0 if all_passed else 1)
