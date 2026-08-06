"""
Built-in functions for Microsoft BASIC-80 (from BASIC-80 Reference Manual Version 5.21).

BASIC built-in functions (SIN, CHR$, INT, etc.) and formatting utilities (TAB, SPC, USING).

Note: This implementation follows BASIC-80 Reference Manual Version 5.21, which documents
Microsoft BASIC-80 as implemented for CP/M systems. This version was chosen as the
reference implementation for maximum compatibility with classic BASIC programs.
"""

import math
import random
from decimal import Decimal, ROUND_HALF_UP

from src.number_format import (SINGLE_DIGITS, _round_to_digits, to_integer,
                               to_single)

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


def _mid_start(start):
    """MID$ counts from 1, and 0 is not a position.

    MID$("A", 0) is "Illegal function call" on the real binary; we returned
    the whole string. Anything past 255 is out of range too.
    """
    if start < 1 or start > 255:
        raise ValueError("Illegal function call")
    return start


def _is_negative(value):
    """Whether PRINT USING should show a minus sign.

    The sign is the value's, not the rounded result's: -0.001 in "#.##" is
    -0.00 on the real binary, and 0.001 is 0.00.

    IEEE's negative zero is not one of them. MBF has no such thing, so on the
    real binary 0 * (-1) is plain zero and prints as $0.00 in "$$#####.##" -
    treating it as negative put a minus in front of every zero total in
    basic/business/budget.bas, which reaches them as TD * (-1).
    """
    try:
        return value < 0
    except TypeError:
        return False


