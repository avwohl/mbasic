#!/usr/bin/env python3
"""
Test for Immediate Mode HELP command

Tests that the HELP command works correctly in immediate mode.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from immediate_executor import ImmediateExecutor, OutputCapturingIOHandler


def test_help_command():
    """Test that HELP command shows help text."""
    print("Testing HELP command...")

    # Create immediate executor with capturing IO
    io = OutputCapturingIOHandler()
    executor = ImmediateExecutor(None, None, io)

    # Test HELP command
    success, output = executor.execute("HELP")

    assert success, "HELP command should succeed"
    assert "IMMEDIATE MODE HELP" in output, "Help output should contain title"
    assert "PRINT" in output, "Help should mention PRINT command"
    assert "EXAMPLES" in output, "Help should have examples section"
    assert "LIMITATIONS" in output, "Help should explain limitations"

    print("✓ HELP command test passed")


def test_help_case_insensitive():
    """Test that HELP works in any case."""
    print("Testing case-insensitive HELP...")

    io = OutputCapturingIOHandler()
    executor = ImmediateExecutor(None, None, io)

    # Test different cases
    for cmd in ['HELP', 'help', 'Help', 'HeLp']:
        success, output = executor.execute(cmd)
        assert success, f"'{cmd}' should work"
        assert "IMMEDIATE MODE HELP" in output, f"'{cmd}' should show help"

    print("✓ Case-insensitive test passed")


def test_help_with_parens():
    """Test that HELP() also works."""
    print("Testing HELP() variant...")

    io = OutputCapturingIOHandler()
    executor = ImmediateExecutor(None, None, io)

    success, output = executor.execute("HELP()")

    assert success, "HELP() should work"
    assert "IMMEDIATE MODE HELP" in output, "HELP() should show help"

    print("✓ HELP() test passed")


def test_question_help():
    """Test that ?HELP works."""
    print("Testing ?HELP variant...")

    io = OutputCapturingIOHandler()
    executor = ImmediateExecutor(None, None, io)

    success, output = executor.execute("?HELP")

    assert success, "?HELP should work"
    assert "IMMEDIATE MODE HELP" in output, "?HELP should show help"

    print("✓ ?HELP test passed")


def test_help_doesnt_break_executor():
    """Test that HELP doesn't break the executor."""
    print("Testing HELP doesn't break executor...")

    io = OutputCapturingIOHandler()
    executor = ImmediateExecutor(None, None, io)

    # Run HELP multiple times
    for _ in range(3):
        success, output = executor.execute("HELP")
        assert success, "HELP should always succeed"
        assert len(output) > 100, "HELP should return substantial output"

    print("✓ HELP stability test passed")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("IMMEDIATE MODE HELP COMMAND TEST SUITE")
    print("=" * 60)
    print()

    try:
        test_help_command()
        test_help_case_insensitive()
        test_help_with_parens()
        test_question_help()
        test_help_doesnt_break_executor()

        print()
        print("=" * 60)
        print("ALL TESTS PASSED ✅")
        print("=" * 60)
        return 0

    except AssertionError as e:
        print()
        print("=" * 60)
        print(f"TEST FAILED ❌: {e}")
        print("=" * 60)
        return 1

    except Exception as e:
        print()
        print("=" * 60)
        print(f"UNEXPECTED ERROR ❌: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
