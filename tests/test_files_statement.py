#!/usr/bin/env python3
"""
Test FILES statement execution with FileIO module.
"""

import sys
import os
import tempfile
from pathlib import Path

# Add parent to path so we can import from src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.runtime import Runtime
from src.interpreter import Interpreter
from src.file_io import RealFileIO
from src.iohandler.console import ConsoleIOHandler
from src.lexer import tokenize
from src.parser import Parser


class OutputCapture:
    """Capture output from interpreter."""
    def __init__(self):
        self.lines = []

    def output(self, text, end='\n'):
        """Output text (matches IOHandler interface)."""
        self.lines.append(text)
        print(f"  OUTPUT: {text}", end=end)

    def input(self, prompt=""):
        return ""


def test_files_statement():
    """Test FILES statement with real interpreter."""

    print("Testing FILES statement with Interpreter...")

    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)

        # Create test files
        Path("test1.bas").write_text("10 PRINT 1\n")
        Path("test2.bas").write_text("10 PRINT 2\n")
        Path("readme.txt").write_text("readme\n")

        # Parse FILES statement
        code = "0 FILES"
        tokens = list(tokenize(code))
        parser = Parser(tokens, {})
        ast = parser.parse()

        # Create runtime and interpreter with RealFileIO
        runtime = Runtime({}, {})
        io_handler = OutputCapture()
        file_io = RealFileIO()

        interpreter = Interpreter(runtime, io_handler, file_io=file_io)

        # Execute FILES statement
        print("\nExecuting: FILES")
        statement = ast.lines[0].statements[0]
        interpreter.execute_statement(statement)

        # Check output
        output_text = "\n".join(io_handler.lines)
        print(f"\nCaptured output:\n{output_text}")

        assert "test1.bas" in output_text
        assert "test2.bas" in output_text
        assert "readme.txt" in output_text
        assert "File(s)" in output_text

        print("\n✅ FILES statement works with Interpreter!")


def test_files_with_pattern():
    """Test FILES with filespec pattern."""

    print("\n\nTesting FILES with pattern...")

    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)

        # Create test files
        Path("test1.bas").write_text("10 PRINT 1\n")
        Path("test2.bas").write_text("10 PRINT 2\n")
        Path("readme.txt").write_text("readme\n")

        # Parse FILES "*.BAS" statement
        code = '0 FILES "*.bas"'
        tokens = list(tokenize(code))
        parser = Parser(tokens, {})
        ast = parser.parse()

        # Create runtime and interpreter
        runtime = Runtime({}, {})
        io_handler = OutputCapture()
        file_io = RealFileIO()

        interpreter = Interpreter(runtime, io_handler, file_io=file_io)

        # Execute FILES statement
        print('\nExecuting: FILES "*.bas"')
        statement = ast.lines[0].statements[0]
        interpreter.execute_statement(statement)

        # Check output
        output_text = "\n".join(io_handler.lines)
        print(f"\nCaptured output:\n{output_text}")

        assert "test1.bas" in output_text
        assert "test2.bas" in output_text
        assert "readme.txt" not in output_text  # Should be filtered out
        assert "File(s)" in output_text

        print("\n✅ FILES with pattern works!")


def test_files_in_program():
    """Test FILES statement inside a BASIC program."""

    print("\n\nTesting FILES inside a program...")

    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)

        # Create test files
        Path("data1.txt").write_text("data\n")
        Path("data2.txt").write_text("data\n")

        # Create BASIC program with FILES statement
        program_code = """
10 PRINT "Listing files:"
20 FILES "*.txt"
30 PRINT "Done"
"""

        tokens = list(tokenize(program_code))
        parser = Parser(tokens, {})
        ast = parser.parse()

        # Build line_asts
        line_asts = {}
        lines = {}
        for line_node in ast.lines:
            line_asts[line_node.line_number] = line_node
            # Reconstruct line text
            line_text = f"{line_node.line_number} "
            lines[line_node.line_number] = line_text

        # Create runtime and interpreter
        runtime = Runtime(line_asts, lines)
        io_handler = OutputCapture()
        file_io = RealFileIO()

        interpreter = Interpreter(runtime, io_handler, file_io=file_io)

        # Run the program
        print("\nRunning program with FILES statement...")
        state = interpreter.start()

        # Execute until done
        while interpreter.runtime.pc.is_running() and state.error_info is None:
            state = interpreter.tick()

        # Check output
        output_text = "\n".join(io_handler.lines)
        print(f"\nProgram output:\n{output_text}")

        assert "Listing files:" in output_text
        assert "data1.txt" in output_text
        assert "data2.txt" in output_text
        assert "Done" in output_text

        print("\n✅ FILES works inside programs!")


if __name__ == "__main__":
    try:
        test_files_statement()
        test_files_with_pattern()
        test_files_in_program()

        print("\n" + "="*60)
        print("ALL FILES STATEMENT TESTS PASSED ✅")
        print("="*60)
        print("\nConclusion:")
        print("- RealFileIO works correctly")
        print("- Interpreter integration works")
        print("- FILES statement works in immediate mode")
        print("- FILES statement works inside programs")
        print("- Pattern matching works")
        print("\nNext step: Test SandboxedFileIO in web UI")

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
