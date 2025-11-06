"""
Built-in functions for MBASIC 5.21.

BASIC built-in functions (SIN, CHR$, INT, etc.) and formatting utilities (TAB, SPC, USING).
"""

import math
import random
import sys
import select
import tty
import termios


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
        - leading_sign: + at start, adds + or - sign
        - trailing_sign: + at end, adds + or - sign
        - trailing_minus_only: - at end, adds - for negative or space for non-negative (always 1 char)
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
            'trailing_minus_only': False,  # - at end only (always adds 1 char: - or space)
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
        # original_negative was captured before rounding (line 269 above), allowing us to detect
        # cases like -0.001 which round to 0 but should display as "-0" (not "0").
        # This matches BASIC behavior. Positive values that round to zero display as "0".
        if rounded == 0 and original_negative:
            is_negative = True
        else:
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
            # Number too large - prepend % and return as-is
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
        # Add sign to content width (trailing_minus_only ALWAYS adds a char, - or space)
        if spec['leading_sign'] or spec['trailing_sign'] or spec['trailing_minus_only']:
            content_width += 1

        padding_needed = field_width - content_width

        # Build result
        result_parts = []

        # For leading sign: padding comes first, then sign immediately before number
        if spec['leading_sign']:
            # Add padding first (but only spaces, not asterisks for leading sign)
            result_parts.append(' ' * max(0, padding_needed))
            # Then the sign
            result_parts.append('-' if is_negative else '+')
        else:
            # No leading sign: add padding/asterisk fill first
            if spec['asterisk_fill']:
                result_parts.append('*' * max(0, padding_needed))
            else:
                result_parts.append(' ' * max(0, padding_needed))

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

    def __init__(self, runtime):
        self.runtime = runtime

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
        Random number.

        MBASIC RND behavior:
        - RND(1) or RND: return random number 0 to 1
        - RND(0): return last random number
        - RND(negative): seed and return random number
        """
        if x is None or x > 0:
            # Generate new random number
            value = random.random()
            self.runtime.rnd_last = value
            return value
        elif x == 0:
            # Return last random number
            return self.runtime.rnd_last
        else:
            # Seed random number generator
            random.seed(abs(x))
            value = random.random()
            self.runtime.rnd_last = value
            return value

    # ========================================================================
    # Type Conversion Functions
    # ========================================================================

    def CINT(self, x):
        """Convert to integer (round to nearest)"""
        return int(round(x))

    def CSNG(self, x):
        """Convert to single precision"""
        return float(x)

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
        """CHR$ - Character from ASCII code"""
        code = int(x)
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
            start = int(start)
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
        """Left n characters of string"""
        n = int(n)
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
            start = int(start)
            return s[start-1:] if start > 0 else s
        elif len(args) == 3:
            s, start, length = args
            start = int(start)
            length = int(length)
            if start < 1:
                start = 1
            return s[start-1:start-1+length]
        else:
            raise ValueError("MID$ requires 2 or 3 arguments")

    def OCT(self, x):
        """Octal string representation"""
        return oct(int(x))[2:]  # Remove '0o' prefix

    def RIGHT(self, s, n):
        """Right n characters of string"""
        n = int(n)
        return s[-n:] if n > 0 else ""

    def SPACE(self, n):
        """String of n spaces"""
        n = int(n)
        return " " * n

    def STR(self, x):
        """
        Convert number to string.

        BASIC STR$ adds a leading space for positive numbers
        """
        if x >= 0:
            return " " + str(x)
        else:
            return str(x)

    def STRING(self, n, char):
        """
        Repeat character n times.

        STRING$(n, code) - repeat CHR$(code) n times
        STRING$(n, string) - repeat first char of string n times
        """
        n = int(n)
        if isinstance(char, str):
            # String argument - use first character
            c = char[0] if char else " "
        else:
            # Numeric argument - convert to character
            c = chr(int(char))
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
        Peek memory (compatibility implementation).

        Returns random value 0-255. Most programs use PEEK to seed
        random number generators, so this provides reasonable compatibility.
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
        return TabMarker(int(n))

    def SPC(self, n):
        """
        SPC(n) - Print n spaces in PRINT statement.

        Returns a marker object that PRINT interprets as "print n spaces".
        """
        return SpcMarker(int(n))

    def EOF(self, file_num):
        """
        Test for end of file.

        Returns -1 if at EOF, 0 otherwise

        Note: For binary input files (mode 'I' from OPEN statement), respects ^Z (ASCII 26)
        as EOF marker (CP/M style). Mode 'I' is set by the OPEN statement for binary input.
        Text mode files and output files use standard Python EOF detection.
        """
        file_num = int(file_num)
        if file_num not in self.runtime.files:
            raise ValueError(f"File #{file_num} not open")

        file_info = self.runtime.files[file_num]

        # Check EOF flag (set by input operations or ^Z detection)
        if file_info['eof']:
            return -1

        # For input files opened in binary mode, check for EOF or ^Z
        # Mode 'I' = binary input mode where ^Z checking is appropriate
        if file_info['mode'] == 'I':
            file_handle = file_info['handle']
            current_pos = file_handle.tell()

            # Peek at next byte to check for ^Z or EOF
            # File opened in binary mode ('rb') per mode 'I' check above
            # read(1) returns bytes object; next_byte[0] accesses the first byte value as integer
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
        """
        # Platform-specific implementation
        if sys.platform == 'win32':
            # Windows implementation
            try:
                import msvcrt
                if msvcrt.kbhit():
                    char = msvcrt.getch()
                    # Handle bytes on Python 3
                    if isinstance(char, bytes):
                        return char.decode('utf-8', errors='ignore')
                    return char
                return ""
            except ImportError:
                # msvcrt not available, return empty string
                return ""
        else:
            # Unix/Linux/Mac implementation using select
            # Check if stdin is a TTY first
            if not sys.stdin.isatty():
                # Not a TTY (probably piped input or file), can't do non-blocking read
                return ""

            try:
                # Check if stdin has data available without blocking
                readable, _, _ = select.select([sys.stdin], [], [], 0)

                if readable:
                    # There's input available - read one character
                    # We need to set terminal to raw mode temporarily
                    fd = sys.stdin.fileno()
                    old_settings = termios.tcgetattr(fd)
                    try:
                        tty.setraw(fd)
                        char = sys.stdin.read(1)
                        return char
                    finally:
                        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                else:
                    # No input available
                    return ""
            except (OSError, IOError):
                # If anything goes wrong with terminal operations, return empty string
                return ""

    def INPUT(self, num, file_num=None):
        """
        INPUT$ - Read num characters from keyboard or file.
        (Method name is INPUT since Python doesn't allow $ in names)

        BASIC syntax:
            INPUT$(n) - read n characters from keyboard
            INPUT$(n, #filenum) - read n characters from file

        Python call syntax (from interpreter):
            INPUT(n) - read n characters from keyboard
            INPUT(n, filenum) - read n characters from file

        Note: The # prefix in BASIC syntax is stripped by the parser before calling this method.
        """
        num = int(num)

        if file_num is None:
            # Read from keyboard
            result = ""
            for i in range(num):
                char = sys.stdin.read(1)
                if not char:
                    break
                result += char
            return result
        else:
            # Read from file
            file_num = int(file_num)
            if file_num not in self.runtime.files:
                raise ValueError(f"File #{file_num} not open")

            # self.runtime.files[file_num] returns a dict with 'handle', 'mode', 'eof' keys
            # Extract the file handle from the file_info dict to perform read operations
            # (this pattern is used by EOF(), LOC(), LOF(), and other file functions)
            file_info = self.runtime.files[file_num]
            file_handle = file_info['handle']
            return file_handle.read(num)
