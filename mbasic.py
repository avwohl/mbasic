#!/usr/bin/env python3
"""
MBASIC 5.21 Interpreter

Usage:
    python3 mbasic.py             # Interactive mode
    python3 mbasic.py program.bas # Execute program
"""

import sys
import os
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
        # Use InteractiveMode to support CHAIN command
        interactive = InteractiveMode()

        # Load the program
        with open(program_path, 'r') as f:
            code = f.read()

        # Parse and store lines
        parse_errors = False
        for line in code.split('\n'):
            line = line.strip()
            if not line:
                continue

            match = __import__('re').match(r'^(\d+)\s', line)
            if match:
                line_num = int(match.group(1))
                interactive.lines[line_num] = line
                line_ast = interactive.parse_single_line(line, basic_line_num=line_num)
                if line_ast:
                    interactive.line_asts[line_num] = line_ast
                else:
                    parse_errors = True

        # Don't run if there were parse errors, but still enter interactive mode
        if not parse_errors:
            # Only auto-run if no parse errors
            interactive.cmd_run()

        # Enter interactive mode (whether there were parse errors or not)
        interactive.start()

    except FileNotFoundError:
        print(f"Error: File not found: {program_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        # Print traceback only in DEBUG mode
        if os.environ.get('DEBUG'):
            import traceback
            traceback.print_exc()
        else:
            print(f"Error: {e}", file=sys.stderr)
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
