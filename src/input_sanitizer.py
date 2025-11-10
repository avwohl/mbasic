"""Input sanitization utilities for MBASIC editor.

This module provides functions to sanitize user input through a two-step process:
1. First: Clear parity bits from incoming characters (bit 7)
2. Then: Filter out unwanted control characters

These utilities help prevent issues with:
- Parity bits (bit 7) causing character mismatches
- Control characters corrupting editor content
- Invalid characters in BASIC programs

The main entry point, sanitize_and_clear_parity(), applies these operations
sequentially. Note: sanitize_input() does NOT validate that parity clearing occurred
before it's called - it simply filters out any characters with codes >= 128 (which
indirectly rejects characters that still have bit 7 set). For proper validation,
always use sanitize_and_clear_parity() which explicitly clears parity before filtering.

Implementation note: Uses standard Python type hints (e.g., tuple[str, bool])
which require Python 3.9+. For earlier Python versions, use Tuple[str, bool] from typing.
"""


def is_valid_input_char(char: str) -> bool:
    """Check if character is valid for editor input.

    Allows:
    - Printable ASCII (32-126): space through tilde
    - Newline (10): line breaks
    - Tab (9): indentation
    - Carriage return (13): Windows line endings

    Rejects:
    - Other control characters (0-31 except 9, 10, 13)
    - Extended ASCII (128-255)
    - Non-ASCII Unicode

    Args:
        char: Single character to check

    Returns:
        True if character is allowed, False otherwise

    Examples:
        >>> is_valid_input_char('A')
        True
        >>> is_valid_input_char('\\n')
        True
        >>> is_valid_input_char('\\x01')  # Control-A
        False
        >>> is_valid_input_char('\\x7F')  # DEL
        False
    """
    if len(char) != 1:
        return False

    code = ord(char)

    # Allow printable ASCII (32-126)
    if 32 <= code <= 126:
        return True

    # Allow newline (10), tab (9), carriage return (13)
    if code in (9, 10, 13):
        return True

    # Reject everything else (control chars, extended ASCII)
    return False


def sanitize_input(text: str) -> str:
    """Remove invalid characters from input text.

    Filters out:
    - Control characters (except tab, newline, CR)
    - Characters outside ASCII range 0-127

    Note: This function is typically called after clear_parity_all() in the
    sanitize_and_clear_parity() pipeline, where parity bits have already been
    cleared. It filters out characters outside the valid range (32-126, plus
    tab/newline/CR). This indirectly rejects any characters with bit 7 set
    (codes >= 128), but does NOT validate that parity clearing actually occurred.
    For guaranteed parity clearing, call clear_parity_all() explicitly or use
    sanitize_and_clear_parity() which combines both operations.

    Args:
        text: Input text to sanitize

    Returns:
        Sanitized text with only valid characters

    Examples:
        >>> sanitize_input('PRINT "Hello"')
        'PRINT "Hello"'
        >>> sanitize_input('PRINT\\x01"Hello"')
        'PRINT"Hello"'
        >>> sanitize_input('Line\\r\\nBreak')
        'Line\\r\\nBreak'
    """
    return ''.join(c for c in text if is_valid_input_char(c))


def clear_parity(char: str) -> str:
    """Clear parity bit (bit 7) from character.

    In serial communication, bit 7 is sometimes used for parity checking.
    This can cause 'A' (65) to become 'A'+128 (193), which breaks character
    comparison and display.

    This function clears bit 7 to ensure characters are in standard ASCII range (0-127).

    Args:
        char: Single character

    Returns:
        Character with parity bit cleared

    Examples:
        >>> clear_parity('A')
        'A'
        >>> clear_parity(chr(193))  # 'A' with bit 7 set
        'A'
        >>> ord(clear_parity(chr(193)))
        65
    """
    if len(char) != 1:
        return char

    # Clear bit 7 to remove parity
    code = ord(char) & 0x7F
    return chr(code)


def clear_parity_all(text: str) -> str:
    """Clear parity bits from all characters in text.

    Processes each character to ensure it's in standard ASCII range (0-127).

    Args:
        text: Input text

    Returns:
        Text with parity bits cleared

    Examples:
        >>> clear_parity_all('PRINT "Test"')
        'PRINT "Test"'
        >>> clear_parity_all(chr(193) + chr(194))  # Characters with bit 7 set
        'AB'
    """
    return ''.join(clear_parity(c) for c in text)


def sanitize_and_clear_parity(text: str) -> tuple[str, bool]:
    """Apply both parity clearing and input sanitization.

    This is the main function to use for all user input, combining:
    1. Parity bit clearing (bit 7)
    2. Control character filtering

    Args:
        text: Input text to process

    Returns:
        Tuple of (sanitized_text, was_modified)
        - sanitized_text: Cleaned text
        - was_modified: True if any characters were removed/changed

    Examples:
        >>> sanitize_and_clear_parity('PRINT "Test"')
        ('PRINT "Test"', False)
        >>> sanitize_and_clear_parity('PRINT\x01"Test"')
        ('PRINT"Test"', True)
    """
    # First clear parity bits
    cleared = clear_parity_all(text)

    # Then sanitize control characters
    sanitized = sanitize_input(cleared)

    # Check if anything changed
    was_modified = (sanitized != text)

    return sanitized, was_modified


if __name__ == '__main__':
    # Quick self-test
    import doctest
    doctest.testmod()

    # Manual tests
    print("Testing input sanitization:")

    # Test 1: Normal text
    text1 = 'PRINT "Hello World"'
    result1, modified1 = sanitize_and_clear_parity(text1)
    print(f"Test 1: '{text1}' -> '{result1}' (modified: {modified1})")
    assert result1 == text1
    assert not modified1

    # Test 2: Control characters
    text2 = 'PRINT\x01\x02"Hello"'
    result2, modified2 = sanitize_and_clear_parity(text2)
    print(f"Test 2: 'PRINT\\x01\\x02\"Hello\"' -> '{result2}' (modified: {modified2})")
    assert result2 == 'PRINT"Hello"'
    assert modified2

    # Test 3: Parity bits
    text3 = chr(193) + chr(194) + chr(195)  # 'A', 'B', 'C' with bit 7 set
    result3, modified3 = sanitize_and_clear_parity(text3)
    print(f"Test 3: chars(193,194,195) -> '{result3}' (modified: {modified3})")
    assert result3 == 'ABC'
    assert modified3

    # Test 4: Newlines and tabs preserved
    text4 = 'Line 1\nLine 2\tTabbed'
    result4, modified4 = sanitize_and_clear_parity(text4)
    print(f"Test 4: 'Line 1\\nLine 2\\tTabbed' -> '{result4}' (modified: {modified4})")
    assert result4 == text4
    assert not modified4

    print("\nAll tests passed!")
