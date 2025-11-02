#!/usr/bin/env python3
"""
Test various curses UI features with real BASIC programs.

This script tests:
1. Loading BASIC programs
2. Running programs
3. Editor features (LIST, NEW)
4. Help system
5. Error handling
"""

import sys
import time
import pexpect
from pathlib import Path

# Test timeout
TIMEOUT = 30

class CursesUITester:
    """Test runner for curses UI features."""

    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_programs = [
            "basic/dev/bas_tests/prime1.bas",
            "basic/dev/bas_tests/test.bas",
            "basic/dev/bas_tests/gosub50.bas",
            "basic/dev/bas_tests/hanoi.bas",
        ]

    def print_header(self, msg):
        """Print section header."""
        print(f"\n{'='*70}")
        print(msg)
        print('='*70)

    def print_test(self, name, passed, details=""):
        """Print test result."""
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
        if details:
            print(f"  {details}")

        if passed:
            self.tests_passed += 1
        else:
            self.tests_failed += 1

    def test_program_load(self, program_path):
        """Test loading a BASIC program."""
        self.print_header(f"Testing: Load {program_path}")

        try:
            child = pexpect.spawn(
                f'python3 mbasic {program_path} --ui curses',
                encoding='utf-8',
                timeout=TIMEOUT,
                dimensions=(24, 80)
            )

            # Wait a bit for UI to initialize
            time.sleep(0.5)

            # Send Ctrl+Q to quit
            child.send('\x11')  # Ctrl+Q

            # Wait for exit
            child.expect(pexpect.EOF, timeout=2)
            child.close()

            if child.exitstatus == 0:
                self.print_test(f"Load {Path(program_path).name}", True,
                               "Program loaded and UI exited cleanly")
                return True
            else:
                self.print_test(f"Load {Path(program_path).name}", False,
                               f"Exit code: {child.exitstatus}")
                return False

        except pexpect.TIMEOUT:
            self.print_test(f"Load {Path(program_path).name}", False,
                           "Timeout waiting for UI")
            try:
                child.terminate(force=True)
            except:
                pass
            return False
        except Exception as e:
            self.print_test(f"Load {Path(program_path).name}", False,
                           f"Error: {e}")
            return False

    def test_new_program(self):
        """Test creating a new program."""
        self.print_header("Testing: NEW command")

        try:
            child = pexpect.spawn(
                'python3 mbasic --ui curses',
                encoding='utf-8',
                timeout=TIMEOUT,
                dimensions=(24, 80)
            )

            time.sleep(0.5)

            # Send Ctrl+N for NEW
            child.send('\x0e')  # Ctrl+N
            time.sleep(0.3)

            # Type a simple program
            child.send('10 PRINT "HELLO"\r')
            time.sleep(0.2)
            child.send('20 END\r')
            time.sleep(0.2)

            # Quit
            child.send('\x11')  # Ctrl+Q

            child.expect(pexpect.EOF, timeout=2)
            child.close()

            if child.exitstatus == 0:
                self.print_test("NEW command", True,
                               "Created new program and exited cleanly")
                return True
            else:
                self.print_test("NEW command", False,
                               f"Exit code: {child.exitstatus}")
                return False

        except pexpect.TIMEOUT:
            self.print_test("NEW command", False, "Timeout")
            try:
                child.terminate(force=True)
            except:
                pass
            return False
        except Exception as e:
            self.print_test("NEW command", False, f"Error: {e}")
            return False

    def test_help_system(self):
        """Test help system."""
        self.print_header("Testing: Help System")

        try:
            child = pexpect.spawn(
                'python3 mbasic --ui curses',
                encoding='utf-8',
                timeout=TIMEOUT,
                dimensions=(24, 80)
            )

            time.sleep(0.5)

            # Open help with Ctrl+H
            child.send('\x08')  # Ctrl+H
            time.sleep(0.5)

            # Close help with Esc or q
            child.send('q')
            time.sleep(0.3)

            # Quit
            child.send('\x11')  # Ctrl+Q

            child.expect(pexpect.EOF, timeout=2)
            child.close()

            if child.exitstatus == 0:
                self.print_test("Help system", True,
                               "Help opened and closed successfully")
                return True
            else:
                self.print_test("Help system", False,
                               f"Exit code: {child.exitstatus}")
                return False

        except pexpect.TIMEOUT:
            self.print_test("Help system", False, "Timeout")
            try:
                child.terminate(force=True)
            except:
                pass
            return False
        except Exception as e:
            self.print_test("Help system", False, f"Error: {e}")
            return False

    def test_run_simple_program(self):
        """Test running a simple program."""
        self.print_header("Testing: Run Program")

        try:
            child = pexpect.spawn(
                'python3 mbasic --ui curses',
                encoding='utf-8',
                timeout=TIMEOUT,
                dimensions=(24, 80)
            )

            time.sleep(0.5)

            # Type a simple program
            child.send('10 PRINT "TESTING"\r')
            time.sleep(0.2)
            child.send('20 END\r')
            time.sleep(0.2)

            # Run with Ctrl+R
            child.send('\x12')  # Ctrl+R
            time.sleep(1.0)

            # Quit
            child.send('\x11')  # Ctrl+Q

            child.expect(pexpect.EOF, timeout=2)
            child.close()

            if child.exitstatus == 0:
                self.print_test("Run program", True,
                               "Program ran successfully")
                return True
            else:
                self.print_test("Run program", False,
                               f"Exit code: {child.exitstatus}")
                return False

        except pexpect.TIMEOUT:
            self.print_test("Run program", False, "Timeout")
            try:
                child.terminate(force=True)
            except:
                pass
            return False
        except Exception as e:
            self.print_test("Run program", False, f"Error: {e}")
            return False

    def test_list_command(self):
        """Test LIST command."""
        self.print_header("Testing: LIST Command")

        try:
            child = pexpect.spawn(
                'python3 mbasic --ui curses',
                encoding='utf-8',
                timeout=TIMEOUT,
                dimensions=(24, 80)
            )

            time.sleep(0.5)

            # Type a program
            child.send('10 PRINT "LINE 1"\r')
            time.sleep(0.2)
            child.send('20 PRINT "LINE 2"\r')
            time.sleep(0.2)

            # Use Ctrl+L for LIST
            child.send('\x0c')  # Ctrl+L
            time.sleep(0.5)

            # Quit
            child.send('\x11')  # Ctrl+Q

            child.expect(pexpect.EOF, timeout=2)
            child.close()

            if child.exitstatus == 0:
                self.print_test("LIST command", True,
                               "LIST executed successfully")
                return True
            else:
                self.print_test("LIST command", False,
                               f"Exit code: {child.exitstatus}")
                return False

        except pexpect.TIMEOUT:
            self.print_test("LIST command", False, "Timeout")
            try:
                child.terminate(force=True)
            except:
                pass
            return False
        except Exception as e:
            self.print_test("LIST command", False, f"Error: {e}")
            return False

    def run_all_tests(self):
        """Run all tests."""
        self.print_header("CURSES UI FEATURE TESTS")

        # Test loading existing programs
        for program in self.test_programs:
            if Path(program).exists():
                self.test_program_load(program)

        # Test interactive features
        self.test_new_program()
        self.test_help_system()
        self.test_run_simple_program()
        self.test_list_command()

        # Print summary
        self.print_header("SUMMARY")
        total = self.tests_passed + self.tests_failed
        print(f"Passed: {self.tests_passed}/{total}")
        print(f"Failed: {self.tests_failed}/{total}")

        return self.tests_failed == 0

def main():
    """Main entry point."""
    tester = CursesUITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
