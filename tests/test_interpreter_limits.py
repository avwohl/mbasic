"""
Integration tests for interpreter resource limits
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
from resource_limits import ResourceLimits
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


def run_program(code, limits=None):
    """Helper to run a BASIC program with given limits.

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
        interpreter = Interpreter(runtime, io_handler, limits=limits)

        # Run program
        interpreter.run()

        return (True, io_handler.get_output(), None)

    except Exception as e:
        return (False, "", str(e))


def test_gosub_depth_limit():
    """Test GOSUB depth limit enforcement"""
    print("Testing GOSUB depth limit:")

    # Program with deep recursion
    code = """
10 N = 0
20 GOSUB 100
30 PRINT "Done"
40 END
100 N = N + 1
110 PRINT "Depth"; N
120 IF N < 10 THEN GOSUB 100
130 RETURN
"""

    # Should succeed with generous limits
    limits = ResourceLimits(max_gosub_depth=20)
    success, output, error = run_program(code, limits)
    if success:
        print("  ✓ Deep GOSUB succeeded with max_gosub_depth=20")
    else:
        print(f"  ✗ Unexpected error: {error}")
        return False

    # Should fail with tight limits
    limits = ResourceLimits(max_gosub_depth=3)
    success, output, error = run_program(code, limits)
    if not success and "GOSUB stack overflow" in error:
        print(f"  ✓ GOSUB correctly limited: {error}")
    else:
        print(f"  ✗ Should have raised GOSUB limit error, got: {error if not success else 'success'}")
        return False

    print("✓ GOSUB depth limit test passed\n")
    return True


def test_for_loop_depth_limit():
    """Test FOR loop depth limit enforcement"""
    print("Testing FOR loop depth limit:")

    # Program with nested loops
    code = """
10 FOR I = 1 TO 2
20   FOR J = 1 TO 2
30     FOR K = 1 TO 2
40       PRINT I; J; K
50     NEXT K
60   NEXT J
70 NEXT I
80 END
"""

    # Should succeed with generous limits
    limits = ResourceLimits(max_for_depth=5)
    success, output, error = run_program(code, limits)
    if success:
        print("  ✓ 3-deep FOR loops succeeded with max_for_depth=5")
    else:
        print(f"  ✗ Unexpected error: {error}")
        return False

    # Should fail with tight limits
    limits = ResourceLimits(max_for_depth=2)
    success, output, error = run_program(code, limits)
    if not success and "FOR loop nesting too deep" in error:
        print(f"  ✓ FOR correctly limited: {error}")
    else:
        print(f"  ✗ Should have raised FOR limit error, got: {error if not success else 'success'}")
        return False

    print("✓ FOR loop depth limit test passed\n")
    return True


def test_while_loop_depth_limit():
    """Test WHILE loop depth limit enforcement"""
    print("Testing WHILE loop depth limit:")

    # Program with nested WHILE loops
    code = """
10 I = 1
20 WHILE I <= 2
30   J = 1
40   WHILE J <= 2
50     K = 1
60     WHILE K <= 2
70       PRINT I; J; K
80       K = K + 1
90     WEND
100    J = J + 1
110  WEND
120  I = I + 1
130 WEND
140 END
"""

    # Should succeed with generous limits
    limits = ResourceLimits(max_while_depth=5)
    success, output, error = run_program(code, limits)
    if success:
        print("  ✓ 3-deep WHILE loops succeeded with max_while_depth=5")
    else:
        print(f"  ✗ Unexpected error: {error}")
        return False

    # Should fail with tight limits
    limits = ResourceLimits(max_while_depth=2)
    success, output, error = run_program(code, limits)
    if not success and "WHILE loop nesting too deep" in error:
        print(f"  ✓ WHILE correctly limited: {error}")
    else:
        print(f"  ✗ Should have raised WHILE limit error, got: {error if not success else 'success'}")
        return False

    print("✓ WHILE loop depth limit test passed\n")
    return True


