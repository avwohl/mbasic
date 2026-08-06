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

These duplicates exist in the original MBASIC 5.21 specification likely due to error codes
being added at different times during development (communication and device errors came later).
All error handling in this implementation uses numeric codes for lookups, so the duplicate
two-letter codes do not cause ambiguity in practice.
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
    10: ("DD", "Duplicate Definition"),
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
    21: ("UE", "Unprintable error"),
    22: ("MO", "Missing operand"),
    23: ("LB", "Line buffer overflow"),
    24: ("DT", "Device timeout"),
    25: ("DF", "Device fault"),
    26: ("FO", "FOR Without NEXT"),
    # 27-28 reserved
    29: ("WH", "WHILE without WEND"),
    30: ("WE", "WEND without WHILE"),
    # 31-49 reserved
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


#: The codes the command handlers reach for by name. MBASIC prints these at
#: the Ok prompt with no "?" and no detail of its own - LOAD "NOSUCH.BAS" is
#: "File not found", not "?File not found: NOSUCH.BAS", and SAVE with no
#: filename is "Missing operand", not "?Syntax error". All measured.
SYNTAX_ERROR = 2
ILLEGAL_FUNCTION_CALL = 5
UNDEFINED_LINE_NUMBER = 8
CANT_CONTINUE = 17
MISSING_OPERAND = 22
FILE_NOT_FOUND = 53
BAD_FILE_NAME = 64


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
    return "UE", "Unprintable error"


def format_error(error_code, line_number=None):
    """Format an error message in MBASIC style.

    Args:
        error_code: Integer error code
        line_number: Optional line number where error occurred

    Returns:
        Formatted error string like "?SN Error in 100" or "?SN Error"

    Note:
        This is the two-letter form, which the CP/M build does NOT use. What
        the real binary prints is format_error_message() below - measured, not
        taken from the manual.
    """
    two_letter, message = get_error_message(error_code)
    if line_number is not None:
        return f"?{two_letter} Error in {line_number}"
    else:
        return f"?{two_letter} Error"


def format_error_message(error_code, line_number=None):
    """The line the real binary prints for an untrapped error.

    Measured byte for byte against com/mbasic.com under cpmemu:

        program mode    File not found in 50
        direct mode     File not found

    There is no leading "?", no two-letter code, no trailing period and no echo
    of the source line - all four of which we used to print, along with the
    Python exception class name. The " in <line>" is there only for an error in
    a program line; a statement typed at the Ok prompt gets the message alone.
    """
    _, message = get_error_message(error_code)
    if line_number is None:
        return message
    return f"{message} in {line_number}"


def message_for(exception, line_number=None):
    """The line MBASIC prints for this exception. One call, for the UIs.

    Every backend needs the same two steps - recover the error number from the
    Python exception, then look up the message - so they get one function
    rather than a two-line idiom each, spelled differently in six places.

        except Exception as error:
            self.output(message_for(error, self.runtime.pc.line_num))

    Pass line_number=None for a statement typed at the prompt, or when the
    surface already shows the line separately.
    """
    return format_error_message(error_code_for(exception), line_number)


#: Message fragments that identify an MBASIC error, most specific first. Our
#: code raises ordinary Python exceptions carrying Python wording, so the code
#: has to be recovered from what was said - and once it is, the *canonical*
#: text is what gets printed, which is why "Cannot open X: No such file or
#: directory" comes out as "File not found".
_MESSAGE_CODES = (
    ("next without for", 1),
    ("return without gosub", 3),
    ("out of data", 4),
    ("division by zero", 11),
    ("subscript out of range", 9),
    ("duplicate definition", 10),
    ("type mismatch", 13),
    ("string too long", 15),
    ("can't continue", 17),
    ("undefined function", 18),
    ("undefined user function", 18),
    ("no resume", 19),
    ("resume without error", 20),
    ("for without next", 26),
    ("while without wend", 29),
    # Ours says "WEND without matching WHILE at line 10".
    ("wend without", 30),
    ("field overflow", 50),
    ("bad file number", 52),
    ("file not found", 53),
    ("cannot open", 53),
    ("no such file", 53),
    ("bad file mode", 54),
    # "File #1 not open for input" is a mode error; "File #9 not open" - a
    # number that was never opened at all - is a bad file NUMBER, so the
    # longer fragment has to be tested first.
    ("not open for", 54),
    ("invalid open mode", 54),
    ("not open", 52),
    ("already open", 55),
    ("file already exists", 58),
    ("input past end", 62),
    ("bad record number", 63),
    ("bad file name", 64),
    ("too many files", 67),
    ("out of memory", 7),
    ("stack overflow", 7),
    ("undefined line", 8),
    ("overflow", 6),
    ("illegal function call", 5),
    ("syntax error", 2),
)

#: Exception types that identify an error on their own, when the wording did
#: not. Checked after the message, because a ValueError carrying "Type
#: mismatch" is a type mismatch, not an illegal function call.
_TYPE_CODES = (
    (ZeroDivisionError, 11),
    (OverflowError, 6),
    (IndexError, 9),
    (MemoryError, 7),
    (RecursionError, 7),
)


def error_code_for(exception):
    """The MBASIC error number for a Python exception we raised.

    Falls back to 5, "Illegal function call", which is what MBASIC uses for
    anything it cannot be more specific about.
    """
    explicit = getattr(exception, 'mbasic_code', None)
    if explicit is not None:
        return explicit
    text = str(exception).lower()
    if 'parse error' in text or 'unknown statement' in text:
        # A parse failure is a syntax error - except when what ran out was an
        # *operand*. Measured across this parser's whole message vocabulary,
        # the binary's split falls exactly on one of our messages:
        #
        #     PRINT 1 +      Unexpected token in expression: EOF  Missing operand
        #     SAVE           Unexpected token in expression: EOF  Missing operand
        #     PRINT EOF      Expected LPAREN, got EOF             Syntax error
        #     PRINT (1       Expected RPAREN, got EOF             Syntax error
        #     X = EOF(1      Expected , or ) in EOF function      Syntax error
        #     GOTO           Expected line number after GOTO      Syntax error
        #
        # Testing for "eof" anywhere in the text got the last four wrong: there
        # EOF is the token some *bracket* was wanted before, or the name of the
        # EOF function, not an operand that never arrived.
        return (MISSING_OPERAND
                if 'unexpected token in expression: eof' in text
                else SYNTAX_ERROR)
    for fragment, code in _MESSAGE_CODES:
        if fragment in text:
            return code
    for exception_type, code in _TYPE_CODES:
        if isinstance(exception, exception_type):
            return code
    if isinstance(exception, (TypeError, ValueError)):
        return 5
    return 5
