#!/usr/bin/env python3
"""
Comprehensive test suite for CLI backend using pexpect.

This test suite verifies all CLI functionality including:
- Basic commands (NEW, LOAD, SAVE, RUN, LIST)
- Program editing (line entry, DELETE, EDIT, RENUM)
- Immediate mode execution
- Error handling
- Help system
- File operations
"""

import pexpect
import sys
import os
import tempfile
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestCLI:
    """Test harness for CLI backend"""

    def __init__(self):
        self.proc = None
        self.test_dir = None
        self.passed = 0
        self.failed = 0
        self.tests = []

    def setup(self):
        """Set up test environment"""
        # Create temp directory for test files
        self.test_dir = tempfile.mkdtemp(prefix="mbasic_cli_test_")
        print(f"Test directory: {self.test_dir}")

        # Start MBASIC in CLI mode
        self.proc = pexpect.spawn('python3 mbasic --backend cli',
                                  cwd=str(Path(__file__).parent.parent),
                                  timeout=5,
                                  encoding='utf-8')

        # Wait for prompt
        self.proc.expect('Ready')
        return True

    def teardown(self):
        """Clean up test environment"""
        if self.proc:
            try:
                self.proc.terminate()
                self.proc.wait()
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

    def test_new_command(self):
        """Test NEW command clears program"""
        # Enter a program
        self.proc.sendline('10 PRINT "TEST"')
        self.proc.expect('Ready')

        # Verify it's there
        self.proc.sendline('LIST')
        self.proc.expect('10 PRINT "TEST"')
        self.proc.expect('Ready')

        # Clear it
        self.proc.sendline('NEW')
        self.proc.expect('Ready')

        # Verify it's gone
        self.proc.sendline('LIST')
        self.proc.expect('Ready')
        # Should not see the program line

    def test_line_entry(self):
        """Test entering program lines"""
        # Clear program first
        self.proc.sendline('NEW')
        self.proc.expect('Ready')

        # Enter lines
        self.proc.sendline('10 REM TEST PROGRAM')
        self.proc.expect('Ready')
        self.proc.sendline('20 PRINT "HELLO"')
        self.proc.expect('Ready')
        self.proc.sendline('30 PRINT "WORLD"')
        self.proc.expect('Ready')

        # List and verify
        self.proc.sendline('LIST')
        self.proc.expect('10 REM TEST PROGRAM')
        self.proc.expect('20 PRINT "HELLO"')
        self.proc.expect('30 PRINT "WORLD"')
        self.proc.expect('Ready')

    def test_run_command(self):
        """Test RUN command"""
        self.proc.sendline('NEW')
        self.proc.expect('Ready')

        # Enter simple program
        self.proc.sendline('10 PRINT "START"')
        self.proc.expect('Ready')
        self.proc.sendline('20 PRINT "END"')
        self.proc.expect('Ready')

        # Run it
        self.proc.sendline('RUN')
        self.proc.expect('START')
        self.proc.expect('END')
        self.proc.expect('Ready')

    def test_immediate_mode(self):
        """Test immediate mode execution"""
        # Clear any program
        self.proc.sendline('NEW')
        self.proc.expect('Ready')

        # Execute immediate commands
        self.proc.sendline('PRINT 2+2')
        self.proc.expect('4')
        self.proc.expect('Ready')

        self.proc.sendline('PRINT "HELLO"+" WORLD"')
        self.proc.expect('HELLO WORLD')
        self.proc.expect('Ready')

    def test_delete_command(self):
        """Test DELETE command"""
        self.proc.sendline('NEW')
        self.proc.expect('Ready')

        # Enter lines
        self.proc.sendline('10 PRINT "A"')
        self.proc.expect('Ready')
        self.proc.sendline('20 PRINT "B"')
        self.proc.expect('Ready')
        self.proc.sendline('30 PRINT "C"')
        self.proc.expect('Ready')

        # Delete middle line
        self.proc.sendline('DELETE 20')
        self.proc.expect('Ready')

        # Verify
        self.proc.sendline('LIST')
        self.proc.expect('10 PRINT "A"')
        self.proc.expect('30 PRINT "C"')
        self.proc.expect('Ready')

    def test_edit_command(self):
        """Test EDIT command"""
        self.proc.sendline('NEW')
        self.proc.expect('Ready')

        # Enter a line
        self.proc.sendline('10 PRINT "OLD"')
        self.proc.expect('Ready')

        # Edit it
        self.proc.sendline('EDIT 10')
        # The EDIT command should show the current line
        self.proc.expect('10 PRINT "OLD"')
        # Send edited version
        self.proc.sendline('10 PRINT "NEW"')
        self.proc.expect('Ready')

        # Verify change
        self.proc.sendline('LIST')
        self.proc.expect('10 PRINT "NEW"')
        self.proc.expect('Ready')

    def test_renum_command(self):
        """Test RENUM command"""
        self.proc.sendline('NEW')
        self.proc.expect('Ready')

        # Enter lines with non-standard numbering
        self.proc.sendline('5 PRINT "A"')
        self.proc.expect('Ready')
        self.proc.sendline('17 PRINT "B"')
        self.proc.expect('Ready')
        self.proc.sendline('99 PRINT "C"')
        self.proc.expect('Ready')

        # Renumber
        self.proc.sendline('RENUM')
        self.proc.expect('Ready')

        # Verify new numbering
        self.proc.sendline('LIST')
        self.proc.expect('10 PRINT "A"')
        self.proc.expect('20 PRINT "B"')
        self.proc.expect('30 PRINT "C"')
        self.proc.expect('Ready')

    def test_save_load(self):
        """Test SAVE and LOAD commands"""
        test_file = os.path.join(self.test_dir, 'test.bas')

        self.proc.sendline('NEW')
        self.proc.expect('Ready')

        # Enter a program
        self.proc.sendline('10 REM SAVE TEST')
        self.proc.expect('Ready')
        self.proc.sendline('20 PRINT "SAVED"')
        self.proc.expect('Ready')

        # Save it
        self.proc.sendline(f'SAVE "{test_file}"')
        self.proc.expect('Ready')

        # Clear and reload
        self.proc.sendline('NEW')
        self.proc.expect('Ready')

        self.proc.sendline(f'LOAD "{test_file}"')
        self.proc.expect('Ready')

        # Verify loaded
        self.proc.sendline('LIST')
        self.proc.expect('10 REM SAVE TEST')
        self.proc.expect('20 PRINT "SAVED"')
        self.proc.expect('Ready')

    def test_auto_command(self):
        """Test AUTO command for automatic line numbering"""
        self.proc.sendline('NEW')
        self.proc.expect('Ready')

        # Start auto mode
        self.proc.sendline('AUTO')
        self.proc.expect('10')  # Should show first line number

        # Enter some lines
        self.proc.sendline('PRINT "LINE 1"')
        self.proc.expect('20')  # Next line number

        self.proc.sendline('PRINT "LINE 2"')
        self.proc.expect('30')

        # Exit auto mode with empty line
        self.proc.sendline('')
        self.proc.expect('Ready')

        # Verify program
        self.proc.sendline('LIST')
        self.proc.expect('10 PRINT "LINE 1"')
        self.proc.expect('20 PRINT "LINE 2"')
        self.proc.expect('Ready')

    def test_error_handling(self):
        """Test error messages"""
        self.proc.sendline('NEW')
        self.proc.expect('Ready')

        # Syntax error
        self.proc.sendline('10 PRIMT "TYPO"')  # Intentional typo
        self.proc.expect('Syntax error')

        # Run empty program
        self.proc.sendline('NEW')
        self.proc.expect('Ready')
        self.proc.sendline('RUN')
        self.proc.expect('Ready')  # Should handle gracefully

        # Invalid command
        self.proc.sendline('INVALID')
        self.proc.expect('Syntax error')

    def test_help_system(self):
        """Test HELP command"""
        # Basic help
        self.proc.sendline('HELP')
        self.proc.expect('Available commands')  # Should show command list
        self.proc.expect('Ready')

        # Help for specific command
        self.proc.sendline('HELP PRINT')
        self.proc.expect('PRINT')  # Should show PRINT documentation
        self.proc.expect('Ready')

        # Help search
        self.proc.sendline('HELP SEARCH loop')
        self.proc.expect_list(['FOR', 'WHILE'])  # Should find loop commands
        self.proc.expect('Ready')

    def test_variables(self):
        """Test variable operations in immediate mode"""
        self.proc.sendline('NEW')
        self.proc.expect('Ready')

        # Set variables
        self.proc.sendline('A = 10')
        self.proc.expect('Ready')

        self.proc.sendline('B$ = "TEST"')
        self.proc.expect('Ready')

        # Use variables
        self.proc.sendline('PRINT A * 2')
        self.proc.expect('20')
        self.proc.expect('Ready')

        self.proc.sendline('PRINT B$')
        self.proc.expect('TEST')
        self.proc.expect('Ready')

    def test_multistatement_lines(self):
        """Test multi-statement lines with colons"""
        self.proc.sendline('NEW')
        self.proc.expect('Ready')

        # Enter multi-statement line
        self.proc.sendline('10 A=1:B=2:PRINT A+B')
        self.proc.expect('Ready')

        # Run it
        self.proc.sendline('RUN')
        self.proc.expect('3')
        self.proc.expect('Ready')

    def test_for_loop(self):
        """Test FOR/NEXT loop"""
        self.proc.sendline('NEW')
        self.proc.expect('Ready')

        # Enter loop program
        self.proc.sendline('10 FOR I = 1 TO 3')
        self.proc.expect('Ready')
        self.proc.sendline('20 PRINT I')
        self.proc.expect('Ready')
        self.proc.sendline('30 NEXT I')
        self.proc.expect('Ready')

        # Run it
        self.proc.sendline('RUN')
        self.proc.expect('1')
        self.proc.expect('2')
        self.proc.expect('3')
        self.proc.expect('Ready')

    def test_gosub_return(self):
        """Test GOSUB/RETURN"""
        self.proc.sendline('NEW')
        self.proc.expect('Ready')

        # Enter program with subroutine
        self.proc.sendline('10 PRINT "MAIN"')
        self.proc.expect('Ready')
        self.proc.sendline('20 GOSUB 100')
        self.proc.expect('Ready')
        self.proc.sendline('30 PRINT "BACK"')
        self.proc.expect('Ready')
        self.proc.sendline('40 END')
        self.proc.expect('Ready')
        self.proc.sendline('100 PRINT "SUB"')
        self.proc.expect('Ready')
        self.proc.sendline('110 RETURN')
        self.proc.expect('Ready')

        # Run it
        self.proc.sendline('RUN')
        self.proc.expect('MAIN')
        self.proc.expect('SUB')
        self.proc.expect('BACK')
        self.proc.expect('Ready')

    def run_all_tests(self):
        """Run all tests and report results"""
        print("\n" + "="*60)
        print("MBASIC CLI COMPREHENSIVE TEST SUITE")
        print("="*60)

        if not self.setup():
            print("Failed to set up test environment")
            return False

        # Run all tests
        self.run_test("NEW command", self.test_new_command)
        self.run_test("Line entry", self.test_line_entry)
        self.run_test("RUN command", self.test_run_command)
        self.run_test("Immediate mode", self.test_immediate_mode)
        self.run_test("DELETE command", self.test_delete_command)
        self.run_test("EDIT command", self.test_edit_command)
        self.run_test("RENUM command", self.test_renum_command)
        self.run_test("SAVE/LOAD", self.test_save_load)
        self.run_test("AUTO command", self.test_auto_command)
        self.run_test("Error handling", self.test_error_handling)
        self.run_test("HELP system", self.test_help_system)
        self.run_test("Variables", self.test_variables)
        self.run_test("Multi-statement lines", self.test_multistatement_lines)
        self.run_test("FOR/NEXT loop", self.test_for_loop)
        self.run_test("GOSUB/RETURN", self.test_gosub_return)

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
    tester = TestCLI()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()