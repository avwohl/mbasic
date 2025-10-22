#!/usr/bin/env python3
"""
MBASIC 5.21 Interpreter

Usage:
    python3 mbasic.py             # Interactive mode
    python3 mbasic.py program.bas # Execute program
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from lexer import tokenize
from parser import Parser
from runtime import Runtime
from interpreter import Interpreter
from interactive import InteractiveMode


def run_file(program_path):
    """Execute a BASIC program from file"""
    try:
        # Read source code
        with open(program_path, 'r') as f:
            code = f.read()

        # Tokenize
        tokens = list(tokenize(code))

        # Parse
        parser = Parser(tokens)
        ast = parser.parse()

        # Setup runtime
        runtime = Runtime(ast)

        # Execute
        interpreter = Interpreter(runtime)
        interpreter.run()

    except FileNotFoundError:
        print(f"Error: File not found: {program_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        # No file specified - enter interactive mode
        interactive = InteractiveMode()
        interactive.start()
    else:
        # File specified - execute it
        program_path = sys.argv[1]
        run_file(program_path)


if __name__ == '__main__':
    main()
