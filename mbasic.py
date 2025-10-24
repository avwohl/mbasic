#!/usr/bin/env python3
"""
MBASIC 5.21 Interpreter

Usage:
    python3 mbasic.py                    # Interactive mode (CLI)
    python3 mbasic.py program.bas        # Execute program
    python3 mbasic.py --backend cli      # Explicitly use CLI backend
    python3 mbasic.py --backend visual   # Use visual backend (stub)
    python3 mbasic.py --debug            # Enable debug output
"""

import sys
import os
import argparse
import importlib
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from parser import TypeInfo


def create_default_def_type_map():
    """Create default DEF type map (all SINGLE precision)"""
    def_type_map = {}
    for letter in 'abcdefghijklmnopqrstuvwxyz':
        def_type_map[letter] = TypeInfo.SINGLE
    return def_type_map


def load_backend(backend_name, io_handler, program_manager):
    """Load a UI backend dynamically using importlib

    Args:
        backend_name: Name of backend ('cli' or 'visual')
        io_handler: IOHandler instance for I/O operations
        program_manager: ProgramManager instance for program storage

    Returns:
        UIBackend instance

    Raises:
        ImportError: If backend module cannot be loaded
        AttributeError: If backend doesn't have required classes
    """
    try:
        # Import the backend module
        backend_module = importlib.import_module(f'ui.{backend_name}')

        # Get the backend class (CLIBackend, VisualBackend, etc.)
        backend_class_name = f'{backend_name.upper()}Backend' if backend_name == 'cli' else f'{backend_name.capitalize()}Backend'
        backend_class = getattr(backend_module, backend_class_name)

        # Create and return the backend instance
        return backend_class(io_handler, program_manager)

    except ImportError as e:
        raise ImportError(f"Failed to load backend '{backend_name}': {e}")
    except AttributeError as e:
        raise AttributeError(f"Backend '{backend_name}' does not have class '{backend_class_name}': {e}")


def run_file(program_path, backend, debug_enabled=False):
    """Execute a BASIC program from file

    Args:
        program_path: Path to BASIC program file
        backend: UIBackend instance to use
        debug_enabled: Enable debug output
    """
    try:
        # Load the program using ProgramManager
        success, errors = backend.program.load_from_file(program_path)

        # Report any errors
        if errors:
            for line_num, error_msg in errors:
                print(f"Parse error at line {line_num}: {error_msg}", file=sys.stderr)

        # Run the program if it loaded successfully
        if success:
            backend.cmd_run()
        else:
            print(f"Failed to load program: {program_path}", file=sys.stderr)
            sys.exit(1)

        # Enter interactive mode after running
        backend.start()

    except FileNotFoundError:
        print(f"Error: File not found: {program_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        # Print traceback only in DEBUG mode
        if debug_enabled or os.environ.get('DEBUG'):
            import traceback
            traceback.print_exc()
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(
        description='MBASIC 5.21 Interpreter',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 mbasic.py                    # Interactive mode (CLI)
  python3 mbasic.py program.bas        # Run program and enter interactive mode
  python3 mbasic.py --backend cli      # Explicitly use CLI backend
  python3 mbasic.py --backend visual   # Use visual backend (stub)
  python3 mbasic.py --debug            # Enable debug output
        """
    )

    parser.add_argument(
        'program',
        nargs='?',
        help='BASIC program file to load and run'
    )

    parser.add_argument(
        '--backend',
        choices=['cli', 'visual'],
        default='cli',
        help='UI backend to use (default: cli)'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output'
    )

    args = parser.parse_args()

    # Create I/O handler based on backend choice
    if args.backend == 'cli':
        from iohandler.console import ConsoleIOHandler
        io_handler = ConsoleIOHandler(debug_enabled=args.debug)
    elif args.backend == 'visual':
        # For now, visual backend uses console I/O (stub)
        from iohandler.console import ConsoleIOHandler
        io_handler = ConsoleIOHandler(debug_enabled=args.debug)
        print("Note: Visual backend is a stub, using console I/O")

    # Create program manager
    from editing import ProgramManager
    program_manager = ProgramManager(create_default_def_type_map())

    # Load backend dynamically
    try:
        backend = load_backend(args.backend, io_handler, program_manager)
    except (ImportError, AttributeError) as e:
        print(f"Error loading backend: {e}", file=sys.stderr)
        sys.exit(1)

    # Run program or enter interactive mode
    if args.program:
        run_file(args.program, backend, debug_enabled=args.debug)
    else:
        backend.start()


if __name__ == '__main__':
    main()
