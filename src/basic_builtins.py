"""
Built-in functions for Microsoft BASIC-80 (from BASIC-80 Reference Manual Version 5.21).

BASIC built-in functions (SIN, CHR$, INT, etc.) and formatting utilities (TAB, SPC, USING).

Note: This implementation follows BASIC-80 Reference Manual Version 5.21, which documents
Microsoft BASIC-80 as implemented for CP/M systems. This version was chosen as the
reference implementation for maximum compatibility with classic BASIC programs.
"""

import math
import random

from src.number_format import SINGLE_DIGITS, to_integer, to_single

# tty, termios, os, sys and win_console used to be imported here for INKEY$ and
# INPUT$.
# Both now read through the I/O handler, so the terminal details - and the
# POSIX-only imports that once made this module unimportable on Windows - live
# in src/iohandler/console.py.


# Special marker classes for TAB and SPC functions
class TabMarker:
    """Marker object returned by TAB() function"""
    def __init__(self, column):
        self.column = column

    def __str__(self):
        return f"<TAB({self.column})>"


class SpcMarker:
    """Marker object returned by SPC() function"""
    def __init__(self, count):
        self.count = count

    def __str__(self):
        return f"<SPC({self.count})>"


class UsingFormatter:
    """Format strings and numbers according to PRINT USING format strings"""

    def __init__(self, format_string):
        """Parse format string and extract format fields"""
        self.format_string = format_string
        self.fields = []  # List of (type, spec) tuples
        self.parse_format()

    def parse_format(self):
        """Parse format string into field specifications"""
        i = 0
        while i < len(self.format_string):
            ch = self.format_string[i]

            # Check for escape character
            if ch == '_' and i + 1 < len(self.format_string):
                # Literal character follows
                self.fields.append(('literal', self.format_string[i + 1]))
                i += 2
                continue

            # Check for string field markers
            if ch == '!':
                # Print first character only
                self.fields.append(('string', {'type': 'first'}))
                i += 1
                continue

            if ch == '&':
                # Variable length string
                self.fields.append(('string', {'type': 'full'}))
                i += 1
                continue

            if ch == '\\':
                # Fixed width string field: \ \
                # Count spaces between backslashes
                j = i + 1
                space_count = 0
                while j < len(self.format_string) and self.format_string[j] == ' ':
                    space_count += 1
                    j += 1
                if j < len(self.format_string) and self.format_string[j] == '\\':
                    # Valid \...\ field: width = 2 + space_count
                    width = 2 + space_count
                    self.fields.append(('string', {'type': 'fixed', 'width': width}))
                    i = j + 1
                    continue
                else:
                    # Not a valid field, treat as literal
                    self.fields.append(('literal', ch))
                    i += 1
                    continue

            # Check for numeric field markers
            if ch in '#.+-' or (ch == '*' and i + 1 < len(self.format_string) and
                               self.format_string[i + 1] in '*$'):
                # Start of numeric field
                num_spec = self.parse_numeric_field(i)
                self.fields.append(('numeric', num_spec))
                i = num_spec['end_pos']
                continue

            # Check for $$ at start of numeric field
            if ch == '$' and i + 1 < len(self.format_string) and self.format_string[i + 1] == '$':
                num_spec = self.parse_numeric_field(i)
                self.fields.append(('numeric', num_spec))
                i = num_spec['end_pos']
                continue

            # Literal character
            self.fields.append(('literal', ch))
            i += 1

    def parse_numeric_field(self, start_pos):
        """Parse a numeric field starting at start_pos

        Sign behavior:
        - leading_sign: + at start, reserves space for sign (displays + or - based on value)
        - trailing_sign: + at end, reserves space for sign (displays + or - based on value)
        - trailing_minus_only: - at end, reserves space for sign (displays - for negative or space for non-negative)
        """
        spec = {
            'start_pos': start_pos,
            'end_pos': start_pos,
            'digit_count': 0,
            'decimal_pos': -1,  # Position of decimal point (0-based from start)
            'digits_after_decimal': 0,
            'has_decimal': False,  # Whether format includes decimal point
            'leading_sign': False,  # + at start
            'trailing_sign': False,  # + or - at end
            'trailing_minus_only': False,
            'dollar_sign': False,  # $$
            'asterisk_fill': False,  # **
            'comma': False,  # Thousand separator
            'exponential': False,  # ^^^^
        }

        i = start_pos
        format_str = self.format_string

        # Check for leading **$
        if (i + 2 < len(format_str) and format_str[i:i+3] == '**$'):
            spec['asterisk_fill'] = True
            spec['dollar_sign'] = True
            spec['digit_count'] += 3  # Counts as 3 positions
            i += 3
        # Check for leading **
        elif (i + 1 < len(format_str) and format_str[i:i+2] == '**'):
            spec['asterisk_fill'] = True
            spec['digit_count'] += 2  # Counts as 2 positions
            i += 2
        # Check for leading $$
        elif (i + 1 < len(format_str) and format_str[i:i+2] == '$$'):
            spec['dollar_sign'] = True
            spec['digit_count'] += 2  # Counts as 2 positions
            i += 2
        # Check for leading +
        elif format_str[i] == '+':
            spec['leading_sign'] = True
            # Note: leading sign doesn't add to digit_count, it's a format modifier
            i += 1

        # Parse digit positions, decimal point, and comma
        decimal_found = False
        while i < len(format_str):
            ch = format_str[i]

            if ch == '#':
                spec['digit_count'] += 1
                if decimal_found:
                    spec['digits_after_decimal'] += 1
                i += 1
            elif ch == '.':
                if not decimal_found:
                    spec['decimal_pos'] = i - start_pos
                    spec['has_decimal'] = True
                    decimal_found = True
                    i += 1
                else:
                    # Second decimal point, end of field
                    break
            elif ch == ',':
                spec['comma'] = True
                spec['digit_count'] += 1
                i += 1
            else:
                break

        # Check for exponential format ^^^^
        if (i + 3 < len(format_str) and
            format_str[i:i+4] in ['^' * 4, '^^^^']):
            spec['exponential'] = True
            i += 4

        # Check for trailing sign
        if i < len(format_str):
            if format_str[i] == '+':
                spec['trailing_sign'] = True
                i += 1
            elif format_str[i] == '-':
                spec['trailing_minus_only'] = True
                i += 1

        spec['end_pos'] = i
        return spec

    def format_values(self, values):
        """Format a list of values using the parsed format fields

        Returns formatted string
        """
        result = []
        value_idx = 0

        for field_type, field_spec in self.fields:
            if field_type == 'literal':
                result.append(field_spec)
            elif field_type == 'string':
                if value_idx < len(values):
                    value = str(values[value_idx])
                    result.append(self.format_string_field(value, field_spec))
                    value_idx += 1
                else:
                    # No more values, field remains empty
                    pass
            elif field_type == 'numeric':
                if value_idx < len(values):
                    value = values[value_idx]
                    # Convert to number if needed
                    if isinstance(value, str):
                        try:
                            value = float(value)
                        except ValueError:
                            value = 0
                    result.append(self.format_numeric_field(value, field_spec))
                    value_idx += 1
                else:
                    # No more values
                    pass

        return ''.join(result)

    def format_string_field(self, value, spec):
        """Format a string according to string field specification"""
        if spec['type'] == 'first':
            # ! - first character only
            return value[0] if value else ' '
        elif spec['type'] == 'full':
            # & - full string
            return value
        elif spec['type'] == 'fixed':
            # \ \ - fixed width
            width = spec['width']
            if len(value) >= width:
                return value[:width]
            else:
                # Left-justify and pad with spaces
                return value.ljust(width)
        return value

    def format_numeric_field(self, value, spec):
        """Format a number according to numeric field specification"""
        # Handle exponential format
        if spec['exponential']:
            return self.format_exponential(value, spec)

        # Determine precision
        if spec['decimal_pos'] >= 0:
            precision = spec['digits_after_decimal']
        else:
            precision = 0

        # Determine sign BEFORE rounding (for negative zero handling)
        original_negative = value < 0

        # Round to precision
        if precision > 0:
            rounded = round(value, precision)
        else:
            rounded = round(value)

        # Determine sign - preserve negative sign for values that round to zero.
        # This matches MBASIC 5.21 behavior: -0.001 rounds to 0 but displays as "-0".
        # We use original_negative (captured before rounding) to detect this case,
        # ensuring: negative values that round to zero display "-0", positive display "0".
        if rounded == 0 and original_negative:
            is_negative = True
        else:
            # For non-zero values, use the rounded value's sign (normal case)
            is_negative = rounded < 0
        abs_value = abs(rounded)

        # Format number string
        if precision > 0:
            num_str = f"{abs_value:.{precision}f}"
            # Special case: if format has no digits before decimal (like .##),
            # and value < 1, omit the leading zero
            if spec['decimal_pos'] == 0 and abs_value < 1:
                # Remove leading "0" from "0.xx"
                if num_str.startswith('0.'):
                    num_str = num_str[1:]  # Keep just ".xx"
        else:
            num_str = f"{int(abs_value)}"

        # Add thousand separators if requested
        if spec['comma'] and '.' in num_str:
            int_part, dec_part = num_str.split('.')
            int_part = self.add_thousand_separators(int_part)
            num_str = int_part + '.' + dec_part
        elif spec['comma']:
            num_str = self.add_thousand_separators(num_str)

        # Calculate total field width (includes decimal point if present)
        field_width = spec['digit_count']
        if spec['has_decimal']:
            field_width += 1  # Decimal point takes up space

        # Add space for sign if needed
        if spec['leading_sign'] or spec['trailing_sign'] or spec['trailing_minus_only']:
            field_width += 1  # Sign takes up one position

        # Available width for the number itself (excluding sign/space)
        available_width = field_width
        if spec['leading_sign'] or spec['trailing_sign'] or spec['trailing_minus_only']:
            available_width -= 1  # Reserve space for sign (or space for trailing_minus_only)

        # Adjust for dollar sign
        if spec['dollar_sign']:
            available_width -= 1  # Reserve space for $

        # Check for overflow
        if len(num_str) > available_width:
            # Number too large - prepend % and return as-is, sign included:
            # the real binary prints %-123.46, not %123.46.
            if is_negative:
                return '%-' + num_str
            return '%' + num_str

        # Build output with padding
        sign_char = ''
        if spec['leading_sign']:
            sign_char = '-' if is_negative else '+'
        elif spec['trailing_sign']:
            sign_char = ''  # Will be added at end
        elif spec['trailing_minus_only'] and is_negative:
            sign_char = ''  # Will be added at end
        elif is_negative and not spec['trailing_minus_only']:
            sign_char = '-'

        # Calculate padding
        content_width = len(num_str)
        if spec['dollar_sign']:
            content_width += 1
        # Add sign to content width
        # Note: trailing_minus_only adds - for negative OR space for non-negative (always reserves 1 char)
        if spec['leading_sign'] or spec['trailing_sign'] or spec['trailing_minus_only']:
            content_width += 1
        elif sign_char:
            # A plain field takes a character for the minus too, or the field
            # comes out one wider than it was asked for.
            content_width += 1

        padding_needed = field_width - content_width

        # Build result
        result_parts = []

        # For leading sign: padding comes first (spaces only), then sign immediately before number
        # Note: Leading sign format uses spaces for padding, never asterisks (even if ** specified)
        if spec['leading_sign']:
            result_parts.append(' ' * max(0, padding_needed))
            result_parts.append('-' if is_negative else '+')
        else:
            # No leading sign: add padding/asterisk fill first
            if spec['asterisk_fill']:
                result_parts.append('*' * max(0, padding_needed))
            else:
                result_parts.append(' ' * max(0, padding_needed))

        # Minus for a plain field, before the $ - the real binary prints
        # -$12.50 for USING "$$###.##" with -12.5, and **-12.50 for "**###.##"
        # (the sign goes after asterisk fill but before the digits).
        if sign_char:
            result_parts.append(sign_char)

        # Dollar sign (immediately before number)
        if spec['dollar_sign']:
            result_parts.append('$')

        # Number
        result_parts.append(num_str)

        # Trailing sign
        if spec['trailing_sign']:
            result_parts.append('-' if is_negative else '+')
        elif spec['trailing_minus_only']:
            # Add '-' for negative, ' ' for positive
            result_parts.append('-' if is_negative else ' ')

        return ''.join(result_parts)

    def format_exponential(self, value, spec):
        """Format number in exponential notation"""
        # Determine precision
        precision = spec['digits_after_decimal'] if spec['digits_after_decimal'] > 0 else 2

        # Format in exponential notation
        if value == 0:
            exp_str = f"0.{'0' * precision}E+00"
        else:
            # Python's format gives us e+00 or e-00, we need E+00 or E-00
            exp_str = f"{value:.{precision}e}"
            exp_str = exp_str.upper()

            # Adjust exponent format to always have sign and 2 digits
            parts = exp_str.split('E')
            mantissa = parts[0]
            exponent = int(parts[1])
            exp_str = f"{mantissa}E{exponent:+03d}"

        # Handle signs
        if spec['leading_sign']:
            if not exp_str.startswith('-'):
                exp_str = '+' + exp_str
        elif spec['trailing_sign']:
            if exp_str.startswith('-'):
                exp_str = exp_str[1:] + '-'
            else:
                exp_str = exp_str + '+'
        elif spec['trailing_minus_only']:
            if exp_str.startswith('-'):
                exp_str = exp_str[1:] + '-'
            else:
                exp_str = ' ' + exp_str
        elif not exp_str.startswith('-'):
            # Add leading space for positive numbers
            exp_str = ' ' + exp_str

        return exp_str

    def add_thousand_separators(self, num_str):
        """Add thousand separators to integer part"""
        if len(num_str) <= 3:
            return num_str

        result = []
        for i, digit in enumerate(reversed(num_str)):
            if i > 0 and i % 3 == 0:
                result.append(',')
            result.append(digit)

        return ''.join(reversed(result))


