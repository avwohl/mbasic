"""
Built-in functions for MBASIC 5.21.

All BASIC built-in functions (SIN, CHR$, INT, etc.)
"""

import math
import random
import sys
import select
import tty
import termios


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
    # String Functions
    # ========================================================================

    def ASC(self, s):
        """ASCII code of first character"""
        if not s:
            raise ValueError("Illegal function call: ASC of empty string")
        return ord(s[0])

    def CHR(self, x):
        """Character from ASCII code"""
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

    def PEEK(self, addr):
        """
        Peek memory (not implemented in interpreter).

        Returns 0 as safe default.
        """
        # Can't actually peek memory in Python interpreter
        return 0

    def INP(self, port):
        """
        Input from port (not implemented in interpreter).

        Returns 0 as safe default.
        """
        # Can't actually read from hardware ports
        return 0

    def POS(self, dummy):
        """
        Current print position.

        Returns approximate column (not fully implemented)
        """
        # Would need to track actual print position
        # For now, return 1
        return 1

    def EOF(self, file_num):
        """
        Test for end of file.

        Returns -1 if at EOF, 0 otherwise
        Note: For input files, respects ^Z (ASCII 26) as EOF marker (CP/M style)
        """
        file_num = int(file_num)
        if file_num not in self.runtime.files:
            raise ValueError(f"File #{file_num} not open")

        file_info = self.runtime.files[file_num]

        # Check EOF flag (set by input operations or ^Z detection)
        if file_info['eof']:
            return -1

        # For input files opened in binary mode, check for EOF or ^Z
        if file_info['mode'] == 'I':
            file_handle = file_info['handle']
            current_pos = file_handle.tell()

            # Peek at next byte to check for ^Z or EOF
            next_byte = file_handle.read(1)
            if not next_byte:
                # Physical EOF
                file_info['eof'] = True
                return -1
            elif next_byte[0] == 26:  # ^Z
                # CP/M EOF marker
                file_info['eof'] = True
                file_handle.seek(current_pos)  # Restore position
                return -1
            else:
                # Not at EOF, restore position
                file_handle.seek(current_pos)
                return 0

        # For output/append files, never at EOF
        return 0

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
        Read keyboard without waiting (non-blocking input).

        Returns a single character if a key is pressed, or empty string if not.
        This is the MBASIC INKEY$ function.
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

    def INPUT_STR(self, num, file_num=None):
        """
        INPUT$ - Read num characters from keyboard or file.

        INPUT$(n) - read n characters from keyboard
        INPUT$(n, #filenum) - read n characters from file
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

            file_handle = self.runtime.files[file_num]
            return file_handle.read(num)
