"""
Integration tests for GOSUB/RETURN behavior
"""

import sys
from pathlib import Path
from io import StringIO

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from lexer import tokenize
from parser import parse
from runtime import Runtime
from interpreter import Interpreter
from iohandler.base import IOHandler


class StringIOHandler(IOHandler):
    """Simple IO handler that captures output to a string"""
    def __init__(self):
        self.output_buffer = StringIO()
        self.input_buffer = []

    def output(self, text: str, end: str = '\n') -> None:
        self.output_buffer.write(text + end)

    def input(self, prompt: str = '') -> str:
        if self.input_buffer:
            return self.input_buffer.pop(0)
        return ""

    def input_line(self, prompt: str = '') -> str:
        return self.input(prompt)

    def input_char(self) -> str:
        return ""

    def error(self, message: str) -> None:
        pass

    def clear_screen(self) -> None:
        pass

    def debug(self, message: str) -> None:
        pass

    def get_output(self) -> str:
        return self.output_buffer.getvalue()


def run_program(code):
    """Helper to run a BASIC program.

    Returns:
        tuple: (success: bool, output: str, error: str or None)
    """
    try:
        # Tokenize and parse
        tokens = tokenize(code)
        ast = parse(tokens)

        # Create runtime and interpreter
        runtime = Runtime(ast)

        io_handler = StringIOHandler()
        interpreter = Interpreter(runtime, io_handler)

        # Run program
        interpreter.run()

        return (True, io_handler.get_output(), None)

    except Exception as e:
        return (False, "", str(e))


def test_gosub_at_end_of_line():
    """Test RETURN from GOSUB at end of line continues at next line"""
    print("Testing GOSUB at end of line:")

    # Program with GOSUB at end of line
    # RETURN should continue at line 30 (next line after GOSUB)
    code = """
10 FOR I=0 TO 5
20 PRINT I
25 GOSUB 100
30 NEXT I
40 END
100 Q=1+1
110 J=J+2
120 RETURN
"""

    success, output, error = run_program(code)
    if not success:
        print(f"  ✗ Program failed: {error}")
        return False

    # Check that loop executed correctly (I should go from 0 to 5)
    lines = output.strip().split('\n')
    # PRINT adds spaces around numbers in BASIC
    expected_values = ['0 ', ' 1 ', ' 2 ', ' 3 ', ' 4 ', ' 5']

    if lines == expected_values:
        print("  ✓ GOSUB at end of line correctly returns to next line")
    else:
        print(f"  ✗ Expected output: {expected_values}")
        print(f"     Got output: {lines}")
        return False

    print("✓ GOSUB at end of line test passed\n")
    return True


def test_gosub_mid_line():
    """Test RETURN from GOSUB in middle of line continues at next statement"""
    print("Testing GOSUB in middle of line:")

    # Program with GOSUB in middle of line with colon-separated statements
    # RETURN should continue at PRINT "B" (statement after GOSUB)
    code = """
10 PRINT "A": GOSUB 100: PRINT "B"
20 END
100 PRINT "subroutine"
110 RETURN
"""

    success, output, error = run_program(code)
    if not success:
        print(f"  ✗ Program failed: {error}")
        return False

    # Check that output is correct
    lines = output.strip().split('\n')
    expected = ['A', 'subroutine', 'B']

    if lines == expected:
        print("  ✓ GOSUB in middle of line correctly returns to next statement")
    else:
        print(f"  ✗ Expected output: {expected}")
        print(f"     Got output: {lines}")
        return False

    print("✓ GOSUB mid-line test passed\n")
    return True


def test_nested_gosub():
    """Test nested GOSUB calls"""
    print("Testing nested GOSUB:")

    code = """
10 PRINT "main"
20 GOSUB 100
30 PRINT "done"
40 END
100 PRINT "sub1"
110 GOSUB 200
120 PRINT "back to sub1"
130 RETURN
200 PRINT "sub2"
210 RETURN
"""

    success, output, error = run_program(code)
    if not success:
        print(f"  ✗ Program failed: {error}")
        return False

    # Check that output is correct
    lines = output.strip().split('\n')
    expected = ['main', 'sub1', 'sub2', 'back to sub1', 'done']

    if lines == expected:
        print("  ✓ Nested GOSUB works correctly")
    else:
        print(f"  ✗ Expected output: {expected}")
        print(f"     Got output: {lines}")
        return False

    print("✓ Nested GOSUB test passed\n")
    return True


if __name__ == '__main__':
    print("=" * 60)
    print("GOSUB/RETURN Tests")
    print("=" * 60 + "\n")

    all_passed = True

    all_passed &= test_gosub_at_end_of_line()
    all_passed &= test_gosub_mid_line()
    all_passed &= test_nested_gosub()

    print("=" * 60)
    if all_passed:
        print("✓ All GOSUB/RETURN tests passed")
        sys.exit(0)
    else:
        print("✗ Some tests failed")
        sys.exit(1)
