"""
MBASIC Error Codes and Messages

Based on Appendix F of the MBASIC-80 Reference Manual.
Each error has a numeric code, a two-letter code, and a message.

Note: Some two-letter codes are duplicated across different numeric error codes.
This matches the original MBASIC 5.21 specification where the two-letter codes
alone are ambiguous - the numeric code is authoritative.

Specific duplicates (from MBASIC 5.21 specification):
- DD: code 10 ("Duplicate definition") and code 68 ("Device unavailable")
- DF: code 25 ("Device fault") and code 61 ("Disk full")
- CN: code 17 ("Can't continue") and code 69 ("Communication buffer overflow")

All error handling in this implementation uses numeric codes for lookups, so the
duplicate two-letter codes do not cause ambiguity in practice.
"""

# Error code mapping: number -> (two_letter_code, message)
ERROR_CODES = {
    1: ("NF", "NEXT without FOR"),
    2: ("SN", "Syntax error"),
    3: ("RG", "RETURN without GOSUB"),
    4: ("OD", "Out of DATA"),
    5: ("FC", "Illegal function call"),
    6: ("OV", "Overflow"),
    7: ("OM", "Out of memory"),
    8: ("UL", "Undefined line number"),
    9: ("BS", "Subscript out of range"),
    10: ("DD", "Duplicate definition"),
    11: ("/0", "Division by zero"),
    12: ("ID", "Illegal direct"),
    13: ("TM", "Type mismatch"),
    14: ("OS", "Out of string space"),
    15: ("LS", "String too long"),
    16: ("ST", "String formula too complex"),
    17: ("CN", "Can't continue"),
    18: ("UF", "Undefined user function"),
    19: ("NR", "No RESUME"),
    20: ("RE", "RESUME without error"),
    # 21-23 reserved
    24: ("DT", "Device timeout"),
    25: ("DF", "Device fault"),
    26: ("FO", "FOR without NEXT"),
    # 27-49 reserved
    50: ("FE", "FIELD overflow"),
    51: ("IE", "Internal error"),
    52: ("BN", "Bad file number"),
    53: ("FF", "File not found"),
    54: ("BM", "Bad file mode"),
    55: ("AO", "File already open"),
    # 56 reserved
    57: ("IO", "Disk I/O error"),
    58: ("FA", "File already exists"),
    # 59-60 reserved
    61: ("DF", "Disk full"),
    62: ("IP", "Input past end"),
    63: ("RN", "Bad record number"),
    64: ("FN", "Bad file name"),
    # 65 reserved
    66: ("DW", "Direct statement in file"),
    67: ("TF", "Too many files"),
    68: ("DD", "Device unavailable"),
    69: ("CN", "Communication buffer overflow"),
    70: ("DP", "Disk write protect"),
    71: ("DN", "Disk not ready"),
    72: ("DR", "Disk media error"),
    # 73-74 reserved
    75: ("PN", "Path/File access error"),
    76: ("PF", "Path not found"),
}


def get_error_message(error_code):
    """Get the full error message for an error code.

    Args:
        error_code: Integer error code

    Returns:
        String in format "?XX Error in line_number" where XX is the two-letter code
        Returns None if error code is not recognized
    """
    if error_code in ERROR_CODES:
        two_letter, message = ERROR_CODES[error_code]
        return two_letter, message
    return None, f"Error {error_code}"


def format_error(error_code, line_number=None):
    """Format an error message in MBASIC style.

    Args:
        error_code: Integer error code
        line_number: Optional line number where error occurred

    Returns:
        Formatted error string like "?SN Error in 100" or "?SN Error"
    """
    two_letter, message = get_error_message(error_code)
    if line_number is not None:
        return f"?{two_letter} Error in {line_number}"
    else:
        return f"?{two_letter} Error"