def _mbasic_decimal(value, digits):
    """The magnitude of `value` as MBASIC's conversion routine sees it.

    PRINT USING does not read the stored binary directly - it goes through the
    same routine PRINT does, which yields six significant figures for a single
    and sixteen for a double. That is why a single-precision 12345.67 prints as
    12,345.70 in "##,###.##": six digits make it 12345.7, and the field then
    pads the tenths place with a zero.
    """
    if isinstance(value, bool):
        value = int(value)
    if not isinstance(value, (int, float)):
        raise ValueError("not a number")
    if isinstance(value, float) and (value != value or value in (
            float('inf'), float('-inf'))):
        raise ValueError("not finite")

    magnitude = abs(value)
    if digits is None:
        # An INTEGER-typed value is exact - there is nothing to round away.
        return Decimal(int(magnitude))
    if magnitude == 0:
        return Decimal(0)
    return _round_to_digits(magnitude, digits)


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
            if (ch in '#.+-'
                    or (ch == '*' and i + 1 < len(self.format_string)
                        and self.format_string[i + 1] in '*$')
                    or (ch == '$' and i + 1 < len(self.format_string)
                        and self.format_string[i + 1] == '$')):
                num_spec = self.parse_numeric_field(i)
                if num_spec['digit_count']:
                    self.fields.append(('numeric', num_spec))
                    i = num_spec['end_pos']
                    continue
                # No digit positions, so it was never a field: a '.' with no
                # '#' after it, or a '+' or '-' with nothing to sign. MBASIC
                # prints the character and moves on - that is what PLSPRT is
                # for, flushing a '+' that turned out not to begin a field -
                # so "A.B" prints A.B, and "-#" of 5 prints -5.
                self.fields.append(('literal', ch))
                i += 1
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

        # Check for trailing sign. A field that already opened with '+' does
        # not get one - ENDNUS tests the leading-plus flag and jumps straight
        # past this scan - so the '+' or '-' after "+###" is an ordinary
        # character and "+###+" of 42 prints " +42+".
        if i < len(format_str) and not spec['leading_sign']:
            if format_str[i] == '+':
                spec['trailing_sign'] = True
                i += 1
            elif format_str[i] == '-':
                spec['trailing_minus_only'] = True
                i += 1

        spec['end_pos'] = i

        # The two counts PUFOUT actually works in - see format_numeric_field.
        #   lead  the character positions to the left of the point. Every #
        #         counts, and so does every comma, the two characters of $$ or
        #         ** (three for **$), and a leading + .
        #   trail zero if the field has no point, otherwise the point itself
        #         plus the digits after it.
        spec['lead'] = (spec['digit_count'] - spec['digits_after_decimal']
                        + (1 if spec['leading_sign'] else 0))
        spec['trail'] = spec['digits_after_decimal'] + 1 if spec['has_decimal'] else 0
        return spec

    def has_field(self):
        """Whether the format string has anywhere to put a value at all."""
        return any(kind != 'literal' for kind, _ in self.fields)

    def format_values(self, values, digits=None):
        """Format a list of values using the parsed format fields.

        The format string is used over and over until the value list runs out,
        which is the part that was missing: PRINT USING "###"; 1; 2; 3 prints
        "  1  2  3" on the real binary, not just "  1". Scanning stops the
        moment a field finds no value left - the literal text passed on the way
        has already been printed by then, which is why
        PRINT USING "### ###"; 10; 20; 30 ends with a trailing space.

        Args:
            values: the values from the PRINT USING list.
            digits: significant figures to convert each value through, one per
                value - SINGLE_DIGITS, DOUBLE_DIGITS or None for an INTEGER.
                MBASIC hands PRINT USING the same conversion routine PRINT
                uses, so a single-precision 12345.67 is six digits there too
                and prints as 12345.70. Defaults to single for every value.

        Returns formatted string
        """
        result = []
        value_idx = 0
        fields = self.fields

        while True:
            for field_type, field_spec in fields:
                if field_type == 'literal':
                    result.append(field_spec)
                    continue

                if value_idx >= len(values):
                    return ''.join(result)

                if field_type == 'string':
                    result.append(
                        self.format_string_field(str(values[value_idx]), field_spec))
                else:
                    value = values[value_idx]
                    # Convert to number if needed
                    if isinstance(value, str):
                        try:
                            value = float(value)
                        except ValueError:
                            value = 0
                    value_digits = SINGLE_DIGITS
                    if digits is not None and value_idx < len(digits):
                        value_digits = digits[value_idx]
                    result.append(
                        self.format_numeric_field(value, field_spec, value_digits))
                value_idx += 1

            if value_idx >= len(values) or not self.has_field():
                # Nothing left to place, or nowhere to place it - the caller
                # reports the second case, once the literal text is out.
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

    def format_numeric_field(self, value, spec, digits=SINGLE_DIGITS):
        """Format a number into a numeric field, the way PUFOUT does.

        The field is described by two counts, which is how the assembler
        carries it (f4.mac, the comment block above PUFOUT):

            lead    character positions to the left of the decimal point,
                    not counting the point
            trail   the point plus the positions to its right, or zero if
                    the field has no point

        The number is right-justified in lead+trail characters and trailing
        zeros are kept. Four rules are easy to miss, and all four were wrong
        here:

        * The value goes through the same conversion routine PRINT uses, so it
          is rounded to six significant figures (single) or sixteen (double)
          *before* the field rounds it to its own decimal places.
          PRINT USING "##,###.##"; 12345.67 is 12,345.70 on the real binary.
        * That second rounding is half away from zero, not Python's half to
          even: "##.##" of 1.005 is 1.01 and of -0.005 is -0.01.
        * The sign occupies one of the lead positions unless it is a trailing
          sign - or unless it is the space in front of a positive number,
          which is only ever written over padding. So "####" holds 1234 but
          overflows on -1234, which prints as %-1234.

        * A value below one keeps its leading zero only while there is room
          for it: "#.###" of -0.5 is -.500, and "##.###" of -0.5 is -0.500.
        """
        lead = spec['lead']
        trail = spec['trail']
        decimals = trail - 1 if trail else 0

        # b+c > 24 is "Illegal function call" on the real binary.
        if lead + trail > 24:
            raise ValueError("Illegal function call")

        try:
            magnitude = _mbasic_decimal(value, digits)
        except (ValueError, ArithmeticError):
            return str(value)                   # NaN/Infinity: nothing to imitate

        negative = _is_negative(value)

        if spec['exponential']:
            int_str, frac_str, suffix = self._exponential_parts(
                magnitude, lead, decimals, spec, digits)
        else:
            int_str, frac_str = self._fixed_parts(magnitude, decimals, spec)
            suffix = ''

        return self._assemble(int_str, frac_str, suffix, negative, lead, trail, spec)

    def _fixed_parts(self, magnitude, decimals, spec):
        """The integer and fraction digits of a fixed-point field."""
        quantum = Decimal(1).scaleb(-decimals)
        rounded = magnitude.quantize(quantum, rounding=ROUND_HALF_UP)
        text = format(rounded, 'f')
        int_str, _, frac_str = text.partition('.')
        if int_str == '0':
            # Written back in by _assemble only if the field has room - the
            # zero in front of the point is not worth an overflow.
            int_str = ''
        elif spec['comma']:
            int_str = self.add_thousand_separators(int_str)
        return int_str, frac_str

    def _exponential_parts(self, magnitude, lead, decimals, spec, digits):
        """The mantissa digits and E/D exponent of a ^^^^ field.

        How many digits the mantissa carries in front of the point is the
        field's business, not the value's: it is one per lead position, less
        the one the sign sits in. PRINT USING "#.#^^^^"; 1.5 is 0.2E+01 and
        "###.#^^^^"; 1.5 is  15.0E-01. A trailing sign leaves the lead
        positions alone, so "#.#^^^^-"; -1.5 is 1.5E+00-.
        """
        trailing = spec['trailing_sign'] or spec['trailing_minus_only']
        int_digits = lead if trailing else lead - 1
        if int_digits < 0:
            int_digits = 0

        exponent = 0
        if magnitude:
            # Scale so the mantissa has exactly int_digits digits in front of
            # the point - or lies in [0.1, 1) when the field allows none.
            exponent = magnitude.adjusted() + 1 - int_digits
            magnitude = magnitude.scaleb(-exponent)
            quantum = Decimal(1).scaleb(-decimals)
            magnitude = magnitude.quantize(quantum, rounding=ROUND_HALF_UP)
            # Rounding 9.99 in a one-digit mantissa carries into 10.0.
            limit = Decimal(1).scaleb(int_digits)
            if magnitude >= limit:
                magnitude = magnitude.scaleb(-1).quantize(quantum,
                                                          rounding=ROUND_HALF_UP)
                exponent += 1
        else:
            magnitude = magnitude.quantize(Decimal(1).scaleb(-decimals))

        text = format(magnitude, 'f')
        int_str, _, frac_str = text.partition('.')
        if int_str == '0':
            int_str = ''
        letter = 'D' if digits is not None and digits > SINGLE_DIGITS else 'E'
        sign = '+' if exponent >= 0 else '-'
        return int_str, frac_str, f"{letter}{sign}{abs(exponent):02d}"

    def _assemble(self, int_str, frac_str, suffix, negative, lead, trail, spec):
        """Lay the digits, sign, dollar and fill into the field."""
        trailing_sign = spec['trailing_sign'] or spec['trailing_minus_only']
        # A leading space in front of a positive number is only ever written
        # over padding, so it costs nothing; a '-', or the '+' of a +field,
        # takes a position of its own.
        sign_slot = not trailing_sign and (negative or spec['leading_sign'])

        needed = len(int_str) + (1 if spec['dollar_sign'] else 0) + (1 if sign_slot else 0)
        if not int_str and needed + 1 <= lead:
            int_str = '0'                       # room for it after all
            needed += 1

        body = int_str + ('.' + frac_str if trail else '') + suffix

        if sign_slot:
            sign = '-' if negative else '+'
        else:
            sign = ''

        if needed > lead:
            # Too big for the field: MBASIC prints % and lets the number run
            # over rather than truncating it.
            out = '%' + sign + ('$' if spec['dollar_sign'] else '') + body
        else:
            content = sign + ('$' if spec['dollar_sign'] else '') + body
            fill = '*' if spec['asterisk_fill'] else ' '
            out = fill * max(0, lead + trail + len(suffix) - len(content)) + content

        if spec['trailing_sign']:
            out += '-' if negative else '+'
        elif spec['trailing_minus_only']:
            out += '-' if negative else ' '
        return out

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
            start = _mid_start(to_integer(start))
            return s[start - 1:]
        elif len(args) == 3:
            s, start, length = args
            start = _mid_start(to_integer(start))
            length = to_integer(length)
            if length < 0 or length > 255:
                raise ValueError("Illegal function call")
            return s[start - 1:start - 1 + length]
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