class BuiltinFunctions:
    """MBASIC 5.21 built-in functions"""

    def __init__(self, runtime, io_provider=None):
        """
        Args:
            runtime: the Runtime whose files and state these functions act on.
            io_provider: zero-argument callable returning the I/O handler to
                read the keyboard through (INKEY$, INPUT$). A callable rather
                than the handler itself because the curses UI replaces
                interpreter.io after construction. Defaults to a console
                handler when absent, which is what direct construction in
                tests gets.
        """
        self.runtime = runtime
        self.io_provider = io_provider

    # ========================================================================
    # Numeric Functions
    # ========================================================================

    def ABS(self, x):
        """Absolute value"""
        return abs(x)

    def ATN(self, x):
        """Arctangent (result in radians)"""
        return math.atan(x)

    def COS(self, x):
        """Cosine (x in radians)"""
        return math.cos(x)

    def EXP(self, x):
        """Exponential (e^x)"""
        return math.exp(x)

    def FIX(self, x):
        """Truncate to integer (towards zero)"""
        return int(x)

    def INT(self, x):
        """Floor (largest integer <= x)"""
        return math.floor(x)

    def LOG(self, x):
        """Natural logarithm"""
        if x <= 0:
            raise ValueError("Illegal function call: LOG of non-positive number")
        return math.log(x)

    def SGN(self, x):
        """Sign: -1 if x<0, 0 if x=0, 1 if x>0"""
        if x < 0:
            return -1
        elif x > 0:
            return 1
        else:
            return 0

    def SIN(self, x):
        """Sine (x in radians)"""
        return math.sin(x)

    def SQR(self, x):
        """Square root"""
        if x < 0:
            raise ValueError("Illegal function call: SQR of negative number")
        return math.sqrt(x)

    def TAN(self, x):
        """Tangent (x in radians)"""
        return math.tan(x)

    def RND(self, x=None):
        """
        Random number, from MBASIC 5.21's own generator.

        - RND, RND(x>0): the next value in the sequence
        - RND(0):        the last value again, without drawing
        - RND(x<0):      restart from a value derived from x

        The sequence is the real machine's, value for value - see
        src/mbasic_rnd.py. RND(0) draws nothing, so there is nothing for a
        retried statement to put back.
        """
        if x is not None and x == 0:
            return self.runtime.rnd.next(0)
        self._note_random()
        return self.runtime.rnd.next(x)

    def _note_random(self):
        """Let a statement that may be retried put the generator back.

        A statement that pauses for a key runs again, and drawing again would
        skip the sequence forward - see src/statement_attempt.py. No attempt
        in progress (every statement on a terminal) means nothing to record.
        """
        attempt = getattr(self.runtime, 'statement_attempt', None)
        if attempt is not None:
            attempt.note_random(self.runtime)

    # ========================================================================
    # Type Conversion Functions
    # ========================================================================

    def CINT(self, x):
        """Convert to integer: nearest, with halves away from zero.

        Python's round() is banker's rounding, which sends 2.5 to 2. The real
        binary says CINT(2.5) is 3 and CINT(-2.5) is -3.
        """
        return to_integer(float(x))

    def CSNG(self, x):
        """Convert to single precision, losing what a single cannot hold."""
        return to_single(float(x))

    def CDBL(self, x):
        """Convert to double precision"""
        return float(x)

    # ========================================================================
    # Binary Conversion Functions
    # ========================================================================

    def CVI(self, s):
        """Convert 2-byte string to integer (little-endian)

        Used for reading binary integer data from random files.
        The string must be exactly 2 bytes long.
        """
        if not isinstance(s, str):
            s = str(s)
        if len(s) != 2:
            raise ValueError(f"Illegal function call: CVI requires 2-byte string, got {len(s)} bytes")

        # Convert string to bytes and unpack as signed 16-bit integer (little-endian)
        import struct
        byte_data = s.encode('latin-1')
        return struct.unpack('<h', byte_data)[0]

    def CVS(self, s):
        """Convert 4-byte string to single-precision float (little-endian)

        Used for reading binary single-precision data from random files.
        The string must be exactly 4 bytes long.
        """
        if not isinstance(s, str):
            s = str(s)
        if len(s) != 4:
            raise ValueError(f"Illegal function call: CVS requires 4-byte string, got {len(s)} bytes")

        # Convert string to bytes and unpack as single-precision float (little-endian)
        import struct
        byte_data = s.encode('latin-1')
        return struct.unpack('<f', byte_data)[0]

    def CVD(self, s):
        """Convert 8-byte string to double-precision float (little-endian)

        Used for reading binary double-precision data from random files.
        The string must be exactly 8 bytes long.
        """
        if not isinstance(s, str):
            s = str(s)
        if len(s) != 8:
            raise ValueError(f"Illegal function call: CVD requires 8-byte string, got {len(s)} bytes")

        # Convert string to bytes and unpack as double-precision float (little-endian)
        import struct
        byte_data = s.encode('latin-1')
        return struct.unpack('<d', byte_data)[0]

    def MKI(self, x):
        """Convert integer to 2-byte string (little-endian)

        Used for writing binary integer data to random files.
        Returns a 2-byte string representation.
        """
        import struct
        # Convert to integer and pack as signed 16-bit (little-endian)
        value = int(x)
        # Clamp to 16-bit signed range
        if value < -32768:
            value = -32768
        elif value > 32767:
            value = 32767
        byte_data = struct.pack('<h', value)
        return byte_data.decode('latin-1')

    def MKS(self, x):
        """Convert single-precision float to 4-byte string (little-endian)

        Used for writing binary single-precision data to random files.
        Returns a 4-byte string representation.
        """
        import struct
        # Convert to float and pack as single-precision (little-endian)
        value = float(x)
        byte_data = struct.pack('<f', value)
        return byte_data.decode('latin-1')

    def MKD(self, x):
        """Convert double-precision float to 8-byte string (little-endian)

        Used for writing binary double-precision data to random files.
        Returns an 8-byte string representation.
        """
        import struct
        # Convert to float and pack as double-precision (little-endian)
        value = float(x)
        byte_data = struct.pack('<d', value)
        return byte_data.decode('latin-1')

    # ========================================================================
    # String Functions
    # ========================================================================

    def ASC(self, s):
        """ASCII code of first character"""
        if not s:
            raise ValueError("Illegal function call: ASC of empty string")
        return ord(s[0])

    def CHR(self, x):
        """CHR$ - Character from ASCII code. CHR$(65.7) is "B" - see to_integer."""
        code = to_integer(x)
        if code < 0 or code > 255:
            raise ValueError("Illegal function call: CHR code out of range")
        return chr(code)

    def HEX(self, x):
        """Hexadecimal string representation"""
        return hex(int(x))[2:].upper()  # Remove '0x' prefix

    def INSTR(self, *args):
        """
        Find substring.

        INSTR(string1, string2) - find string2 in string1 from position 1
        INSTR(start, string1, string2) - find string2 in string1 from position start

        Returns position (1-based) or 0 if not found
        """
        if len(args) == 2:
            start = 1
            haystack, needle = args
        elif len(args) == 3:
            start, haystack, needle = args
            start = to_integer(start)
        else:
            raise ValueError("INSTR requires 2 or 3 arguments")

        # Convert to 0-based index
        start_idx = start - 1
        if start_idx < 0:
            start_idx = 0

        # Find substring
        pos = haystack.find(needle, start_idx)

        # Return 1-based position or 0
        return pos + 1 if pos >= 0 else 0

    def LEFT(self, s, n):
        """Left n characters of string. A fractional n rounds: 2.7 gives 3."""
        n = to_integer(n)
        return s[:n]

    def LEN(self, s):
        """Length of string"""
        return len(s)

    def MID(self, *args):
        """
        Middle substring.

        MID$(string, start) - from start to end
        MID$(string, start, length) - length characters from start

        Start is 1-based
        """
        if len(args) == 2:
            s, start = args
            start = to_integer(start)
            return s[start-1:] if start > 0 else s
        elif len(args) == 3:
            s, start, length = args
            start = to_integer(start)
            length = to_integer(length)
            if start < 1:
                start = 1
            return s[start-1:start-1+length]
        else:
            raise ValueError("MID$ requires 2 or 3 arguments")

    def OCT(self, x):
        """Octal string representation"""
        return oct(int(x))[2:]  # Remove '0o' prefix

    def RIGHT(self, s, n):
        """Right n characters of string. A fractional n rounds."""
        n = to_integer(n)
        return s[-n:] if n > 0 else ""

    def SPACE(self, n):
        """String of n spaces. A fractional n rounds: SPACE$(2.7) is 3 spaces."""
        n = to_integer(n)
        return " " * n

    def STR(self, x):
        """
        Convert number to string.

        The same characters PRINT would show, which means MBASIC's number
        formatting rather than Python's: STR$(-2) is "-2", not "-2.0", and
        STR$(1/3) is " .333333". A leading space for positives, and - unlike
        PRINT - no trailing one. See src/number_format.py.

        The caller's precision is not known here, so single is assumed: STR$
        has no expression to inspect, and single is the default type.
        """
        from src.number_format import format_number
        text = format_number(x, SINGLE_DIGITS)
        return " " + text if x >= 0 else text

    def STRING(self, n, char):
        """
        Repeat character n times.

        STRING$(n, code) - repeat CHR$(code) n times
        STRING$(n, string) - repeat first char of string n times

        Both arguments round: STRING$(3, 65.7) is "BBB".
        """
        n = to_integer(n)
        if isinstance(char, str):
            # String argument - use first character
            c = char[0] if char else " "
        else:
            # Numeric argument - convert to character
            c = chr(to_integer(char))
        return c * n

    def VAL(self, s):
        """
        Convert string to number.

        Stops at first non-numeric character
        """
        s = s.strip()
        if not s:
            return 0

        # Parse number (stop at first invalid character)
        result = ""
        for char in s:
            if char in "0123456789.-+eE":
                result += char
            else:
                break

        if not result or result in ['+', '-', '.']:
            return 0

        try:
            return float(result)
        except ValueError:
            return 0

    # ========================================================================
    # System Functions
    # ========================================================================

    def PEEK(self, _addr):
        """
        A random byte, 0-255. This is a decision, not a stub.

        There is no memory model in this interpreter - a variable is a Python
        object, not bytes at an address - so there is nothing for PEEK to read.
        What programs actually use PEEK for is seeding a random number
        generator from whatever happens to be in memory, and a random byte is
        the answer that makes that work. Returning a fixed 0 would be
        deterministic and would defeat the only line that asks for it.

        Do not "fix" this to return 0 or to emulate a 64K space without reading
        docs/dev/NO_MEMORY_MODEL.md first, which records why. Byte-level
        fidelity belongs in an 8080 emulator running the real com/mbasic.com,
        not here.
        """
        import random
        return random.randint(0, 255)

    def INP(self, port):
        """
        Input from port (not implemented in interpreter).

        Returns 0 as safe default.
        """
        # Can't actually read from hardware ports
        return 0

    def POS(self, _dummy):
        """
        Current print position.

        Returns approximate column (not fully implemented)
        """
        # Would need to track actual print position
        # For now, return 1
        return 1

    def TAB(self, n):
        """
        TAB(n) - Tab to column n in PRINT statement.

        Returns a marker object that PRINT interprets as "move to column n".
        Column numbering is 1-based (column 1 is leftmost).
        """
        return TabMarker(to_integer(n))     # TAB(4.7) is column 5

    def SPC(self, n):
        """
        SPC(n) - Print n spaces in PRINT statement.

        Returns a marker object that PRINT interprets as "print n spaces".
        """
        return SpcMarker(to_integer(n))     # SPC(3.7) is four spaces

    def EOF(self, file_num):
        """
        Test for end of file.

        Returns -1 if at EOF, 0 otherwise

        Note: For input files (OPEN statement mode 'I'), respects ^Z (ASCII 26)
        as EOF marker (CP/M style). Input files are opened in Python binary mode ('rb')
        to enable ^Z detection.

        Implementation details:
        - execute_open() in interpreter.py stores mode ('I', 'O', 'A', 'R') in file_info['mode']
        - Mode 'I' (input): Opened in Python binary mode ('rb'), allowing ^Z detection
        - Modes 'O' (output), 'A' (append): Use standard Python EOF detection without ^Z
        - See execute_open() in interpreter.py for file opening implementation (search for "execute_open")
        """
        file_num = int(file_num)
        if file_num not in self.runtime.files:
            raise ValueError(f"File #{file_num} not open")

        file_info = self.runtime.files[file_num]

        # Check EOF flag (set by input operations or ^Z detection)
        if file_info['eof']:
            return -1

        # For mode 'I' files (binary input), check for EOF or ^Z
        # Mode 'I' files are opened in binary mode ('rb' - see execute_open() in interpreter.py)
        # which allows ^Z checking for CP/M-style EOF detection
        if file_info['mode'] == 'I':
            file_handle = file_info['handle']
            current_pos = file_handle.tell()

            # Peek at next byte to check for ^Z or EOF
            # Binary mode files ('rb'): read(1) returns bytes object
            # next_byte[0] accesses the first byte value as integer (0-255)
            next_byte = file_handle.read(1)
            if not next_byte:
                # Physical EOF
                file_info['eof'] = True
                return -1
            elif next_byte[0] == 26:  # ^Z (ASCII 26)
                # CP/M EOF marker - only checked in binary input mode
                file_info['eof'] = True
                file_handle.seek(current_pos)  # Restore position
                return -1
            else:
                # Not at EOF, restore position
                file_handle.seek(current_pos)
                return 0

        # For output/append files, never at EOF
        return 0

    def LOC(self, file_num):
        """
        Return current record position for random access file.

        Returns the record number of the last GET or PUT operation.
        For sequential files, returns approximate byte position / 128.
        """
        file_num = int(file_num)
        if file_num not in self.runtime.files:
            raise ValueError(f"File #{file_num} not open")

        # For random access files, return current record number
        if file_num in self.runtime.field_buffers:
            return self.runtime.field_buffers[file_num]['current_record']

        # For sequential files, return approximate block number (byte position / 128)
        file_info = self.runtime.files[file_num]
        file_handle = file_info['handle']
        pos = file_handle.tell()
        return pos // 128

    def LOF(self, file_num):
        """
        Return length of file in bytes.

        Returns the total size of the file.
        """
        file_num = int(file_num)
        if file_num not in self.runtime.files:
            raise ValueError(f"File #{file_num} not open")

        file_info = self.runtime.files[file_num]
        file_handle = file_info['handle']

        # Save current position
        current_pos = file_handle.tell()

        # Seek to end to get size
        file_handle.seek(0, 2)
        size = file_handle.tell()

        # Restore position
        file_handle.seek(current_pos)

        return size

    def USR(self, x):
        """
        Call user machine language routine (not implemented).

        Returns 0 as safe default.
        """
        # Can't call machine code from Python
        return 0

    # ========================================================================
    # Special Functions
    # ========================================================================

    def INKEY(self):
        """
        INKEY$ - Read keyboard without waiting (non-blocking input).
        (Method name is INKEY since Python doesn't allow $ in names)

        Returns a single character if a key is pressed, or empty string if not.

        Goes through the I/O handler, so the backend that owns the keyboard is
        the one asked for it. The terminal machinery this used to hold inline -
        isatty, select, raw mode, the Windows prefix+scan-code protocol - now
        lives in ConsoleIOHandler.input_char, which is where three separate
        comments always claimed it was.
        """
        return self._io().input_char(blocking=False)

    def INPUT(self, num, file_num=None):
        """
        INPUT$ - Read num characters from keyboard or file.
        (Method name is INPUT since Python doesn't allow $ in names)

        This method receives the file number WITHOUT the # prefix (parser strips it).

        BASIC syntax:
            INPUT$(n) - read n characters from keyboard
            INPUT$(n, #filenum) - read n characters from file

        Python call syntax (from interpreter - # prefix already stripped by parser):
            INPUT(n) - read n characters from keyboard
            INPUT(n, filenum) - read n characters from file

        Note: The file_num parameter (when provided) is a numeric value, not the original
        BASIC source syntax with # prefix. The parser removes the # during parsing.

        A keyboard read is raw: nothing is echoed, Enter is not required, and
        Ctrl+C breaks rather than being returned. See _read_console.
        """
        num = int(num)

        if file_num is None:
            # Read from keyboard
            return self._read_console(num)
        else:
            # Read from file
            file_num = int(file_num)
            if file_num not in self.runtime.files:
                raise ValueError(f"File #{file_num} not open")

            file_info = self.runtime.files[file_num]
            file_handle = file_info['handle']
            # Same reason as _note_random: a retried statement would read the
            # NEXT bytes rather than the ones the abandoned attempt saw.
            attempt = getattr(self.runtime, 'statement_attempt', None)
            if attempt is not None:
                attempt.note_file_position(file_num, file_handle)

            data = file_handle.read(num)
            if isinstance(data, bytes):
                # Mode 'I' files are opened 'rb' so EOF can spot a ^Z, so the
                # read comes back as bytes and the string it produced was a
                # Python repr: PRINT showed b'ABC', and the help page's own
                # example - PRINT HEX$(ASC(INPUT$(1,#1))) - read the 'b' and
                # answered 98 instead of 65. latin-1 keeps it byte-transparent,
                # the same as the keyboard path.
                data = data.decode('latin-1')
            return data

    # ------------------------------------------------------------------
    # INPUT$ keyboard reading
    #
    # MBASIC 5.21 reads these characters raw: nothing is echoed, no Enter is
    # required, and every control character reaches the program except
    # Ctrl+C, which interrupts the read. How that is done on a given terminal
    # is the I/O handler's business; what it MEANS is decided here.
    # ------------------------------------------------------------------

    #: Ctrl+C, as the I/O handler hands it back. The console handler only sees
    #: it at all because raw mode clears ISIG; in cooked mode the line
    #: discipline turns it into a SIGINT instead - which is what
    #: _take_break_request picks up.
    _BREAK_CHAR = '\x03'

    def _read_console(self, num):
        """Read num characters from the keyboard for INPUT$(n)."""
        if num <= 0:
            return ""

        # Consumed by _interrupted() below, and read after the handler
        # returns: the handler reports "I stopped", not why.
        self._break_seen = False
        chars = self._io_read(num)
        if self._break_seen or self._BREAK_CHAR in chars:
            self._raise_break()
        return chars

    def _io_read(self, num):
        """Ask the I/O handler for num characters, however it can manage it."""
        handler = self._io()

        def interrupted():
            if self._take_break_request():
                self._break_seen = True
                return True
            return False

        reader = getattr(handler, 'input_chars', None)
        if reader is not None:
            return reader(num, interrupted=interrupted)

        # A handler predating input_chars, or one that is not an IOHandler
        # subclass at all - CapturingIOHandler is a plain class. One call per
        # character is what the base class does anyway; it is only the console
        # that needs to hold the terminal across the whole read.
        chars = ""
        for _ in range(num):
            if interrupted():
                break
            char = handler.input_char(blocking=True)
            if not char:
                break
            chars += char
            if char == self._BREAK_CHAR:
                break
        return chars

    def _io(self):
        """The I/O handler to read the keyboard through.

        Resolved per call, not cached: the curses UI swaps out
        interpreter.io after construction (src/ui/curses_ui.py), and a reader
        holding the handler it was built with would keep reading the wrong one.

        Falling back to a console handler covers BuiltinFunctions built
        directly, which the tests do with __new__ and no runtime at all.
        """
        provider = getattr(self, 'io_provider', None)
        handler = provider() if provider is not None else None
        if handler is not None:
            return handler
        handler = getattr(self, '_fallback_io', None)
        if handler is None:
            from src.iohandler.console import ConsoleIOHandler
            handler = ConsoleIOHandler()
            self._fallback_io = handler
        return handler

    def _take_break_request(self):
        """Consume the flag the SIGINT handler sets, if it is set.

        This is the Ctrl+C that arrived before the terminal was in raw mode -
        it became a SIGINT, and `_setup_break_handler` only sets a flag, so
        without noticing it here the read stays blocked and then swallows
        whatever key finally ends it.

        Cleared here rather than left for the tick loop's own check, or the
        break would fire a second time on the statement CONT resumes into.
        Written defensively because the tests build BuiltinFunctions with
        __new__ and no runtime.
        """
        runtime = getattr(self, 'runtime', None)
        if getattr(runtime, 'break_requested', False):
            runtime.break_requested = False
            return True
        return False

    @classmethod
    def _raise_break(cls):
        """Interrupt INPUT$ on Ctrl+C, the way MBASIC 5.21 does.

        The 5.21 manual: "all control characters are passed through except
        Control-C, which is used to interrupt the execution of the INPUT$
        function". Raw mode is what makes this ours to decide - it clears
        ISIG, so the byte is delivered to the reader instead of becoming a
        SIGINT, and without this a program sitting in INPUT$ could not be
        interrupted from the keyboard at all.

        Raised as soon as the byte arrives, not after the read completes:
        checking the finished string meant a Ctrl+C typed at INPUT$(3) did
        nothing until two more keys were typed, which is worse than the
        cooked read it replaced.

        Every console read, typed or piped, matching real 5.21 under cpmemu -
        which aborts on a piped 0x03 exactly as it does on a typed one. Only
        INPUT$(n,#f) is exempt, because a file is not the console.

        The break is resumable, as it is under real 5.21: CONT re-enters the
        INPUT$. One deliberate difference - 5.21 returns silently to "Ok" and
        this prints "Break in nn", matching what STOP and Ctrl+C during INPUT
        already print here.

        INKEY$ is deliberately left alone. It only enters raw mode once
        select() has already reported a key, so on POSIX the terminal is
        cooked while a program polls it and Ctrl+C usually becomes a SIGINT
        before INKEY$ can see the byte at all - measured: "Break in 10", not
        CHR$(3). It also never blocks, so it cannot trap the user the way a
        pending INPUT$ would.
        """
        # Imported here because src.interpreter imports this module: at module
        # scope this would be a circular import.
        from src.interpreter import BreakException
        raise BreakException()
