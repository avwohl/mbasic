#!/usr/bin/env python3
"""
Test input sanitization functionality.

Tests control character filtering and parity bit clearing
across different input scenarios.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from input_sanitizer import (
    is_valid_input_char,
    sanitize_input,
    clear_parity,
    clear_parity_all,
    sanitize_and_clear_parity
)


def test_is_valid_input_char():
    """Test character validation."""
    print("Testing is_valid_input_char()...")

    # Valid characters
    assert is_valid_input_char('A'), "Should accept uppercase letter"
    assert is_valid_input_char('z'), "Should accept lowercase letter"
    assert is_valid_input_char('0'), "Should accept digit"
    assert is_valid_input_char(' '), "Should accept space"
    assert is_valid_input_char('\n'), "Should accept newline"
    assert is_valid_input_char('\t'), "Should accept tab"
    assert is_valid_input_char('\r'), "Should accept carriage return"
    assert is_valid_input_char('"'), "Should accept double quote"
    assert is_valid_input_char('$'), "Should accept dollar sign"
    assert is_valid_input_char('%'), "Should accept percent"

    # Invalid control characters
    assert not is_valid_input_char('\x00'), "Should reject NULL"
    assert not is_valid_input_char('\x01'), "Should reject Ctrl+A"
    assert not is_valid_input_char('\x02'), "Should reject Ctrl+B"
    assert not is_valid_input_char('\x03'), "Should reject Ctrl+C (except in terminal)"
    assert not is_valid_input_char('\x07'), "Should reject BELL"
    assert not is_valid_input_char('\x08'), "Should reject BACKSPACE"
    assert not is_valid_input_char('\x1B'), "Should reject ESC"
    assert not is_valid_input_char('\x7F'), "Should reject DEL"

    # Extended ASCII
    assert not is_valid_input_char(chr(128)), "Should reject extended ASCII"
    assert not is_valid_input_char(chr(255)), "Should reject high extended ASCII"

    print("✓ is_valid_input_char() tests passed")


def test_sanitize_input():
    """Test input sanitization."""
    print("\nTesting sanitize_input()...")

    # Clean input
    assert sanitize_input('PRINT "Hello"') == 'PRINT "Hello"', "Should keep valid input"

    # Control characters
    assert sanitize_input('PRINT\x01"Hello"') == 'PRINT"Hello"', "Should remove Ctrl+A"
    assert sanitize_input('A\x00B\x01C\x02D') == 'ABCD', "Should remove multiple control chars"

    # Newlines and tabs preserved
    assert sanitize_input('Line1\nLine2') == 'Line1\nLine2', "Should keep newlines"
    assert sanitize_input('A\tB') == 'A\tB', "Should keep tabs"
    assert sanitize_input('A\r\nB') == 'A\r\nB', "Should keep CRLF"

    # Extended ASCII
    assert sanitize_input('A' + chr(193) + 'B') == 'AB', "Should remove extended ASCII"

    # Mixed valid and invalid
    assert sanitize_input('10 PRINT\x07 "HELLO"\x1B') == '10 PRINT "HELLO"', "Should filter mixed"

    print("✓ sanitize_input() tests passed")


def test_clear_parity():
    """Test parity bit clearing."""
    print("\nTesting clear_parity()...")

    # Normal ASCII (no parity)
    assert clear_parity('A') == 'A', "Should keep normal ASCII"
    assert ord(clear_parity('A')) == 65, "Should maintain ASCII value"

    # Parity bit set (bit 7 = 1)
    assert clear_parity(chr(193)) == 'A', "Should clear parity: chr(193) -> 'A'"
    assert clear_parity(chr(194)) == 'B', "Should clear parity: chr(194) -> 'B'"
    assert clear_parity(chr(195)) == 'C', "Should clear parity: chr(195) -> 'C'"

    # Verify parity clearing formula
    for i in range(128):
        char = chr(i)
        parity_char = chr(i | 0x80)  # Set bit 7
        assert clear_parity(parity_char) == char, f"Should clear parity for chr({i})"

    print("✓ clear_parity() tests passed")


def test_clear_parity_all():
    """Test parity bit clearing for strings."""
    print("\nTesting clear_parity_all()...")

    # Normal text
    assert clear_parity_all('PRINT "TEST"') == 'PRINT "TEST"', "Should keep normal text"

    # Text with parity bits
    text_with_parity = chr(193) + chr(194) + chr(195)  # A, B, C with bit 7 set
    assert clear_parity_all(text_with_parity) == 'ABC', "Should clear all parity bits"

    # Mixed normal and parity
    mixed = 'A' + chr(194) + 'C'  # A, B (parity), C
    assert clear_parity_all(mixed) == 'ABC', "Should handle mixed text"

    print("✓ clear_parity_all() tests passed")


def test_sanitize_and_clear_parity():
    """Test combined sanitization and parity clearing."""
    print("\nTesting sanitize_and_clear_parity()...")

    # Clean input - no modification
    result, modified = sanitize_and_clear_parity('PRINT "Hello"')
    assert result == 'PRINT "Hello"', "Should keep clean input"
    assert not modified, "Should report no modification"

    # Control characters - modified
    result, modified = sanitize_and_clear_parity('PRINT\x01"Hello"')
    assert result == 'PRINT"Hello"', "Should remove control chars"
    assert modified, "Should report modification"

    # Parity bits - modified
    result, modified = sanitize_and_clear_parity(chr(193) + chr(194) + chr(195))
    assert result == 'ABC', "Should clear parity bits"
    assert modified, "Should report modification"

    # Both control chars and parity - modified
    mixed = chr(193) + '\x01' + chr(194) + '\x02' + chr(195)
    result, modified = sanitize_and_clear_parity(mixed)
    assert result == 'ABC', "Should handle both issues"
    assert modified, "Should report modification"

    # Newlines and tabs preserved
    result, modified = sanitize_and_clear_parity('Line1\nLine2\tTabbed')
    assert result == 'Line1\nLine2\tTabbed', "Should preserve newlines/tabs"
    assert not modified, "Should report no modification"

    print("✓ sanitize_and_clear_parity() tests passed")


def test_basic_program_sanitization():
    """Test sanitizing actual BASIC programs."""
    print("\nTesting BASIC program sanitization...")

    # Normal program
    program = '10 PRINT "HELLO"\n20 FOR I=1 TO 10\n30 NEXT I'
    result, modified = sanitize_and_clear_parity(program)
    assert result == program, "Should keep valid program"
    assert not modified, "Should report no modification"

    # Program with control characters
    bad_program = '10 PRINT\x01 "HELLO"\x07\n20 FOR I=1 TO 10\n30 NEXT I'
    result, modified = sanitize_and_clear_parity(bad_program)
    expected = '10 PRINT "HELLO"\n20 FOR I=1 TO 10\n30 NEXT I'
    assert result == expected, "Should remove control chars from program"
    assert modified, "Should report modification"

    # Program with parity bits
    parity_program = chr(193) + chr(194) + chr(195) + '\n' + chr(194) + chr(197)
    result, modified = sanitize_and_clear_parity(parity_program)
    assert 'A' in result and 'B' in result and 'C' in result, "Should clear parity in program"
    assert modified, "Should report modification"

    print("✓ BASIC program sanitization tests passed")


def test_file_content_scenarios():
    """Test real-world file content scenarios."""
    print("\nTesting file content scenarios...")

    # Scenario 1: DOS file with CRLF line endings
    dos_file = '10 PRINT "TEST"\r\n20 END\r\n'
    result, modified = sanitize_and_clear_parity(dos_file)
    assert '\r\n' in result, "Should preserve CRLF"
    assert not modified, "DOS files should not be modified"

    # Scenario 2: Unix file with LF line endings
    unix_file = '10 PRINT "TEST"\n20 END\n'
    result, modified = sanitize_and_clear_parity(unix_file)
    assert result == unix_file, "Should preserve LF"
    assert not modified, "Unix files should not be modified"

    # Scenario 3: File with trailing whitespace
    whitespace_file = '10 PRINT "TEST"  \n20 END\t\n'
    result, modified = sanitize_and_clear_parity(whitespace_file)
    assert result == whitespace_file, "Should preserve whitespace"
    assert not modified, "Whitespace should not trigger modification"

    # Scenario 4: Old file with parity bits (simulated serial transfer)
    serial_file = chr(177) + chr(176) + chr(160) + chr(208) + chr(210) + chr(201) + chr(206) + chr(212)  # "10 PRINT" with parity
    result, modified = sanitize_and_clear_parity(serial_file)
    assert modified, "Serial file should be modified"
    # Just check it doesn't crash and produces ASCII

    print("✓ File content scenario tests passed")


def run_all_tests():
    """Run all test suites."""
    print("=" * 60)
    print("INPUT SANITIZATION TEST SUITE")
    print("=" * 60)

    try:
        test_is_valid_input_char()
        test_sanitize_input()
        test_clear_parity()
        test_clear_parity_all()
        test_sanitize_and_clear_parity()
        test_basic_program_sanitization()
        test_file_content_scenarios()

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
        return 0

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