def test_array_size_limit():
    """Test array size limit enforcement"""
    print("Testing array size limit:")

    # Small array
    code_small = """
10 DIM A(10)
20 FOR I = 0 TO 10
30   A(I) = I * 2
40 NEXT I
50 PRINT "Done"
60 END
"""

    # Should succeed
    limits = ResourceLimits(max_array_size=1000)
    success, output, error = run_program(code_small, limits)
    if success and "Done" in output:
        print("  ✓ Small array (10 elements) succeeded")
    else:
        print(f"  ✗ Unexpected error: {error}")
        return False

    # Large array
    code_large = """
10 DIM B(1000)
20 PRINT "Done"
30 END
"""

    # Should fail with tight limits (1000 SINGLE = 4000 bytes)
    limits = ResourceLimits(max_array_size=1000)
    success, output, error = run_program(code_large, limits)
    if not success and "Array" in error and "too large" in error:
        print(f"  ✓ Large array correctly limited: {error}")
    else:
        print(f"  ✗ Should have raised array size error, got: {error if not success else 'success'}")
        return False

    print("✓ Array size limit test passed\n")
    return True


def test_total_memory_limit():
    """Test total memory limit enforcement"""
    print("Testing total memory limit:")

    # Multiple arrays
    code = """
10 DIM A(50)
20 DIM B(50)
30 DIM C(50)
40 PRINT "Done"
50 END
"""

    # Should succeed with generous limits
    # 3 arrays * 51 elements * 4 bytes = 612 bytes
    limits = ResourceLimits(max_array_size=500, max_total_memory=1000)
    success, output, error = run_program(code, limits)
    if success and "Done" in output:
        print("  ✓ Multiple arrays succeeded with 1000 byte limit")
    else:
        print(f"  ✗ Unexpected error: {error}")
        return False

    # Should fail with tight total memory limit
    limits = ResourceLimits(max_array_size=500, max_total_memory=400)
    success, output, error = run_program(code, limits)
    if not success and "Out of memory" in error:
        print(f"  ✓ Total memory correctly limited: {error}")
    else:
        print(f"  ✗ Should have raised memory limit error, got: {error if not success else 'success'}")
        return False

    print("✓ Total memory limit test passed\n")
    return True


def test_clear_resets_limits():
    """Test that CLEAR resets resource limit tracking"""
    print("Testing CLEAR resets limits:")

    code = """
10 DIM A(100)
20 CLEAR
30 DIM B(100)
40 PRINT "Done"
50 END
"""

    # With tight limits, should succeed because CLEAR frees A
    # 101 elements * 4 bytes = 404 bytes per array
    limits = ResourceLimits(max_array_size=500, max_total_memory=500)
    success, output, error = run_program(code, limits)
    if success and "Done" in output:
        print("  ✓ CLEAR correctly reset memory tracking")
    else:
        print(f"  ✗ CLEAR should have freed memory, got error: {error}")
        return False

    print("✓ CLEAR resets limits test passed\n")
    return True


def test_erase_frees_memory():
    """Test that ERASE frees array from limits"""
    print("Testing ERASE frees memory:")

    code = """
10 DIM A(100)
20 ERASE A
30 DIM B(100)
40 PRINT "Done"
50 END
"""

    # Should succeed because ERASE frees A
    limits = ResourceLimits(max_array_size=500, max_total_memory=500)
    success, output, error = run_program(code, limits)
    if success and "Done" in output:
        print("  ✓ ERASE correctly freed memory")
    else:
        print(f"  ✗ ERASE should have freed memory, got error: {error}")
        return False

    print("✓ ERASE frees memory test passed\n")
    return True


def test_redim_limits():
    """Test that re-dimensioning checks limits correctly"""
    print("Testing re-dimension limits:")

    # Re-dimension to smaller array should succeed
    code = """
10 DIM A(100)
20 DIM A(50)
30 PRINT "Done"
40 END
"""

    limits = ResourceLimits(max_array_size=500, max_total_memory=500)
    success, output, error = run_program(code, limits)
    if success and "Done" in output:
        print("  ✓ Re-dimension to smaller size succeeded")
    else:
        print(f"  ✗ Unexpected error: {error}")
        return False

    print("✓ Re-dimension limits test passed\n")
    return True


def run_all_tests():
    """Run all integration tests"""
    tests = [
        test_gosub_depth_limit,
        test_for_loop_depth_limit,
        test_while_loop_depth_limit,
        test_array_size_limit,
        test_total_memory_limit,
        test_clear_resets_limits,
        test_erase_frees_memory,
        test_redim_limits,
    ]

    print("=" * 60)
    print("INTERPRETER RESOURCE LIMITS INTEGRATION TESTS")
    print("=" * 60)
    print()

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}\n")
            import traceback
            traceback.print_exc()
            failed += 1

    print("=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
